# backend/main.py
# Versión limpia del backend para Azure

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

# Variables de entorno para Azure OpenAI (opcionales)
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Log de configuración
logger.info("🔧 Configurando EvaluaTE Backend...")
logger.info(f"API_KEY: {'✅' if API_KEY else '❌'}")
logger.info(f"ENDPOINT: {'✅' if ENDPOINT else '❌'}")
logger.info(f"DEPLOYMENT: {'✅' if DEPLOYMENT else '❌'}")
logger.info(f"API_VERSION: {'✅' if API_VERSION else '❌'}")

# Cliente de Azure OpenAI (solo si está configurado)
client = None
if all([API_KEY, ENDPOINT, DEPLOYMENT, API_VERSION]):
    try:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            api_key=API_KEY, 
            api_version=API_VERSION, 
            azure_endpoint=ENDPOINT
        )
        logger.info("✅ Azure OpenAI configurado correctamente")
    except Exception as e:
        logger.warning(f"⚠️ Error configurando Azure OpenAI: {e}")
        client = None

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

@app.post("/api/logs/scene", response_model=Dict[str, Any])
async def log_scene_decision(data: Dict[str, Any]):
    """Registra una decisión de escena"""
    try:
        logger.info(f"Decisión de escena registrada: {data}")
        return {"status": "success", "message": "Decisión registrada"}
    except Exception as e:
        logger.error(f"Error registrando decisión: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logs/game-complete", response_model=Dict[str, Any])
async def log_game_complete(data: Dict[str, Any]):
    """Registra la finalización de un juego"""
    try:
        logger.info(f"Juego completado: {data}")
        return {"status": "success", "message": "Juego completado registrado"}
    except Exception as e:
        logger.error(f"Error registrando juego completado: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/informe-ia", response_model=ReportResponse)
async def generate_ia_report(request: EmployabilityReportRequest):
    """Genera un informe de empleabilidad"""
    try:
        logger.info(f"Generando informe para usuario: {request.userId}")
        
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

        # Crear reporte con jobPreferences incluido
        report = {
            "userId": request.userId,
            "fullName": request.fullName,
            "softSkills": [skill.dict() for skill in request.softSkills],
            "jobPreferences": request.jobPreferences.dict() if request.jobPreferences else {
                "areas": [],
                "needs": [],
                "workMode": "remoto",
                "availability": "completa",
                "willingToRelocate": False,
                "hasDisabilityCert": False
            },
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

@app.get("/api/informe-ia")
async def get_ia_report():
    """Obtiene el último informe generado"""
    return {"message": "Endpoint de informe disponible"}

@app.post("/api/logs/report", response_model=ReportResponse)
async def generate_report(request: EmployabilityReportRequest):
    """Genera un reporte (alias para generate_ia_report)"""
    return await generate_ia_report(request)

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

@app.post("/api/pdf/analyze-cv")
async def analyze_cv_pdf(file: UploadFile = File(...)):
    """Analiza un CV en formato PDF"""
    try:
        logger.info(f"Analizando CV PDF: {file.filename}")
        
        # Simular análisis de CV
        analysis = CvAnalysis(
            strengths=["Experiencia en desarrollo web", "Conocimientos de JavaScript", "Trabajo en equipo"],
            weaknesses=["Falta de experiencia en proyectos grandes", "Necesita mejorar documentación"],
            feedback="CV bien estructurado con buenas habilidades técnicas",
            structure="buena",
            coherence="buena", 
            experience="regular",
            skills=["JavaScript", "React", "HTML", "CSS"],
            education=["Ingeniería Informática", "Bootcamp Desarrollo Web"],
            alerts=["Considerar agregar más proyectos personales"]
        )
        
        return analysis.dict()
        
    except Exception as e:
        logger.error(f"Error analizando CV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """Sube un CV para análisis"""
    try:
        logger.info(f"CV subido: {file.filename}")
        return {
            "message": "CV subido correctamente",
            "filename": file.filename,
            "size": file.size
        }
    except Exception as e:
        logger.error(f"Error subiendo CV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)