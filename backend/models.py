# backend/models.py
from pydantic import BaseModel
from typing import List, Dict, Optional

class SoftSkillResult(BaseModel):
    skill: str
    level: str  # 'Bajo', 'Medio', 'Alto'
    confidence: float
    feedback: Optional[str] = None

class CvAnalysis(BaseModel):
    score: int
    strengths: List[str]
    weaknesses: List[str]
    feedback: Optional[str] = None
    structure: Optional[str] = None
    coherence: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[List[str]] = None
    education: Optional[List[str]] = None
    alerts: Optional[List[str]] = None
    # Campos adicionales para información detallada del CV
    cv_structured: Optional[Dict] = None
    candidate: Optional[Dict] = None
    contact: Optional[Dict] = None
    experience_detailed: Optional[List[Dict]] = None
    education_detailed: Optional[List[Dict]] = None
    languages: Optional[List[Dict]] = None
    periods: Optional[List[str]] = None
    highlights: Optional[List[str]] = None

class JobPreference(BaseModel):
    areas: List[str]
    needs: List[str]
    workMode: str  # 'remoto', 'presencial', 'híbrido'
    availability: str  # 'mañana', 'tarde', 'completa'
    willingToRelocate: bool
    hasDisabilityCert: bool
    accessibilitySettings: Optional[Dict] = {}

class GameDecisionLog(BaseModel):
    sceneId: int
    decisions: List[SoftSkillResult]
    totalSteps: int
    totalTime: int
    averageConfidence: float
    emotionalTrend: List[str]
    accessibilityUsed: bool
    accessibilitySettings: Optional[Dict] = {}