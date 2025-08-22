# main.py
import io
import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, validator

# ==========
# Integraciones propias (deben existir en tu repo)
# ==========
try:
    from document_intelligence import DocumentIntelligenceService
except Exception as e:  # pragma: no cover
    DocumentIntelligenceService = None
    logging.warning("DocumentIntelligenceService no disponible: %s", e)

try:
    from generate_report import generar_informe  # debe devolver JSON (str o dict)
except Exception as e:  # pragma: no cover
    generar_informe = None
    logging.warning("generar_informe no disponible: %s", e)

try:
    from pdf_service import create_employability_pdf  # debe devolver bytes o ruta
except Exception as e:  # pragma: no cover
    create_employability_pdf = None
    logging.warning("create_employability_pdf no disponible: %s", e)

# ==========
# Configuración y app única
# ==========
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s - %(message)s")
logger = logging.getLogger("evaluador-backend")

app = FastAPI(title="EvaluaTE Backend", version="1.0.0")

ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*")
origins = [o.strip() for o in ALLOWED_ORIGINS.split(",")] if ALLOWED_ORIGINS else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========
# Modelos (única definición)
# ==========
class SoftSkillResult(BaseModel):
    skill: str
    score: int = Field(ge=0, le=100)
    level: Optional[str] = None
    confidence: Optional[int] = Field(default=None, ge=0, le=100)


class CvStars(BaseModel):
    formato: Optional[int] = Field(default=None, ge=1, le=5)
    claridad: Optional[int] = Field(default=None, ge=1, le=5)
    coherencia: Optional[int] = Field(default=None, ge=1, le=5)
    informacion_clave: Optional[int] = Field(default=None, ge=1, le=5)
    ortografia: Optional[int] = Field(default=None, ge=1, le=5)


class CvAnalysis(BaseModel):
    strengths: List[str] = []
    weaknesses: List[str] = []
    feedback: Optional[str] = None
    summary: Optional[str] = None
    stars: Optional[CvStars] = None  # para el bloque de estrellas
    raw_text: Optional[str] = None   # texto extraído
    # campos flexibles para experiencia/formación mínimos
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    languages: Optional[List[Dict[str, Any]]] = None
    software: Optional[List[str]] = None
    contact: Optional[Dict[str, Any]] = None


class JobPreference(BaseModel):
    areas: List[str] = []
    needs: List[str] = []
    workMode: Optional[str] = None
    availability: Optional[str] = None
    willingToRelocate: Optional[bool] = None
    hasDisabilityCert: Optional[bool] = None


class EmployabilityReportRequest(BaseModel):
    userId: Optional[str] = None
    fullName: Optional[str] = None
    softSkills: List[SoftSkillResult] = []
    cvAnalysis: Optional[CvAnalysis] = None
    jobPreferences: Optional[JobPreference] = None
    completedGames: Optional[List[str]] = None
    logs: Optional[List[Dict[str, Any]]] = None


class ReportResponse(BaseModel):
    report: Dict[str, Any] = {}
    recommendations: Optional[List[str]] = None
    level: Optional[str] = None
    employabilityScore: Optional[int] = Field(default=None, ge=0, le=100)


# ==========
# Utilidades (únicas)
# ==========
def _safe_json_loads(maybe_json: Optional[str]) -> Any:
    if not maybe_json:
        return None
    try:
        return json.loads(maybe_json)
    except Exception:
        # Si viene como array/objeto ya parseado (poco probable por Form), devuélvelo
        return maybe_json


def format_cv_analysis(cv: Optional[CvAnalysis]) -> str:
    """
    Construye el bloque 'CV ANALIZADO' que esperan las plantillas largas,
    incluyendo estrellas (1–5) si están disponibles.
    """
    if not cv:
        return (
            "CV ANALIZADO\n"
            "- No se ha podido analizar el CV. Aporta logros, responsabilidades, fechas y enlaces.\n"
        )

    lines = ["CV ANALIZADO"]
    if cv.summary:
        lines.append(f"Resumen: {cv.summary}")

    if cv.stars:
        def stars(n: Optional[int]) -> str:
            return "★" * int(n or 0) + "☆" * (5 - int(n or 0))
        lines.extend(
            [
                f"Formato: {stars(cv.stars.formato)}",
                f"Claridad: {stars(cv.stars.claridad)}",
                f"Coherencia: {stars(cv.stars.coherencia)}",
                f"Información clave: {stars(cv.stars.informacion_clave)}",
                f"Ortografía: {stars(cv.stars.ortografia)}",
            ]
        )

    if cv.strengths:
        lines.append("Fortalezas:")
        for s in cv.strengths:
            lines.append(f"- {s}")

    if cv.weaknesses:
        lines.append("Áreas de mejora:")
        for w in cv.weaknesses:
            lines.append(f"- {w}")

    if cv.feedback:
        lines.append("Correcciones/Acciones:")
        for line in cv.feedback.split("\n"):
            line = line.strip()
            if line:
                lines.append(f"- {line}")

    return "\n".join(lines)


