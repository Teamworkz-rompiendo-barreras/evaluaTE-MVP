# backend/main.py
# Versión limpia del backend para Azure

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel, Field
import uvicorn
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import time
import io
import json
import os
import logging
import sys
import tempfile
import re

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    import os
    # Mostrar directorio actual y buscar archivo .env
    current_dir = os.getcwd()
    env_file = os.path.join(current_dir, '.env')
    print(f"🔍 DEBUG - Directorio actual: {current_dir}")
    print(f"🔍 DEBUG - Buscando archivo .env en: {env_file}")
    print(f"🔍 DEBUG - ¿Existe archivo .env?: {os.path.exists(env_file)}")
    
    load_dotenv()
    print("✅ Archivo .env cargado correctamente")
except ImportError:
    print("⚠️ python-dotenv no está instalado, usando variables de entorno del sistema")
except Exception as e:
    print(f"⚠️ Error cargando .env: {e}")

# Limpiar variables de proxy del sistema que pueden causar problemas
import os
if 'HTTP_PROXY' in os.environ:
    del os.environ['HTTP_PROXY']
if 'HTTPS_PROXY' in os.environ:
    del os.environ['HTTPS_PROXY']
if 'ALL_PROXY' in os.environ:
    del os.environ['ALL_PROXY']

print("✅ Variables de proxy del sistema limpiadas")

# Forzar UTF-8 para stdout/stderr y logging (evita mojibake en Azure/AppService)
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("LANG", "C.UTF-8")
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    # Si el entorno no soporta reconfigure, continuamos sin interrumpir el arranque
    pass

# Configurar logging con formato explícito y forzando la configuración actual
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
    handlers=[logging.StreamHandler(stream=sys.stdout)],
    force=True,
)
logger = logging.getLogger(__name__)

# Variables de entorno para Azure OpenAI (opcionales)
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Debug: Mostrar valores cargados (enmascarando secretos)
def _mask(value: Optional[str], visible: int = 4) -> str:  # type: ignore[name-defined]
    try:
        if not value:
            return ""
        value_str = str(value)
        if len(value_str) <= visible:
            return "*" * len(value_str)
        return ("*" * (len(value_str) - visible)) + value_str[-visible:]
    except Exception:
        return "***"

print(f"🔍 DEBUG - API_KEY: {_mask(API_KEY)}")
print(f"🔍 DEBUG - ENDPOINT: {ENDPOINT}")
print(f"🔍 DEBUG - DEPLOYMENT: {DEPLOYMENT}")
print(f"🔍 DEBUG - API_VERSION: {API_VERSION}")

# Utilidad: comprobar si la versión de API soporta response_format json_schema (>= 2024-08-01-preview)
def _supports_json_schema_response_format(version_str: Optional[str]) -> bool:
    try:
        if not version_str:
            return False
        import re as _re
        m = _re.search(r"(\d{4})-(\d{2})-(\d{2})", version_str)
        if not m:
            return False
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return (y, mo, d) >= (2024, 8, 1)
    except Exception:
        return False

# Configurar NO_PROXY específicamente para el endpoint de Azure OpenAI
if ENDPOINT:
    # Extraer el dominio del endpoint (ej: teamworkzevaluate-openai.openai.azure.com)
    from urllib.parse import urlparse
    parsed_url = urlparse(ENDPOINT)
    domain = parsed_url.netloc
    os.environ['NO_PROXY'] = domain
    print(f"✅ NO_PROXY configurado para: {domain}")
else:
    os.environ['NO_PROXY'] = '*.openai.azure.com'
    print("✅ NO_PROXY configurado para *.openai.azure.com")

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
        
        # Configuración mínima sin argumentos problemáticos
        client = AzureOpenAI(
            api_key=API_KEY, 
            api_version=API_VERSION, 
            azure_endpoint=ENDPOINT
        )
        logger.info("✅ Azure OpenAI configurado correctamente")
    except Exception as e:
        logger.warning(f"⚠️ Error configurando Azure OpenAI: {e}")
        # Intentar configuración alternativa
        try:
            import os
            # Forzar configuración de entorno para evitar proxies
            os.environ['NO_PROXY'] = '*'
            os.environ['no_proxy'] = '*'
            
            client = AzureOpenAI(
                api_key=API_KEY, 
                api_version=API_VERSION, 
                azure_endpoint=ENDPOINT
            )
            logger.info("✅ Azure OpenAI configurado correctamente (configuración alternativa)")
        except Exception as e2:
            logger.warning(f"⚠️ Error en configuración alternativa: {e2}")
            client = None

# Tipos compartidos
class SoftSkillResult(BaseModel):
    skill: str
    score: int
    level: str  # 'bajo', 'medio', 'alto'
    # Confianza expresada en porcentaje 0-100. Admitimos float para ser tolerantes con el cliente
    confidence: float = Field(ge=0, le=100)

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
    recommendations: Dict[str, Any]  # Cambiado para aceptar estructura compleja
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

# ===== Normalizadores y utilidades de extracción estructurada =====
try:
    import dateparser  # type: ignore
except Exception:
    dateparser = None  # type: ignore

try:
    import phonenumbers  # type: ignore
except Exception:
    phonenumbers = None  # type: ignore

try:
    import language_tool_python  # type: ignore
except Exception:
    language_tool_python = None  # type: ignore


def norm_phone(raw: str, region: str = "ES") -> Optional[str]:
    if not raw or not phonenumbers:
        return None
    try:
        num = phonenumbers.parse(raw, region)
        if phonenumbers.is_valid_number(num):
            return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return None
    return None


def _date_to_iso_ym(d) -> Optional[str]:
    try:
        if not d:
            return None
        return f"{d.year:04d}-{d.month:02d}"
    except Exception:
        return None


def parse_range(txt: str, ref_locale: str = "es") -> Tuple[Optional[str], Optional[str], bool]:
    """Normaliza rangos de fecha en una línea cualquiera.
    Devuelve (start_yyyy_mm, end_yyyy_mm_or_None, current_flag).
    """
    if not txt:
        return None, None, False
    t = txt.strip()
    # Marcadores de presente
    present_tokens = [
        "actualidad", "presente", "ahora", "now", "current", "present"
    ]
    # Rápido: si aparece presente en el texto, marcaremos current=True sobre el segundo término
    has_present = any(tok in t.lower() for tok in present_tokens)
    if not dateparser:
        # Fallback si no está dateparser
        return None, None, has_present
    # Intentar detectar dos fechas en la línea
    parts = re.split(r"[-–—toa]\s+|\s+al\s+|\s+to\s+|\s+hasta\s+|\s+a\s+", t, maxsplit=1)
    start_dt = None
    end_dt = None
    start_iso = None
    end_iso = None
    try:
        settings = {"PREFER_DAY_OF_MONTH": "first", "REQUIRE_PARTS": ["year"], "RELATIVE_BASE": datetime.now()}
        if len(parts) == 2:
            start_dt = dateparser.parse(parts[0], languages=[ref_locale], settings=settings)
            # Solo parsear end si no es presente
            if not has_present:
                end_dt = dateparser.parse(parts[1], languages=[ref_locale], settings=settings)
        else:
            # Buscar patrón habitual y parsear ambos grupos
            m = re.search(r"([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{3,9}\.?(?:\s+\d{4})?|\d{1,2}/\d{4}|\d{4})\s*[-–—]\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{3,9}\.?(?:\s+\d{4})?|\d{1,2}/\d{4}|\d{4}|actualidad|presente)", t, re.IGNORECASE)
            if m:
                start_dt = dateparser.parse(m.group(1), languages=[ref_locale], settings=settings)
                if not any(tok in m.group(2).lower() for tok in present_tokens):
                    end_dt = dateparser.parse(m.group(2), languages=[ref_locale], settings=settings)
    except Exception:
        pass
    start_iso = _date_to_iso_ym(start_dt)
    end_iso = _date_to_iso_ym(end_dt) if end_dt else None
    current = has_present or (end_dt is None and any(tok in t.lower() for tok in present_tokens))
    return start_iso, (None if current else end_iso), current


