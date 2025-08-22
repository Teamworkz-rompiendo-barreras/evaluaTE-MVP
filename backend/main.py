# main.py  (versión limpia)
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging

from document_intelligence import analyze_cv_with_improved_intelligence
from report_generator import render_informe_estructurado

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

app = FastAPI(title="EvaluaTE Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3005", "http://localhost:3006", "http://localhost:5173",
        "https://yellow-mud-0b6281c1e.6.azurestaticapps.net", "https://*.azurestaticapps.net",
        "https://*.azurewebsites.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SoftSkillResult(BaseModel):
    skill: str
    score: int
    level: str
    confidence: int

class CvAnalysis(BaseModel):
    strengths: List[str] = []
    weaknesses: List[str] = []
    feedback: Optional[str] = None
    structure: Optional[str] = None
    coherence: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[List[str]] = []
    education: Optional[List[str]] = []
    alerts: Optional[List[str]] = []

class JobPreference(BaseModel):
    areas: List[str] = []
    needs: List[str] = []
    workMode: Optional[str] = "remoto"
    availability: Optional[str] = "completa"
    willingToRelocate: bool = False
    hasDisabilityCert: bool = False

class EmployabilityReportRequest(BaseModel):
    userId: str
    fullName: str
    softSkills: List[SoftSkillResult]
    cvAnalysis: Optional[CvAnalysis] = None
    jobPreferences: Optional[JobPreference] = None
    completedGames: List[str] = []
    logs: List[Dict[str, Any]] = []

class ReportResponse(BaseModel):
    report: Dict[str, Any]
    recommendations: Dict[str, List[str]]
    employabilityScore: int
    level: str
    summary: str
    createdAt: str

@app.get("/")
async def root():
    return {"message": "Bienvenida/o a EvaluaTE", "status": "running"}

def _map_di_to_cvinfo(di: Dict[str, Any]) -> Dict[str, Any]:
    # Asegura claves esperadas por el renderizador
    return {
        "contacto": di.get("contact", {}) or di.get("contacto", {}),
        "software": di.get("skills", []) or di.get("software", []),
        "idiomas": di.get("languages", []) or di.get("idiomas", []),
        "perfil": di.get("raw_text") or di.get("perfil") or "",
        "experiencia": di.get("experience", []) or di.get("experiencia", []),
        "educacion": di.get("education", []) or di.get("educacion", []),
        "proyectos": di.get("projects", []) or di.get("proyectos", []),
    }

def _level_from_score(score: int) -> str:
    return "Alta empleabilidad" if score >= 80 else ("Empleabilidad media" if score >= 50 else "Baja empleabilidad")

@app.post("/api/informe", response_model=ReportResponse)
async def generar_informe_sync(
    payload: str = Form(...),
    cv: UploadFile | None = File(None)
):
    """
    Endpoint ÚNICO: recibe el JSON (campo 'payload') y opcionalmente un PDF 'cv'.
    - Si no viene cvAnalysis en el JSON y recibimos 'cv', ejecuta Azure DI y lo inyecta.
    - Genera SIEMPRE el informe con tu estructura.
    """
    try:
        data = EmployabilityReportRequest(**json.loads(payload))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Payload inválido: {e}")

    cv_info: Dict[str, Any] = {}
    if data.cvAnalysis:
        # Si ya viene análisis, úsalo tal cual
        cv_info = _map_di_to_cvinfo(data.cvAnalysis.dict())
    elif cv is not None:
        # Analiza PDF y mapea
        pdf_bytes = await cv.read()
        di_raw = analyze_cv_with_improved_intelligence(pdf_bytes)  # espera resultado
        cv_info = _map_di_to_cvinfo(di_raw)

    # Construir informe con estructura exacta
    soft_skills = [s.dict() for s in data.softSkills]
    job_prefs = data.jobPreferences.dict() if data.jobPreferences else {}
    profile = {"fullName": data.fullName, "userId": data.userId}
    informe_texto = render_informe_estructurado(profile, cv_info, soft_skills, job_prefs, data.completedGames)

    # Puntuación simple y estable
    high = sum(1 for s in soft_skills if (s.get("score", 0) >= 70))
    med = sum(1 for s in soft_skills if (50 <= s.get("score", 0) < 70))
    low = sum(1 for s in soft_skills if (s.get("score", 0) < 50))
    total = len(soft_skills) or 1
    score = (high*100 + med*65 + low*30)//total
    level = _level_from_score(score)

    resp = {
        "report": {
            "userId": data.userId,
            "fullName": data.fullName,
            "softSkills": soft_skills,
            "employabilityScore": score,
            "jobPreferences": job_prefs,
            "cvAnalysis": cv_info,  # ahora SIEMPRE viaja
            "createdAt": datetime.now().isoformat(),
            "completedGames": data.completedGames,
            "level": level,
            "informeProfesional": informe_texto
        },
        "recommendations": {
            "roles": ["Data Entry", "Back-office", "Data QA"],
            "resources": ["Coursera", "LinkedIn Learning"],
            "cvImprovements": ["Cuantificar logros", "Añadir enlaces"],
            "nextSteps": ["Actualizar CV y LinkedIn", "Preparar portfolio ligero"]
        },
        "summary": f"{data.fullName}, tu informe profesional está listo.",
        "employabilityScore": score,
        "level": level,
        "createdAt": datetime.now().isoformat()
    }
    return resp