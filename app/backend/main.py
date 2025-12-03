from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .schemas import (
    MedsRequest, IDRequest, AnalysisRequest, ReportRequest,
    InteractionResponse, FoodResponse, ReferenceResponse, ReportResponse, SeverityResponse,
    MechanismResponse, RecommendationResponse, RiskResponse,
    DrugSearchResult
)
from .services.resolver import DrugResolver
from .services.interaction import InteractionEngine
from .services.summarizer import ClinicalSummarizer
from .database import db_manager

app = FastAPI(title="Medication Interaction Checker")



#1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*", "ngrok-skip-browser-warning"],  # Explicitly allow ngrok header
)

#2. Initialize Services
resolver = DrugResolver()
engine = InteractionEngine()
summarizer = ClinicalSummarizer()

# HELPER: Context Fetcher
def fetch_contexts(interactions):
    drug_contexts = {}
    involved_ids = set()
    for i in interactions:
        involved_ids.add(i.drug_a)
        involved_ids.add(i.drug_b)
        
    for uid in involved_ids:
        drug_contexts[uid] = summarizer.get_drug_context(uid)
    return drug_contexts

# ENDPOINTS:

# 1. Search (Autocomplete)
@app.get("/search", response_model=List[DrugSearchResult])
async def search_drugs(q: str = Query(..., min_length=2)):
    try:
        search_term = q.strip()
        results = set()
        limit = 50
        
        # Search Mixtures (Brands)
        res_mix = db_manager.query("SELECT name, drugbank_id FROM mixtures WHERE name LIKE ? LIMIT ?", (f"%{search_term}%", limit))
        for r in res_mix: 
            results.add((r['name'], r['drugbank_id'], "Brand"))
            
        # Search Generics
        res_gen = db_manager.query("SELECT name, drugbank_id FROM general_info WHERE name LIKE ? LIMIT ?", (f"%{search_term}%", limit))
        for r in res_gen: 
            results.add((r['name'], r['drugbank_id'], "Generic"))
            
        # Search Synonyms
        res_syn = db_manager.query("SELECT synonym, drugbank_id FROM synonyms WHERE synonym LIKE ? LIMIT ?", (f"%{search_term}%", limit))
        for r in res_syn: 
            results.add((r['synonym'], r['drugbank_id'], "Synonym"))
        
        # Format
        final_results = []
        for name, did, dtype in results:
            final_results.append({"name": name, "id": did, "type": dtype})

        # Sort: Starts With -> Length
        def sort_key(item):
            name_lower = item['name'].lower()
            q_lower = search_term.lower()
            starts_with = 0 if name_lower.startswith(q_lower) else 1
            length = len(item['name'])
            return (starts_with, length)

        sorted_results = sorted(final_results, key=sort_key)
        return sorted_results[:10]
        
    except Exception as e:
        print(f"Search Error: {e}")
        return []

# 2. Interactions 
@app.post("/analyze/interactions", response_model=InteractionResponse)
async def get_interactions(request: MedsRequest):
    if len(request.medications) > 5:
        raise HTTPException(status_code=400, detail="Max 5 medications allowed.")
    
    # Call resolver
    resolved_map = resolver.resolve_input(request.medications)
    unique_ids = list(set(resolved_map.values()))
    
    if len(unique_ids) < 2:
        return InteractionResponse(
            resolved_medications=resolved_map,
            interactions_found=[]
        )

    interactions = engine.check_interactions(unique_ids)
    
    return InteractionResponse(
        resolved_medications=resolved_map,
        interactions_found=interactions
    )

# 3. Food Warnings
@app.post("/analyze/food", response_model=FoodResponse)
async def get_food_warnings(request: IDRequest):
    warnings = {}
    for uid in request.drug_ids:
        name_res = db_manager.query("SELECT name FROM general_info WHERE drugbank_id = ?", (uid,))
        name = name_res[0]['name'] if name_res else uid
        
        food_res = db_manager.query("SELECT interaction FROM food_interactions WHERE drugbank_id = ?", (uid,))
        if food_res:
            warnings[name] = [r['interaction'] for r in food_res]
            
    return FoodResponse(food_warnings=warnings)