def normalize_languages(langs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    level_map = {
        "nativo": "nativo",
        "bilingüe": "bilingue",
        "bilingue": "bilingue",
        "c2": "bilingue",
        "avanzado": "avanzado",
        "alto": "avanzado",
        "c1": "avanzado",
        "intermedio": "intermedio",
        "b2": "intermedio",
        "b1": "intermedio",
        "básico": "basico",
        "basico": "basico",
        "a2": "basico",
        "a1": "basico",
    }
    out: List[Dict[str, Any]] = []
    for it in langs or []:
        name = (it.get("name") or it.get("idioma") or "").strip()
        level = (it.get("level") or it.get("nivel") or "").lower().strip()
        out.append({"name": name, "level": level_map.get(level, level or "")})
    return out


def grammar_issues_es(text: str) -> List[str]:
    if not text or not language_tool_python:
        return []
    try:
        tool = language_tool_python.LanguageTool("es")
        matches = tool.check(text[:20000])
        issues: List[str] = []
        for m in matches[:50]:
            sug = ", ".join(m.replacements[:3]) if getattr(m, "replacements", None) else ""
            issues.append(f"{m.message} (regla: {m.ruleId}; sugerencia: {sug})")
        return issues
    except Exception:
        return []


def build_cv_json_schema() -> Dict[str, Any]:
    return {
        "name": "CVSchema",
        "schema": {
            "type": "object",
            "properties": {
                "candidate": {
                    "type": "object",
                    "properties": {
                        "full_name": {"type": "string"},
                        "location": {"type": "string"},
                        "emails": {"type": "array", "items": {"type": "string", "format": "email"}},
                        "phones": {"type": "array", "items": {"type": "string"}},
                        "links": {
                            "type": "object",
                            "properties": {"linkedin": {"type": "string"}, "portfolio": {"type": "string"}},
                        },
                    },
                    "required": ["emails"],
                },
                "summary": {"type": "string"},
                "experience": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "position": {"type": "string"},
                            "company": {"type": "string"},
                            "location": {"type": "string"},
                            "start_date": {"type": "string", "pattern": "^\\\d{4}(-\\\d{2})?$"},
                            "end_date": {"type": ["string", "null"], "pattern": "^\\\d{4}(-\\\d{2})?$"},
                            "current": {"type": "boolean"},
                            "description": {"type": "string"},
                            "bullets": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["position", "company"],
                    },
                },
                "education": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "degree": {"type": "string"},
                            "institution": {"type": "string"},
                            "location": {"type": "string"},
                            "start_date": {"type": "string", "pattern": "^\\\d{4}(-\\\d{2})?$"},
                            "end_date": {"type": "string", "pattern": "^\\\d{4}(-\\\d{2})?$"},
                            "notes": {"type": "string"},
                        },
                    },
                },
                "languages": {
                    "type": "array",
                    "items": {"type": "object", "properties": {"name": {"type": "string"}, "level": {"type": "string"}}},
                },
                "skills": {
                    "type": "object",
                    "properties": {
                        "hard": {"type": "array", "items": {"type": "string"}},
                        "soft": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "certifications": {
                    "type": "array",
                    "items": {"type": "object", "properties": {"name": {"type": "string"}, "date": {"type": "string", "pattern": "^\\\d{4}(-\\\d{2})?$"}}},
                },
                "projects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}, "tech": {"type": "array", "items": {"type": "string"}}, "description": {"type": "string"}},
                    },
                },
            },
            "required": ["candidate"],
        },
        "strict": True,
    }