def format_job_preferences(prefs: Optional[JobPreference]) -> str:
    if not prefs:
        return "PREFERENCIAS LABORALES\n- No especificadas."
    parts = ["PREFERENCIAS LABORALES"]
    if prefs.areas:
        parts.append(f"- Roles/Sectores: {', '.join(prefs.areas)}")
    if prefs.workMode:
        parts.append(f"- Modalidad: {prefs.workMode}")
    if prefs.availability:
        parts.append(f"- Disponibilidad: {prefs.availability}")
    if prefs.willingToRelocate is not None:
        parts.append(f"- Relocalización: {prefs.willingToRelocate}")
    if prefs.hasDisabilityCert is not None:
        parts.append(f"- Certificado de discapacidad: {prefs.hasDisabilityCert}")
    if prefs.needs:
        parts.append(f"- Necesidades: {', '.join(prefs.needs)}")
    return "\n".join(parts)


def build_prompt(req: EmployabilityReportRequest) -> str:
    """
    Prompt largo con los marcadores que comprobabas en logs:
    incluye 'CV ANALIZADO', 'JUEGOS COMPLETADOS', 'PREFERENCIAS LABORALES' y '13) FRASE FINAL'.
    """
    lines = []
    lines.append("1) RESUMEN EJECUTIVO")
    if req.fullName:
        lines.append(f"Nombre: {req.fullName}")

    lines.append("\n2) SOFT SKILLS")
    if req.softSkills:
        for s in req.softSkills:
            lines.append(f"- {s.skill}: {s.score}/100 ({s.level or 'NA'})")
    else:
        lines.append("- No disponibles")

    lines.append("\n3) " + format_cv_analysis(req.cvAnalysis))

    lines.append("\n4) " + format_job_preferences(req.jobPreferences))

    lines.append("\n5) JUEGOS COMPLETADOS")
    if req.completedGames:
        lines.append("- " + ", ".join(req.completedGames))
    else:
        lines.append("- No consta")

    # Espacio para otras 6–12 secciones si tu plantilla las usa
    lines.append("\n13) FRASE FINAL")
    lines.append("Cierra con un consejo accionable y motivador en 2–3 frases.")

    prompt = "\n".join(lines)
    logger.info("Prompt generado (longitud %s). Contiene marcadores: CV ANALIZADO=%s, JUEGOS COMPLETADOS=%s, PREFERENCIAS LABORALES=%s, 13) FRASE FINAL=%s",
                len(prompt),
                "CV ANALIZADO" in prompt,
                "JUEGOS COMPLETADOS" in prompt,
                "PREFERENCIAS LABORALES" in prompt,
                "13) FRASE FINAL" in prompt)
    return prompt


def normalize_ai_response(raw: Any) -> Dict[str, Any]:
    """
    Acepta dict o str (JSON) y devuelve dict con claves base.
    """
    if raw is None:
        return {}
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return {"summary": raw}
    if isinstance(raw, dict):
        return raw
    return {"summary": str(raw)}


# ==========
# Endpoints
# ==========
@app.get("/health")
def health():
    return {"ok": True, "status": "healthy"}


@app.post("/api/pdf/analyze-cv")
async def analyze_cv(
    file: UploadFile = File(...),
    softSkillsJson: Optional[str] = Form(None),
    jobPreferencesJson: Optional[str] = Form(None),
    completedGamesJson: Optional[str] = Form(None),
    logsJson: Optional[str] = Form(None),
):
    """
    1) Analiza el CV (Azure Document Intelligence si está disponible).
    Devuelve un bloque 'cvAnalysis' preparado para el siguiente paso.
    """
    logger.info("Analizando CV PDF: %s", file.filename)

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Archivo vacío")

    # Analizador principal
    cv_data: Dict[str, Any] = {}
    if DocumentIntelligenceService is None:
        logger.warning("DocumentIntelligenceService no configurado. Se devolverá análisis mínimo.")
        cv_data = {
            "summary": "No disponible",
            "strengths": [],
            "weaknesses": [],
            "feedback": "No se pudo procesar el CV en este entorno.",
            "stars": None,
            "raw_text": None,
        }
    else:
        try:
            model_id = os.getenv("AZURE_DI_MODEL_ID", "prebuilt-document")
            di = DocumentIntelligenceService(model_id=model_id)
            result = di.analyze_cv_with_document_intelligence(content)
            # Normaliza campos esperados por la app
            cv_data = {
                "summary": result.get("summary") or result.get("cv_summary"),
                "strengths": result.get("strengths", []),
                "weaknesses": result.get("weaknesses", []),
                "feedback": result.get("feedback") or result.get("recommendations"),
                "stars": result.get("stars"),
                "raw_text": result.get("raw_text") or result.get("text"),
                "experience": result.get("experience"),
                "education": result.get("education"),
                "languages": result.get("languages"),
                "software": result.get("software"),
                "contact": result.get("contact"),
            }
        except Exception as e:
            logger.exception("Fallo analizando CV con Document Intelligence: %s", e)
            raise HTTPException(status_code=500, detail=f"Error analizando CV: {e}")

    # empaquetar respuesta
    payload = {
        "ok": True,
        "cvAnalysis": cv_data,
        "softSkills": _safe_json_loads(softSkillsJson) or [],
        "jobPreferences": _safe_json_loads(jobPreferencesJson) or {},
        "completedGames": _safe_json_loads(completedGamesJson) or [],
        "logs": _safe_json_loads(logsJson) or [],
    }
    return JSONResponse(payload)


