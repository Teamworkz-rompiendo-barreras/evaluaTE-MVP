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
from uuid import uuid4

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
cv_logger = logging.getLogger("cv")

def with_ctx(**kv):
    return {"ctx": kv}

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

def _as_json_schema_payload(schema_obj: dict, name: str = "EmployabilityReport") -> dict:
    """
    Asegura el formato requerido por Azure para response_format.json_schema:
    - Si ya viene envuelto con 'schema', lo devuelve tal cual.
    - Si es el esquema "puro", lo envuelve con {name, schema, strict}.
    """
    if isinstance(schema_obj, dict) and "schema" in schema_obj:
        return schema_obj
    
    # Verificación rápida del schema (para debugging)
    if name == "EmployabilityReport" and "properties" in schema_obj:
        sr = schema_obj["properties"]["suggested_roles"]["items"]
        logger.info("suggested_roles.items.required = %s", sr.get("required"))
        # Esperado: ['role','reason','seniority','remote_viable']
    
    return {"name": name, "schema": schema_obj, "strict": True}


def _ensure_required_everywhere(schema: dict) -> dict:
    """
    Función preventiva: asegura que todos los objetos tengan campos required.
    Si en el futuro alguien añade propiedades y se olvida de actualizar required,
    esta función las añade automáticamente.
    """
    import copy
    s = copy.deepcopy(schema)
    
    def walk(node):
        if not isinstance(node, dict):
            return
        t = node.get("type")
        if t == "object" and "properties" in node:
            props = node["properties"]
            node["required"] = list(props.keys())
            for child in props.values():
                walk(child)
        if t == "array" and "items" in node:
            walk(node["items"])
    
    walk(s)
    return s

def _allow_null(t):
    """Permite null en tipos para hacer campos opcionales"""
    if isinstance(t, list):
        return t if "null" in t else t + ["null"]
    if isinstance(t, str):
        return [t, "null"]
    return t

def harden_schema(node: dict, _depth: int = 0) -> dict:
    """
    Sanitiza un JSON Schema para Azure OpenAI strict mode:
    1) Cierra todos los objetos con additionalProperties: false.
    2) Si el nodo no define "required", lo pone a todas las props (pero si ya define "required", se respeta).
    3) NO introduce tipos con 'null' (evitamos que el modelo devuelva null).
    """
    if not isinstance(node, dict):
        return node

    t = node.get("type")

    if t == "object":
        props = node.get("properties", {}) or {}
        node["additionalProperties"] = False
        # Respetar 'required' existente; si no hay, las hacemos todas requeridas
        if "required" not in node:
            node["required"] = list(props.keys())
        # Recorremos propiedades
        for k, v in list(props.items()):
            node["properties"][k] = harden_schema(v, _depth + 1)

    elif t == "array":
        if "items" in node and isinstance(node["items"], dict):
            node["items"] = harden_schema(node["items"], _depth + 1)

    # Combinadores
    for key in ("oneOf", "anyOf", "allOf"):
        if key in node and isinstance(node[key], list):
            node[key] = [harden_schema(x, _depth + 1) if isinstance(x, dict) else x for x in node[key]]

    return node

# --- Limpieza estable de texto del CV (solo para informe) ---
_LIGATURES = {"ﬁ":"fi","ﬂ":"fl","ﬀ":"ff","ﬃ":"ffi","ﬄ":"ffl"}
_BULLETS = ("•","-","–","—","·","*","◦","▪")

def _fix_ligatures(t: str) -> str:
    for k,v in _LIGATURES.items():
        t = t.replace(k, v)
    return t

def _normalize_eols(t: str) -> str:
    t = t.replace("\r\n","\n").replace("\r","\n")
    return t

def _unhyphenate(t: str) -> str:
    # une palabras cortadas al final de línea: infor-\nmación -> información
    return re.sub(r"(?<=\w)-\n(?=\w)", "", t)

def _collapse_spaces(t: str) -> str:
    return "\n".join(re.sub(r"\s{2,}", " ", ln).strip() for ln in t.splitlines())

def _preserve_bullets(t: str) -> str:
    lines = []
    for raw in t.splitlines():
        ln = raw.strip()
        if not ln:
            lines.append("")
            continue
        if ln.startswith(_BULLETS) or re.match(r"^[\-\–—·*]\s+\S+", ln):
            lines.append(ln)
        else:
            lines.append(ln)
    return "\n".join(lines)

def _clean_text_for_report(t: str) -> str:
    t = _fix_ligatures(t)
    t = _normalize_eols(t)
    t = _unhyphenate(t)
    t = _collapse_spaces(t)
    t = _preserve_bullets(t)
    return t.strip()

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

    # Campos estructurados adicionales que puede enviar el frontend tras analizar el PDF
    cv_structured: Optional[Any] = None
    cv_info: Optional[Any] = None
    # Puede venir como string (nombre) o como objeto; aceptamos ambos
    candidate: Optional[Any] = None
    contact: Optional[Any] = None
    experience_detailed: Optional[Any] = None
    education_detailed: Optional[Any] = None
    languages: Optional[Any] = None
    periods: Optional[Any] = None
    highlights: Optional[Any] = None
    volunteering: Optional[Any] = None
    cv_analysis_structured: Optional[Any] = None

    # Campos de texto/libres
    raw_text: Optional[str] = None
    layout_sections: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    basic_hints: Optional[Dict[str, Any]] = None
    provenance: Optional[Dict[str, Any]] = None

    class Config:
        extra = 'allow'

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

# Memoria temporal: último CV analizado por usuario (clave: userId)
_LAST_CV_BY_USER: Dict[str, Any] = {}

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
                            "start_date": {"type": "string", "pattern": "^\\d{4}(-\\d{2})?$"},
                            "end_date": {"type": ["string", "null"], "pattern": "^\\d{4}(-\\d{2})?$"},
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
                            "start_date": {"type": "string", "pattern": "^\\d{4}(-\\d{2})?$"},
                            "end_date": {"type": "string", "pattern": "^\\d{4}(-\\d{2})?$"},
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
                                            "items": {"type": "object", "properties": {"name": {"type": "string"}, "date": {"type": "string", "pattern": "^\\d{4}(-\\d{2})?$"}}},
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