def _sections_from_layout_result(result: Any) -> Dict[str, Any]:
    """Extrae secciones por headings y tablas del Layout v4."""
    sections: Dict[str, Dict[str, Any]] = {}
    try:
        paragraphs = getattr(result, "paragraphs", None)
        if paragraphs:
            current_key = "header"
            buffer: List[str] = []
            for p in paragraphs:
                role = getattr(p, "role", None)
                text = getattr(p, "content", "")
                if role in ("title", "heading") and text and len(text) < 80:
                    if buffer:
                        sections.setdefault(current_key, {"text": ""})
                        sections[current_key]["text"] = (sections[current_key].get("text", "") + "\n" + "\n".join(buffer)).strip()
                        buffer = []
                    current_key = re.sub(r"\s+", " ", text).strip().lower()
                else:
                    if text:
                        buffer.append(text)
            if buffer:
                sections.setdefault(current_key, {"text": ""})
                sections[current_key]["text"] = (sections[current_key].get("text", "") + "\n" + "\n".join(buffer)).strip()
        # Tablas
        tables = getattr(result, "tables", None)
        if tables:
            tables_text = []
            for tb in tables[:20]:
                try:
                    rows = []
                    for cell in tb.cells:
                        rows.append((cell.row_index, cell.column_index, cell.content))
                    grid: Dict[int, Dict[int, str]] = {}
                    for r, c, v in rows:
                        grid.setdefault(r, {})[c] = v
                    for r in sorted(grid.keys()):
                        cols = [grid[r].get(c, "") for c in sorted(grid[r].keys())]
                        tables_text.append(" | ".join(cols))
                except Exception:
                    continue
            if tables_text:
                sections.setdefault("tables", {})["text"] = "\n".join(tables_text)
    except Exception:
        pass
    if not sections:
        try:
            collected = []
            for page in getattr(result, "pages", []) or []:
                for line in getattr(page, "lines", []) or []:
                    collected.append(getattr(line, "content", ""))
            if collected:
                sections["document"] = {"text": "\n".join(collected)}
        except Exception:
            pass
    return sections

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
    """Genera un informe profesional de empleabilidad con IA"""
    try:
        logger.info(f"Generando informe profesional para usuario: {request.userId}")
        
        # Calcular puntaje de empleabilidad
        total_skills = len(request.softSkills)
        if total_skills == 0:
            # SOLUCIÓN: Dar puntaje base más alto para usuarios sin habilidades evaluadas
            employability_score = 60  # Cambio de 50 a 60 para ser más optimista
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

        # Generar informe profesional con IA
        if client:
            professional_report = await generate_professional_report_with_ai(request, employability_score, level)
        else:
            professional_report = generate_basic_report(request, employability_score, level)

        # Crear reporte con jobPreferences incluido
        report = {
            "userId": request.userId,
            "fullName": request.fullName,
            "softSkills": [skill.dict() for skill in request.softSkills],
            # Incluir cvAnalysis original si vino en la solicitud para mayor trazabilidad
            "cvAnalysis": request.cvAnalysis.dict() if request.cvAnalysis else None,
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

        # Recalcular puntaje global como media de todas las soft skills actuales si hay datos válidos
        try:
            scores = [int(s.get("score", 0)) for s in report["softSkills"] if isinstance(s, dict)]
            avg_score = (sum(scores) // len(scores)) if scores else employability_score
        except Exception:
            avg_score = employability_score

        # Adjuntar análisis de CV si se subió durante el flujo (/api/pdf/analyze-cv)
        final_recommendations = professional_report.get("recommendations", {}) if isinstance(professional_report, dict) else {}
        try:
            # Si existe un campo cvAnalysis enriquecido en el informe devuelto por IA, úsalo; si no, conservar el del request
            enriched_cv = None
            if isinstance(final_recommendations, dict):
                enriched_cv = final_recommendations.get("cv_analysis_structured")
            
            # Asegurar que la información del CV se incluya en el informe final
            if enriched_cv and isinstance(enriched_cv, dict):
                # Si la IA generó información enriquecida del CV, úsala
                if not report.get("cvAnalysis"):
                    report["cvAnalysis"] = {}
                # Fusionar información enriquecida con la existente
                if isinstance(report["cvAnalysis"], dict):
                    report["cvAnalysis"].update(enriched_cv)
                else:
                    report["cvAnalysis"] = enriched_cv
            elif request.cvAnalysis:
                # Si no hay información enriquecida pero sí hay análisis del CV, asegurar que se incluya
                if not report.get("cvAnalysis"):
                    report["cvAnalysis"] = request.cvAnalysis.dict()
                
                # También incluir información detallada si está disponible
                cv_data = request.cvAnalysis.dict()
                if hasattr(request.cvAnalysis, 'cv_structured') and request.cvAnalysis.cv_structured:
                    cv_data['cv_structured'] = request.cvAnalysis.cv_structured
                if hasattr(request.cvAnalysis, 'candidate') and request.cvAnalysis.candidate:
                    cv_data['candidate'] = request.cvAnalysis.candidate
                if hasattr(request.cvAnalysis, 'contact') and request.cvAnalysis.contact:
                    cv_data['contact'] = request.cvAnalysis.contact
                if hasattr(request.cvAnalysis, 'experience') and request.cvAnalysis.experience:
                    cv_data['experience'] = request.cvAnalysis.experience
                if hasattr(request.cvAnalysis, 'education') and request.cvAnalysis.education:
                    cv_data['education'] = request.cvAnalysis.education
                if hasattr(request.cvAnalysis, 'languages') and request.cvAnalysis.languages:
                    cv_data['languages'] = request.cvAnalysis.languages
                if hasattr(request.cvAnalysis, 'periods') and request.cvAnalysis.periods:
                    cv_data['periods'] = request.cvAnalysis.periods
                
                report["cvAnalysis"] = cv_data
        except Exception as e:
            logger.warning(f"Error procesando información del CV: {e}")
            pass

        response_data = ReportResponse(
            report=report,
            recommendations=final_recommendations,
            employabilityScore=avg_score,
            level=("alto" if avg_score >= 80 else ("medio" if avg_score >= 50 else "bajo")),
            summary=str(professional_report.get("summary", "")) if isinstance(professional_report, dict) else "",
            createdAt=datetime.now().isoformat()
        )
        
        logger.info(f"Respuesta final del informe generada exitosamente para {request.userId}")
        logger.info(f"Summary presente: {'✅' if response_data.summary else '❌'}")
        logger.info(f"Recommendations presente: {'✅' if response_data.recommendations else '❌'}")
        
        # Logging adicional para verificar información del CV
        if report.get("cvAnalysis"):
            cv_info = report["cvAnalysis"]
            logger.info(f"Información del CV incluida en el informe:")
            logger.info(f"  - Fortalezas: {cv_info.get('strengths', [])}")
            logger.info(f"  - Experiencia: {cv_info.get('experience', [])}")
            logger.info(f"  - Formación: {cv_info.get('education', [])}")
            if hasattr(request.cvAnalysis, 'cv_structured') and request.cvAnalysis.cv_structured:
                logger.info(f"  - CV estructurado: ✅")
            if hasattr(request.cvAnalysis, 'candidate') and request.cvAnalysis.candidate:
                logger.info(f"  - Candidato: {request.cvAnalysis.candidate}")
        else:
            logger.warning("❌ No se incluyó información del CV en el informe final")
        
        return response_data

    except Exception as e:
        logger.error(f"Error generando informe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_professional_report_with_ai(request: EmployabilityReportRequest, employability_score: int, level: str) -> dict:
    """Genera un informe profesional usando IA con el prompt maestro mejorado"""
    
    # Preparar datos estructurados para el prompt
    candidate_data = {
        "fullName": request.fullName,
        "location": getattr(request.cvAnalysis, 'contact', {}).get('location', 'No consta') if request.cvAnalysis else 'No consta',
        "email": getattr(request.cvAnalysis, 'contact', {}).get('emails', ['No consta'])[0] if request.cvAnalysis and getattr(request.cvAnalysis, 'contact', {}) else 'No consta',
        "phone": getattr(request.cvAnalysis, 'contact', {}).get('phones', ['No consta'])[0] if request.cvAnalysis and getattr(request.cvAnalysis, 'contact', {}) else 'No consta',
        "hasDisabilityCertificate": request.jobPreferences.hasDisabilityCert if request.jobPreferences else None,
        "disabilityType": "No especificado"  # Campo opcional que no tienes implementado
    }
    
    # Preparar soft skills con puntuaciones
    soft_skills_data = []
    for skill in request.softSkills:
        # Convertir level a puntuación numérica para el análisis
        level_score = {"Bajo": 30, "Medio": 60, "Alto": 90}.get(skill.level, 50)
        soft_skills_data.append({
            "skill": skill.skill,
            "score": level_score,
            "level": skill.level,
            "evidence": skill.feedback or "Evaluado mediante juego interactivo"
        })
    
    # Preparar análisis del CV
    cv_data = {
        "rawText": "No disponible",  # No tienes el texto raw del CV
        "sections": {}
    }
    
    if request.cvAnalysis:
        # Extraer información estructurada del CV
        cv_structured = getattr(request.cvAnalysis, 'cv_structured', {})
        if cv_structured:
            cv_data["sections"] = {
                "profile": cv_structured.get('candidate', 'No especificado'),
                "experience": cv_structured.get('experience', []),
                "education": cv_structured.get('education', []),
                "courses": "No especificado",  # Campo que no tienes
                "languages": cv_structured.get('languages', []),
                "software": cv_structured.get('skills', []),
                "contact": cv_structured.get('contact', {})
            }
        else:
            # Fallback a información básica
            cv_data["sections"] = {
                "profile": getattr(request.cvAnalysis, 'candidate', 'No especificado'),
                "experience": getattr(request.cvAnalysis, 'experience_detailed', []),
                "education": getattr(request.cvAnalysis, 'education_detailed', []),
                "courses": "No especificado",
                "languages": getattr(request.cvAnalysis, 'languages', []),
                "software": getattr(request.cvAnalysis, 'skills', []),
                "contact": getattr(request.cvAnalysis, 'contact', {})
            }
    
    # Preparar preferencias laborales
    job_preferences_data = {
        "desired_roles": request.jobPreferences.areas if request.jobPreferences else [],
        "desired_sectors": request.jobPreferences.areas if request.jobPreferences else [],
        "work_modes": [request.jobPreferences.workMode] if request.jobPreferences else ["No especificado"],
        "availability": request.jobPreferences.availability if request.jobPreferences else "No especificado",
        "salary_range": "No especificado",  # Campo que no tienes
        "relocation": request.jobPreferences.willingToRelocate if request.jobPreferences else None,
        "notes": f"Necesidades: {', '.join(request.jobPreferences.needs) if request.jobPreferences and hasattr(request.jobPreferences, 'needs') and request.jobPreferences.needs else 'No especificadas'}" if request.jobPreferences else "No especificado"
    }
    
    # Preparar idiomas
    languages_data = []
    if request.cvAnalysis and hasattr(request.cvAnalysis, 'languages'):
        for lang in request.cvAnalysis.languages:
            if isinstance(lang, dict):
                languages_data.append({
                    "language": lang.get('language', 'No especificado'),
                    "level": lang.get('level', 'No especificado')
                })
            else:
                languages_data.append({
                    "language": str(lang),
                    "level": "No especificado"
                })
    
    # Importar configuración de prompts
    try:
        from .prompt_config import PromptConfig
    except ImportError:
        from prompt_config import PromptConfig
    
    # Prompt maestro mejorado usando configuración centralizada
    prompt = PromptConfig.get_employability_report_prompt(
        candidate_data=candidate_data,
        soft_skills_data=soft_skills_data,
        cv_data=cv_data,
        job_preferences_data=job_preferences_data,
        employability_score=employability_score,
        level=level,
        completed_games=request.completedGames,
        languages_data=languages_data
    )

    
    try:
        # Limpiar el nombre del deployment para evitar problemas con espacios
        deployment_name = DEPLOYMENT.strip()
        
        # Structured Outputs para el informe mejorado usando configuración centralizada
        report_schema = PromptConfig.get_report_schema()

        chat_kwargs = {
            "model": deployment_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 3000,  # Aumentado para el informe más detallado
            "timeout": 90,  # Aumentado para el análisis más complejo
        }
        if _supports_json_schema_response_format(API_VERSION):
            chat_kwargs["response_format"] = {"type": "json_schema", "json_schema": report_schema}
        response = client.chat.completions.create(**chat_kwargs)
        
        # Obtener y loggear la respuesta cruda
        raw_content = response.choices[0].message.content
        logger.info(f"Respuesta cruda de Azure OpenAI (informe mejorado): {repr(raw_content[:500])}...")
        
        if not raw_content or not raw_content.strip():
            logger.error("Azure OpenAI devolvió respuesta vacía para informe mejorado")
            raise Exception("Respuesta vacía de Azure OpenAI")
        
        # Limpiar la respuesta antes de parsear
        content_to_parse = raw_content.strip()
        
        # Buscar el JSON dentro de la respuesta
        import re
        
        # Primero, intentar extraer contenido entre ```json y ```
        json_code_block_match = re.search(r'```json\s*([\s\S]*?)\s*```', content_to_parse, re.IGNORECASE)
        if json_code_block_match:
            content_to_parse = json_code_block_match.group(1).strip()
            logger.info(f"JSON extraído de bloque de código para informe mejorado: {repr(content_to_parse[:200])}...")
        else:
            # Si no hay bloque de código, buscar el JSON directamente
            json_match = re.search(r'\{.*\}', content_to_parse, re.DOTALL)
            if json_match:
                content_to_parse = json_match.group(0)
                logger.info(f"JSON extraído directamente para informe mejorado: {repr(content_to_parse[:200])}...")
            else:
                logger.error(f"No se pudo extraer JSON de la respuesta de informe mejorado: {repr(content_to_parse[:500])}")
                raise Exception("No se encontró JSON válido en la respuesta")
        
        import json
        try:
            report_data = json.loads(content_to_parse)
            logger.info(f"JSON parseado exitosamente para informe mejorado. Claves: {list(report_data.keys()) if isinstance(report_data, dict) else 'No es dict'}")
            return report_data
        except json.JSONDecodeError as je:
            logger.error(f"Error parseando JSON del informe mejorado: {je}")
            logger.error(f"Contenido que causó el error: {repr(content_to_parse[:1000])}")
            raise Exception(f"Error parseando respuesta JSON del informe mejorado: {je}")
        
    except Exception as e:
        logger.error(f"Error generando informe mejorado con IA: {e}")
        return generate_basic_report(request, employability_score, level)

def generate_basic_report(request: EmployabilityReportRequest, employability_score: int, level: str) -> dict:
    """Genera un informe básico sin IA"""
    
    has_disability_cert = request.jobPreferences and request.jobPreferences.hasDisabilityCert
    
    resources = [
        {
            "name": "LinkedIn",
            "url": "https://www.linkedin.com",
            "description": "Red profesional para networking y búsqueda de empleo"
        },
        {
            "name": "InfoJobs",
            "url": "https://www.infojobs.net",
            "description": "Portal de empleo líder en España"
        },
        {
            "name": "Platzi",
            "url": "https://platzi.com",
            "description": "Plataforma de cursos online de tecnología"
        }
    ]
    
    if has_disability_cert:
        resources.append({
            "name": "Fundación ONCE",
            "url": "https://www.fundaciononce.es",
            "description": "Recursos específicos para personas con discapacidad"
        })
    
    # SOLUCIÓN: Informe básico más detallado y útil
    skills_summary = ""
    if len(request.softSkills) > 0:
        skills_summary = f" Has completado la evaluación de {len(request.softSkills)} habilidades soft."
    else:
        skills_summary = " Aunque no se han evaluado habilidades específicas, tienes potencial para desarrollarte profesionalmente."
    
    cv_info = ""
    if request.cvAnalysis:
        cv_info = " Tu CV ha sido analizado y contiene información valiosa para tu desarrollo profesional."
    
    return {
        "summary": f"Basado en la información disponible, tu nivel de empleabilidad es {level} con un puntaje de {employability_score}/100.{skills_summary}{cv_info}",
        "recommendations": {
            "profile_analysis": f"Perfil de {request.fullName}{skills_summary} Tu perfil muestra potencial para el crecimiento profesional y hay varias áreas donde puedes destacar.",
            "strengths_analysis": "Fortalezas identificadas incluyen tu motivación para completar una evaluación profesional y tu interés en el desarrollo personal. Esto demuestra proactividad y compromiso con tu crecimiento profesional.",
            "improvement_areas": "Las principales áreas de mejora incluyen: completar evaluaciones de habilidades soft adicionales, optimizar tu CV según estándares actuales, y definir claramente tus objetivos profesionales a corto y largo plazo.",
            "cv_analysis": f"{'Tu CV ha sido analizado y ' if request.cvAnalysis else ''}Para mejorar tu CV, considera: usar un formato limpio y profesional, incluir palabras clave relevantes para tu sector, cuantificar tus logros cuando sea posible, y mantener la información actualizada.",
            "job_suggestions": f"Basado en {'tus preferencias laborales y ' if request.jobPreferences else ''}tu perfil, considera explorar roles que coincidan con tus intereses y habilidades. Es importante investigar las tendencias del mercado laboral en tu área de interés.",
            "next_steps": {
                "short_term": ["Actualizar y optimizar tu CV", "Crear o mejorar tu perfil en LinkedIn", "Definir tus objetivos profesionales", "Investigar empresas de interés"],
                "medium_term": ["Completar formación específica en tu área", "Ampliar tu red profesional", "Obtener certificaciones relevantes", "Practicar habilidades de entrevista"],
                "long_term": ["Desarrollar una especialización", "Buscar oportunidades de liderazgo", "Considerar formación avanzada", "Planificar tu carrera a 5 años"]
            },
            "resources": resources
        }
    }

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
    """Analiza un CV en formato PDF usando Azure Document Intelligence"""
    temp_file_path = None
    try:
        logger.info(f"Analizando CV PDF: {file.filename}")
        
        # Leer el contenido del archivo
        content = await file.read()
        
        # Guardar temporalmente el archivo
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Ejecutar TODAS las rutas disponibles y fusionar resultados para máxima cobertura
        texts: List[str] = []
        merged: Dict[str, Any] = {}

        # A) Módulo mejorado de Document Intelligence
        try:
            from document_intelligence import analyze_cv_with_improved_intelligence  # type: ignore
            di_res = analyze_cv_with_improved_intelligence(content)
            if isinstance(di_res, dict):
                if di_res.get("raw_text"):
                    texts.append(str(di_res.get("raw_text")))
                cv_info = di_res.get("cv_info") or {}
                if isinstance(cv_info, dict):
                    # Preferimos estos datos iniciales
                    for k, v in cv_info.items():
                        if v and k not in merged:
                            merged[k] = v
        except Exception as e:
            logger.warning(f"Módulo document_intelligence no disponible o falló: {e}")

        # B) Azure Document Intelligence
        try:
            az_res = await analyze_cv_with_azure(temp_file_path, file.filename)
            if isinstance(az_res, dict):
                if az_res.get('raw_text'):
                    texts.append(str(az_res.get('raw_text')))
                # Guardar secciones layout para Structured Outputs
                layout_sections = az_res.get('layout_sections') or {}
                for k, v in az_res.items():
                    if k not in ('raw_text', 'layout_sections') and v:
                        if k not in merged:
                            merged[k] = v
        except Exception as e:
            logger.warning(f"Azure Document Intelligence falló: {e}")

        # C) OCR (solo si hay credenciales configuradas)
        if os.getenv("AZURE_COMPUTERVISION_ENDPOINT") and os.getenv("AZURE_COMPUTERVISION_KEY"):
            try:
                ocr_res = await analyze_cv_with_ocr(temp_file_path, file.filename)
                if isinstance(ocr_res, dict):
                    if ocr_res.get('raw_text'):
                        texts.append(str(ocr_res.get('raw_text')))
                    for k, v in ocr_res.items():
                        if k not in merged and v and k != 'raw_text':
                            merged[k] = v
            except Exception as e:
                logger.warning(f"OCR no disponible/falló: {e}")

        # D) PyMuPDF
        try:
            pm_res = await analyze_cv_with_pymupdf(temp_file_path, file.filename)
            if isinstance(pm_res, dict):
                if pm_res.get('raw_text'):
                    texts.append(str(pm_res.get('raw_text')))
                for k, v in pm_res.items():
                    if k not in merged and v and k != 'raw_text':
                        merged[k] = v
        except Exception as e:
            logger.warning(f"PyMuPDF falló: {e}")

        # Texto combinado
        combined_text = "\n".join([t for t in texts if t])
        basic = _extract_basic_cv_info_from_text(combined_text) if combined_text else None

        # 1) Structured Outputs sobre secciones Layout si disponibles
        structured: Dict[str, Any] = {}
        try:
            if locals().get('layout_sections'):
                structured = _structured_extract_with_ai(layout_sections, file.filename)
        except Exception:
            structured = {}

        # 2) LLM clásico como respaldo
        ai_res = await analyze_cv_content_with_ai(combined_text, file.filename, basic)
        final: Dict[str, Any] = {**ai_res}
        # Mezclar también los básicos y lo ya fusionado
        if basic:
            for k, v in basic.items():
                if v and k not in final:
                    final[k] = v
        # Fusión con provenance simple
        provenance: Dict[str, Any] = {}
        def set_field(path: str, value: Any, source: str, confidence: float):
            if value in (None, "", [], {}):
                return
            provenance.setdefault(path, [])
            provenance[path].append({"value": value, "source": source, "confidence": confidence})

        if structured:
            set_field("cv_structured", structured, "layout+structured", 0.85)
        if ai_res:
            set_field("ai_analysis", ai_res, "llm_freeform", 0.60)
        if basic:
            set_field("basic_hints", basic, "regex_basic", 0.40)

        # Normalización post-proceso sobre structured
        standardized = structured or {}
        try:
            # normalizar teléfonos
            phones = []
            cand = (standardized.get("candidate") or {})
            for ph in (cand.get("phones") or [])[:5]:
                norm = norm_phone(ph, region="ES")
                if norm and norm not in phones:
                    phones.append(norm)
            if phones:
                standardized.setdefault("candidate", {})["phones"] = phones
            # normalizar idiomas
            standardized["languages"] = normalize_languages(standardized.get("languages") or [])
            # normalizar fechas experiencia
            exp_norm: List[Dict[str, Any]] = []
            for e in standardized.get("experience") or []:
                s, en, cur = parse_range(" ".join([str(e.get("start_date") or ""), "-", str(e.get("end_date") or "")]).strip())
                exp_norm.append({**e, "start_date": s or e.get("start_date"), "end_date": en if not cur else None, "current": bool(e.get("current")) or cur})
            if exp_norm:
                standardized["experience"] = exp_norm
        except Exception:
            pass

        if standardized:
            final["cv_structured"] = standardized
            final["provenance"] = provenance

        for k, v in merged.items():
            if v and k not in final:
                final[k] = v

        return final
        
    except Exception as e:
        logger.error(f"Error analizando CV: {str(e)}")
        # Devolver análisis básico en caso de error
        return CvAnalysis(
            strengths=["Experiencia detectada", "Habilidades técnicas"],
            weaknesses=["Necesita mejorar estructura", "Falta de detalles específicos"],
            feedback="CV analizado con limitaciones técnicas",
            structure="regular",
            coherence="regular",
            experience="regular",
            skills=["Habilidades generales"],
            education=["Formación detectada"],
            alerts=["Error en análisis automático"]
        ).dict()
    
    finally:
        # Limpiar archivo temporal
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Error eliminando archivo temporal: {e}")

@app.post("/api/pdf/generate-report")
async def generate_pdf_endpoint(payload: Dict[str, Any]):
    """Genera y devuelve el PDF del informe de empleabilidad.

    Espera un JSON con al menos:
    - userInfo: { fullName, userId }
    - gameData: lista de habilidades (skill, score, level, confidence)
    - cvAnalysis: objeto de análisis de CV
    - jobPreferences: preferencias laborales
    - informeProfesional: string Markdown/Texto
    """
    try:
        # Importar on-demand para evitar fallos en arranque si faltan dependencias
        try:
            # Cuando se ejecuta como paquete (uvicorn backend.main:app)
            from .pdf_service import create_employability_pdf  # type: ignore[relative-beyond-top-level]
        except Exception:
            # Fallback cuando se ejecuta el archivo directamente
            from pdf_service import create_employability_pdf

        # Generar PDF
        pdf_bytes = create_employability_pdf(payload)

        # Responder como fichero descargable
        filename_safe = (
            (payload.get("userInfo", {}) or {}).get("fullName", "informe")
        ) or "informe"
        filename_safe = filename_safe.replace(" ", "_")

        headers = {
            "Content-Disposition": f"attachment; filename=informe_empleabilidad_{filename_safe}.pdf"
        }
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)
    except Exception as e:
        logger.error(f"Error generando PDF: {e}")
        raise HTTPException(status_code=500, detail="No se pudo generar el PDF")

def _extract_basic_cv_info_from_text(text_content: str) -> Dict[str, Any]:
    """Extrae heurísticamente nombre del candidato, contactos y periodos laborales/educativos."""
    try:
        lines = [ln.strip() for ln in text_content.splitlines() if ln.strip()]
        # Email y teléfono
        import re
        email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
        phone_re = re.compile(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,3}\)?[\s.-]?){2,4}\d{2,4}")
        emails = []
        phones = []
        for ln in lines[:100]:
            emails += email_re.findall(ln)
            phones += phone_re.findall(ln)
        emails = list(dict.fromkeys(emails))[:3]
        phones = list(dict.fromkeys(phones))[:3]

        # Nombre probable: primeras 5-8 líneas con 2+ palabras capitalizadas y sin @
        candidate = None
        name_re = re.compile(r"^(?:[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+\s+){1,3}[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+$")
        for ln in lines[:12]:
            if '@' in ln or len(ln) > 60:
                continue
            if name_re.match(ln):
                candidate = ln
                break
        # Ubicación: línea con ciudad/provincia típica si aparece tras contacto
        location = None
        loc_candidates = [ln for ln in lines[:30] if any(t in ln.lower() for t in ["madrid", "barcelona", "valencia", "sevilla", "bilbao", "coruña", "león", "zaragoza", "malaga", "granada", "vigo", "palma", "alicante"]) and '@' not in ln]
        if loc_candidates:
            location = loc_candidates[0]

        # Fechas/periodos: detectar rangos tipo "junio 2023 - actualidad" o "2018–2020"
        months = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre|ene\.|feb\.|mar\.|abr\.|may\.|jun\.|jul\.|ago\.|sep\.|oct\.|nov\.|dic\."
        period_re = re.compile(rf"((?:{months})?\s*\d{{4}})\s*[-–a]\s*((?:{months})?\s*(?:\d{{4}}|actualidad|presente))", re.IGNORECASE)
        periods: List[str] = []
        for ln in lines:
            for m in period_re.finditer(ln):
                periods.append(f"{m.group(1)} - {m.group(2)}")
        periods = list(dict.fromkeys(periods))[:20]

        contact = {"emails": emails, "phones": phones, "location": location}
        basic = {"candidate": candidate, "contact": contact, "periods": periods}
        return basic
    except Exception:
        return {"candidate": None, "contact": {}, "periods": []}


