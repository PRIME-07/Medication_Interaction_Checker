from pydantic import BaseModel
from typing import List, Dict, Optional

# SUB-MODELS
class PatientProfile(BaseModel):
    age: int
    gender: str
    weight: Optional[float] = None
    height: Optional[float] = None
    conditions: Optional[List[str]] = []

class DrugSearchResult(BaseModel):
    name: str
    id: str
    type: str 

class InteractionItem(BaseModel):
    drug_a: str
    drug_b: str
    description: str


# REQUEST MODELS
class MedsRequest(BaseModel):
    medications: List[str]

class IDRequest(BaseModel):
    drug_ids: List[str]

# Core request model for analysis
class AnalysisRequest(BaseModel):
    interactions: List[InteractionItem] 
    patient: PatientProfile
    drug_ids: Optional[List[str]] = None

# Explicit definition to ensure importability
class ReportRequest(AnalysisRequest):
    pass


# RESPONSE MODELS
class InteractionResponse(BaseModel):
    resolved_medications: Dict[str, str]
    interactions_found: List[InteractionItem]

class FoodResponse(BaseModel):
    food_warnings: Dict[str, List[str]]

class ReferenceResponse(BaseModel):
    references: Dict[str, Dict[str, List[str]]]


# Used for AI Responses
class SeverityResult(BaseModel):
    drug_a: str
    drug_b: str
    severity: str 
    short_reason: str

class SeverityResponse(BaseModel):
    results: List[SeverityResult]

class MechanismResult(BaseModel):
    drug_a: str
    drug_b: str
    interaction_summary: str

class MechanismResponse(BaseModel):
    results: List[MechanismResult]

class RecommendationResult(BaseModel):
    drug_a: str
    drug_b: str
    recommendation: str

class RecommendationResponse(BaseModel):
    results: List[RecommendationResult]

class RiskResult(BaseModel):
    drug_a: str
    drug_b: str
    patient_risk: str

class RiskResponse(BaseModel):
    results: List[RiskResult]

class ClinicalAnalysisItem(BaseModel):
    drug_a: str
    drug_b: str
    severity: str
    interaction_summary: str
    recommendation: str
    patient_risk: str

class ReportResponse(BaseModel):
    clinical_analysis: str 
    analysis_cards: List[ClinicalAnalysisItem]