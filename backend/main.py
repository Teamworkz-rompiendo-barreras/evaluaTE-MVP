# backend/main.py

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from typing import List, Optional, Dict, Any
from datetime import datetime
import io
import json
from PyPDF2 import PdfReader
import os
import openai

# Tipos compartidos – puedes moverlos a un paquete común si lo usas también en frontend
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
        # if request.cvAnalysis:
        #     if request.cvAnalysis.score < 60:
        #         total_score = max(20, total_score - 10)

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

@app.post("/api/pdf/analyze-cv", response_model=CvAnalysis)
async def analyze_cv(
    file: UploadFile = File(...),
    userId: str = Form(...),
    fullName: str = Form(...),
    softSkills: str = Form(...),  # JSON stringified array
    jobPreferences: str = Form(...),  # JSON stringified object
    completedGames: str = Form(...),  # JSON stringified array
):
    """
    Analiza el CV PDF y genera un informe de empleabilidad usando IA.
    """
    # Leer el PDF
    contents = await file.read()
    pdf_text = ""
    try:
        pdf_reader = PdfReader(io.BytesIO(contents))
        for page in pdf_reader.pages:
            pdf_text += page.extract_text() or ""
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"No se pudo leer el PDF: {str(e)}"})

    # Parsear los datos recibidos
    try:
        soft_skills = json.loads(softSkills)
        job_preferences = json.loads(jobPreferences)
        completed_games = json.loads(completedGames)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Error en los datos enviados: {str(e)}"})

    # --- PROMPT PARA LA IA ---
    prompt = f"""
# === CONTEXTO Y ROL =========================================================
Eres un/a ORIENTADOR/A LABORAL senior con:
• Formación en Psicología y en Inclusión Laboral de personas neurodivergentes
• Conocimiento actualizado del marco de competencias WEF 2025
• Experiencia en redacción accesible (WCAG 2.2 y lectura fácil)

Tu misión es analizar el texto de un CV y devolver un análisis estructurado en formato JSON.

# === ENTRADA ===============================================================
Analiza el siguiente texto extraído de un CV:
cvText = ```{pdf_text[:2000]}```

# === SALIDA REQUERIDA (FORMATO JSON) =======================================
Devuelve **SOLO** un objeto JSON válido con la siguiente estructura. No incluyas explicaciones, comentarios ni la palabra 'json' al principio. El JSON debe contener estas claves:

{{
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "feedback": "...",
  "structure": "Análisis de la estructura del CV (ej: 'Clara y fácil de seguir' o 'Algo desordenada')",
  "coherence": "Análisis de la coherencia (ej: 'La experiencia es coherente con los objetivos')",
  "experience": "Resumen de la experiencia laboral detectada",
  "skills": ["Lista de habilidades técnicas clave detectadas"],
  "education": ["Lista de la formación principal detectada"],
  "alerts": ["Alertas o puntos críticos, como falta de información de contacto o periodos sin actividad no explicados"]
}}
"""

    # --- Llamada a OpenAI (GPT-4) ---
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        analysis_data = json.loads(response.choices[0].message.content)
        return CvAnalysis(**analysis_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando informe IA: {str(e)}")