async def analyze_cv_with_azure(file_path: str, filename: str) -> Dict[str, Any]:
    """Analiza CV usando Azure Document Intelligence"""
    try:
        from azure.ai.formrecognizer import DocumentAnalysisClient
        from azure.core.credentials import AzureKeyCredential
        
        # Configuración de Azure Document Intelligence
        endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        
        if not endpoint or not key:
            logger.warning("Azure Document Intelligence no configurado - variables de entorno faltantes")
            raise Exception("Azure Form Recognizer no configurado")
        
        logger.info(f"Conectando a Azure Document Intelligence: {endpoint}")
        client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        
        with open(file_path, "rb") as document:
            model_id = (os.getenv("AZURE_DOCINTEL_MODEL_ID") or "prebuilt-layout").strip()
            try:
                logger.info(f"Iniciando análisis de documento con modelo '{model_id}'...")
                poller = client.begin_analyze_document(model_id, document)
                result = poller.result()
            except Exception as e:
                if model_id != "prebuilt-layout":
                    logger.warning(f"Fallo con modelo custom '{model_id}', reintentando con 'prebuilt-layout': {e}")
                    document.seek(0)
                    poller = client.begin_analyze_document("prebuilt-layout", document)
                    result = poller.result()
                else:
                    raise

        # Extraer texto y secciones aware de layout
        text_content = ""
        try:
            for page in getattr(result, 'pages', []) or []:
                for line in getattr(page, 'lines', []) or []:
                    text_content += getattr(line, 'content', '') + "\n"
        except Exception:
            text_content = getattr(result, 'content', '') or ''
        layout_sections = _sections_from_layout_result(result)
        # Información básica extraída por regex (nombre/contacto/periodos)
        basic = _extract_basic_cv_info_from_text(text_content)
        logger.info(f"Texto extraído: {len(text_content)} caracteres")
        if len(text_content) < 20:
            logger.warning("Texto extraído muy corto; el PDF podría estar escaneado/protegido. Activando fallback PyMuPDF y OCR si disponibles.")
        
        # Analizar contenido con IA (pasando hints básicos)
        analysis = await analyze_cv_content_with_ai(text_content, filename, basic)
        # Unir análisis con básicos
        merged: Dict[str, Any] = {**analysis}
        merged.update({k: v for k, v in basic.items() if v})
        merged.update({"raw_text": text_content, "layout_sections": layout_sections})
        return merged
        
    except Exception as e:
        logger.error(f"Error con Azure Document Intelligence: {e}")
        raise

