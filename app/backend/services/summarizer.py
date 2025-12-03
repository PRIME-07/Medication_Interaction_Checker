import requests
import json
from typing import List, Dict, Any
from ..database import db_manager
from ..config import OLLAMA_URL, MODEL_NAME

class ClinicalSummarizer:
    """Context & LLM Generation"""
    
    def __init__(self):
        self.db = db_manager

    def get_drug_context(self, drug_id: str) -> Dict:
        context = {}
        # General Info
        res = self.db.query("SELECT name, description FROM general_info WHERE drugbank_id = ?", (drug_id,))
        if res:
            context['name'] = res[0]['name']
            context['desc'] = res[0]['description']
        
        # Pharmacology
        res = self.db.query("SELECT mechanism_of_action, toxicity, clearance, pharmacodynamics FROM pharmacology WHERE drugbank_id = ?", (drug_id,))
        if res:
            pharm_data = dict(res[0])
            context.update({k: v for k, v in pharm_data.items() if v})
            
        return context

    def _call_llm(self, prompt: str, temp: float = 0.1) -> Dict:
        try:
            resp = requests.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temp},
                "format": "json" 
            })
            if resp.status_code == 200:
                return json.loads(resp.json()['response'])
            return None
        except Exception as e:
            print(f"LLM Error: {e}")
            return None

    def _sanitize_string(self, value: Any, default: str) -> str:
        """
        Ensures the output is a flat string, even if LLM returns a dict/list.
        """
        if not value:
            return default
        
        if isinstance(value, str):
            return value
            
        if isinstance(value, (dict, list)):
            # If LLM returned a complex object, try to dump it to string extract values if it's a simple dict
            try:
                if isinstance(value, dict):
                    # Try to join values if they are strings
                    return ". ".join([str(v) for v in value.values() if isinstance(v, (str, int, float))])
                return json.dumps(value)
            except:
                return str(value)
                
        return str(value)

    # 1. Severity
    def classify_severity_batch(self, interactions: List[Dict]) -> List[Dict]:
        results = []
        for inter in interactions:
            prompt = f"""
            Classify severity. Description: "{inter['description']}"
            RULES:
            - HIGH: Life-threatening, permanent damage, intracranial pressure, hospitalization.
            - MODERATE: Therapy modification/monitoring required.
            - LOW: Minor effects.
            Return JSON: {{ "severity": "High/Moderate/Low", "reason": "Short 5-word summary" }}
            """
            data = self._call_llm(prompt, 0.0)
            results.append({
                "drug_a": inter['drug_a'],
                "drug_b": inter['drug_b'],
                "severity": self._sanitize_string(data.get("severity") if data else None, "Unknown"),
                "short_reason": self._sanitize_string(data.get("reason") if data else None, "Analysis failed")
            })
        return results

    # 2. Interaction Summary
    def generate_interaction_summary_batch(self, interactions: List[Dict]) -> List[Dict]:
        results = []
        for inter in interactions:
            prompt = f"""
            Summarize this drug interaction in 1 clear sentence for a doctor.
            Input Description: "{inter['description']}"
            Return JSON: {{ "summary": "..." }}
            """
            data = self._call_llm(prompt, 0.2)
            
            summary_text = inter['description'] # Fallback
            if data:
                summary_text = self._sanitize_string(data.get("summary"), inter['description'])

            results.append({
                "drug_a": inter['drug_a'],
                "drug_b": inter['drug_b'],
                "interaction_summary": summary_text
            })
        return results

    # 3. Clinical Recommendations
    def generate_recommendation_batch(self, interactions: List[Dict], drug_contexts: Dict) -> List[Dict]:
        results = []
        for inter in interactions:
            id_a, id_b = inter['drug_a'], inter['drug_b']
            ctx_a = drug_contexts.get(id_a, {})
            ctx_b = drug_contexts.get(id_b, {})
            
            def extract_recomm_fields(ctx):
                return {
                    "Indication": ctx.get('indication', 'N/A'),
                    "Mechanism": ctx.get('mechanism_of_action', 'N/A'),
                    "Toxicity": ctx.get('toxicity', 'N/A')
                }

            context_text = {
                ctx_a.get('name', id_a): extract_recomm_fields(ctx_a),
                ctx_b.get('name', id_b): extract_recomm_fields(ctx_b)
            }

            prompt = f"""
            Provide a CLINICAL RECOMMENDATION (2-3 lines).
            Interaction: "{inter['description']}"
            Context: {json.dumps(context_text)}
            Return JSON: {{ "recommendation": "..." }}
            """
            
            data = self._call_llm(prompt, 0.2)
            results.append({
                "drug_a": inter['drug_a'],
                "drug_b": inter['drug_b'],
                "recommendation": self._sanitize_string(data.get("recommendation") if data else None, "Monitor patient closely.")
            })
        return results

    # 4. Patient Risk
    def generate_risk_batch(self, interactions: List[Dict], drug_contexts: Dict, patient: Dict) -> List[Dict]:
        results = []
        for inter in interactions:
            id_a, id_b = inter['drug_a'], inter['drug_b']
            ctx_a = drug_contexts.get(id_a, {})
            ctx_b = drug_contexts.get(id_b, {})
            
            def extract_risk_fields(ctx):
                return {
                    "Metabolism": ctx.get('metabolism', 'N/A'),
                    "Clearance": ctx.get('clearance', 'N/A'),
                    "Toxicity": ctx.get('toxicity', 'N/A')
                }

            context_text = {
                ctx_a.get('name', id_a): extract_risk_fields(ctx_a),
                ctx_b.get('name', id_b): extract_risk_fields(ctx_b)
            }
            
            prompt = f"""
            Assess PATIENT SPECIFIC RISK.
            Patient: {patient['age']} year old {patient['gender']}
            Interaction: "{inter['description']}"
            Context: {json.dumps(context_text)}
            Return JSON: {{ "patient_risk": "Single string explaining risk." }}
            """
            
            data = self._call_llm(prompt, 0.1)
            results.append({
                "drug_a": inter['drug_a'],
                "drug_b": inter['drug_b'],
                "patient_risk": self._sanitize_string(data.get("patient_risk") if data else None, "Standard risk profile.")
            })
        return results

    # 5. Orchestrator
    def generate_structured_analysis(self, interactions: List[Dict], drug_contexts: Dict, patient: Dict) -> List[Dict]:
        cards = []
        
        # Sequential execution of sub-tasks
        summaries = self.generate_interaction_summary_batch(interactions)
        recomms = self.generate_recommendation_batch(interactions, drug_contexts)
        risks = self.generate_risk_batch(interactions, drug_contexts, patient)
        
        for i, inter in enumerate(interactions):
            id_a = inter['drug_a']
            id_b = inter['drug_b']
            
            name_a = drug_contexts.get(id_a, {}).get('name', id_a)
            name_b = drug_contexts.get(id_b, {}).get('name', id_b)
            
            cards.append({
                "drug_a": name_a,
                "drug_b": name_b,
                "severity": "Unknown", 
                "interaction_summary": summaries[i]['interaction_summary'],
                "recommendation": recomms[i]['recommendation'],
                "patient_risk": risks[i]['patient_risk']
            })
            
        return cards
        