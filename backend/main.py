# main.py
from __future__ import annotations
import io
import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

# ==========
# Integraciones propias (deben existir en tu repo)
# ==========
try:
    from document_intelligence import DocumentIntelligenceService
except Exception as e:  # pragma: no cover
    DocumentIntelligenceService = None
    logging.warning("DocumentIntelligenceService no disponible: %s", e)

try:
    from generate_report import generar_informe  # devuelve dict estructurado
except Exception as e:  # pragma: no cover
    generar_informe = None
    logging.warning("generar_informe no disponible: %s", e)

try:
    from pdf_service import create_employability_pdf  # devuelve bytes o ruta
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
# Modelos permisivos
# ==========
class LooseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # ignorar/guardar campos desconocidos en .__dict__


class SoftSkillResult(LooseModel):
    skill: str
    score: int = Field(ge=0, le=100)
    level: Optional[str] = None
    confidence: Optional[int] = Field(default=None, ge=0, le=100)


class CvStars(LooseModel):
    formato: Optional[int] = Field(default=None, ge=1, le=5)
    claridad: Optional[int] = Field(default=None, ge=1, le=5)
    coherencia: Optional[int] = Field(default=None, ge=1, le=5)
    informacion_clave: Optional[int] = Field(default=None, ge=1, le=5)
    ortografia: Optional[int] = Field(default=None, ge=1, le=5)


class CvAnalysis(LooseModel):
    strengths: List[str] = []
    weaknesses: List[str] = []
    feedback: Optional[str] = None
    summary: Optional[str] = None
    stars: Optional[CvStars] = None  # estrellas 1–5
    raw_text: Optional[str] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    languages: Optional[List[Dict[str, Any]]] = None
    software: Optional[List[str]] = None
    contact: Optional[Dict[str, Any]] = None


class JobPreference(LooseModel):
    areas: List[str] = []          # también mapearemos roles/sectores
    needs: List[str] = []
    workMode: Optional[str] = None
    availability: Optional[str] = None
    willingToRelocate: Optional[bool] = None
    hasDisabilityCert: Optional[bool] = None


class EmployabilityReportRequest(LooseModel):
    userId: Optional[str] = None
    fullName: Optional[str] = None
    softSkills: List[SoftSkillResult] = []
    cvAnalysis: Optional[CvAnalysis] = None
    jobPreferences: Optional[JobPreference] = None
    completedGames: Optional[List[str]] = None
    logs: Optional[List[Dict[str, Any]]] = None


class ReportResponse(LooseModel):
    report: Dict[str, Any] = {}
    recommendations: Optional[List[str]] = None
    level: Optional[str] = None
    employabilityScore: Optional[int] = Field(default=None, ge=0, le=100)


# ==========
# Utilidades
# ==========
def _safe_json_loads(maybe_json: Optional[str]) -> Any:
    if not maybe_json:
        return None
    try:
        return json.loads(maybe_json)
    except Exception:
        return maybe_json


def _stars(n: Optional[int]) -> str:
    return "★" * int(n or 0) + "☆" * (5 - int(n or 0))