async def analyze_cv_with_pymupdf(file_path: str, filename: str) -> Dict[str, Any]:
    """Analiza CV usando PyMuPDF como fallback"""
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(file_path)
        text_content = ""
        
        for page in doc:
            text_content += page.get_text()
        
        doc.close()
        # Información básica
        basic = _extract_basic_cv_info_from_text(text_content)
        # Analizar contenido con IA
        analysis = await analyze_cv_content_with_ai(text_content, filename, basic)
        merged: Dict[str, Any] = {**analysis}
        merged.update({k: v for k, v in basic.items() if v})
        return merged
        
    except Exception as e:
        logger.error(f"Error con PyMuPDF: {e}")
        raise

async def analyze_cv_with_ocr(file_path: str, filename: str) -> Dict[str, Any]:
    """Analiza CV usando OCR (Azure Computer Vision) como alternativa"""
    try:
        from azure.cognitiveservices.vision.computervision import ComputerVisionClient
        from msrest.authentication import CognitiveServicesCredentials
    except Exception as e:
        raise Exception(f"Dependencias de OCR no disponibles: {e}")

    endpoint = os.getenv("AZURE_COMPUTERVISION_ENDPOINT")
    key = os.getenv("AZURE_COMPUTERVISION_KEY")
    if not endpoint or not key:
        raise Exception("OCR no configurado")

    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))
    with open(file_path, 'rb') as f:
        ocr_result = client.recognize_printed_text_in_stream(image=f, language='es')  # type: ignore[attr-defined]

    # Construir texto concatenado
    lines: List[str] = []
    try:
        for region in ocr_result.regions:  # type: ignore[attr-defined]
            for line in region.lines:
                words = [w.text for w in line.words]
                lines.append(' '.join(words))
    except Exception:
        pass
    text_content = "\n".join(lines)
    basic = _extract_basic_cv_info_from_text(text_content)
    analysis = await analyze_cv_content_with_ai(text_content, filename, basic)
    merged: Dict[str, Any] = {**analysis}
    merged.update({k: v for k, v in basic.items() if v})
    merged['ocr_used'] = True
    return merged