def shape_report_for_ui(r: dict) -> dict:
    """
    Adaptador: convierte la salida JSON del modelo al layout de 13 apartados de la UI.
    Garantiza strings en secciones textuales y sanea None -> "No consta".
    """
    def _txt(x, default="No consta"):
        if x is None:
            return default
        if isinstance(x, str) and x.strip() == "":
            return default
        return str(x)

    def _list_str(xs):
        if not isinstance(xs, list) or not xs:
            return []
        return [_txt(x) for x in xs]

    shaped: dict = {
        # 1) Datos personales (objeto)
        "datos_personales": {
            "name": _txt((r.get("personal_data") or {}).get("name")),
            "location": _txt((r.get("personal_data") or {}).get("location")),
            "email": _txt((r.get("personal_data") or {}).get("email")),
            "phone": _txt((r.get("personal_data") or {}).get("phone")),
            "disability_certificate": _txt((r.get("personal_data") or {}).get("disability_certificate")),
        },

        # 2) Resumen del perfil
        "resumen_perfil": _txt(r.get("profile_summary") or r.get("profile_analysis") or ""),

        # 3) Resumen del CV
        "resumen_cv": _txt(r.get("cv_summary") or ""),

        # 4) Fortalezas
        "fortalezas_clave": _list_str(r.get("strengths") or []),

        # 5) Áreas de mejora (sin em-dash)
        "areas_mejora": [
            _txt(f"{it.get('area','Área')}: {it.get('reason','')}. Acción: {it.get('suggested_action','')}")
            for it in (r.get("improvement_areas") or [])
            if isinstance(it, dict)
        ],

        # 6) Diagnóstico del CV (tabla 1–5 + evidencias/correcciones)
        "diagnostico_cv": (lambda cv: (
            (lambda _cv: (
                # Ensamblar diagnóstico base
                {
                    "structure_score": int((_cv.get("structure_score") or 1) or 1),
                    "coherence_score": int((_cv.get("coherence_score") or 1) or 1),
                    "key_info_score": int((_cv.get("key_info_score") or 1) or 1),
                    "clarity_score": int((_cv.get("clarity_score") or 1) or 1),
                    "spelling_style_score": int((_cv.get("style_score") or _cv.get("spelling_style_score") or 1) or 1),
                    "evidence": (lambda E, S: {
                        "structure": (
                            E.get("structure") if (E.get("structure") and not str(E.get("structure")).lower().startswith("no hay información"))
                            else ((
                                f"Secciones presentes: experiencia={len(S.get('experience') or [])}, "
                                f"educación={len(S.get('education') or [])}, idiomas={len(S.get('languages') or [])}"
                            ) if isinstance(S, dict) and (S.get('experience') or S.get('education') or S.get('languages')) else "")
                        ),
                        "coherence": (
                            E.get("coherence") if (E.get("coherence") and not str(E.get("coherence")).lower().startswith("no hay información"))
                            else ("Fechas normalizadas en experiencia" if isinstance(S, dict) and (S.get('experience') or []) else "")
                        ),
                        "key_info": (
                            E.get("key_info") if (E.get("key_info") and not str(E.get("key_info")).lower().startswith("no hay información"))
                            else ((
                                f"Contacto detectado: email={bool(((S.get('contact') or {}).get('emails') or []))}, "
                                f"teléfono={bool(((S.get('contact') or {}).get('phones') or []))}"
                            ) if isinstance(S, dict) else "")
                        ),
                        "clarity": E.get("clarity") or ("Se detectan bullets y títulos claros en secciones extraídas" if isinstance(S, dict) else ""),
                        "style": E.get("style") or "Corrección ortográfica no evaluable sin texto raw; se recomiendan tildes y mayúsculas adecuadas",
                    })(
                        {
                            "structure": _txt((_cv.get("evidence") or {}).get("structure", "")),
                            "coherence": _txt((_cv.get("evidence") or {}).get("coherence", "")),
                            "key_info": _txt((_cv.get("evidence") or {}).get("key_info", "")),
                            "clarity": _txt((_cv.get("evidence") or {}).get("clarity", "")),
                            "style": _txt((_cv.get("evidence") or {}).get("style", "")),
                        },
                        (r.get("cv_analysis") or {}).get("cv_structured") or {}
                    ),
                    "corrections": _list_str(_cv.get("corrections") or []),
                    "reordering_suggestions": _list_str(_cv.get("reordering_suggestions") or []),
                }
            ))(cv)
        ))(r.get("cv_analysis") or r.get("diagnostico_cv") or {}),

        # 7) Entornos ideales
        "entornos_ideales": _txt(r.get("ideal_work_environment") or ""),

        # 8) Roles sugeridos (texto legible)
        "roles_sugeridos": [
            _txt(f"{it.get('role','Rol')} — {it.get('reason','')} (Seniority: {it.get('seniority','No especificado')}; Remoto: {'Sí' if it.get('remote_viable') else 'No'})")
            for it in (r.get("suggested_roles") or [])
            if isinstance(it, dict)
        ],

        # 9) Plan de acción
        "plan_accion": {
            "corto_plazo": _list_str((r.get("action_plan") or {}).get("short_term") or []),
            "medio_plazo": _list_str((r.get("action_plan") or {}).get("medium_term") or []),
            "largo_plazo": _list_str((r.get("action_plan") or {}).get("long_term") or []),
        },

        # 10) Consejos de búsqueda
        "consejos_busqueda": {
            "cv_optimization": _list_str((r.get("job_search_advice") or {}).get("cv_optimization") or []),
            "letters_portfolio": _txt((r.get("job_search_advice") or {}).get("letters_portfolio") or ""),
            "recommended_platforms": _list_str((r.get("job_search_advice") or {}).get("recommended_platforms") or []),
            "networking": _txt((r.get("job_search_advice") or {}).get("networking") or ""),
            "interview_tips": _txt((r.get("job_search_advice") or {}).get("interview_tips") or ""),
        },

        # 11) Herramientas útiles (normalizamos a objetos {name, description, url})
        "herramientas_utiles": (lambda tools: {
            "productividad": [
                (it if isinstance(it, dict) else {"name": str(it), "description": "", "url": ""})
                for it in _list_str((tools or {}).get("productivity") or [])
            ],
            "busqueda": [
                (it if isinstance(it, dict) else {"name": str(it), "description": "", "url": ""})
                for it in _list_str((tools or {}).get("search_alerts") or (tools or {}).get("job_search") or [])
            ],
            "aprendizaje": [
                (it if isinstance(it, dict) else {"name": str(it), "description": "", "url": ""})
                for it in _list_str((tools or {}).get("learning_certification") or (tools or {}).get("learning") or [])
            ],
            "accesibilidad": [
                (it if isinstance(it, dict) else {"name": str(it), "description": "", "url": ""})
                for it in _list_str((tools or {}).get("accessibility") or [])
            ],
        })(r.get("useful_tools") or {}),

        # 12) Juegos completados
        "juegos_completados": _list_str(r.get("completed_games") or []),

        # 13) Frase final
        "frase_final": _txt(r.get("final_message") or ""),

        # Extra: resumen ejecutivo
        "resumen_ejecutivo": _txt(r.get("summary") or ""),
    }

    # Compatibilidad con front legacy: alias esperados por UI antigua
    try:
        # Alias 2) Análisis del perfil
        shaped["analisis_perfil"] = shaped.get("resumen_perfil", "")

        # Alias 6) Análisis del CV (texto): construimos un resumen corto con las puntuaciones
        cvx = shaped.get("diagnostico_cv", {}) or {}
        def _cv_brief(cv):
            try:
                parts = []
                if cv.get("structure_score"):
                    parts.append(f"Estructura {cv['structure_score']}/5")
                if cv.get("coherence_score"):
                    parts.append(f"Coherencia {cv['coherence_score']}/5")
                if cv.get("key_info_score"):
                    parts.append(f"Información clave {cv['key_info_score']}/5")
                if cv.get("clarity_score"):
                    parts.append(f"Claridad {cv['clarity_score']}/5")
                if cv.get("spelling_style_score"):
                    parts.append(f"Ortografía/estilo {cv['spelling_style_score']}/5")
                base = ", ".join(parts)
                evid = cv.get("evidence") or {}
                evid_summary = "; ".join(
                    [
                        f"{k.capitalize()}: {v}" for k, v in evid.items() if isinstance(v, str) and v.strip()
                    ]
                )
                txt = base
                if evid_summary:
                    txt = (base + ". " if base else "") + evid_summary
                return _txt(txt or (r.get("cv_summary") or ""))
            except Exception:
                return _txt(r.get("cv_summary") or "")
        shaped["evaluacion_cv"] = _cv_brief(cvx)
    except Exception:
        pass

    try:
        expected_keys = [
            "datos_personales","resumen_perfil","resumen_cv","fortalezas_clave","areas_mejora",
            "diagnostico_cv","entornos_ideales","roles_sugeridos","plan_accion","consejos_busqueda",
            "herramientas_utiles","juegos_completados","frase_final","resumen_ejecutivo"
        ]
        logger.info("🔎 UI adapter keys: %s", list(shaped.keys()))
        missing = [k for k in expected_keys if k not in shaped]
        if missing:
            logger.warning("⚠️ Claves faltantes en recomendaciones UI: %s", missing)
    except Exception:
        pass

    return shaped


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
        # Fallback: si no vino cvAnalysis en la request, intentar recuperar el último por userId
        try:
            if not request.cvAnalysis and request.userId:
                cached = _LAST_CV_BY_USER.get(request.userId)
                if cached and isinstance(cached, dict):
                    logger.info("♻️ Fallback: usando CV almacenado temporalmente para este usuario")
                    if not report.get("cvAnalysis"):
                        report["cvAnalysis"] = {}
                    if isinstance(report["cvAnalysis"], dict):
                        report["cvAnalysis"].update(cached)
        except Exception:
            pass
        # Usar el adaptador para convertir la salida del modelo a las 13 secciones estándar
        if isinstance(professional_report, dict):
            shaped = shape_report_for_ui(professional_report)
        else:
            shaped = shape_report_for_ui({})
        
        # Mantener compatibilidad con el frontend actual usando final_recommendations
        final_recommendations = dict(shaped)
        # Extender con claves legacy que consume el front actual
        try:
            # 2) Perfil
            final_recommendations["profile_analysis"] = shaped.get("resumen_perfil", "") or ""
            # 4) Fortalezas
            strengths_list = shaped.get("fortalezas_clave") or []
            final_recommendations["strengths_analysis"] = \
                ("\n".join(f"- {s}" for s in strengths_list)) if isinstance(strengths_list, list) else (str(strengths_list) if strengths_list is not None else "")
            # 5) Áreas de mejora
            areas_list = shaped.get("areas_mejora") or []
            final_recommendations["improvement_areas"] = \
                ("\n".join(f"- {x}" for x in areas_list)) if isinstance(areas_list, list) else (str(areas_list) if areas_list is not None else "")
            # 6) CV (resumen textual)
            final_recommendations["cv_analysis"] = shaped.get("evaluacion_cv", "") or ""
            # 8) Sugerencias laborales
            roles_list = shaped.get("roles_sugeridos") or []
            final_recommendations["job_suggestions"] = \
                ("\n".join(f"- {r}" for r in roles_list)) if isinstance(roles_list, list) else (str(roles_list) if roles_list is not None else "")
            # 9) Próximos pasos
            plan = shaped.get("plan_accion") or {}
            final_recommendations["next_steps"] = {
                "short_term": plan.get("corto_plazo") or [],
                "medium_term": plan.get("medio_plazo") or [],
                "long_term": plan.get("largo_plazo") or [],
            }
            # 11) Recursos (apoyo)
            tools = shaped.get("herramientas_utiles") or {}
            resources_flat = []
            for cat_key in ("productividad", "busqueda", "aprendizaje", "accesibilidad"):
                items = tools.get(cat_key) or []
                if isinstance(items, list):
                    for it in items:
                        if isinstance(it, dict):
                            name = str(it.get("name") or it.get("title") or "Recurso")
                            description = str(it.get("description") or it.get("desc") or "")
                            url = str(it.get("url") or it.get("link") or "")
                            resources_flat.append({"name": name, "description": description, "url": url})
                        else:
                            resources_flat.append({"name": str(it), "description": "", "url": ""})
            final_recommendations["resources"] = resources_flat
        except Exception:
            pass
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

        # Enriquecer 'report' con representaciones estándar para el front
        try:
            if isinstance(professional_report, dict):
                # Markdown legible (opcional para front legacy)
                try:
                    from .prompt_config import PromptConfig as _PC  # type: ignore
                    markdown_report = _PC.convert_json_to_markdown_report(professional_report)
                except Exception:
                    markdown_report = ""
                report["json"] = professional_report
                report["ui"] = shaped
                report["markdown"] = markdown_report
            else:
                report["ui"] = shaped
        except Exception:
            report["ui"] = shaped

        response_data = ReportResponse(
            report=report,
            recommendations=final_recommendations,
            employabilityScore=avg_score,
            level=("alto" if avg_score >= 80 else ("medio" if avg_score >= 50 else "bajo")),
            summary=str(professional_report.get("summary", "")) if isinstance(professional_report, dict) else "",
            createdAt=datetime.now().isoformat()
        )
        # Refuerzo defensivo de compatibilidad de estructuras (alias y contacto desde candidate)
        try:
            if isinstance(report.get("cvAnalysis"), dict):
                ca = report["cvAnalysis"]
                if ca.get("cv_analysis_structured") and not ca.get("cv_structured"):
                    ca["cv_structured"] = ca["cv_analysis_structured"]
                if not ca.get("contact"):
                    cand = (ca.get("cv_structured") or {}).get("candidate") or {}
                    if isinstance(cand, dict) and any([cand.get("emails"), cand.get("phones"), cand.get("location")]):
                        ca["contact"] = {
                            "emails": cand.get("emails") or [],
                            "phones": cand.get("phones") or [],
                            "location": cand.get("location"),
                            "linkedin": ((cand.get("links") or {}) or {}).get("linkedin")
                        }
        except Exception:
            pass

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
    # Normalizar contacto para evitar None.get
    _contact = None
    if request.cvAnalysis:
        try:
            _contact = getattr(request.cvAnalysis, 'contact', None)
        except Exception:
            _contact = None
    if not isinstance(_contact, dict):
        _contact = {}

    candidate_data = {
        "fullName": request.fullName,
        "location": _contact.get('location', 'No consta'),
        "email": (_contact.get('emails', ['No consta']) or ['No consta'])[0],
        "phone": (_contact.get('phones', ['No especificado']) or ['No especificado'])[0],
        "hasDisabilityCertificate": request.jobPreferences.hasDisabilityCert if request.jobPreferences else None,
        "disabilityType": "No especificado"  # Campo opcional que no tienes implementado
    }
    
    # Preparar soft skills con puntuaciones
    soft_skills_data = []
    for skill in request.softSkills:
        # Convertir level a puntuación numérica para el análisis
        level_norm = (skill.level or "").strip().lower()
        level_score = {"bajo": 35, "medio": 60, "alto": 85}.get(level_norm, 50)
        soft_skills_data.append({
            "skill": skill.skill,
            "score": level_score,
            "level": skill.level,
            "evidence": getattr(skill, 'feedback', None) or "Evaluado mediante juego interactivo"
        })
    
    # Preparar análisis del CV - CORRECCIÓN CRÍTICA
    cv_data = {
        "rawText": "No disponible",
        "sections": {}
    }
    
    # Logging para debug
    logger.info(f"🔍 Preparando datos del CV para el prompt")
    logger.info(f"  - cvAnalysis presente: {'✅' if request.cvAnalysis else '❌'}")
    
    if request.cvAnalysis:
        # CRÍTICO: Priorizar cv_structured (donde CV-Extractor guarda los datos)
        cv_structured = (
            getattr(request.cvAnalysis, 'cv_structured', None)
            or getattr(request.cvAnalysis, 'cv_analysis_structured', {})
        )
        
        if cv_structured and isinstance(cv_structured, dict):
            logger.info(f"✅ CV estructurado encontrado con campos: {list(cv_structured.keys())}")
            # Mapear campos de CV-Extractor a la estructura del prompt
            # Normalizar skills y contacto
            cand = cv_structured.get('candidate') or {}
            skills_field = cv_structured.get('skills', [])
            skills_list = []
            if isinstance(skills_field, dict):
                if isinstance(skills_field.get("hard"), list):
                    skills_list += skills_field["hard"]
                if isinstance(skills_field.get("soft"), list):
                    skills_list += skills_field["soft"]
            elif isinstance(skills_field, list):
                skills_list = skills_field
            contact_struct = cv_structured.get('contact') or {}
            if not contact_struct and isinstance(cand, dict):
                contact_struct = {
                    "emails": cand.get("emails") or [],
                    "phones": cand.get("phones") or [],
                    "location": cand.get("location"),
                    "linkedin": ((cand.get("links") or {}) or {}).get("linkedin")
                }

            cv_data["sections"] = {
                "profile": cand or cv_structured.get('candidate', 'No especificado'),
                "experience": cv_structured.get('experience', []),
                "education": cv_structured.get('education', []),
                "courses": "No especificado",
                "languages": cv_structured.get('languages', []),
                "software": skills_list,
                "contact": contact_struct
            }
            
            # CRÍTICO: Extraer texto raw del CV si está disponible
            if hasattr(request.cvAnalysis, 'raw_text') and request.cvAnalysis.raw_text:
                cv_data["rawText"] = request.cvAnalysis.raw_text[:3000]  # Limitar a 3000 caracteres
                logger.info(f"✅ Texto raw del CV extraído: {len(request.cvAnalysis.raw_text)} caracteres")
            elif hasattr(request.cvAnalysis, 'layout_sections') and request.cvAnalysis.layout_sections:
                # Extraer texto de las secciones de layout
                layout_text = ""
                for section_name, section_data in request.cvAnalysis.layout_sections.items():
                    if isinstance(section_data, dict) and section_data.get('text'):
                        layout_text += f"\n{section_name}: {section_data['text']}"
                if layout_text:
                    cv_data["rawText"] = layout_text[:3000]
                    logger.info(f"✅ Texto de layout extraído: {len(layout_text)} caracteres")
            
            # Logging detallado de lo que se extrajo
            logger.info(f"📊 Datos extraídos de CV-Extractor:")
            logger.info(f"  - Profile: {cv_data['sections']['profile']}")
            logger.info(f"  - Experience: {len(cv_data['sections']['experience']) if isinstance(cv_data['sections']['experience'], list) else 'No es lista'}")
            logger.info(f"  - Education: {len(cv_data['sections']['education']) if isinstance(cv_data['sections']['education'], list) else 'No es lista'}")
            logger.info(f"  - Languages: {len(cv_data['sections']['languages']) if isinstance(cv_data['sections']['languages'], list) else 'No es lista'}")
            logger.info(f"  - Skills: {len(cv_data['sections']['software']) if isinstance(cv_data['sections']['software'], list) else 'No es lista'}")
            logger.info(f"  - Contact: {cv_data['sections']['contact']}")
            
        else:
            # CORRECCIÓN CRÍTICA: Usar la estructura correcta de document_intelligence.py
            # Verificar si hay datos en cv_info (estructura de document_intelligence.py)
            cv_info = getattr(request.cvAnalysis, 'cv_info', {})
            if cv_info and isinstance(cv_info, dict):
                logger.info(f"✅ cv_info encontrado con campos: {list(cv_info.keys())}")
                # Mapear campos de document_intelligence.py a la estructura del prompt
                cv_data["sections"] = {
                    "profile": cv_info.get('perfil', 'No especificado'),
                    "experience": cv_info.get('experiencia', []),
                    "education": cv_info.get('educacion', []),
                    "courses": "No especificado",
                    "languages": cv_info.get('idiomas', []),
                    "software": cv_info.get('software', []),
                    "contact": cv_info.get('contacto', {})
                }
                
                # Extraer texto raw del CV
                if hasattr(request.cvAnalysis, 'raw_text') and request.cvAnalysis.raw_text:
                    cv_data["rawText"] = request.cvAnalysis.raw_text[:3000]
                    logger.info(f"✅ Texto raw del CV extraído: {len(request.cvAnalysis.raw_text)} caracteres")
                
                logger.info(f"📊 Datos extraídos de cv_info:")
                logger.info(f"  - Profile: {cv_data['sections']['profile']}")
                logger.info(f"  - Experience: {len(cv_data['sections']['experience']) if isinstance(cv_data['sections']['experience'], list) else 'No es lista'}")
                logger.info(f"  - Education: {len(cv_data['sections']['education']) if isinstance(cv_data['sections']['education'], list) else 'No es lista'}")
                logger.info(f"  - Languages: {len(cv_data['sections']['languages']) if isinstance(cv_data['sections']['languages'], list) else 'No es lista'}")
                logger.info(f"  - Skills: {len(cv_data['sections']['software']) if isinstance(cv_data['sections']['software'], list) else 'No es lista'}")
                logger.info(f"  - Contact: {cv_data['sections']['contact']}")
            
            else:
                # Fallback a campos directos solo si cv_structured y cv_info están vacíos
                logger.info("⚠️ cv_structured y cv_info vacíos, usando campos directos como fallback")
                _cand = getattr(request.cvAnalysis, 'candidate', None)
                _exp = getattr(request.cvAnalysis, 'experience_detailed', [])
                _edu = getattr(request.cvAnalysis, 'education_detailed', [])
                _langs = getattr(request.cvAnalysis, 'languages', [])
                _skills = getattr(request.cvAnalysis, 'skills', [])
                _contact_fallback = getattr(request.cvAnalysis, 'contact', {})
                cv_data["sections"] = {
                    "profile": _cand if (_cand and _cand != 'No especificado') else 'No especificado',
                    "experience": _exp if isinstance(_exp, list) else [],
                    "education": _edu if isinstance(_edu, list) else [],
                    "courses": "No especificado",
                    "languages": _langs if isinstance(_langs, list) else [],
                    "software": _skills if isinstance(_skills, list) else [],
                    "contact": _contact_fallback if isinstance(_contact_fallback, dict) else {}
                }
                
                # Logging del fallback
                logger.info(f"📊 Datos extraídos de campos directos:")
                logger.info(f"  - Profile: {cv_data['sections']['profile']}")
                logger.info(f"  - Experience: {len(cv_data['sections']['experience']) if isinstance(cv_data['sections']['experience'], list) else 'No es lista'}")
                logger.info(f"  - Education: {len(cv_data['sections']['education']) if isinstance(cv_data['sections']['education'], list) else 'No es lista'}")
        
        # También intentar extraer información de cv_analysis_structured si está disponible
        cv_analysis_structured = getattr(request.cvAnalysis, 'cv_analysis_structured', {})
        if cv_analysis_structured and isinstance(cv_analysis_structured, dict):
            logger.info(f"✅ cv_analysis_structured encontrado, mezclando información")
            # Mezclar información estructurada con la básica
            if cv_analysis_structured.get('candidate') and cv_analysis_structured.get('candidate') != 'No especificado':
                cv_data["sections"]["profile"] = cv_analysis_structured['candidate']
            if cv_analysis_structured.get('experience'):
                cv_data["sections"]["experience"] = cv_analysis_structured['experience']
            if cv_analysis_structured.get('education'):
                cv_data["sections"]["education"] = cv_analysis_structured['education']
            if cv_analysis_structured.get('languages'):
                cv_data["sections"]["languages"] = cv_analysis_structured['languages']
            if cv_analysis_structured.get('skills'):
                cv_data["sections"]["software"] = cv_analysis_structured['skills']
            if cv_analysis_structured.get('contact'):
                cv_data["sections"]["contact"] = cv_analysis_structured['contact']
        
        # Verificar si hay datos reales o solo valores por defecto
        has_real_data = False
        for section_name, section_data in cv_data['sections'].items():
            if section_data and section_data != 'No especificado' and section_data != [] and section_data != {}:
                has_real_data = True
                break
        
        logger.info(f"🔍 ¿Hay datos reales del CV?: {'✅ SÍ' if has_real_data else '❌ NO'}")
        if not has_real_data:
            logger.warning("⚠️ CRÍTICO: No hay datos reales del CV para enviar al prompt")
            logger.warning("⚠️ Esto causará que la IA genere 'CV no disponible'")
            
            # Intentar extraer información adicional de otros campos del CV
            logger.info("🔍 Intentando extraer información adicional de otros campos...")
            
            # Buscar información en campos adicionales
            additional_fields = ['raw_text', 'layout_sections', 'ai_analysis', 'basic_hints']
            for field in additional_fields:
                field_value = getattr(request.cvAnalysis, field, None)
                if field_value:
                    logger.info(f"  - {field}: {type(field_value)} - {str(field_value)[:100]}...")
                    if field == 'raw_text' and isinstance(field_value, str) and len(field_value) > 50:
                        cv_data["rawText"] = field_value[:2000]  # Limitar a 2000 caracteres
                        logger.info(f"✅ Texto raw del CV extraído: {len(field_value)} caracteres")
                    elif field == 'layout_sections' and isinstance(field_value, dict):
                        # Extraer texto de las secciones de layout
                        layout_text = ""
                        for section_name, section_data in field_value.items():
                            if isinstance(section_data, dict) and section_data.get('text'):
                                layout_text += f"\n{section_name}: {section_data['text']}"
                        if layout_text:
                            cv_data["rawText"] = layout_text[:2000]
                            logger.info(f"✅ Texto de layout extraído: {len(layout_text)} caracteres")

        logger.info(f"✅ Información del CV extraída: {list(cv_data['sections'].keys())}")
        logger.info(f"  - Profile: {cv_data['sections']['profile']}")
        logger.info(f"  - Experience: {len(cv_data['sections']['experience']) if isinstance(cv_data['sections']['experience'], list) else 'No es lista'} elementos")
        logger.info(f"  - Education: {len(cv_data['sections']['education']) if isinstance(cv_data['sections']['education'], list) else 'No es lista'} elementos")
        logger.info(f"  - Languages: {len(cv_data['sections']['languages']) if isinstance(cv_data['sections']['languages'], list) else 'No es lista'} elementos")
        logger.info(f"  - Software: {len(cv_data['sections']['software']) if isinstance(cv_data['sections']['software'], list) else 'No es lista'} elementos")
    
    # Preparar preferencias laborales
    job_preferences_data = {
        "desired_roles": request.jobPreferences.areas if request.jobPreferences else [],
        "desired_sectors": request.jobPreferences.areas if request.jobPreferences else [],
        "work_modes": [request.jobPreferences.workMode] if request.jobPreferences else ["No especificado"],
        "availability": request.jobPreferences.availability if request.jobPreferences else "No especificado",
        "salary_range": "No especificado",
        "relocation": request.jobPreferences.willingToRelocate if request.jobPreferences else None,
        "notes": f"Necesidades: {', '.join(request.jobPreferences.needs) if request.jobPreferences and hasattr(request.jobPreferences, 'needs') and request.jobPreferences.needs else 'No especificadas'}" if request.jobPreferences else "No especificado"
    }
    
    # CRÍTICO: Logging detallado de preferencias laborales
    logger.info(f"🔍 Preferencias laborales procesadas:")
    logger.info(f"  - Roles deseados: {job_preferences_data['desired_roles']}")
    logger.info(f"  - Sectores: {job_preferences_data['desired_sectors']}")
    logger.info(f"  - Modalidad: {job_preferences_data['work_modes']}")
    logger.info(f"  - Disponibilidad: {job_preferences_data['availability']}")
    logger.info(f"  - Relocalización: {job_preferences_data['relocation']}")
    logger.info(f"  - Notas: {job_preferences_data['notes']}")
    
    # Preparar idiomas (robusto ante None o tipos inesperados)
    languages_data = []
    if request.cvAnalysis and hasattr(request.cvAnalysis, 'languages'):
        try:
            langs = getattr(request.cvAnalysis, 'languages')
            if not isinstance(langs, list):
                langs = []
            for lang in langs:
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
        except Exception:
            languages_data = []
    
    # CRÍTICO: Logging detallado de minijuegos completados
    logger.info(f"🔍 Minijuegos completados:")
    logger.info(f"  - Lista: {request.completedGames}")
    logger.info(f"  - Cantidad: {len(request.completedGames)}")
    logger.info(f"  - Detalles: {request.completedGames[:5] if request.completedGames else 'Ninguno'}")
    
    # CRÍTICO: Logging detallado de soft skills evaluadas
    logger.info(f"🔍 Soft skills evaluadas:")
    for i, skill in enumerate(soft_skills_data):
        logger.info(f"  - {i+1}. {skill.get('skill', 'N/A')}: {skill.get('level', 'N/A')} ({skill.get('score', 'N/A')}/100)")
    
    # Importar configuración de prompts
    try:
        from .prompt_config import PromptConfig
    except ImportError:
        from prompt_config import PromptConfig
    
    # Adjuntar analysis.json si report_id llegó por cvAnalysis
    try:
        report_id = None
        if isinstance(request.cvAnalysis, dict):
            report_id = (request.cvAnalysis or {}).get("report_id")
        elif request.cvAnalysis and hasattr(request.cvAnalysis, "report_id"):
            report_id = getattr(request.cvAnalysis, "report_id")
        # Importar attach para enriquecer cv_data
        try:
            from .generate_report import attach_analysis_json_to_prompt as _attach
        except Exception:
            from generate_report import attach_analysis_json_to_prompt as _attach
        if report_id:
            cv_data = _attach(cv_data, report_id)
        elif isinstance(report.get("cvAnalysis"), dict) and report["cvAnalysis"].get("analysis"):
            # Si el analyze-cv v2 devolvió inline analysis, adjuntarlo
            cv_data = _attach({**cv_data, "analysis": report["cvAnalysis"].get("analysis")}, None)
    except Exception:
        pass

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
    
    # CRÍTICO: Verificar que el prompt se generó correctamente
    logger.info(f"🔍 Prompt generado exitosamente:")
    logger.info(f"  - Longitud: {len(prompt)} caracteres")
    logger.info(f"  - Contiene '13) FRASE FINAL': {'✅' if '13) FRASE FINAL' in prompt else '❌'}")
    logger.info(f"  - Contiene 'CV ANALIZADO': {'✅' if 'CV ANALIZADO' in prompt else '❌'}")
    logger.info(f"  - Contiene 'JUEGOS COMPLETADOS': {'✅' if 'JUEGOS COMPLETADOS' in prompt else '❌'}")
    logger.info(f"  - Contiene 'PREFERENCIAS LABORALES': {'✅' if 'PREFERENCIAS LABORALES' in prompt else '❌'}")
    
    # Logging del prompt generado para debug
    logger.info(f"📝 Prompt generado con información del CV:")
    logger.info(f"  - rawText: {cv_data['rawText']}")
    logger.info(f"  - sections: {list(cv_data['sections'].keys())}")
    logger.info(f"  - profile: {cv_data['sections'].get('profile', 'No disponible')}")
    logger.info(f"  - experience: {len(cv_data['sections'].get('experience', [])) if isinstance(cv_data['sections'].get('experience'), list) else 'No es lista'} elementos")
    logger.info(f"  - education: {len(cv_data['sections'].get('education', [])) if isinstance(cv_data['sections'].get('education'), list) else 'No es lista'} elementos")
    
    # CRÍTICO: Verificar que los datos del CV se están enviando al prompt
    logger.info(f"🔍 VERIFICACIÓN FINAL - Datos del CV enviados al prompt:")
    for section_name, section_data in cv_data['sections'].items():
        if isinstance(section_data, list):
            logger.info(f"  - {section_name}: {len(section_data)} elementos - {section_data[:3] if section_data else 'Lista vacía'}")
        elif isinstance(section_data, dict):
            logger.info(f"  - {section_name}: {list(section_data.keys()) if section_data else 'Diccionario vacío'}")
        else:
            logger.info(f"  - {section_name}: {section_data}")
    
    # Verificar si hay datos reales o solo valores por defecto
    has_real_data = False
    for section_name, section_data in cv_data['sections'].items():
        if section_data and section_data != 'No especificado' and section_data != [] and section_data != {}:
            has_real_data = True
            break
    
    logger.info(f"🔍 ¿Hay datos reales del CV?: {'✅ SÍ' if has_real_data else '❌ NO'}")
    if not has_real_data:
        logger.warning("⚠️ CRÍTICO: No hay datos reales del CV para enviar al prompt")
        logger.warning("⚠️ Esto causará que la IA genere 'CV no disponible'")
        # Logging adicional para debug
        logger.info(f"🔍 Campos del request.cvAnalysis disponibles:")
        if request.cvAnalysis:
            for attr_name in dir(request.cvAnalysis):
                if not attr_name.startswith('_'):
                    try:
                        attr_value = getattr(request.cvAnalysis, attr_name)
                        if attr_value and attr_value != 'No especificado' and attr_value != [] and attr_value != {}:
                            logger.info(f"  - {attr_name}: {attr_value}")
                    except Exception:
                        pass

    
    try:
        # Limpiar el nombre del deployment para evitar problemas con espacios
        deployment_name = DEPLOYMENT.strip()
        
        # Structured Outputs para el informe mejorado usando configuración centralizada
        report_schema = PromptConfig.get_report_schema()
        report_schema = _ensure_required_everywhere(report_schema)  # <--- función preventiva aquí
        # 🔧 Azure SO no admite ['object','null'] en la raíz
        if isinstance(report_schema.get("type"), list):
            report_schema["type"] = "object"
        
        # CRÍTICO: Verificar que el esquema JSON se cargó correctamente
        logger.info(f"🔍 Esquema JSON del informe:")
        logger.info(f"  - Esquema cargado: {'✅' if report_schema else '❌'}")
        logger.info(f"  - Propiedades requeridas: {report_schema.get('required', []) if report_schema else 'N/A'}")
        logger.info(f"  - Cantidad de propiedades: {len(report_schema.get('properties', {})) if report_schema else 0}")

        chat_kwargs = {
            "model": deployment_name,
            "messages": [
                {"role": "system", "content": PromptConfig.get_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 4000,  # Aumentado para el informe más detallado
            "timeout": 120,  # Aumentado para el análisis más complejo
        }
        if _supports_json_schema_response_format(API_VERSION):
            chat_kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": _as_json_schema_payload(report_schema, name="EmployabilityReport")
            }
            # (Opcional) sanity log:
            js = chat_kwargs["response_format"]["json_schema"]
            logger.info(f"Wrapper JSON schema keys: {list(js.keys())}")  # debe incluir 'schema' y 'name'
            logger.info(f"✅ JSON Schema aplicado para respuesta estructurada")
        else:
            chat_kwargs["response_format"] = {"type": "json_object"}
            logger.warning(f"⚠️ JSON Schema no disponible en API version {API_VERSION}")
        cv_logger.info("openai_request", extra=with_ctx(model=deployment_name))
        response = client.chat.completions.create(**chat_kwargs)
        cv_logger.info("openai_response", extra=with_ctx(tokens=len(str(response.choices[0].message.content or ""))))
        
        # Obtener y loggear la respuesta cruda
        raw_content = response.choices[0].message.content
        logger.info(f"Respuesta cruda de Azure OpenAI (informe mejorado): {repr(raw_content[:500])}...")
        
        if not raw_content or not raw_content.strip():
            logger.error("Azure OpenAI devolvió respuesta vacía para informe mejorado")
            raise Exception("Respuesta vacía de Azure OpenAI")
        
        # Limpiar la respuesta antes de parsear
        content_to_parse = raw_content.strip()
        
        # Si ya parece JSON puro, úsalo tal cual
        if content_to_parse.strip().startswith("{") and content_to_parse.strip().endswith("}"):
            pass  # ya está OK
        else:
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
async def analyze_cv_pdf(file: UploadFile = File(...), userId: Optional[str] = Form(None)):
    """Analiza un CV en formato PDF usando Azure Document Intelligence o la tubería V2 (feature flag)."""
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
        logger.info(f"🔍 Iniciando análisis completo del CV: {file.filename}")
        correlation_id = str(uuid4())
        cv_logger.info("extraction_start", extra=with_ctx(correlation_id=correlation_id))

        # CV_PIPELINE_V2 feature flag
        use_v2 = (os.getenv("CV_PIPELINE_V2", "off").lower() in ("1", "on", "true", "yes"))
        if use_v2:
            try:
                from app.cv_pipeline.extract import extract_cv  # type: ignore
                from app.cv_pipeline.normalize import normalize_contact, pick_candidate_name  # type: ignore
                from app.cv_pipeline.quality import cv_quality_ok  # type: ignore
                from app.cv_pipeline.scoring import compute_cv_analysis  # type: ignore
            except Exception as e:
                logger.warning(f"⚠️ CV_PIPELINE_V2 activo pero módulos no disponibles: {e}")
                use_v2 = False

        if use_v2:
            endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "")
            key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY", "")
            try:
                cv_logger.info("extraction_v2_run", extra=with_ctx(correlation_id=correlation_id))
                extraction = extract_cv(content, endpoint=endpoint, key=key)
                base_cv: Dict[str, Any] = {
                    "text": extraction.text,
                    "char_count": extraction.char_count,
                    "sections": extraction.sections or {},
                    "source": extraction.source,
                }
                # contacto básico
                contact_raw: Dict[str, Any] = (base_cv.get("sections", {}) or {}).get("contact") or {}
                base_cv["contact"] = normalize_contact(contact_raw)
                base_cv["candidate"] = {"name": pick_candidate_name(base_cv)}

                ok, reason = cv_quality_ok(base_cv)
                if not ok:
                    cv_logger.info("quality_gate_failed", extra=with_ctx(correlation_id=correlation_id, reason=reason))
                    raise HTTPException(status_code=422, detail={"code": "CV_PARSE_FAILED", "reason": reason})

                # construir objeto para scoring determinista
                scoring_input: Dict[str, Any] = {
                    "experience": (base_cv.get("sections") or {}).get("experience") or [],
                    "education": (base_cv.get("sections") or {}).get("education") or [],
                    "languages": (base_cv.get("sections") or {}).get("languages") or [],
                    "skills": (base_cv.get("sections") or {}).get("skills") or (base_cv.get("sections") or {}).get("software") or [],
                    "contact": base_cv.get("contact") or {},
                    "summary": (base_cv.get("sections") or {}).get("profile"),
                    "sections": base_cv.get("sections") or {},
                }
                analysis_json = compute_cv_analysis(scoring_input)
                cv_logger.info("scoring_done", extra=with_ctx(correlation_id=correlation_id, overall=analysis_json.get("overall", {}).get("score")))

                # Persistencia blob/local
                report_id = str(uuid4())
                storage_conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
                container_reports = os.getenv("AZURE_STORAGE_CONTAINER_REPORTS", "reports")
                pdf_blob_path = f"blob://reports/{report_id}/cv.pdf"
                json_blob_path = f"blob://reports/{report_id}/analysis.json"

                # Guardar localmente en ./reports si no hay storage
                base_dir = os.path.join(os.getcwd(), "reports", report_id)
                os.makedirs(base_dir, exist_ok=True)
                # Guardar pdf
                try:
                    with open(os.path.join(base_dir, "cv.pdf"), "wb") as fh:
                        fh.write(content)
                except Exception:
                    pass
                # Guardar analysis.json
                try:
                    with open(os.path.join(base_dir, "analysis.json"), "w", encoding="utf-8") as fh:
                        json.dump(analysis_json, fh, ensure_ascii=False, indent=2)
                except Exception:
                    pass

                # Subir a Blob si está configurado
                if storage_conn:
                    try:
                        from azure.storage.blob import BlobServiceClient  # type: ignore
                        bsc = BlobServiceClient.from_connection_string(storage_conn)
                        cont = bsc.get_container_client(container_reports)
                        try:
                            if not cont.exists():
                                cont.create_container()
                        except Exception:
                            pass
                        cv_client = cont.get_blob_client(f"reports/{report_id}/cv.pdf")
                        cv_client.upload_blob(content, overwrite=True, content_type="application/pdf")
                        an_client = cont.get_blob_client(f"reports/{report_id}/analysis.json")
                        an_client.upload_blob(json.dumps(analysis_json).encode("utf-8"), overwrite=True, content_type="application/json")
                    except Exception as e:
                        logger.warning(f"No se pudo subir a Blob Storage (reports): {e}")

                final_v2 = {
                    "report_id": report_id,
                    "blob_paths": {"pdf": pdf_blob_path, "analysis": json_blob_path},
                    "analysis": analysis_json,
                    "char_count": extraction.char_count,
                    "source": extraction.source,
                }
                _LAST_CV_BY_USER[userId.strip() if userId else "anonymous"] = dict(final_v2)
                cv_logger.info("extraction_done", extra=with_ctx(correlation_id=correlation_id))
                return final_v2
            except HTTPException:
                raise
            except Exception as e:
                logger.warning(f"CV_PIPELINE_V2 falló, intentando flujo legacy: {e}")
                cv_logger.info("extraction_fallback_legacy", extra=with_ctx(correlation_id=correlation_id))

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
        logger.info(f"📝 Texto combinado extraído: {len(combined_text)} caracteres")
        basic = _extract_basic_cv_info_from_text(combined_text) if combined_text else None
        if basic:
            logger.info(f"✅ Información básica extraída: {list(basic.keys())}")
        else:
            logger.warning("⚠️ No se pudo extraer información básica del CV")

        # 1) Structured Outputs sobre secciones Layout si disponibles
        structured: Dict[str, Any] = {}
        try:
            if locals().get('layout_sections') and layout_sections:
                structured = await _structured_extract_with_ai(layout_sections, file.filename)
                logger.info(f"✅ Extracción estructurada completada: {len(structured)} campos")
        except Exception as e:
            logger.warning(f"⚠️ Error en extracción estructurada: {e}")
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

        # 3) Analizador determinista de estructura → mapeo a diagnostico_cv UI
        try:
            from .cv_structure_analyzer import compute_review_from_text_sections, review_to_ui_diagnostico
        except Exception:
            try:
                from cv_structure_analyzer import compute_review_from_text_sections, review_to_ui_diagnostico
            except Exception:
                compute_review_from_text_sections = None  # type: ignore
                review_to_ui_diagnostico = None  # type: ignore

        try:
            if compute_review_from_text_sections and review_to_ui_diagnostico:
                sections_for_review: Dict[str, Any] = {}
                # Adaptar posibles estructuras ya calculadas
                if standardized:
                    sections_for_review = {
                        "profile": (standardized.get("candidate") or {}).get("summary") if isinstance(standardized.get("candidate"), dict) else standardized.get("candidate"),
                        "experience": standardized.get("experience") or [],
                        "education": standardized.get("education") or [],
                        "languages": standardized.get("languages") or [],
                        "skills": standardized.get("skills") or (standardized.get("software") or []),
                        "contact": standardized.get("candidate") or standardized.get("contact") or {},
                    }
                review = compute_review_from_text_sections(combined_text, sections_for_review)
                final["cv_structure_review"] = review
                final["diagnostico_cv"] = review_to_ui_diagnostico(review)
        except Exception:
            # No bloquear el flujo si el analizador determinista falla
            pass

        # Guardar en memoria temporal por usuario si se proporcionó userId
        try:
            if userId and isinstance(userId, str) and userId.strip():
                _LAST_CV_BY_USER[userId.strip()] = dict(final)
                logger.info(f"💾 CV almacenado temporalmente para userId={userId.strip()}")
        except Exception:
            pass
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

        # Aserción: si hay analysis_json declarado, validar overall.score
        analysis_json = None
        try:
            analysis_json = ((payload.get("cvAnalysis") or {}).get("analysis_json"))
        except Exception:
            analysis_json = None
        if analysis_json is not None:
            try:
                overall_score = (analysis_json.get("overall") or {}).get("score")
                if overall_score is None:
                    raise HTTPException(status_code=422, detail="Falta overall.score en analysis_json. No se puede renderizar PDF.")
            except Exception:
                raise HTTPException(status_code=422, detail="Falta overall.score en analysis_json. No se puede renderizar PDF.")

        # Generar PDF
        cv_logger.info("pdf_render_start", extra=with_ctx())
        pdf_bytes = create_employability_pdf(payload)
        cv_logger.info("pdf_render_done", extra=with_ctx(bytes=len(pdf_bytes) if isinstance(pdf_bytes, (bytes, bytearray)) else None))

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

