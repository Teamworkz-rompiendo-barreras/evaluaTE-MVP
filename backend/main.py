# backend/main.py

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
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
    level: str  # 'Bajo', 'Medio', 'Alto'
    confidence: float
    feedback: Optional[str] = None

class CvAnalysis(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    feedback: Optional[str] = None
    structure: Optional[str] = None
    coherence: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[List[str]] = []
    education: Optional[List[str]] = []
    alerts: Optional[List[str]] = []

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

@app.post("/api/pdf/analyze-cv")
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

Tu misión es elaborar un **Informe de Empleabilidad** inclusivo y profesional a partir de:
1. Un array `softSkills` con las habilidades evaluadas en minijuegos
2. Un objeto `jobPreferences` con las preferencias laborales del candidato
3. El texto extraído del CV (PDF) del candidato (`cvText`)

NO uses fuentes externas ni inventes datos: limita tus conclusiones a la información entregada.

# === ENTRADA ESPERADA =======================================================
Recibirás tres variables ya parseadas:

softSkills = {json.dumps(soft_skills, ensure_ascii=False, indent=2)}

jobPreferences = {json.dumps(job_preferences, ensure_ascii=False, indent=2)}

cvText = f"{pdf_text[:2000]}"

# === SALIDA REQUERIDA (FORMATO MARKDOWN) ===================================
Devuelve **SOLO** Markdown con la siguiente estructura de nivel 1 (###):

### 1. Resumen Ejecutivo
– 3-5 frases claras (<20 palabras cada una) resumiendo: fortalezas clave, áreas de mejora y encaje general con sus preferencias.

### 2. Datos de Soft Skills
Tablas accesibles (formato Markdown) con encabezados:
| Habilidad | Nivel | Confianza (%) |
Incluye inmediatamente después de la tabla un bloque de código JSON denominado
```json
{{
  "radarData": [
    {{ "skill": "<skill>", "score": <confidence> }},
    …
  ]
}}
```

### 3. Análisis de Fortalezas y Áreas de Mejora
- Explica brevemente las principales fortalezas detectadas y las áreas de mejora, usando lenguaje positivo y accesible.

### 4. Oportunidades Laborales
- Sugiere tipos de puestos, sectores o entornos laborales alineados con el perfil y preferencias.

### 5. Consejos para el CV y la Búsqueda de Empleo
- Ofrece recomendaciones prácticas para mejorar el CV y la empleabilidad, adaptadas al perfil.

No añadas explicaciones ni comentarios fuera de la estructura solicitada. Redacta siempre en el idioma del CV.
"""

    # --- Llamada a OpenAI (GPT-3.5/4) ---
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.7,
        )
        informe_markdown = response.choices[0].message.content
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error generando informe IA: {str(e)}"})

    return {"informe": informe_markdown}