async def analyze_cv_content_with_ai(content: str, filename: str, basic: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Analiza el contenido del CV usando IA"""
    try:
        # Chequeo de ortografía simple con fallback silencioso
        spelling_issues: list[str] = []
        try:
            from spellchecker import SpellChecker  # type: ignore
            sp = SpellChecker(language='es')
            # Tomar palabras alfabéticas, minúsculas y sin tildes cambia mucho el diccionario; nos quedamos en lo básico
            import re as _re
            words = [w.lower() for w in _re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{3,}", content)]
            # Evaluar hasta cierto límite para rendimiento
            sample = words[:3000]
            miss = sp.unknown(sample)
            # Guardar hasta 50 ejemplos
            spelling_issues = sorted(list(miss))[:50]
        except Exception:
            # No bloquear el flujo si falla el corrector
            spelling_issues = []

        if not client:
            # Fallback sin IA
            base = CvAnalysis(
                strengths=["Contenido detectado en CV"],
                weaknesses=["Análisis limitado sin IA"],
                feedback="CV analizado básicamente",
                structure="regular",
                coherence="regular",
                experience="regular",
                skills=["Habilidades detectadas"],
                education=["Formación detectada"],
                alerts=( ["Análisis sin IA disponible"] + ([f"Faltas de ortografía potenciales: {', '.join(spelling_issues[:10])}"] if spelling_issues else []) )
            )
            result: Dict[str, Any] = base.dict()
            if basic:
                result.update({k: v for k, v in basic.items() if v})
            return result
        
        # Prompt para análisis de CV
        basic_hint = ""
        try:
            if basic:
                basic_hint = f"""
                HINTS EXTRAIDOS AUTOMÁTICAMENTE DEL CV:
                - CANDIDATO: {basic.get('candidate') or ''}
                - CONTACTO: emails={basic.get('contact', {}).get('emails', [])}, phones={basic.get('contact', {}).get('phones', [])}, location={basic.get('contact', {}).get('location')}
                - PERIODOS DETECTADOS: {basic.get('periods', [])}
                """
        except Exception:
            basic_hint = ""

        prompt = f"""
        Eres un orientador laboral experto, con experiencia en neurodivergencias y discapacidad intelectual.
        Debes generar información precisa, útil y de lectura fácil (frases cortas, listas, términos claros).
        Analiza el siguiente CV y proporciona un análisis detallado en formato JSON:
        
        CV: {content[:4000]}
        {basic_hint}
        
        Responde en este formato JSON exacto:
        {{
            "strengths": ["fortaleza1", "fortaleza2"],
            "weaknesses": ["debilidad1", "debilidad2"],
            "feedback": "feedback general",
            "structure": "buena/regular/mala",
            "coherence": "buena/regular/mala",
            "experience": "alta/regular/baja",
            "skills": ["skill1", "skill2"],
            "education": ["educación1", "educación2"],
            "alerts": ["alerta1", "alerta2"],
            "cv_analysis_structured": {{
                "candidate": "Nombre completo si aparece",
                "contact": {{"emails": ["..."], "phones": ["..."], "location": "...", "linkedin": "..."}},
                "periods": ["ene 2020 - dic 2022", "2023 - actualidad"],
                "languages": ["Español (nativo)", "Inglés (intermedio)"],
                "highlights": ["...", "..."],
                "volunteering": ["Entidad y rol si aparece"],
                "education_synonyms": ["estudios", "formación", "educación", "cursos"]
            }}
        }}
        """
        
        # Limpiar el nombre del deployment para evitar problemas con espacios
        deployment_name = DEPLOYMENT.strip()

        # Structured Outputs con esquema laxo para el análisis + esquema fuerte para cv_analysis_structured
        analysis_schema = {
            "name": "CVFreeformAnalysis",
            "schema": {
                "type": "object",
                "properties": {
                    "strengths": {"type": "array", "items": {"type": "string"}},
                    "weaknesses": {"type": "array", "items": {"type": "string"}},
                    "feedback": {"type": "string"},
                    "structure": {"type": "string"},
                    "coherence": {"type": "string"},
                    "experience": {"type": "string"},
                    "skills": {"type": "array", "items": {"type": "string"}},
                    "education": {"type": "array", "items": {"type": "string"}},
                    "alerts": {"type": "array", "items": {"type": "string"}},
                    "cv_analysis_structured": build_cv_json_schema()["schema"],
                },
            },
            "strict": False,
        }

        chat_kwargs = {
            "model": deployment_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 1500,
            "timeout": 60,
        }
        if _supports_json_schema_response_format(API_VERSION):
            chat_kwargs["response_format"] = {"type": "json_schema", "json_schema": analysis_schema}
        response = client.chat.completions.create(**chat_kwargs)
        
        # Obtener y loggear la respuesta cruda
        raw_content = response.choices[0].message.content
        logger.info(f"Respuesta cruda de Azure OpenAI (CV): {repr(raw_content[:500])}...")
        
        if not raw_content or not raw_content.strip():
            logger.error("Azure OpenAI devolvió respuesta vacía para análisis de CV")
            raise Exception("Respuesta vacía de Azure OpenAI")
        
        # Limpiar la respuesta antes de parsear
        content_to_parse = raw_content.strip()
        
        # Buscar el JSON dentro de la respuesta (puede estar rodeado de texto o markdown)
        import re
        
        # Primero, intentar extraer contenido entre ```json y ```
        json_code_block_match = re.search(r'```json\s*([\s\S]*?)\s*```', content_to_parse, re.IGNORECASE)
        if json_code_block_match:
            content_to_parse = json_code_block_match.group(1).strip()
        else:
            # Si no hay bloque de código, buscar el JSON directamente
            json_match = re.search(r'\{.*\}', content_to_parse, re.DOTALL)
            if json_match:
                content_to_parse = json_match.group(0)
        
        # Parsear respuesta JSON
        import json
        try:
            analysis_data = json.loads(content_to_parse)
            # Inyectar pista de ortografía si no viene
            if isinstance(analysis_data, dict):
                if spelling_issues and not analysis_data.get('alerts'):
                    analysis_data['alerts'] = [f"Faltas de ortografía potenciales: {', '.join(spelling_issues[:10])}"]
                elif spelling_issues and isinstance(analysis_data.get('alerts'), list):
                    analysis_data['alerts'] = analysis_data['alerts'] + [f"Faltas de ortografía potenciales: {', '.join(spelling_issues[:10])}"]
            # Devolver dict plano del análisis más estructura; si falla validación, caeremos al except
            base = CvAnalysis(**analysis_data)
            result: Dict[str, Any] = base.dict()
            
            # Anexar estructura detallada del CV si existe
            if isinstance(analysis_data, dict) and isinstance(analysis_data.get('cv_analysis_structured'), dict):
                cv_structured = analysis_data['cv_analysis_structured']
                # Mapear campos estructurados a campos del modelo
                if cv_structured.get('candidate'):
                    result['candidate'] = cv_structured['candidate']
                if cv_structured.get('contact'):
                    result['contact'] = cv_structured['contact']
                if cv_structured.get('experience'):
                    result['experience_detailed'] = cv_structured['experience']
                if cv_structured.get('education'):
                    result['education_detailed'] = cv_structured['education']
                if cv_structured.get('languages'):
                    result['languages'] = cv_structured['languages']
                if cv_structured.get('periods'):
                    result['periods'] = cv_structured['periods']
                if cv_structured.get('highlights'):
                    result['highlights'] = cv_structured['highlights']
                
                # También incluir en cv_structured para compatibilidad
                result['cv_structured'] = cv_structured
            
            # Mezclar hints básicos
            if basic:
                result.update({k: v for k, v in (basic or {}).items() if v})
            
            # Logging para verificar que la información del CV se procesó correctamente
            logger.info(f"✅ Análisis del CV procesado exitosamente")
            if result.get('cv_structured'):
                logger.info(f"  - CV estructurado: ✅")
                cv_struct = result['cv_structured']
                if cv_struct.get('candidate'):
                    logger.info(f"  - Candidato: {cv_struct['candidate']}")
                if cv_struct.get('experience'):
                    logger.info(f"  - Experiencia: {len(cv_struct['experience'])} posiciones")
                if cv_struct.get('education'):
                    logger.info(f"  - Formación: {len(cv_struct['education'])} elementos")
                if cv_struct.get('languages'):
                    logger.info(f"  - Idiomas: {len(cv_struct['languages'])} detectados")
            
            return result
        except json.JSONDecodeError as je:
            logger.error(f"Error parseando JSON en análisis CV: {je}")
            logger.error(f"Contenido que causó el error: {repr(content_to_parse[:1000])}")
            raise Exception(f"Error parseando respuesta JSON: {je}")
        
    except Exception as e:
        logger.error(f"Error en análisis con IA: {e}")
        # Devolver análisis básico
        base = CvAnalysis(
            strengths=["Contenido detectado"],
            weaknesses=["Error en análisis IA"],
            feedback="CV analizado con limitaciones",
            structure="regular",
            coherence="regular",
            experience="regular",
            skills=["Habilidades generales"],
            education=["Formación detectada"],
            alerts=["Error en análisis automático"]
        )
        result: Dict[str, Any] = base.dict()
        if basic:
            result.update({k: v for k, v in basic.items() if v})
        return result

@app.post("/api/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """Sube un CV para análisis"""
    try:
        logger.info(f"CV subido: {file.filename}")
        # Calcular tamaño de forma segura (UploadFile no expone 'size')
        content = await file.read()
        size_bytes = len(content)
        # Validaciones básicas
        if not file.filename.lower().endswith((".pdf",)):
            raise HTTPException(status_code=400, detail="Formato no soportado. Sube un PDF")
        if size_bytes <= 0:
            raise HTTPException(status_code=400, detail="Archivo vacío")
        if size_bytes > 15 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Archivo demasiado grande (>15MB)")

        # Subir al contenedor de Azure Blob para curación/entrenamiento posterior
        storage_conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("AZURE_STORAGE_CONTAINER_CV", "cv-incoming")
        blob_name = None
        uploaded = False
        if storage_conn:
            try:
                from azure.storage.blob import BlobServiceClient  # type: ignore
                blob_service = BlobServiceClient.from_connection_string(storage_conn)
                container = blob_service.get_container_client(container_name)
                try:
                    if not container.exists():
                        container.create_container()
                except Exception:
                    pass
                # Nombre único
                safe_name = (file.filename or "cv.pdf").replace(" ", "_")
                from datetime import datetime as _dt
                blob_name = f"{_dt.now().strftime('%Y%m%d-%H%M%S')}_{safe_name}"
                blob = container.get_blob_client(blob_name)
                blob.upload_blob(content, overwrite=True, content_type="application/pdf", metadata={"source": "mvp-upload"})
                uploaded = True
            except Exception as e:
                logger.warning(f"No se pudo subir a Blob Storage: {e}")

        return {
            "message": "CV subido correctamente",
            "filename": file.filename,
            "size": size_bytes,
            "storage": {
                "uploaded": uploaded,
                "container": container_name if uploaded else None,
                "blob_name": blob_name,
            },
        }
    except Exception as e:
        logger.error(f"Error subiendo CV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Usar variables de entorno para host y puerto, con fallbacks
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    
    logger.info(f"🚀 Iniciando servidor en {host}:{port}")
    uvicorn.run(app, host=host, port=port)