async def _structured_extract_with_ai(layout_sections: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """Extrae información estructurada del CV usando IA sobre las secciones de layout"""
    try:
        if not client:
            logger.warning("Azure OpenAI no disponible para extracción estructurada")
            return {}
        
        # Preparar contexto de las secciones
        sections_text = ""
        for section_name, section_data in layout_sections.items():
            if isinstance(section_data, dict) and section_data.get('text'):
                sections_text += f"\n## {section_name.upper()}\n{section_data['text']}\n"
        
        if not sections_text.strip():
            logger.warning("No hay texto en las secciones de layout para extraer")
            return {}
        
        # Prompt para extracción estructurada
        prompt = f"""
        Eres un experto en análisis de CVs. Analiza las siguientes secciones extraídas de un CV y proporciona información estructurada en formato JSON.
        
        CV: {sections_text[:3000]}
        
        Extrae y estructura la siguiente información:
        - candidate: nombre completo del candidato
        - contact: emails, teléfonos, ubicación, LinkedIn si aparece
        - experience: experiencia laboral con empresa, cargo, fechas, descripción
        - education: formación académica con institución, título, fechas
        - languages: idiomas con niveles
        - skills: habilidades técnicas y herramientas
        - summary: resumen profesional del candidato
        
        Responde SOLO en formato JSON válido, sin texto adicional.
        """
        
        # Configurar parámetros de Azure OpenAI
        deployment_name = DEPLOYMENT.strip()
        chat_kwargs = {
            "model": deployment_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,  # Baja temperatura para extracción precisa
            "max_tokens": 2000,
            "timeout": 60,
        }
        
        # Usar JSON Schema si está disponible
        if _supports_json_schema_response_format(API_VERSION):
            schema = {
                "type": "object",
                "properties": {
                    "candidate": {"type": "string"},
                    "contact": {
                        "type": "object",
                        "properties": {
                            "emails": {"type": "array", "items": {"type": "string"}},
                            "phones": {"type": "array", "items": {"type": "string"}},
                            "location": {"type": "string"},
                            "linkedin": {"type": "string"}
                        }
                    },
                    "experience": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "position": {"type": "string"},
                                "company": {"type": "string"},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"},
                                "current": {"type": "boolean"},
                                "description": {"type": "string"}
                            }
                        }
                    },
                    "education": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "degree": {"type": "string"},
                                "institution": {"type": "string"},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"}
                            }
                        }
                    },
                    "languages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "language": {"type": "string"},
                                "level": {"type": "string"}
                            }
                        }
                    },
                    "skills": {"type": "array", "items": {"type": "string"}},
                    "summary": {"type": "string"}
                }
            }
            schema = harden_schema(schema)  # <---
            # 🔧 Azure SO no admite ['object','null'] en la raíz
            if isinstance(schema.get("type"), list):
                schema["type"] = "object"
            chat_kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": _as_json_schema_payload(schema, name="CVLayoutExtraction")
            }
        
        # Llamar a Azure OpenAI con fallback si el schema estricto falla
        try:
            response = client.chat.completions.create(**chat_kwargs)
        except Exception as e:
            try:
                msg = str(e)
            except Exception:
                msg = ""
            logger.warning(f"⚠️ Error con Structured Outputs (layout extraction): {msg}. Reintentando sin JSON Schema...")
            # Quitar response_format para usar json_object
            chat_kwargs.pop("response_format", None)
            chat_kwargs["response_format"] = {"type": "json_object"}
            response = client.chat.completions.create(**chat_kwargs)
        raw_content = response.choices[0].message.content
        
        if not raw_content or not raw_content.strip():
            logger.warning("Respuesta vacía de Azure OpenAI para extracción estructurada")
            return {}
        
        # Parsear JSON
        import json
        try:
            structured_data = json.loads(raw_content.strip())
            logger.info(f"✅ Datos estructurados extraídos: {list(structured_data.keys())}")
            return structured_data
        except json.JSONDecodeError as je:
            logger.error(f"Error parseando JSON de extracción estructurada: {je}")
            logger.error(f"Contenido: {repr(raw_content[:500])}")
            return {}
            
    except Exception as e:
        logger.error(f"Error en extracción estructurada: {e}")
        return {}

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
        months = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre|ene\\.|feb\\.|mar\\.|abr\\.|may\\.|jun\\.|jul\\.|ago\\.|sep\\.|oct\\.|nov\\.|dic\\."
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


