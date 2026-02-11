from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class PersonalData(BaseModel):
    name: str
    location: str
    email: str
    phone: str
    disability_certificate: str
    linkedin: Optional[str] = None

class CvDetails(BaseModel):
    experience: List[str]
    education: List[str]
    languages: List[str]
    tools: List[str]

class ImprovementArea(BaseModel):
    area: str
    reason: str
    suggested_action: str
    score: Optional[int] = None

class CvAnalysisEvidence(BaseModel):
    structure: str
    coherence: str
    key_info: str
    clarity: str
    style: str

class CvAnalysis(BaseModel):
    structure_score: int
    coherence_score: int
    key_info_score: int
    clarity_score: int
    style_score: int
    evidence: CvAnalysisEvidence
    corrections: List[str]
    reordering_suggestions: List[str]

class SuggestedRole(BaseModel):
    role: str
    reason: str
    seniority: str
    remote_viable: bool

class ActionPlan(BaseModel):
    short_term: List[str]
    medium_term: List[str]
    long_term: List[str]

class JobSearchAdvice(BaseModel):
    cv_optimization: List[str]
    letters_portfolio: Optional[str] = None
    recommended_platforms: List[str]
    networking: Optional[str] = None
    interview_tips: Optional[str] = None

class UsefulTools(BaseModel):
    productivity: List[str]
    job_search: List[str]
    learning: List[str]
    accessibility: List[str]

class ReadyPhrases(BaseModel):
    headline: str
    about_me: str
    short_message: str

class NewReportSchema(BaseModel):
    summary: str
    personal_data: PersonalData
    profile_summary: str
    cv_summary: str
    cv_details: CvDetails
    strengths: List[str]
    improvement_areas: List[ImprovementArea]
    cv_analysis: CvAnalysis
    ideal_work_environment: str
    suggested_roles: List[SuggestedRole]
    action_plan: ActionPlan
    job_search_advice: JobSearchAdvice
    useful_tools: UsefulTools
    completed_games: List[str]
    ready_phrases: ReadyPhrases
    final_message: str
    
    # Campos opcionales para compatibilidad
    employability_score: Optional[int] = 0
    soft_skills: Optional[List[Dict[str, Any]]] = []