# 4. References
@app.post("/analyze/references", response_model=ReferenceResponse)
async def get_references(request: IDRequest):
    refs = {}
    for uid in request.drug_ids:
        name_res = db_manager.query("SELECT name FROM general_info WHERE drugbank_id = ?", (uid,))
        name = name_res[0]['name'] if name_res else uid
        
        drug_refs = {"articles": [], "links": [], "attachments": [], "books": []}
        
        try:
            # Articles
            res_art = db_manager.query("SELECT citation, pubmed_id FROM ref_articles WHERE drugbank_id = ? LIMIT 5", (uid,))
            drug_refs["articles"] = [f"{r['citation']} (PMID: {r['pubmed_id']})" if r['pubmed_id'] else r['citation'] for r in res_art]
            
            # Attachments
            res_att = db_manager.query("SELECT title, url FROM ref_attachments WHERE drugbank_id = ? LIMIT 5", (uid,))
            drug_refs["attachments"] = [f"{r['title']}: {r['url']}" for r in res_att]

            # Books
            res_book = db_manager.query("SELECT citation, isbn FROM ref_books WHERE drugbank_id = ? LIMIT 5", (uid,))
            drug_refs["books"] = [f"{r['citation']} (ISBN: {r['isbn']})" if r['isbn'] else r['citation'] for r in res_book]

            # Links
            res_link = db_manager.query("SELECT title, url FROM ref_links WHERE drugbank_id = ? LIMIT 5", (uid,))
            drug_refs["links"] = [f"{r['title']}: {r['url']}" for r in res_link]

        except Exception as e:
            print(f"Reference Fetch Error for {uid}: {e}")
            
        refs[name] = drug_refs
        
    return ReferenceResponse(references=refs)

# 5. Severity Classification
@app.post("/analyze/severity", response_model=SeverityResponse)
async def classify_severity(request: AnalysisRequest): 
    interactions_list = [i.model_dump() for i in request.interactions]
    results = summarizer.classify_severity_batch(interactions_list)
    return SeverityResponse(results=results) 

# 6. Mechanism Explanation
@app.post("/analyze/mechanism", response_model=MechanismResponse)
async def explain_mechanism(request: AnalysisRequest):
    drug_contexts = fetch_contexts(request.interactions)
    interactions_list = [i.model_dump() for i in request.interactions]
    results = summarizer.generate_interaction_summary_batch(interactions_list)
    
    final_results = []
    for r in results:
        final_results.append({
            "drug_a": r['drug_a'], 
            "drug_b": r['drug_b'], 
            "interaction_summary": r['interaction_summary'] 
        })
    return MechanismResponse(results=final_results)

# 7. Clinical Recommendation
@app.post("/analyze/recommendation", response_model=RecommendationResponse)
async def give_recommendation(request: AnalysisRequest):
    drug_contexts = fetch_contexts(request.interactions)
    interactions_list = [i.model_dump() for i in request.interactions]
    results = summarizer.generate_recommendation_batch(interactions_list, drug_contexts)
    return RecommendationResponse(results=results) 

# 8. Patient Risk Assessment
@app.post("/analyze/risk", response_model=RiskResponse)
async def assess_risk(request: AnalysisRequest):
    drug_contexts = fetch_contexts(request.interactions)
    interactions_list = [i.model_dump() for i in request.interactions]
    
    results = summarizer.generate_risk_batch(
        interactions_list, 
        drug_contexts, 
        request.patient.model_dump()
    )
    return RiskResponse(results=results) 

#  Full Report
@app.post("/analyze/report", response_model=ReportResponse)
async def get_ai_report(request: ReportRequest):
    drug_contexts = fetch_contexts(request.interactions)
    interactions_list = [i.model_dump() for i in request.interactions]

    # Get Structured Cards
    cards = summarizer.generate_structured_analysis(
        interactions_list,
        drug_contexts,
        request.patient.model_dump()
    )
    
    severity_map = summarizer.classify_severity_batch(interactions_list)
    
    for i, card in enumerate(cards):
        if i < len(severity_map):
            card['severity'] = severity_map[i]['severity']

    return ReportResponse(
        clinical_analysis="See cards below", 
        analysis_cards=cards 
    )



'''
Example:

high: Isotretinoin, Doxycycline
morderate: Calcium carbonate, Doxycycline
low: Digoxin, Metronidazole [Metrogel]
none: Acetaminophen, Ethyl loflazepate
'''