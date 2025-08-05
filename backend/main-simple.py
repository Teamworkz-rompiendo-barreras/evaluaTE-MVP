# backend/main-simple.py
# Versión simplificada del backend para Azure

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn
from typing import List, Optional, Dict, Any
from datetime import datetime
import io
import json
import os
import logging
import tempfile

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tipos compartidos
class SoftSkillResult(BaseModel):
    skill: str
    score: int
    level: str  # 'bajo', 'medio', 'alto'
    confidence: int

class CvAnalysis(BaseModel):
    strengths: List[str] = Field(description="Puntos fuertes del CV")
    weaknesses: List[str] = Field(description="Áreas de mejora del CV")
    feedback: Optional[str] = Field(None, description="Feedback general sobre el CV")
    structure: Optional[str] = Field(None, description="Análisis de la estructura del CV")
    coherence: Optional[str] = Field(None, description="Análisis de la coherencia del CV")
    experience: Optional[str] = Field(None, description="Análisis de la experiencia laboral")
    skills: Optional[List[str]] = Field([], description="Habilidades técnicas detectadas")
    education: Optional[List[str]] = Field([], description="Formación detectada")
    alerts: Optional[List[str]] = Field([], description="Alertas o puntos críticos detectados")

class JobPreference(BaseModel):
    areas: List[str]
    needs: List[str]
    workMode: Optional[str] = "remoto"
    availability: Optional[str] = "completa"
    willingToRelocate: bool = False
    hasDisabilityCert: bool = False

class AccessibilitySettings(BaseModel):
    easyReadingMode: bool = False
    audioAssistiveMode: bool = False
    showPictograms: bool = False
    contrastLevel: str = "normal"

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
    completedGames: List[str] = []
    logs: List[GameDecisionLog] = []

class ReportResponse(BaseModel):
    report: Dict[str, Any]
    recommendations: Dict[str, List[str]]
    employabilityScore: int
    level: str
    summary: str
    createdAt: str

class FeedbackRequest(BaseModel):
    informe: str
    rating: str
    comment: str
    userData: dict

app = FastAPI(title="EvaluaTE Backend", version="1.0.0")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Bienvenida/o a EvaluaTE MVP", "status": "running"}

@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoreo"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "EvaluaTE Backend",
        "version": "1.0.0"
    }

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/informe-ia", response_model=ReportResponse)
async def generate_ia_report(request: EmployabilityReportRequest):
    """Genera un informe de empleabilidad básico"""
    try:
        # Calcular puntaje de empleabilidad
        total_skills = len(request.softSkills)
        if total_skills == 0:
            employability_score = 50
        else:
            total_score = sum(skill.score for skill in request.softSkills)
            employability_score = total_score // total_skills

        # Determinar nivel
        if employability_score >= 80:
            level = "alto"
        elif employability_score >= 50:
            level = "medio"
        else:
            level = "bajo"

        # Generar recomendaciones básicas
        recommendations = {
            "roles": ["Desarrollador Frontend", "Soporte Técnico", "Analista de Datos"],
            "resources": ["Platzi", "Microsoft Learn", "Coursera"],
            "cvImprovements": ["Mejorar la estructura", "Agregar más detalles técnicos"],
            "nextSteps": ["Completar todos los juegos", "Actualizar CV", "Practicar habilidades"]
        }

        # Generar resumen
        summary = f"Basado en tu evaluación, tu nivel de empleabilidad es {level} con un puntaje de {employability_score}/100."

        # Crear reporte
        report = {
            "userId": request.userId,
            "fullName": request.fullName,
            "softSkills": [skill.dict() for skill in request.softSkills],
            "employabilityScore": employability_score,
            "level": level,
            "createdAt": datetime.now().isoformat()
        }

        return ReportResponse(
            report=report,
            recommendations=recommendations,
            employabilityScore=employability_score,
            level=level,
            summary=summary,
            createdAt=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generando informe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/informe-ia/feedback")
async def receive_feedback(request: FeedbackRequest):
    """Recibe feedback del usuario"""
    try:
        logger.info(f"Feedback recibido: {request.rating} - {request.comment}")
        return {"message": "Feedback recibido correctamente"}
    except Exception as e:
        logger.error(f"Error procesando feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/informe-ia/feedback/stats")
async def get_feedback_stats():
    """Obtiene estadísticas de feedback"""
    return {
        "total_feedback": 0,
        "positive_feedback": 0,
        "negative_feedback": 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 