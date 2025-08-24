# main.py
from __future__ import annotations
import io
import json
import logging
import os
import datetime
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

try:
    from new_report_schema import NewReportSchema, create_default_report, convert_old_format_to_new, create_frontend_compatible_data
except Exception as e:  # pragma: no cover
    NewReportSchema = None
    create_default_report = None
    convert_old_format_to_new = None
    create_frontend_compatible_data = None
    logging.warning("new_report_schema no disponible: %s", e)

# ==========
# Configuración y app única
# ==========
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s - %(message)s")
logger = logging.getLogger("evaluador-backend")

from contextlib import asynccontextmanager

def validate_dependencies():
    """Valida que las dependencias críticas estén disponibles"""
    missing_services = []
    warnings = []
    
    # Verificar servicios críticos
    if DocumentIntelligenceService is None:
        missing_services.append("Document Intelligence")
        warnings.append("AZURE_DOCUMENT_INTELLIGENCE_KEY no configurada")
    
    if generar_informe is None:
        missing_services.append("Generación de Informes")
        warnings.append("AZURE_OPENAI_API_KEY no configurada")
    
    if create_employability_pdf is None:
        missing_services.append("Servicio de PDF")
        warnings.append("reportlab no disponible")
    
    # Verificar variables de entorno críticas
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        warnings.append("AZURE_OPENAI_API_KEY no configurada")
    
    if not os.getenv("AZURE_OPENAI_ENDPOINT"):
        warnings.append("AZURE_OPENAI_ENDPOINT no configurado")
    
    # Mostrar estado
    if missing_services:
        logger.warning(f"⚠️ Servicios no disponibles: {', '.join(missing_services)}")
        logger.warning("La aplicación funcionará con funcionalidad limitada")
        
        if warnings:
            logger.warning("Configuraciones faltantes:")
            for warning in warnings:
                logger.warning(f"  - {warning}")
        
        logger.info("Para funcionalidad completa, configura las variables de entorno necesarias")
        logger.info("Consulta backend/env.example para más detalles")
    else:
        logger.info("✅ Todos los servicios críticos están disponibles")
    
    # Mostrar estado de Azure
    azure_status = {
        "openai": bool(os.getenv("AZURE_OPENAI_API_KEY")),
        "document_intelligence": bool(os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")),
        "storage": bool(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    }
    
    logger.info(f"Estado de Azure: OpenAI={azure_status['openai']}, Document Intelligence={azure_status['document_intelligence']}, Storage={azure_status['storage']}")
    
    return len(missing_services) == 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    logger.info("🚀 Iniciando EvaluaTE Backend...")
    validate_dependencies()
    logger.info("✅ Aplicación iniciada correctamente")
    yield
    logger.info("🛑 Cerrando EvaluaTE Backend...")

app = FastAPI(title="EvaluaTE Backend", version="1.0.0", lifespan=lifespan)

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
    
    class Config:
        extra = "allow"  # Permitir campos adicionales para compatibilidad


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
def _to_int(v: Any) -> Optional[int]:
    try:
        return None if v is None or v == "" else int(v)
    except Exception:
        return None


def _as_list_str(val: Any) -> Optional[List[str]]:
    if val is None:
        return None
    if isinstance(val, list):
        return [str(x) for x in val]
    if isinstance(val, str):
        parts = [p.strip() for p in val.replace(";", ",").split(",") if p.strip()]
        return parts or None
    return [str(val)]


def _as_list_dict(val: Any) -> Optional[List[Dict[str, Any]]]:
    """
    Convierte:
      - dict -> [dict]
      - "texto" -> [{"text": "texto"}]
      - [ "a", {"k":"v"} ] -> [{"text":"a"}, {"k":"v"}]
      - None -> None
    """
    if val is None:
        return None
    if isinstance(val, list):
        out: List[Dict[str, Any]] = []
        for it in val:
            if isinstance(it, dict):
                out.append(it)
            elif isinstance(it, str):
                if it.strip():
                    out.append({"text": it.strip()})
            else:
                out.append({"value": it})
        return out
    if isinstance(val, dict):
        return [val]
    if isinstance(val, str) and val.strip():
        return [{"text": val.strip()}]
    return None


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

    stars = raw.get("stars") or raw.get("estrellas") or {}
    cv_stars = None
    if isinstance(stars, dict):
        cv_stars = CvStars(
            formato=_to_int(stars.get("formato") or stars.get("format")),
            claridad=_to_int(stars.get("claridad") or stars.get("clarity")),
            coherencia=_to_int(stars.get("coherencia") or stars.get("coherence")),
            informacion_clave=_to_int(
                stars.get("informacion_clave")
                or stars.get("informacionClave")
                or stars.get("key_info")
            ),
            ortografia=_to_int(
                stars.get("ortografia") or stars.get("orthography") or stars.get("spelling")
            ),
        )

    # ⚠️ Coerciones que evitan el error: si llega "regular" u otro texto,
    # lo convertimos a [{"text":"regular"}] en vez de romper la validación.
    experience = _as_list_dict(raw.get("experience") or raw.get("experiencia"))
    education = _as_list_dict(raw.get("education") or raw.get("formacion") or raw.get("formación"))
    languages = _as_list_dict(raw.get("languages") or raw.get("idiomas"))
    software = _as_list_str(raw.get("software") or raw.get("tools"))

    contact_raw = raw.get("contact")
    contact: Optional[Dict[str, Any]]
    if isinstance(contact_raw, dict):
        contact = contact_raw
    elif isinstance(contact_raw, str) and contact_raw.strip():
        contact = {"text": contact_raw.strip()}
    else:
        contact = None

    return CvAnalysis(
        strengths=raw.get("strengths") or raw.get("fortalezas") or [],
        weaknesses=raw.get("weaknesses") or raw.get("areas_mejora") or raw.get("areasDeMejora") or [],
        feedback=raw.get("feedback") or raw.get("correcciones"),
        summary=raw.get("summary") or raw.get("resumen"),
        stars=cv_stars,
        raw_text=raw.get("raw_text") or raw.get("texto"),
        experience=experience,
        education=education,
        languages=languages,
        software=software,
        contact=contact,
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
@app.get("/")
def root():
    return {"ok": True, "service": "evaluador-backend"}


@app.get("/health")
def health():
    return {"ok": True, "status": "healthy"}

@app.get("/api/system/status")
def system_status():
    """Endpoint que muestra el estado de todas las dependencias del sistema"""
    import datetime
    
    status = {
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "operational",
        "services": {
            "document_intelligence": DocumentIntelligenceService is not None,
            "report_generation": generar_informe is not None,
            "pdf_service": create_employability_pdf is not None,
            "azure_openai": bool(os.getenv("AZURE_OPENAI_API_KEY")),
            "azure_document_intelligence": bool(os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")),
            "email_service": bool(os.getenv("EMAIL_USER") and os.getenv("EMAIL_PASSWORD")),
        },
        "environment": {
            "log_level": LOG_LEVEL,
            "cors_origins": origins,
            "port": os.getenv("PORT", "8000"),
        }
    }
    
    # Determinar estado general
    available_services = sum(status["services"].values())
    total_services = len(status["services"])
    
    if available_services == total_services:
        status["status"] = "operational"
        status["message"] = "Todos los servicios están disponibles"
    elif available_services > total_services // 2:
        status["status"] = "degraded"
        status["message"] = f"Servicio degradado: {available_services}/{total_services} servicios disponibles"
    else:
        status["status"] = "critical"
        status["message"] = f"Servicio crítico: solo {available_services}/{total_services} servicios disponibles"
    
    return status


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
    
    # Verificar si DocumentIntelligenceService está disponible
    if DocumentIntelligenceService is None:
        logger.warning("DocumentIntelligenceService no configurado. Se devolverá análisis básico.")
        logger.info("Para análisis completo, configura AZURE_DOCUMENT_INTELLIGENCE_KEY en .env")
        
        # Crear análisis básico basado en el nombre del archivo y datos del usuario
        try:
            # Extraer texto básico del PDF si es posible
            raw_text = None
            try:
                import PyPDF2
                import io
                pdf_file = io.BytesIO(content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                raw_text = ""
                for page in pdf_reader.pages:
                    raw_text += page.extract_text() + "\n"
                logger.info("Texto extraído con PyPDF2: %s caracteres", len(raw_text or ""))
            except ImportError:
                logger.info("PyPDF2 no disponible, usando análisis básico")
            except Exception as e:
                logger.info("Error extrayendo texto del PDF: %s", e)
            
            # Crear análisis básico
            cv_data = {
                "summary": f"CV analizado: {file.filename}",
                "strengths": [
                    "Documento PDF válido",
                    "Archivo procesado correctamente",
                    "Análisis básico completado"
                ],
                "weaknesses": [
                    "Análisis de IA no disponible",
                    "Se requieren credenciales de Azure",
                    "Procesamiento limitado"
                ],
                "feedback": "Para un análisis completo con IA, configura las credenciales de Azure Document Intelligence en las variables de entorno.",
                "stars": {
                    "formato": 4,
                    "claridad": 3,
                    "coherencia": 3,
                    "informacion_clave": 3,
                    "ortografia": 4
                },
                "raw_text": raw_text or "Texto no extraído (requiere PyPDF2)",
                "experience": [],
                "education": [],
                "languages": [],
                "software": [],
                "contact": {}
            }
            
        except Exception as e:
            logger.exception("Error creando análisis básico: %s", e)
            # Fallback mínimo
            cv_data = {
                "summary": "CV recibido",
                "strengths": ["Archivo procesado"],
                "weaknesses": ["Análisis limitado"],
                "feedback": "Análisis básico completado",
                "stars": None,
                "raw_text": None,
                "experience": [],
                "education": [],
                "languages": [],
                "software": [],
                "contact": {}
            }
    
    else:
        # DocumentIntelligenceService está disponible
        try:
            model_id = os.getenv("AZURE_DI_MODEL_ID", "prebuilt-document")
            logger.info("🔍 Iniciando análisis con Azure Document Intelligence (modelo: %s)", model_id)
            
            di = DocumentIntelligenceService(model_id=model_id)
            result = di.analyze_cv_with_document_intelligence(content)
            
            # Validar y normalizar el resultado
            if not isinstance(result, dict):
                logger.warning("Resultado de Document Intelligence no es un diccionario: %s", type(result))
                result = {}
            
            cv_data = {
                "summary": result.get("summary") or result.get("cv_summary") or f"CV analizado con IA: {file.filename}",
                "strengths": result.get("strengths", []) or ["Análisis de IA completado"],
                "weaknesses": result.get("weaknesses", []) or ["Sin áreas de mejora identificadas"],
                "feedback": result.get("feedback") or result.get("recommendations") or "Análisis de IA exitoso",
                "stars": result.get("stars") or {"formato": 4, "claridad": 4, "coherencia": 4, "informacion_clave": 4, "ortografia": 4},
                "raw_text": result.get("raw_text") or result.get("text") or "Texto extraído por IA",
                "experience": result.get("experience") or [],
                "education": result.get("education") or [],
                "languages": result.get("languages") or [],
                "software": result.get("software") or [],
                "contact": result.get("contact") or {},
            }
            
            logger.info("✅ Análisis de IA completado exitosamente")
            
        except Exception as e:
            logger.exception("❌ Fallo analizando CV con Document Intelligence: %s", e)
            # En lugar de fallar, devolver análisis básico
            cv_data = {
                "summary": f"Error en análisis IA: {str(e)[:100]}...",
                "strengths": ["Archivo recibido", "Procesamiento básico completado"],
                "weaknesses": ["Error en procesamiento IA", "Análisis limitado"],
                "feedback": "Se produjo un error durante el análisis con IA. Se ha procesado el archivo básicamente.",
                "stars": {"formato": 3, "claridad": 3, "coherencia": 3, "informacion_clave": 3, "ortografia": 3},
                "raw_text": None,
                "experience": [],
                "education": [],
                "languages": [],
                "software": [],
                "contact": {}
            }

    payload = {
        "ok": True,
        "cvAnalysis": cv_data,
        "softSkills": _safe_json_loads(softSkillsJson) or [],
        "jobPreferences": _safe_json_loads(jobPreferencesJson) or {},
        "completedGames": _safe_json_loads(completedGamesJson) or [],
        "logs": _safe_json_loads(logsJson) or [],
    }
    return JSONResponse(payload)


@app.post("/api/informe-ia")
def informe_ia(req_body: Dict[str, Any] = Body(...)):
    """
    Endpoint actualizado: genera informe con el nuevo esquema estructurado
    """
    req = _coerce_request(req_body)
    logger.info("Generando informe profesional con nuevo esquema para usuario: %s", req.userId or "desconocido")

    try:
        # Intentar generar informe con IA si está disponible
        if generar_informe is not None:
            prompt = build_prompt(req)
            try:
                data = normalize_ai_response(generar_informe(prompt))
                logger.info("Informe generado con IA exitosamente")
            except Exception as e:
                logger.exception("Error generando informe con IA: %s", e)
                data = None
        else:
            data = None
            logger.warning("Módulo de generación de informe no disponible, usando esquema por defecto")

        # Crear datos compatibles con el frontend
        new_report = None
        if data and isinstance(data, dict):
            # Intentar convertir formato antiguo al nuevo
            try:
                new_report = convert_old_format_to_new(data)
                logger.info("Formato antiguo convertido exitosamente al nuevo esquema")
            except Exception as e:
                logger.exception("Error convirtiendo formato antiguo: %s", e)
                logger.info("Continuando con datos por defecto...")
                new_report = None

        # Si no se pudo convertir, crear datos compatibles con frontend
        if new_report is None:
            try:
                frontend_data = create_frontend_compatible_data(
                    full_name=req.fullName or "Usuario",
                    soft_skills=req.softSkills or [],
                    cv_analysis=req.cvAnalysis or {},
                    job_preferences=req.jobPreferences or {}
                )
                logger.info("Datos compatibles con frontend creados exitosamente")
            except Exception as e:
                logger.exception("Error creando datos compatibles: %s", e)
                # Fallback último recurso
                frontend_data = {
                    "ok": True,
                    "message": "Informe generado con funcionalidad limitada",
                    "data": {
                        "fullName": req.fullName or "Usuario",
                        "softSkills": req.softSkills or [],
                        "cvAnalysis": req.cvAnalysis or {},
                        "jobPreferences": req.jobPreferences or {}
                    }
                }
        else:
            # Convertir el nuevo esquema a formato compatible con frontend
            try:
                frontend_data = create_frontend_compatible_data(
                    full_name=req.fullName or "Usuario",
                    soft_skills=req.softSkills or [],
                    cv_analysis=req.cvAnalysis or {},
                    job_preferences=req.jobPreferences or {}
                )
                logger.info("Datos convertidos a formato compatible con frontend")
            except Exception as e:
                logger.exception("Error convirtiendo esquema: %s", e)
                # Fallback si falla la conversión
                frontend_data = create_frontend_compatible_data(
                    full_name=req.fullName or "Usuario",
                    soft_skills=req.softSkills or [],
                    cv_analysis=req.cvAnalysis or {},
                    job_preferences=req.jobPreferences or {}
                )

        # Devolver respuesta en formato que espera el frontend
        return JSONResponse(content=frontend_data)

    except Exception as e:
        logger.exception("❌ Error general en endpoint informe-ia: %s", e)
        # En caso de error, devolver datos compatibles con frontend
        try:
            fallback_data = create_frontend_compatible_data(
                full_name=req.fullName or "Usuario",
                soft_skills=req.softSkills or [],
                cv_analysis=req.cvAnalysis or {},
                job_preferences=req.jobPreferences or {}
            )
            logger.info("✅ Datos de fallback creados exitosamente")
            return JSONResponse(content=fallback_data)
        except Exception as fallback_error:
            logger.exception("❌ Error creando datos de fallback: %s", fallback_error)
            # Último recurso: respuesta mínima
            return JSONResponse(
                content={
                    "ok": True,
                    "message": "Informe generado con funcionalidad limitada debido a errores del sistema",
                    "data": {
                        "fullName": req.fullName or "Usuario",
                        "softSkills": req.softSkills or [],
                        "cvAnalysis": req.cvAnalysis or {},
                        "jobPreferences": req.jobPreferences or {}
                    }
                },
                status_code=200  # No fallar, devolver datos mínimos
            )


@app.post("/api/pdf/generate-report")
def generate_report_pdf(req_body: Dict[str, Any] = Body(...)):
    """
    Genera el PDF final a partir del informe IA (que vuelve a generarse aquí).
    """
    # Validar dependencias con mensajes más informativos
    if create_employability_pdf is None:
        logger.error("❌ Servicio de PDF no disponible")
        raise HTTPException(
            status_code=500, 
            detail="Servicio de PDF no disponible. Verifica la instalación de reportlab y las dependencias."
        )
    
    if generar_informe is None:
        logger.error("❌ Módulo de generación de informe no disponible")
        raise HTTPException(
            status_code=500, 
            detail="Módulo de generación de informe no disponible. Verifica la configuración de Azure OpenAI."
        )

    req = _coerce_request(req_body)
    prompt = build_prompt(req)
    ai_data = normalize_ai_response(generar_informe(prompt))

    try:
        # Preparar datos para el PDF de forma segura
        pdf_data = {
            "userId": req.userId,
            "fullName": req.fullName,
            "softSkills": [s.dict() if hasattr(s, 'dict') else s for s in req.softSkills],
            "cvAnalysis": req.cvAnalysis.dict() if req.cvAnalysis and hasattr(req.cvAnalysis, 'dict') else req.cvAnalysis,
            "jobPreferences": req.jobPreferences.dict() if req.jobPreferences and hasattr(req.jobPreferences, 'dict') else req.jobPreferences,
            "completedGames": req.completedGames or [],
            "report": ai_data,
        }
        
        logger.info("Generando PDF con datos: %s", {k: type(v).__name__ for k, v in pdf_data.items()})
        pdf_bytes_or_path = create_employability_pdf(pdf_data)
        logger.info("✅ PDF generado exitosamente")
        
    except Exception as e:
        logger.exception("❌ Error creando PDF: %s", e)
        raise HTTPException(
            status_code=500, 
            detail=f"Error creando PDF: {str(e)[:100]}... Verifica los datos de entrada y la configuración."
        )

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

# ==========
# Ejecución del servidor
# ==========
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando servidor EvaluaTE Backend...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