# --- UTILIDADES PARA MODELO CUSTOM cv-extractor-v1 ---
def _field_value(f) -> Any:
    """Extrae el valor de un campo de Document Intelligence de forma robusta"""
    if f is None:
        return None
    # SDK v4 expone content + value_*; intentamos varias
    for attr in ("value", "value_string", "value_phone_number", "value_email", "value_date", "value_boolean", "content"):
        if hasattr(f, attr):
            v = getattr(f, attr)
            if v not in (None, ""):
                return v
    # Arrays / objetos
    if hasattr(f, "value_array") and f.value_array:
        return [_field_value(x) for x in f.value_array]
    if hasattr(f, "value_object") and f.value_object:
        return {k: _field_value(v) for k, v in f.value_object.items()}
    try:
        return str(f)
    except Exception:
        return None

_SPLIT_RE = re.compile(r"[,\n;•·|]+")
def _split_list(txt: Any) -> list[str]:
    """Divide texto en lista usando separadores comunes"""
    if not txt:
        return []
    return [s.strip(" •-").strip() for s in _SPLIT_RE.split(str(txt)) if s.strip()]

def _truthy(x: Any) -> bool:
    """Convierte valor a booleano de forma robusta"""
    return str(x).strip().lower() in {"1", "true", "sí", "si", "yes", "y", "s"}