@app.post("/api/informe-ia", response_model=ReportResponse)
def informe_ia(req: EmployabilityReportRequest):
    """
    2) Genera el informe IA a partir del análisis del CV (si existe) + soft skills + preferencias.
    """
    logger.info("Generando informe profesional para usuario: %s", req.userId or "desconocido")

    if generar_informe is None:
        raise HTTPException(status_code=500, detail="Módulo de generación de informe no disponible")

    prompt = build_prompt(req)

    try:
        raw = generar_informe(prompt)  # puede devolver str (JSON) o dict
        data = normalize_ai_response(raw)
    except Exception as e:
        logger.exception("Error generando informe con IA: %s", e)
        raise HTTPException(status_code=500, detail=f"Error generando informe con IA: {e}")

    # Normalización de claves esperadas en la UI
    report = data.get("report") or data  # si ya viene formateado como report
    recommendations = data.get("recommendations") or report.get("consejos_busqueda") or []
    level = data.get("level") or report.get("nivel") or None
    score = data.get("employabilityScore") or report.get("puntuacion") or None

    return ReportResponse(
        report=report,
        recommendations=recommendations,
        level=level,
        employabilityScore=score,
    )


@app.post("/api/pdf/generate-report")
def generate_report_pdf(req: EmployabilityReportRequest):
    """
    3) Genera el PDF final. Requiere el resultado del paso 2 (informe IA) embebido
       o, en su defecto, volverá a invocar a la IA con el prompt.
    """
    if create_employability_pdf is None:
        raise HTTPException(status_code=500, detail="Servicio de PDF no disponible")

    # Asegurar que tenemos contenido de informe
    if generar_informe is None:
        raise HTTPException(status_code=500, detail="Módulo de generación de informe no disponible")

    # Si el cliente no pasó el informe ya estructurado, lo generamos
    prompt = build_prompt(req)
    ai_raw = generar_informe(prompt)
    ai_data = normalize_ai_response(ai_raw)

    try:
        pdf_bytes_or_path = create_employability_pdf({
            "userId": req.userId,
            "fullName": req.fullName,
            "softSkills": [s.dict() for s in req.softSkills],
            "cvAnalysis": req.cvAnalysis.dict() if req.cvAnalysis else None,
            "jobPreferences": req.jobPreferences.dict() if req.jobPreferences else None,
            "completedGames": req.completedGames or [],
            "report": ai_data,  # pasa todo el informe IA
        })
    except Exception as e:
        logger.exception("Error creando PDF: %s", e)
        raise HTTPException(status_code=500, detail=f"Error creando PDF: {e}")

    # Soporta función que devuelva bytes o una ruta
    if isinstance(pdf_bytes_or_path, (bytes, bytearray)):
        return StreamingResponse(
            io.BytesIO(pdf_bytes_or_path),
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="informe_empleabilidad.pdf"'},
        )
    elif isinstance(pdf_bytes_or_path, str) and os.path.exists(pdf_bytes_or_path):
        with open(pdf_bytes_or_path, "rb") as f:
            return StreamingResponse(
                io.BytesIO(f.read()),
                media_type="application/pdf",
                headers={"Content-Disposition": 'attachment; filename="informe_empleabilidad.pdf"'},
            )
    else:
        # Por si el servicio devuelve una URL firmada u otra estructura
        return JSONResponse({"ok": True, "resource": pdf_bytes_or_path})

# --- Punto de arranque (local / Azure App Service sin Docker) ---
if __name__ == "__main__":
    import os, uvicorn
    uvicorn.run(
        "main:app",                 # <- instancia FastAPI definida arriba
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),  # Azure expone PORT; por defecto 8080
        log_level="info",
    )