def format_cv_analysis(cv: Optional[CvAnalysis]) -> str:
    if not cv:
        return (
            "CV ANALIZADO\n"
            "- No se ha podido analizar el CV. Aporta logros, responsabilidades, fechas y enlaces.\n"
        )

    lines = ["CV ANALIZADO"]
    if cv.summary:
        lines.append(f"Resumen: {cv.summary}")

    if cv.stars:
        lines.extend(
            [
                f"Formato: {_stars(cv.stars.formato)}",
                f"Claridad: {_stars(cv.stars.claridad)}",
                f"Coherencia: {_stars(cv.stars.coherencia)}",
                f"Información clave: {_stars(cv.stars.informacion_clave)}",
                f"Ortografía: {_stars(cv.stars.ortografia)}",
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
            line = line.strip("• ").strip()
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

    lines.append("\n13) FRASE FINAL")
    lines.append("Cierra con un consejo accionable y motivador en 2–3 frases.")

    prompt = "\n".join(lines)
    logger.info(
        "Prompt generado (len=%s) | Marcadores: CV ANALIZADO=%s, JUEGOS COMPLETADOS=%s, PREFERENCIAS LABORALES=%s, 13) FRASE FINAL=%s",
        len(prompt),
        "CV ANALIZADO" in prompt,
        "JUEGOS COMPLETADOS" in prompt,
        "PREFERENCIAS LABORALES" in prompt,
        "13) FRASE FINAL" in prompt,
    )
    return prompt


def normalize_ai_response(raw: Any) -> Dict[str, Any]:
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


# ---------- Adaptadores de entrada (evitan 422) ----------
def _norm_bool(v: Any) -> Optional[bool]:
    if isinstance(v, bool):
        return v
    if v in (None, "", "null"):
        return None
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "si", "sí"):
        return True
    if s in ("false", "0", "no"):
        return False
    return None

def _normalize_softskills(raw: Any) -> List[SoftSkillResult]:
    out: List[SoftSkillResult] = []
    if not raw:
        return out
    for item in list(raw):
        if not isinstance(item, dict):
            continue
        skill = item.get("skill") or item.get("name") or item.get("nombre")
        score = item.get("score", item.get("value", item.get("puntuacion", 0)))
        level = item.get("level") or item.get("nivel")
        conf = item.get("confidence") or item.get("confianza")
        try:
            out.append(SoftSkillResult(skill=str(skill), score=int(score), level=level, confidence=None if conf is None else int(conf)))
        except Exception:
            # Si un ítem viene mal formado, lo ignoramos para no romper la petición
            continue
    return out

def _normalize_prefs(raw: Any) -> JobPreference:
    if not isinstance(raw, dict):
        return JobPreference()
    areas = raw.get("areas") or raw.get("roles") or raw.get("sectores") or []
    if isinstance(areas, str):
        areas = [a.strip() for a in areas.split(",") if a.strip()]
    needs = raw.get("needs") or raw.get("necesidades") or []
    if isinstance(needs, str):
        needs = [n.strip() for n in needs.split(",") if n.strip()]
    return JobPreference(
        areas=list(areas),
        needs=list(needs),
        workMode=raw.get("workMode") or raw.get("modalidad"),
        availability=raw.get("availability") or raw.get("disponibilidad"),
        willingToRelocate=_norm_bool(raw.get("willingToRelocate") or raw.get("relocalizacion") or raw.get("relocalización")),
        hasDisabilityCert=_norm_bool(raw.get("hasDisabilityCert") or raw.get("certificadoDiscapacidad")),
    )

def _normalize_cv(raw: Any) -> Optional[CvAnalysis]:
    if not isinstance(raw, dict):
        return None
    stars = raw.get("stars") or raw.get("estrellas")
    cv_stars = None
    if isinstance(stars, dict):
        cv_stars = CvStars(
            formato=stars.get("formato") or stars.get("format"),
            claridad=stars.get("claridad") or stars.get("clarity"),
            coherencia=stars.get("coherencia") or stars.get("coherence"),
            informacion_clave=stars.get("informacion_clave") or stars.get("informacionClave") or stars.get("key_info"),
            ortografia=stars.get("ortografia") or stars.get("orthography") or stars.get("spelling"),
        )
    return CvAnalysis(
        strengths=raw.get("strengths") or raw.get("fortalezas") or [],
        weaknesses=raw.get("weaknesses") or raw.get("areas_mejora") or raw.get("areasDeMejora") or [],
        feedback=raw.get("feedback") or raw.get("correcciones"),
        summary=raw.get("summary") or raw.get("resumen"),
        stars=cv_stars,
        raw_text=raw.get("raw_text") or raw.get("texto"),
        experience=raw.get("experience"),
        education=raw.get("education"),
        languages=raw.get("languages"),
        software=raw.get("software"),
        contact=raw.get("contact"),
    )

def _coerce_request(body: Dict[str, Any]) -> EmployabilityReportRequest:
    return EmployabilityReportRequest(
        userId=body.get("userId") or body.get("usuarioId"),
        fullName=body.get("fullName") or body.get("nombre"),
        softSkills=_normalize_softskills(body.get("softSkills") or body.get("soft_skills")),
        cvAnalysis=_normalize_cv(body.get("cvAnalysis") or body.get("cv")),
        jobPreferences=_normalize_prefs(body.get("jobPreferences") or body.get("preferencias")),
        completedGames=body.get("completedGames") or body.get("juegos") or [],
        logs=body.get("logs") or [],
    )


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
    logger.info("Analizando CV PDF: %s", file.filename)

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Archivo vacío")

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
def informe_ia(req_body: Dict[str, Any] = Body(...)):
    """
    Endpoint permisivo: acepta cualquier payload "razonable" del frontend,
    lo normaliza y genera un informe estructurado.
    """
    req = _coerce_request(req_body)
    logger.info("Generando informe profesional para usuario: %s", req.userId or "desconocido")

    if generar_informe is None:
        raise HTTPException(status_code=500, detail="Módulo de generación de informe no disponible")

    prompt = build_prompt(req)
    try:
        data = normalize_ai_response(generar_informe(prompt))
    except Exception as e:
        logger.exception("Error generando informe con IA: %s", e)
        raise HTTPException(status_code=500, detail=f"Error generando informe con IA: {e}")

    report = data.get("report") or data
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
def generate_report_pdf(req_body: Dict[str, Any] = Body(...)):
    """
    Genera el PDF final a partir del informe IA (que vuelve a generarse aquí).
    """
    if create_employability_pdf is None:
        raise HTTPException(status_code=500, detail="Servicio de PDF no disponible")
    if generar_informe is None:
        raise HTTPException(status_code=500, detail="Módulo de generación de informe no disponible")

    req = _coerce_request(req_body)
    prompt = build_prompt(req)
    ai_data = normalize_ai_response(generar_informe(prompt))

    try:
        pdf_bytes_or_path = create_employability_pdf({
            "userId": req.userId,
            "fullName": req.fullName,
            "softSkills": [s.dict() for s in req.softSkills],
            "cvAnalysis": req.cvAnalysis.dict() if req.cvAnalysis else None,
            "jobPreferences": req.jobPreferences.dict() if req.jobPreferences else None,
            "completedGames": req.completedGames or [],
            "report": ai_data,
        })
    except Exception as e:
        logger.exception("Error creando PDF: %s", e)
        raise HTTPException(status_code=500, detail=f"Error creando PDF: {e}")

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
        return JSONResponse({"ok": True, "resource": pdf_bytes_or_path})