def _map_cv_extractor_fields(doc) -> tuple[dict, dict]:
    """Mapea campos del modelo custom cv-extractor-v1 a estructuras estándar"""
    # doc.fields -> dict[str, DocumentField]
    flds = getattr(doc, "fields", {}) or {}
    g = lambda k: _field_value(flds.get(k))

    # Candidate + Contacto
    emails = [g("candidate_email_1"), g("candidate_email_2")]
    emails = [e for e in emails if e]
    phones = [g("candidate_phone_1"), g("candidate_phone_2")]
    phones = [p for p in phones if p]

    candidate = {
        "full_name": g("candidate_full_name"),
        "location": g("candidate_location"),
        "emails": emails,
        "phones": phones,
        "links": {"linkedin": g("candidate_linkedin")},
        "role": g("candidate_rol"),
        "has_driving_license": _truthy(g("candidate_has_driving_license")),
    }

    # Idiomas
    languages = []
    for i in range(1, 6):
        name = g(f"lang{i}_name")
        level = g(f"lang{i}_level")
        if name or level:
            languages.append({"name": str(name or ""), "level": str(level or "")})

    # Skills
    hard = _split_list(g("hard_skills"))
    soft = _split_list(g("soft_skills"))

    # Certificaciones (2 pares)
    certs = []
    n1, y1 = g("candidate_certifications"), g("candidate_certification_years")
    n2, y2 = g("candidate_certifications_2"), g("candidate_certification_years_2")
    if n1 or y1: certs.append({"name": str(n1 or ""), "date": str(y1 or "")})
    if n2 or y2: certs.append({"name": str(n2 or ""), "date": str(y2 or "")})

    # Cursos -> los metemos en education como entries con notas
    education = []
    if any([g("course3_provider"), g("course3_date"), g("course3_hours")]):
        education.append({
            "degree": str(g("course3_provider") or "Curso"),
            "institution": str(g("course3_provider") or ""),
            "start_date": None,
            "end_date": str(g("course3_date") or ""),
            "notes": f"Horas: {g('course3_hours') or ''}".strip()
        })
    if any([g("course4_name"), g("course4_provider"), g("course4_date"), g("course4_hours")]):
        education.append({
            "degree": str(g("course4_name") or "Curso"),
            "institution": str(g("course4_provider") or ""),
            "start_date": None,
            "end_date": str(g("course4_date") or ""),
            "notes": f"Horas: {g('course4_hours') or ''}".strip()
        })

    # Voluntariado
    volunteering = []
    for i in range(1, 4):
        if any([g(f"vol{i}_org"), g(f"vol{i}_role"), g(f"vol{i}_start_date"), g(f"vol{i}_end_date"), g(f"vol{i}_description")]):
            volunteering.append({
                "organization": g(f"vol{i}_org"),
                "role": g(f"vol{i}_role"),
                "location": g(f"vol{i}_location"),
                "start_date": g(f"vol{i}_start_date"),
                "end_date": g(f"vol{i}_end_date"),
                "description": g(f"vol{i}_description"),
            })

    # cv_info (la forma "ligera" usada por tu prompt)
    cv_info = {
        "perfil": candidate["role"] or candidate["full_name"],
        "contacto": {
            "emails": candidate["emails"],
            "phones": candidate["phones"],
            "location": candidate["location"],
            "linkedin": candidate["links"]["linkedin"],
        },
        "idiomas": languages,
        "software": hard,          # hard skills
        "aptitudes": soft,         # soft skills
        "certificaciones": certs,
        "voluntariado": volunteering,
    }

    # cv_structured (encaja con tu JSON Schema usado más adelante)
    cv_structured = {
        "candidate": {
            "full_name": candidate["full_name"],
            "location": candidate["location"],
            "emails": candidate["emails"],
            "phones": candidate["phones"],
            "links": {"linkedin": candidate["links"]["linkedin"]} if candidate["links"]["linkedin"] else {},
        },
        "summary": None,
        "experience": [],                             # tu modelo aún no etiqueta experiencia
        "education": education,
        "languages": [{"name": l["name"], "level": l["level"]} for l in languages],
        "skills": {"hard": hard, "soft": soft},
        "certifications": certs,
        "projects": [],
    }
    return cv_info, cv_structured


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
                
                # (Opcional para depurar): loguea los campos que te devuelve el modelo
                try:
                    if getattr(result, "documents", None):
                        for k, v in result.documents[0].fields.items():
                            logger.info(f"[cv-extractor] {k} = {_field_value(v)} (conf={getattr(v,'confidence',None)})")
                except Exception:
                    pass
                
                # --- NUEVO: si es tu modelo custom, mapeamos sus campos ---
                try:
                    if getattr(result, "documents", None):
                        doc0 = result.documents[0]
                        cv_info_map, cv_struct = _map_cv_extractor_fields(doc0)
                        logger.info(f"🧩 Mapper cv-extractor aplicado: {list(cv_info_map.keys()) if cv_info_map else 'sin datos'}")
                    else:
                        cv_info_map, cv_struct = {}, {}
                except Exception as _e:
                    logger.warning(f"Mapper cv-extractor falló: {_e}")
                    cv_info_map, cv_struct = {}, {}
                
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
        # Limpiar texto solo para el informe (no afecta combined_text del punto 6)
        clean_text = _clean_text_for_report(text_content or "")
        merged.update({"raw_text": clean_text, "layout_sections": layout_sections})
        
        # --- NUEVO: incorpora salidas del modelo custom
        if cv_info_map:
            merged["cv_info"] = cv_info_map
        if cv_struct:
            merged["cv_structured"] = cv_struct
        
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
        clean_text = _clean_text_for_report(text_content or "")
        # Información básica (se puede extraer del limpio)
        basic = _extract_basic_cv_info_from_text(clean_text)
        # Analizar contenido con IA usando texto limpio
        analysis = await analyze_cv_content_with_ai(clean_text, filename, basic)
        merged: Dict[str, Any] = {**analysis}
        merged.update({k: v for k, v in basic.items() if v})
        merged["raw_text"] = clean_text
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
    # 👇 Aplicar el mismo patrón de limpieza estable
    clean_text = _clean_text_for_report(text_content or "")
    # Extraer básicos desde el texto limpio (mejor email/teléfono/periodos)
    basic = _extract_basic_cv_info_from_text(clean_text)
    # Analizar con IA sobre texto limpio (más coherente para el informe)
    analysis = await analyze_cv_content_with_ai(clean_text, filename, basic)
    merged: Dict[str, Any] = {**analysis}
    merged.update({k: v for k, v in basic.items() if v})
    merged['raw_text'] = clean_text
    merged['ocr_used'] = True
    return merged

