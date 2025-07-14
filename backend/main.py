# backend/main.py

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import List, Optional, Dict, Any
from datetime import datetime

# Tipos compartidos – puedes moverlos a un paquete común si lo usas también en frontend
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

class JobPreference(BaseModel):
    areas: List[str]
    needs: List[str]
    workMode: Optional[str] = "remoto"  # 'remoto', 'presencial', 'híbrido'
    availability: Optional[str] = "completa"  # 'mañana', 'tarde', 'completa'
    willingToRelocate: bool = False
    hasDisabilityCert: bool = False

class AccessibilitySettings(BaseModel):
    easyReadingMode: bool = False
    audioAssistiveMode: bool = False
    showPictograms: bool = False
    contrastLevel: str = "normal"  # 'normal', 'alto', 'muy-alto'

class GameDecisionLog(BaseModel):
    sceneId: int
    decisions: List[Dict[str, Any]]
    totalSteps: int
    totalTime: int
    averageConfidence: float
    emotionalTrend: List[str]
    accessibilityUsed: bool
    accessibilitySettings: Optional[AccessibilitySettings] = None

class EmployabilityReportRequest(BaseModel):
    userId: str
    fullName: str
    softSkills: List[SoftSkillResult]
    cvAnalysis: Optional[CvAnalysis] = None
    jobPreferences: Optional[JobPreference] = None
    completedGames: List[int] = []
    logs: List[GameDecisionLog] = []

class ReportResponse(BaseModel):
    report: Dict[str, Any]
    recommendations: Dict[str, List[str]]
    employabilityScore: int
    level: str
    summary: str
    createdAt: str

app = FastAPI(title="EvaluaTE Backend", version="1.0.0")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Bienvenida/o a EvaluaTE MVP", "status": "running"}

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3005",
        "http://localhost:5173",
        "https://yellow-mud-0b6281c1e.6.azurestaticapps.net",
        "https://*.azurestaticapps.net",
        "https://*.azurewebsites.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/logs/scene", response_model=Dict[str, Any])
async def log_scene_decision(data: Dict[str, Any]):
    """Guarda decisiones tomadas en cada escena"""
    print("LOG SCENE:", data)
    return {"success": True}

@app.post("/api/logs/game-complete", response_model=Dict[str, Any])
async def log_game_complete(data: Dict[str, Any]):
    """Guarda cuando se completa un juego"""
    print("GAME COMPLETE:", data)
    return {"success": True}

@app.post("/api/informe-ia", response_model=ReportResponse)
async def generate_ia_report(request: EmployabilityReportRequest):
    """Genera informe de IA basado en datos del usuario"""
    return await generate_report(request)

@app.get("/api/informe-ia")
async def get_ia_report():
    """Endpoint GET para el informe de IA"""
    return {"message": "Endpoint de informe de IA disponible"}

@app.post("/api/logs/report", response_model=ReportResponse)
async def generate_report(request: EmployabilityReportRequest):
    """Genera informe final basado en datos del usuario"""

    try:
        # Simula análisis de soft skills
        high_skills = [skill for skill in request.softSkills if skill.level == "Alto"]
        medium_skills = [skill for skill in request.softSkills if skill.level == "Medio"]
        low_skills = [skill for skill in request.softSkills if skill.level == "Bajo"]

        # Puntaje global basado en habilidades blandas
        score_high = len(high_skills) * 100
        score_medium = len(medium_skills) * 65
        score_low = len(low_skills) * 30
        total_score = (score_high + score_medium + score_low) // max(1, len(request.softSkills))

        # Ajuste según CV
        if request.cvAnalysis:
            if request.cvAnalysis.score < 60:
                total_score = max(20, total_score - 10)

        # Nivel de empleabilidad
        level = (
            "Alta empleabilidad"
            if total_score >= 80
            else "Empleabilidad media"
            if total_score >= 50
            else "Baja empleabilidad"
        )

        # Recomendaciones personalizadas
        roles = []
        resources = ["Platzi", "Microsoft Learn"]
        improvements = []
        next_steps = []

        if any(skill.level == "Alto" for skill in request.softSkills):
            roles.append("Desarrollador frontend")
            roles.append("Soporte técnico")

        if request.cvAnalysis and request.cvAnalysis.weaknesses:
            improvements.extend(request.cvAnalysis.weaknesses)

        next_steps.append("Completar todos los juegos")
        next_steps.append("Actualizar tu CV")
        next_steps.append("Revisar tus preferencias")

        return {
            "report": {
                "userId": request.userId,
                "fullName": request.fullName,
                "softSkills": [
                    {**skill.dict(), "confidence": round(skill.confidence * 100)}
                    for skill in request.softSkills
                ],
                "employabilityScore": total_score,
                "jobPreferences": request.jobPreferences.dict() if request.jobPreferences else {},
                "cvAnalysis": request.cvAnalysis.dict() if request.cvAnalysis else None,
                "createdAt": datetime.now().isoformat(),
                "completedGames": request.completedGames,
                "level": level,
            },
            "recommendations": {
                "roles": roles,
                "resources": resources,
                "cvImprovements": improvements,
                "nextSteps": next_steps,
            },
            "summary": f"{request.fullName}, tienes un nivel de empleabilidad: {level}",
            "employabilityScore": total_score,
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))