async def analyze_cv_content_with_ai(content: str, filename: str, basic: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Analiza el contenido del CV usando IA"""
    try:
        # Importar PromptConfig para usar el prompt centralizado
        try:
            from .prompt_config import PromptConfig
        except ImportError:
            from prompt_config import PromptConfig
        
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

        # Usar prompt centralizado para análisis de CV
        prompt = PromptConfig.get_cv_analysis_prompt(content, basic)
        
        # Limpiar el nombre del deployment para evitar problemas con espacios
        deployment_name = DEPLOYMENT.strip()

        # Structured Outputs con esquema laxo para el análisis + esquema fuerte para cv_analysis_structured
        analysis_schema = {
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
                # 👇 Añadimos espacio para que el modelo devuelva también el resumen determinista si lo desea
                "cv_structure_review": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "language": {"type": "string"},
                        "scores": {
                            "type": "object",
                            "properties": {
                                "format": {
                                    "type": "object",
                                    "properties": {
                                        "score": {"type": "number"},
                                        "stars": {"type": "integer"},
                                        "explanation": {"type": "string"}
                                    }
                                },
                                "clarity": {
                                    "type": "object",
                                    "properties": {
                                        "score": {"type": "number"},
                                        "stars": {"type": "integer"},
                                        "explanation": {"type": "string"}
                                    }
                                },
                                "coherence": {
                                    "type": "object",
                                    "properties": {
                                        "score": {"type": "number"},
                                        "stars": {"type": "integer"},
                                        "explanation": {"type": "string"}
                                    }
                                },
                                "key_information": {
                                    "type": "object",
                                    "properties": {
                                        "score": {"type": "number"},
                                        "stars": {"type": "integer"},
                                        "explanation": {"type": "string"}
                                    }
                                },
                                "spelling": {
                                    "type": "object",
                                    "properties": {
                                        "score": {"type": "number"},
                                        "stars": {"type": "integer"},
                                        "explanation": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
        }
        # Asegurar 'required' exhaustivo en todos los objetos y cerrar objetos para modo estricto
        analysis_schema = _ensure_required_everywhere(analysis_schema)
        analysis_schema = harden_schema(analysis_schema)
        # 🔧 Azure SO no admite ['object','null'] en la raíz
        if isinstance(analysis_schema.get("type"), list):
            analysis_schema["type"] = "object"

        chat_kwargs = {
            "model": deployment_name,
            "messages": [
                {"role": "system", "content": PromptConfig.get_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1500,
            "timeout": 60,
        }
        if _supports_json_schema_response_format(API_VERSION):
            chat_kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": _as_json_schema_payload(analysis_schema, name="CVAnalysis")
            }
        else:
            chat_kwargs["response_format"] = {"type": "json_object"}
        try:
            response = client.chat.completions.create(**chat_kwargs)
        except Exception as e:
            # Fallback sin JSON Schema si hay problemas de validación de esquema
            try:
                msg = str(e)
            except Exception:
                msg = ""
            logger.warning(f"⚠️ Error con Structured Outputs (CVAnalysis): {msg}. Reintentando sin JSON Schema...")
            chat_kwargs.pop("response_format", None)
            chat_kwargs["response_format"] = {"type": "json_object"}
            response = client.chat.completions.create(**chat_kwargs)
        
        # Obtener y loggear la respuesta cruda
        raw_content = response.choices[0].message.content
        logger.info(f"Respuesta cruda de Azure OpenAI (CV): {repr(raw_content[:500])}...")
        
        if not raw_content or not raw_content.strip():
            logger.error("Azure OpenAI devolvió respuesta vacía para análisis de CV")
            raise Exception("Respuesta vacía de Azure OpenAI")
        
        # Limpiar la respuesta antes de parsear
        content_to_parse = raw_content.strip()
        
        # Si ya parece JSON puro, úsalo tal cual
        if content_to_parse.strip().startswith("{") and content_to_parse.strip().endswith("}"):
            pass  # ya está OK
        else:
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
    
    # Test de la función harden_schema
    def test_harden_schema_handles_strict_mode():
        src = {
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {
                    "type": "object",
                    "properties": {"c": {"type": "number"}}
                },
                "d": {
                    "type": "array",
                    "items": {"type": "object", "properties": {"e": {"type": "boolean"}}}
                }
            }
        }
        out = harden_schema(src)
        assert out["additionalProperties"] is False
        assert out["required"] == ["a", "b", "d"]  # Todas las propiedades
        assert out["properties"]["b"]["additionalProperties"] is False
        assert out["properties"]["b"]["required"] == ["c"]  # Todas las propiedades
        assert out["properties"]["d"]["items"]["additionalProperties"] is False
        assert out["properties"]["d"]["items"]["required"] == ["e"]  # Todas las propiedades
        assert out["type"] == ["object", "null"]  # Permite null
        print("✅ Test harden_schema: PASSED")
    
    try:
        test_harden_schema_handles_strict_mode()
    except Exception as e:
        print(f"❌ Test harden_schema: FAILED - {e}")
    
    logger.info(f"🚀 Iniciando servidor en {host}:{port}")
    uvicorn.run(app, host=host, port=port)