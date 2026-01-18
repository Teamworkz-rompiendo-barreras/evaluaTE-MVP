#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cv_analyzer.py

Este módulo proporciona utilidades para extraer texto de archivos PDF y analizar
su contenido para extraer información relevante de un Curriculum Vitae (CV) usando
Google Gemini como motor de IA principal.
"""

import os
import fitz  # type: ignore  # PyMuPDF
import json
import logging
import asyncio
import re
from typing import Dict, Any, List, Optional
import math
from collections import Counter
import base64
import io

def _default_stars() -> Dict[str, int]:
    return {
        "formato": 3,
        "claridad": 3,
        "coherencia": 3,
        "informacion_clave": 2,
        "ortografia": 3,
    }

logger = logging.getLogger(__name__)

try:
    # La carga de variables de entorno es opcional. Si python-dotenv no está
    # instalado, esta importación puede fallar. En tal caso, simplemente se
    # omiten las variables de entorno y se asume que el entorno ya las
    # proporciona (por ejemplo, variables de entorno del sistema).
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ModuleNotFoundError:
    # dotenv no está disponible; las variables de entorno no se cargarán de un archivo .env
    pass

# Configuración de Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai_configured = False
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        genai_configured = True
    except ImportError:
        logger.warning("google-generativeai no instalado")
else:
    logger.warning("GEMINI_API_KEY no configurada")

# Importaciones para OCR (carga lazy)
OCR_AVAILABLE = False
_pytesseract_imported = False
_pil_imported = False


def _dedup_list(items: List[Any]) -> List[Any]:
    seen = set()
    out: List[Any] = []
    for it in items:
        if it in (None, "", " ", [], {}):
            continue
        key = str(it).strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def _extract_experience_from_text(text: str) -> List[Dict[str, Any]]:
    """Heurística básica: busca líneas con años/rangos y construye entradas mínimas."""
    if not text:
        return []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    date_rx = re.compile(r"(\b20\d{2}\b|\b19\d{2}\b)")
    entries: List[Dict[str, Any]] = []
    for ln in lines:
        hits = date_rx.findall(ln)
        if len(hits) >= 1:
            entries.append({
                "empresa": "",
                "cargo": "",
                "fecha_inicio": hits[0],
                "fecha_fin": hits[-1] if len(hits) > 1 else "",
                "descripcion": ln,
                "responsabilidades": [],
                "logros": [],
                "tecnologias": [],
            })
    return entries[:8]


def _extract_education_from_text(text: str) -> List[Dict[str, Any]]:
    """Heurística: detecta palabras clave de estudios + año."""
    if not text:
        return []
    edu_keywords = ("universidad", "grado", "licenciatura", "master", "máster", "curso", "formación", "diplomatura")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    date_rx = re.compile(r"(\b20\d{2}\b|\b19\d{2}\b)")
    entries: List[Dict[str, Any]] = []
    for ln in lines:
        lower = ln.lower()
        if any(k in lower for k in edu_keywords):
            year = ""
            m = date_rx.search(ln)
            if m:
                year = m.group(1)
            entries.append({
                "titulo": ln,
                "institucion": "",
                "fecha_inicio": year,
                "fecha_fin": "",
                "nivel": "",
            })
    return entries[:8]


def _extract_languages_from_text(txt: str) -> List[Dict[str, str]]:
    if not txt:
        return []
    langs = []
    known = [
        "inglés", "ingles", "english",
        "español", "spanish",
        "francés", "frances", "french",
        "alemán", "aleman", "german",
        "italiano", "italian",
        "portugués", "portugues", "portuguese",
        "gallego", "basque", "euskera", "catalán", "catalan", "valenciano",
    ]
    seen = set()
    lower = txt.lower()
    for lang in known:
        if lang in lower and lang not in seen:
            langs.append({"idioma": lang.capitalize(), "nivel": ""})
            seen.add(lang)
    return langs


def _extract_tools_from_text(txt: str) -> List[str]:
    if not txt:
        return []
    tools = []
    known_tools = [
        "Word", "Excel", "PowerPoint", "Powerpoint",
        "Photoshop", "Illustrator", "InDesign",
        "Procreate", "Clip Studio", "Paint", "Movie Maker",
        "After Effects", "Office", "Teams", "Outlook",
    ]
    lower = txt.lower()
    seen = set()
    for tool in known_tools:
        if tool.lower() in lower and tool.lower() not in seen:
            tools.append(tool)
            seen.add(tool.lower())
    return tools


def _import_ocr_dependencies() -> bool:
    """Importa dependencias de OCR solo cuando se necesitan."""
    global OCR_AVAILABLE, _pytesseract_imported, _pil_imported

    if not _pytesseract_imported:
        try:
            import pytesseract  # type: ignore  # noqa: F401
            _pytesseract_imported = True
        except ImportError:
            return False

    if not _pil_imported:
        try:
            from PIL import Image  # type: ignore  # noqa: F401
            _pil_imported = True
        except ImportError:
            return False

    OCR_AVAILABLE = True
    return True


async def extract_text_with_advanced_ocr(pdf_buffer: bytes) -> tuple[str, Dict[str, Any]]:
    """Extrae texto combinando PyMuPDF y OCR para todas las páginas.

    Devuelve una tupla ``(texto, metadata)`` donde ``metadata`` describe si se
    utilizaron PyMuPDF y/o OCR, páginas procesadas y posibles errores.
    """

    doc = None
    metadata: Dict[str, Any] = {
        "pages": 0,
        "py_mupdf_attempted": True,
        "py_mupdf_used": False,
        "py_mupdf_pages": [],
        "ocr_available": False,
        "ocr_attempted": False,
        "ocr_used": False,
        "ocr_pages": [],
        "ocr_errors": [],
    }

    try:
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")  # type: ignore
        text_segments: List[str] = []
        seen_segments: set[str] = set()

        ocr_ready = _import_ocr_dependencies()
        metadata["ocr_available"] = bool(ocr_ready)
        if ocr_ready:
            try:
                import pytesseract  # type: ignore
                from PIL import Image  # type: ignore
            except ImportError:
                metadata["ocr_available"] = False
                ocr_ready = False

        for page_num in range(len(doc)):
            page = doc[page_num]
            metadata["pages"] += 1

            # Siempre intentamos extraer texto con PyMuPDF
            page_text = (page.get_text("text") or "").strip()
            metadata["py_mupdf_pages"].append(page_num)
            if page_text:
                metadata["py_mupdf_used"] = True
                if page_text not in seen_segments:
                    text_segments.append(page_text)
                    seen_segments.add(page_text)

            # Optimización: Solo usar OCR si no se detectó suficiente texto con PyMuPDF
            if ocr_ready and len(page_text) < 50:
                metadata["ocr_attempted"] = True
                try:
                    zoom = 2.0  # Mayor resolución para OCR
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))

                    ocr_config = (
                        "--psm 6 --oem 3 "
                        "-c tessedit_char_whitelist="
                        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@.-_()/\\|,;: "
                    )

                    ocr_text = await asyncio.to_thread(
                        pytesseract.image_to_string,
                        img,
                        lang="spa+eng",
                        config=ocr_config,
                    )
                    normalized = (ocr_text or "").strip()
                    if normalized:
                        metadata["ocr_used"] = True
                        metadata["ocr_pages"].append(page_num)
                        if normalized not in seen_segments:
                            text_segments.append(normalized)
                            seen_segments.add(normalized)
                except Exception as ocr_error:  # pragma: no cover - diagnóstico
                    metadata["ocr_errors"].append({
                        "page": page_num,
                        "error": str(ocr_error),
                    })

        combined_text = "\n\n".join(text_segments).strip()
        metadata["combined_text_length"] = len(combined_text)
        return combined_text, metadata

    except Exception as e:  # pragma: no cover - errores inesperados
        print(f"❌ Error extrayendo texto: {e}")
        metadata["error"] = str(e)
        return "", metadata
    finally:
        try:
            if doc is not None:
                doc.close()
        except Exception:  # pragma: no cover - cleanup defensivo
            pass


_JSON_CODE_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL | re.IGNORECASE)


def _normalize_ai_json_response(content: str) -> str:
    """Normaliza la respuesta de Azure OpenAI para extraer únicamente el JSON."""

    if not isinstance(content, str):
        return str(content)

    cleaned = content.strip()

    block_match = _JSON_CODE_BLOCK_RE.search(cleaned)
    if block_match:
        return block_match.group(1).strip()

    lowered = cleaned.lower()
    if lowered.startswith("json"):
        cleaned = cleaned[4:].strip(": \n\r\t")

    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace >= first_brace:
        return cleaned[first_brace:last_brace + 1].strip()

    return cleaned


def analyze_cv_with_ai(text: str) -> Dict[str, Any]:
    """
    Analiza el CV usando Gemini para extraer información de manera inteligente
    """
    if not genai_configured:
        logger.warning("Gemini no configurado, usando análisis básico")
        return {"error": "Gemini no configurado"}
    
    try:
        logger.info("Iniciando análisis con Google Gemini...")
        
        # System instructions separate
        system_instruction = "Eres un experto en análisis de CVs con más de 15 años de experiencia en recursos humanos y tecnología. Tu especialidad es extraer información precisa y estructurada de CVs en cualquier formato, idioma o estructura. Siempre devuelves JSON válido y bien estructurado."
        
        # Prompt profesional y completo para análisis de CV
        prompt = f"""
Eres un experto en análisis de CVs y recursos humanos con más de 15 años de experiencia. Tu tarea es analizar el siguiente texto extraído de un CV y extraer toda la información relevante de manera estructurada y profesional.

TEXTO DEL CV:
{text[:10000]}

INSTRUCCIONES DETALLADAS:
1. **Información Personal**: Extrae nombre completo, email, teléfono, ubicación, LinkedIn, portfolio
2. **Experiencia Laboral**: Identifica empresas, cargos, fechas (inicio-fin), responsabilidades, logros cuantificables, tecnologías utilizadas
3. **Formación Académica**: Títulos, instituciones, fechas, calificaciones, proyectos destacados
4. **Habilidades Técnicas**: Lenguajes de programación, frameworks, herramientas, bases de datos, metodologías. Para cada herramienta, identifica el nivel de competencia (avanzado, intermedio, básico, experto, etc.) basándote en indicadores visuales como puntos, barras, estrellas o texto descriptivo
5. **Habilidades Blandas**: Comunicación, liderazgo, trabajo en equipo, resolución de problemas, adaptabilidad
6. **Idiomas**: Idiomas y niveles (nativo, avanzado, intermedio, básico)
7. **Certificaciones**: Certificaciones profesionales, cursos, acreditaciones
8. **Proyectos**: Proyectos personales o profesionales con descripción, tecnologías, resultados
9. **Logros**: Premios, reconocimientos, publicaciones, contribuciones destacadas
10. **Intereses**: Áreas de interés profesional, hobbies relevantes

REQUISITOS ESPECÍFICOS:
- Maneja CVs en español e inglés indistintamente
- Interpreta fechas en cualquier formato (MM/YYYY, YYYY-MM, etc.)
- Identifica información aunque esté mal formateada o desordenada
- Extrae habilidades aunque no estén en una sección específica
- Detecta experiencia relevante aunque no esté claramente etiquetada
- Identifica logros cuantificables (porcentajes, números, métricas)

Devuelve SOLO un JSON válido con esta estructura exacta:

{{
  "contacto": {{
    "nombre": "string",
    "email": "string",
    "telefono": "string",
    "ubicacion": "string",
    "linkedin": "string",
    "portfolio": "string"
  }},
  "experiencia_laboral": [
    {{
      "empresa": "string",
      "cargo": "string",
      "fecha_inicio": "string",
      "fecha_fin": "string",
      "responsabilidades": ["string"],
      "logros": ["string"],
      "tecnologias": ["string"]
    }}
  ],
  "formacion_academica": [
    {{
      "titulo": "string",
      "institucion": "string",
      "fecha_inicio": "string",
      "fecha_fin": "string",
      "calificacion": "string",
      "proyectos": ["string"]
    }}
  ],
  "habilidades_tecnicas": [
    {{
      "herramienta": "string",
      "nivel": "string"
    }}
  ],
  "habilidades_blandas": ["string"],
  "idiomas": [
    {{
      "idioma": "string",
      "nivel": "string"
    }}
  ],
  "certificaciones": [
    {{
      "nombre": "string",
      "institucion": "string",
      "fecha": "string"
    }}
  ],
  "proyectos": [
    {{
      "nombre": "string",
      "descripcion": "string",
      "tecnologias": ["string"],
      "resultados": ["string"]
    }}
  ],
  "logros": ["string"],
  "intereses": ["string"]
}}

IMPORTANTE:
- Si no encuentras información para algún campo, usa null o array vacío
- Mantén la estructura JSON exacta
- No agregues campos adicionales
- Usa arrays vacíos [] en lugar de null para listas
- Asegúrate de que el JSON sea válido
"""

        print("📤 Enviando solicitud a Gemini...")
        
        # Configurar modelo
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=system_instruction
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4000,
                response_mime_type="application/json"
            )
        )
        
        print("📥 Respuesta recibida de Gemini")
        
        content = response.text
        if not content:
            raise ValueError("Respuesta vacía de Gemini")
            
        normalized_content = _normalize_ai_json_response(content)

        # Intentar parsear el JSON
        try:
            cv_data = json.loads(normalized_content)
            logger.info("JSON parseado correctamente")
            return cv_data
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning("Error parseando JSON: %s", e)
            print(f"📝 Contenido recibido: {str(content)[:200]}...")
            if normalized_content != content:
                print(f"🧹 Contenido normalizado: {normalized_content[:200]}...")

            # Fallback: intentar extraer información básica del texto
            return extract_basic_cv_data_from_text(text)
            
    except Exception as e:
        print(f"❌ Error en análisis con Gemini: {str(e)}")
        
        # Fallback: usar análisis básico
        print("🔄 Usando análisis básico como fallback...")
        return extract_basic_cv_data_from_text(text)

def extract_contact_info_enhanced(text: str) -> Dict[str, str]:
    """
    Extrae información de contacto con patrones mejorados
    """
    contact = {}
    
    # Patrones mejorados para email
    email_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,}\b'
    ]
    
    for pattern in email_patterns:
        email_match = re.search(pattern, text)
        if email_match:
            contact["email"] = email_match.group().replace(" ", "")
            break
    
    # Patrones mejorados para teléfono
    phone_patterns = [
        r'\+?[\d\s\-\(\)]{9,15}',  # Teléfonos internacionales
        r'[\d\s\-\(\)]{9,}',       # Teléfonos locales
        r'Tel[:\s]*([\d\s\-\(\)]+)',  # Tel: 123-456-789
        r'Phone[:\s]*([\d\s\-\(\)]+)', # Phone: 123-456-789
        r'[Tt]eléfono[:\s]*([\d\s\-\(\)]+)'  # Teléfono: 123-456-789
    ]
    
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            phone = phone_match.group(1) if len(phone_match.groups()) > 0 else phone_match.group()
            phone = re.sub(r'[^\d\s\-\(\)\+]', '', phone).strip()
            if len(phone) >= 9 and not re.match(r'\d{4}', phone):
                contact["telefono"] = phone
                break
    
    # Buscar nombre (patrón básico)
    name_patterns = [
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',  # Primera línea con nombre
        r'Nombre[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'Name[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
    ]
    
    for pattern in name_patterns:
        name_match = re.search(pattern, text, re.MULTILINE)
        if name_match:
            contact["nombre"] = name_match.group(1)
            break
    
    return contact

def analyze_cv_structure_ai(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analiza la estructura del CV usando los datos extraídos por IA.

    Backward compatible: mantiene las claves históricas
    - structure, coherence, experience, skills, softSkills, languages, education,
      strengths, weaknesses, feedback, alerts, total_years_experience, *_count

    Nuevos campos (para análisis real, no heurístico):
    - observations: Lista de hallazgos específicos basados en evidencia
    - direct_scores: Puntuaciones 0–100
        - overall, dates_completeness, chronology, sections_coverage,
          metrics_and_achievements, skills_depth, languages_coverage, education_depth
    - structured: Análisis estructurado
        - dates: métricas de fechas y rangos
        - chronology: verificación de orden por fecha de inicio
        - sections: presentes y faltantes
        - achievements: conteo de logros con métricas y ejemplos
        - skills, languages, education: métricas detalladas
    """
    # Helpers locales para fechas y normalización ----------------------------
    def _normalize_str(value: Any) -> str:
        return (value or "").strip() if isinstance(value, str) else ""

    def _parse_year_month(date_str: Any) -> Optional[tuple[int, int]]:
        """Parsea una fecha flexible (ES/EN) devolviendo (año, mes) aproximados.
        Devuelve None cuando no se puede inferir.
        """
        s = _normalize_str(date_str).lower()
        if not s:
            return None

        # Ongoing roles
        if any(k in s for k in ["actual", "actualidad", "presente", "present", "now", "hoy"]):
            return (datetime.utcnow().year, datetime.utcnow().month)

        # Meses ES/EN
        month_map = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
            "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
            "noviembre": 11, "diciembre": 12,
            "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
            "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
            "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        }

        # Buscar año
        year_match = re.search(r"(19|20)\d{2}", s)
        year = int(year_match.group()) if year_match else None

        # Buscar mes por nombre o número
        month = None
        for name, num in month_map.items():
            if re.search(rf"\b{name}\b", s):
                month = num
                break
        if month is None:
            # Formatos 2021-05, 05/2021, 2021/5, etc.
            m = re.search(r"(?:(?:^|[^\d])(\d{4})[-/\.](\d{1,2}))|(?:(\d{1,2})[-/\.]((?:19|20)\d{2}))", s)
            if m:
                try:
                    if m.group(1) and m.group(2):
                        year = int(m.group(1))
                        month = int(m.group(2))
                    elif m.group(3) and m.group(4):
                        month = int(m.group(3))
                        year = int(m.group(4))
                except Exception:
                    pass

        if year is None:
            return None
        if month is None or month < 1 or month > 12:
            month = 1
        return (year, month)

    def _months_between(start: Optional[tuple[int, int]], end: Optional[tuple[int, int]]) -> int:
        if not start or not end:
            return 0
        sy, sm = start
        ey, em = end
        return max(0, (ey - sy) * 12 + (em - sm))

    # Calcular métricas básicas de presencia ---------------------------------
    has_contact = bool(cv_data.get("contacto", {}))
    has_experience = len(cv_data.get("experiencia_laboral", [])) > 0
    has_education = len(cv_data.get("formacion_academica", [])) > 0
    has_skills = len(cv_data.get("habilidades_tecnicas", [])) > 0
    has_soft_skills = len(cv_data.get("habilidades_blandas", [])) > 0
    has_languages = len(cv_data.get("idiomas", [])) > 0
    has_projects = len(cv_data.get("proyectos", [])) > 0
    
    # Calcular puntuación de estructura
    structure_score = 0
    if has_contact: structure_score += 1
    if has_experience: structure_score += 3
    if has_education: structure_score += 2
    if has_skills: structure_score += 2
    if has_soft_skills: structure_score += 1
    if has_languages: structure_score += 1
    if has_projects: structure_score += 1
    
    # Evaluar estructura
    if structure_score >= 8:
        structure = "excelente"
    elif structure_score >= 5:
        structure = "bueno"
    elif structure_score >= 3:
        structure = "regular"
    else:
        structure = "mejorable"
    
    # Analizar experiencia: fechas, cronología y duración ---------------------
    experience = cv_data.get("experiencia_laboral", [])
    total_months_experience = 0
    missing_start_date_items: List[Dict[str, Any]] = []
    missing_end_date_items: List[Dict[str, Any]] = []
    inconsistent_ranges: List[Dict[str, Any]] = []
    ongoing_roles_count = 0

    parsed_experience: List[Dict[str, Any]] = []
    for idx, exp in enumerate(experience):
        empresa = _normalize_str(exp.get("empresa")) or _normalize_str(exp.get("company"))
        cargo = _normalize_str(exp.get("cargo")) or _normalize_str(exp.get("role"))
        s_raw = exp.get("fecha_inicio") or exp.get("start_date")
        e_raw = exp.get("fecha_fin") or exp.get("end_date")
        s_parsed = _parse_year_month(s_raw)
        e_parsed = _parse_year_month(e_raw)

        if s_parsed is None:
            missing_start_date_items.append({"index": idx, "empresa": empresa, "cargo": cargo})
        if e_parsed is None:
            missing_end_date_items.append({"index": idx, "empresa": empresa, "cargo": cargo})
        else:
            # Si el texto indica presente/actualidad, lo contamos como en curso
            if isinstance(e_raw, str) and e_raw.strip().lower() in ["actualidad", "presente", "present", "now", "hoy", "actual"]:
                ongoing_roles_count += 1

        if s_parsed and e_parsed:
            total_months_experience += _months_between(s_parsed, e_parsed)
            if (e_parsed[0], e_parsed[1]) < (s_parsed[0], s_parsed[1]):
                # Fin anterior a inicio → inconsistencia real
                inconsistent_ranges.append({
                    "index": idx,
                    "empresa": empresa,
                    "cargo": cargo,
                    "inicio": s_raw,
                    "fin": e_raw,
                })
            elif (e_parsed[0], e_parsed[1]) == (s_parsed[0], s_parsed[1]):
                # mismo mes permitido; no inconsistencia
                pass
            else:
                # fin posterior a inicio → correcto
                pass

        parsed_experience.append({
            "index": idx,
            "empresa": empresa,
            "cargo": cargo,
            "start": s_parsed,
            "end": e_parsed,
        })
    
    # Evaluar nivel de experiencia
    total_years = total_months_experience / 12.0
    if total_years > 5:
        experience_level = "excelente"
    elif total_years > 2:
        experience_level = "bueno"
    elif total_years > 0:
        experience_level = "regular"
    else:
        experience_level = "mejorable"
    
    # Comprobar orden cronológico (descendente por fecha de inicio)
    misordered_pairs = 0
    for i in range(len(parsed_experience) - 1):
        a = parsed_experience[i].get("start")
        b = parsed_experience[i + 1].get("start")
        if a and b:
            if (a[0], a[1]) < (b[0], b[1]):
                misordered_pairs += 1
    is_descending = misordered_pairs == 0

    # Generar fortalezas y debilidades
    strengths = []
    weaknesses = []
    
    if len(cv_data.get("habilidades_tecnicas", [])) > 5:
        strengths.append("Perfil técnico sólido con múltiples tecnologías")
    if len(experience) > 2:
        strengths.append("Experiencia profesional diversa")
    if len(cv_data.get("proyectos", [])) > 0:
        strengths.append("Experiencia en proyectos demostrable")
    if len(cv_data.get("formacion_academica", [])) > 0:
        strengths.append("Formación académica presente")
    if len(cv_data.get("habilidades_blandas", [])) > 3:
        strengths.append("Perfil equilibrado con habilidades blandas")
    if len(cv_data.get("idiomas", [])) > 1:
        strengths.append("Perfil internacional con múltiples idiomas")
    if cv_data.get("resumen_profesional"):
        strengths.append("CV con resumen profesional claro")
    
    if len(cv_data.get("habilidades_tecnicas", [])) < 3:
        weaknesses.append("Pocas habilidades técnicas específicas")
    if len(cv_data.get("habilidades_blandas", [])) < 2:
        weaknesses.append("Falta de habilidades blandas específicas")
    if len(cv_data.get("idiomas", [])) < 2:
        weaknesses.append("Perfil limitado en idiomas")
    if not has_contact:
        weaknesses.append("Información de contacto no detectada")
    if not cv_data.get("resumen_profesional"):
        weaknesses.append("Falta resumen profesional")
    if total_years < 1:
        weaknesses.append("Poca experiencia laboral")
    
    # Generar feedback constructivo
    feedback = ""
    if structure == "excelente":
        feedback += "Tu CV tiene una estructura muy profesional y completa. "
    elif structure == "bueno":
        feedback += "Tu CV tiene una buena estructura, pero podrías mejorarla. "
    else:
        feedback += "Tu CV necesita mejorar su estructura. "
    
    if len(experience) > 0:
        feedback += f"Has incluido {len(experience)} experiencias laborales. "
    
    if len(cv_data.get("habilidades_tecnicas", [])) > 0:
        feedback += f"Has mencionado {len(cv_data.get('habilidades_tecnicas', []))} tecnologías. "
    
    # Alertas
    alerts = []
    if len(cv_data.get("habilidades_tecnicas", [])) < 3:
        alerts.append("Considera agregar más habilidades técnicas específicas")
    if len(cv_data.get("habilidades_blandas", [])) < 2:
        alerts.append("Incluye habilidades blandas como liderazgo, comunicación, trabajo en equipo")
    if len(cv_data.get("idiomas", [])) < 2:
        alerts.append("Considera agregar más idiomas para mejorar tu perfil internacional")
    if not has_contact:
        alerts.append("Asegúrate de incluir información de contacto")
    if not cv_data.get("resumen_profesional"):
        alerts.append("Considera agregar un resumen profesional")
    
    # Observaciones específicas basadas en evidencia
    observations: List[str] = []
    if missing_start_date_items:
        observations.append(
            f"Faltan fechas de inicio en {len(missing_start_date_items)} experiencias."
        )
    if missing_end_date_items:
        observations.append(
            f"Faltan fechas de fin en {len(missing_end_date_items)} experiencias."
        )
    if inconsistent_ranges:
        observations.append(
            f"Se detectaron {len(inconsistent_ranges)} rangos de fechas inconsistentes (fin anterior o igual al inicio)."
        )
    if has_experience and not is_descending:
        observations.append(
            f"El orden cronológico no es descendente en {misordered_pairs} caso(s)."
        )

    # Métricas y logros cuantificables
    roles_with_logros = 0
    roles_with_metric_logros = 0
    metric_examples: List[str] = []
    metric_pattern = re.compile(r"(\d+\s?%|\b\d{2,}\b)")
    for exp in experience:
        logros = exp.get("logros") or exp.get("achievements") or []
        responsabilidades = exp.get("responsabilidades") or exp.get("responsibilities") or []
        text_items: List[str] = []
        if isinstance(logros, list):
            text_items.extend([_normalize_str(x) for x in logros if isinstance(x, str)])
        if isinstance(responsabilidades, list):
            text_items.extend([_normalize_str(x) for x in responsabilidades if isinstance(x, str)])
        if text_items:
            roles_with_logros += 1
            if any(metric_pattern.search(t) for t in text_items):
                roles_with_metric_logros += 1
                # Guardar hasta 3 ejemplos
                for t in text_items:
                    if metric_pattern.search(t) and len(metric_examples) < 3:
                        metric_examples.append(t)

    # Direct scores (0-100) ---------------------------------------------------
    total_roles = len(experience)
    with_both_dates = total_roles - len(missing_start_date_items) - len(missing_end_date_items)
    dates_completeness = 100.0 * with_both_dates / total_roles if total_roles else 0.0
    chronology_score = 100.0 if is_descending else max(0.0, 100.0 - (misordered_pairs * 25.0))

    # Cobertura de secciones ponderada a 100
    section_weights = {
        "contact": 10,
        "experience": 35,
        "education": 20,
        "skills": 20,
        "soft_skills": 5,
        "languages": 5,
        "projects": 5,
    }
    sections_coverage = 0.0
    if has_contact:
        sections_coverage += section_weights["contact"]
    if has_experience:
        sections_coverage += section_weights["experience"]
    if has_education:
        sections_coverage += section_weights["education"]
    if has_skills:
        sections_coverage += section_weights["skills"]
    if has_soft_skills:
        sections_coverage += section_weights["soft_skills"]
    if has_languages:
        sections_coverage += section_weights["languages"]
    if has_projects:
        sections_coverage += section_weights["projects"]

    metrics_achievements_score = 100.0 * roles_with_metric_logros / total_roles if total_roles else 0.0
    skills_count = len(cv_data.get("habilidades_tecnicas", []) or [])
    skills_depth_score = min(100.0, float(skills_count * 5))  # satura en 20 skills → 100
    languages_count = len(cv_data.get("idiomas", []) or [])
    languages_coverage_score = 100.0 if languages_count >= 2 else (60.0 if languages_count == 1 else 0.0)

    # Educación: entradas con título, institución y al menos una fecha
    education_entries = cv_data.get("formacion_academica", []) or []
    rich_edu = 0
    for edu in education_entries:
        titulo = _normalize_str(edu.get("titulo") or edu.get("degree") or edu.get("title"))
        inst = _normalize_str(edu.get("institucion") or edu.get("institution"))
        fs = _parse_year_month(edu.get("fecha_inicio") or edu.get("start_date"))
        fe = _parse_year_month(edu.get("fecha_fin") or edu.get("end_date"))
        if titulo and inst and (fs or fe):
            rich_edu += 1
    education_depth_score = 100.0 * rich_edu / len(education_entries) if education_entries else (100.0 if has_education else 0.0)

    # Score global ponderado
    overall_score = (
        dates_completeness * 0.2
        + chronology_score * 0.2
        + sections_coverage * 0.2
        + metrics_achievements_score * 0.2
        + skills_depth_score * 0.1
        + education_depth_score * 0.05
        + languages_coverage_score * 0.05
    )

    direct_scores = {
        "overall": round(overall_score, 1),
        "dates_completeness": round(dates_completeness, 1),
        "chronology": round(chronology_score, 1),
        "sections_coverage": round(sections_coverage, 1),
        "metrics_and_achievements": round(metrics_achievements_score, 1),
        "skills_depth": round(skills_depth_score, 1),
        "languages_coverage": round(languages_coverage_score, 1),
        "education_depth": round(education_depth_score, 1),
    }

    # Structured analysis -----------------------------------------------------
    structured = {
        "dates": {
            "total_experiences": total_roles,
            "with_start_date": total_roles - len(missing_start_date_items),
            "with_end_date": total_roles - len(missing_end_date_items),
            "missing_start_date": missing_start_date_items,
            "missing_end_date": missing_end_date_items,
            "ongoing_roles_count": ongoing_roles_count,
            "inconsistent_ranges": inconsistent_ranges,
        },
        "chronology": {
            "descending_by_start_date": is_descending,
            "misordered_pairs": misordered_pairs,
        },
        "sections": {
            "present": {
                "contact": has_contact,
                "experience": has_experience,
                "education": has_education,
                "skills": has_skills,
                "soft_skills": has_soft_skills,
                "languages": has_languages,
                "projects": has_projects,
                "summary": bool(cv_data.get("resumen_profesional")),
                "certifications": len(cv_data.get("certificaciones", [])) > 0,
            },
            "missing": [
                name
                for name, present in [
                    ("contact", has_contact),
                    ("experience", has_experience),
                    ("education", has_education),
                    ("skills", has_skills),
                    ("soft_skills", has_soft_skills),
                    ("languages", has_languages),
                    ("projects", has_projects),
                    ("summary", bool(cv_data.get("resumen_profesional"))),
                    ("certifications", len(cv_data.get("certificaciones", [])) > 0),
                ]
                if not present
            ],
        },
        "achievements": {
            "roles_with_logros": roles_with_logros,
            "roles_with_metric_logros": roles_with_metric_logros,
            "examples": metric_examples,
        },
        "skills": {
            "technologies_count": skills_count,
            "top_technologies": (cv_data.get("habilidades_tecnicas", []) or [])[:10],
        },
        "languages": {
            "count": languages_count,
            "items": [
                {"name": l.get("idioma") or l.get("name"), "level": l.get("nivel") or l.get("level")}
                for l in (cv_data.get("idiomas") or []) if isinstance(l, dict)
            ],
        },
        "education": {
            "count": len(education_entries),
            "entries_with_dates": rich_edu,
        },
    }

    return {
        "structure": structure,
        "coherence": "bueno" if len(experience) > 0 else "mejorable",
        "experience": experience_level,
        "skills": cv_data.get("habilidades_tecnicas", []),
        "softSkills": cv_data.get("habilidades_blandas", []),
        "languages": [f"{lang.get('idioma', '')} ({lang.get('nivel', '')})" for lang in cv_data.get("idiomas", [])],
        "education": [f"{edu.get('titulo', '')} - {edu.get('institucion', '')}" for edu in cv_data.get("formacion_academica", [])],
        "strengths": strengths,
        "weaknesses": weaknesses,
        "feedback": feedback,
        "alerts": alerts,
        "observations": observations,
        # Puntuaciones directas y análisis estructurado
        "direct_scores": direct_scores,
        "structured": structured,
        "total_years_experience": total_years,
        "technologies_count": len(cv_data.get("habilidades_tecnicas", [])),
        "soft_skills_count": len(cv_data.get("habilidades_blandas", [])),
        "languages_count": len(cv_data.get("idiomas", [])),
        "experience_count": len(experience),
        "education_count": len(cv_data.get("formacion_academica", [])),
        "projects_count": len(cv_data.get("proyectos", []))
    }

def extract_basic_cv_data_from_text(text: str) -> Dict[str, Any]:
    """
    Extrae información básica del CV cuando Azure OpenAI no está disponible
    """
    print("📋 Extrayendo información básica del texto...")
    
    # Buscar información de contacto
    import re
    
    # Buscar email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Buscar teléfono
    phone_pattern = r'[\+]?[0-9\s\-\(\)]{9,}'
    phones = re.findall(phone_pattern, text)
    
    # Buscar nombre (asumir que está en las primeras líneas)
    lines = text.split('\n')
    name = ""
    for line in lines[:5]:
        if len(line.strip()) > 3 and not any(word in line.lower() for word in ['email', 'teléfono', 'tel:', 'cv', 'curriculum']):
            name = line.strip()
            break
    
    # Buscar habilidades técnicas
    tech_keywords = [
        "javascript", "python", "java", "c++", "c#", "php", "ruby", "go", "rust",
        "react", "angular", "vue", "node.js", "express", "django", "flask",
        "sql", "mysql", "postgresql", "mongodb", "redis",
        "html", "css", "bootstrap", "tailwind", "sass", "less",
        "git", "docker", "kubernetes", "aws", "azure", "gcp",
        "machine learning", "ai", "data science", "analytics"
    ]
    
    found_skills = []
    for line in lines:
        line_lower = line.lower()
        for keyword in tech_keywords:
            if keyword in line_lower:
                found_skills.append(keyword.title())
    
    # Buscar formación académica
    education_keywords = ["universidad", "grado", "licenciatura", "ingeniería", "master", "máster", "doctorado", "curso", "certificación"]
    found_education = []
    for line in lines:
        line_lower = line.lower()
        for keyword in education_keywords:
            if keyword in line_lower:
                found_education.append(line.strip())
    
    # Buscar experiencia laboral
    experience_keywords = ["años", "experiencia", "desarrollador", "programador", "analista", "ingeniero", "consultor"]
    experience = []
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in experience_keywords):
            experience.append(line.strip())
    
    return {
        "contacto": {
            "nombre": name,
            "email": emails[0] if emails else "",
            "telefono": phones[0] if phones else "",
            "ubicacion": ""
        },
        # No generar experiencia/educación ficticia: si no se detecta, dejar vacío
        "experiencia_laboral": [],
        "formacion_academica": [],
        "habilidades_tecnicas": list(set(found_skills)),
        "habilidades_blandas": [],
        "idiomas": [],
        "certificaciones": [],
        "proyectos": [],
        "resumen_profesional": text[:200] + "..." if len(text) > 200 else text,
        "intereses": [],
        "voluntariado": []
    }

# Document Intelligence (Azure) eliminado
DOCUMENT_INTELLIGENCE_AVAILABLE = False


async def extract_pdf_info(pdf_buffer: bytes) -> Dict[str, Any]:
    """Extrae y analiza información de un CV en PDF."""

    file_size = len(pdf_buffer) if pdf_buffer else 0
    logger.info("Iniciando análisis de CV (%d bytes)", file_size)
    processing_metadata: Dict[str, Any] = {
        "document_intelligence": {
            "attempted": bool(DOCUMENT_INTELLIGENCE_AVAILABLE),
            "used": False,
            "error": None,
        },
        "text_extraction": {},
    }

    try:
        logger.info("Iniciando analisis de CV (modo combinado DI + PyMuPDF/OCR)...")

        di_result: Optional[Dict[str, Any]] = None
        di_error: Optional[str] = None

        if DOCUMENT_INTELLIGENCE_AVAILABLE:
            logger.info("Intentando análisis con Azure AI Document Intelligence...")
            try:
                di_attempt = await asyncio.to_thread(
                    analyze_cv_with_improved_intelligence, pdf_buffer
                )
            except Exception as di_exc:  # pragma: no cover - diagnóstico
                di_error = str(di_exc)
            else:
                if di_attempt and not di_attempt.get("error") and di_attempt.get("document_intelligence_used"):
                    di_result = di_attempt
                    processing_metadata["document_intelligence"]["used"] = True
                    logger.info("Analisis completado con Document Intelligence")
                else:
                    di_error = (di_attempt or {}).get("error") or "Resultado vacío de Document Intelligence"

            if di_error:
                processing_metadata["document_intelligence"]["error"] = di_error
                logger.warning("Document Intelligence no disponible o fallo: %s", di_error)
        else:
            logger.info("Document Intelligence no disponible, se combinarán métodos locales")

        logger.info("Extrayendo texto del PDF con PyMuPDF + OCR...")
        text, text_meta = await extract_text_with_advanced_ocr(pdf_buffer)
        processing_metadata["text_extraction"] = text_meta
        logger.info(
            "Texto combinado extraído: %s caracteres",
            text_meta.get("combined_text_length", len(text)),
        )

        # Helper para listas únicas y limpias
        def _to_unique_list(*values: Any) -> List[str]:
            merged: List[str] = []
            seen: set[str] = set()
            for value in values:
                if isinstance(value, list):
                    iter_values = value
                elif value is None or value == "":
                    iter_values = []
                else:
                    iter_values = [value]
                for item in iter_values:
                    if item is None:
                        continue
                    normalized = str(item).strip()
                    if not normalized or normalized.lower() == "none":
                        continue
                    if normalized not in seen:
                        merged.append(normalized)
                        seen.add(normalized)
            return merged

        # Determinar texto útil para heurísticas adicionales
        di_raw_text = ""
        if di_result and isinstance(di_result.get("raw_text"), str):
            di_raw_text = di_result["raw_text"]

        candidate_text = text if text.strip() else di_raw_text

        tool_keywords = {"word", "excel", "powerpoint", "photoshop", "procreate", "clip studio", "paint", "movie maker"}

        def _clean_name_candidate(name: str) -> str:
            if not name:
                return ""
            normalized = name.strip()
            if len(normalized) > 60 or any(ch.isdigit() for ch in normalized):
                return ""
            lower = normalized.lower()
            if any(k in lower for k in tool_keywords):
                return ""
            tokens = normalized.split()
            if len(tokens) > 5:
                return ""
            return normalized

        def _extract_languages_from_text(txt: str) -> List[Dict[str, str]]:
            if not txt:
                return []
            langs = []
            known = [
                "inglés", "ingles", "english",
                "español", "spanish",
                "francés", "frances", "french",
                "alemán", "aleman", "german",
                "italiano", "italian",
                "portugués", "portugues", "portuguese",
            ]
            seen = set()
            lower = txt.lower()
            for lang in known:
                if lang in lower and lang not in seen:
                    langs.append({"idioma": lang.capitalize(), "nivel": ""})
                    seen.add(lang)
            return langs

        def _extract_tools_from_text(txt: str) -> List[str]:
            if not txt:
                return []
            tools = []
            known_tools = [
                "Word", "Excel", "PowerPoint", "Powerpoint",
                "Photoshop", "Illustrator", "InDesign",
                "Procreate", "Clip Studio", "Paint", "Movie Maker",
            ]
            lower = txt.lower()
            seen = set()
            for tool in known_tools:
                if tool.lower() in lower and tool.lower() not in seen:
                    tools.append(tool)
                    seen.add(tool.lower())
            return tools

        if di_result:
            # Fusionar datos de Document Intelligence con la extracción local
            contact_di = di_result.get("contact") or {}
            fallback_contact = extract_contact_info_enhanced(candidate_text or di_raw_text)

            name_candidate = (
                contact_di.get("name")
                or contact_di.get("nombre")
                or fallback_contact.get("nombre")
                or ""
            )
            name_candidate = _clean_name_candidate(name_candidate)
            merged_contact = {
                "name": name_candidate,
                "nombre": name_candidate,
                "emails": _to_unique_list(contact_di.get("emails"), fallback_contact.get("email")),
                "phones": _to_unique_list(contact_di.get("phones"), fallback_contact.get("telefono")),
                "location": contact_di.get("location") or fallback_contact.get("ubicacion") or "",
                "linkedin": contact_di.get("linkedin") or fallback_contact.get("linkedin") or "",
            }

            def _normalize_experience(items: Any) -> List[Dict[str, Any]]:
                normalized: List[Dict[str, Any]] = []
                for item in items or []:
                    if isinstance(item, dict):
                        normalized.append({
                            "empresa": (item.get("company") or item.get("empresa") or "").strip(),
                            "cargo": (item.get("position") or item.get("cargo") or "").strip(),
                            "fecha_inicio": (item.get("start_date") or item.get("fecha_inicio") or "").strip(),
                            "fecha_fin": (item.get("end_date") or item.get("fecha_fin") or ("Actualidad" if item.get("current") else "")).strip(),
                            "descripcion": (item.get("description") or item.get("descripcion") or "").strip(),
                            "responsabilidades": item.get("responsibilities") or item.get("responsabilidades") or [],
                            "logros": item.get("achievements") or item.get("logros") or [],
                            "tecnologias": item.get("technologies") or item.get("tecnologias") or [],
                        })
                    else:
                        normalized.append({
                            "empresa": str(item),
                            "cargo": "",
                            "fecha_inicio": "",
                            "fecha_fin": "",
                            "descripcion": "",
                            "responsabilidades": [],
                            "logros": [],
                            "tecnologias": [],
                        })
                return normalized

            def _normalize_education(items: Any) -> List[Dict[str, Any]]:
                normalized: List[Dict[str, Any]] = []
                for item in items or []:
                    if isinstance(item, dict):
                        normalized.append({
                            "titulo": (item.get("degree") or item.get("titulo") or item.get("title") or "").strip(),
                            "institucion": (item.get("institution") or item.get("institucion") or item.get("school") or "").strip(),
                            "fecha_inicio": (item.get("start_date") or item.get("fecha_inicio") or "").strip(),
                            "fecha_fin": (item.get("end_date") or item.get("fecha_fin") or "").strip(),
                            "nivel": (item.get("level") or item.get("nivel") or "").strip(),
                        })
                    else:
                        normalized.append({
                            "titulo": str(item),
                            "institucion": "",
                            "fecha_inicio": "",
                            "fecha_fin": "",
                            "nivel": "",
                        })
                return normalized

            def _normalize_languages(items: Any) -> List[Dict[str, Any]]:
                normalized: List[Dict[str, Any]] = []
                for item in items or []:
                    if isinstance(item, dict):
                        idioma = item.get("language") or item.get("idioma") or ""
                        nivel = item.get("level") or item.get("nivel") or ""
                        normalized.append({"idioma": idioma, "nivel": nivel})
                    else:
                        normalized.append({"idioma": str(item), "nivel": ""})
                return normalized

            experience_structured = _normalize_experience(di_result.get("experience"))
            education_structured = _normalize_education(di_result.get("education"))
            languages_structured = _normalize_languages(di_result.get("languages"))

            software_items = di_result.get("software") or []
            # Normalizar software si viene en dict
            norm_software: List[str] = []
            for item in software_items:
                if isinstance(item, dict):
                    for k in ("name", "tool", "software"):
                        if item.get(k):
                            norm_software.append(str(item.get(k)))
                            break
                elif item:
                    norm_software.append(str(item))
            software_items = norm_software or software_items

            # Fallback con análisis básico si Document Intelligence no devolvió listas útiles
            basic_data = extract_basic_cv_data_from_text(candidate_text or di_raw_text)
            if basic_data:
                if not experience_structured and basic_data.get("experiencia_laboral"):
                    experience_structured = _normalize_experience(basic_data.get("experiencia_laboral"))
                if not education_structured and basic_data.get("formacion_academica"):
                    education_structured = _normalize_education(basic_data.get("formacion_academica"))
                if not languages_structured and basic_data.get("idiomas"):
                    languages_structured = _normalize_languages(basic_data.get("idiomas"))
                if not software_items and basic_data.get("habilidades_tecnicas"):
                    software_items = basic_data.get("habilidades_tecnicas")
                # No usar el nombre estimado del extractor básico para evitar falsos positivos (p.ej. listas de software)
                if not merged_contact.get("location") and (basic_data.get("contacto") or {}).get("ubicacion"):
                    merged_contact["location"] = (basic_data.get("contacto") or {}).get("ubicacion")
            # Fallback extra de idiomas/herramientas por regex simple
            if not languages_structured:
                languages_structured = _extract_languages_from_text(candidate_text or di_raw_text)
            if not software_items:
                software_items = _extract_tools_from_text(candidate_text or di_raw_text)

            # Si sigue sin experiencia/educación, extraer heurísticamente del texto
            if not experience_structured:
                experience_structured = _extract_experience_from_text(candidate_text or di_raw_text)  # type: ignore[name-defined]
            if not education_structured:
                education_structured = _extract_education_from_text(candidate_text or di_raw_text)  # type: ignore[name-defined]
            software_for_cv_info = [
                {"name": str(item), "level": ""}
                for item in software_items
                if item
            ]
            software_for_structure = [
                {"herramienta": str(item), "nivel": "No especificado"}
                for item in software_items
                if item
            ]

            resumen_profesional = (di_result.get("summary") or di_result.get("feedback") or candidate_text[:400]).strip()

            cv_info = {
                "contacto": {
                    "nombre": merged_contact["name"],
                    "email": merged_contact["emails"][0] if merged_contact["emails"] else "",
                    "telefono": merged_contact["phones"][0] if merged_contact["phones"] else "",
                    "ubicacion": merged_contact["location"],
                    "linkedin": merged_contact["linkedin"],
                },
                "software": software_for_cv_info,
                "idiomas": [
                    f"{lang.get('idioma', '')} ({lang.get('nivel', '')})".strip()
                    for lang in languages_structured
                ],
                "perfil": resumen_profesional,
                "experiencia": experience_structured,
                "educacion": education_structured,
                "habilidades": di_result.get("strengths") or [],
                "proyectos": di_result.get("projects") or [],
            }

            cv_data_for_structure = {
                "contacto": cv_info["contacto"],
                "experiencia_laboral": [
                    {
                        "empresa": exp.get("empresa"),
                        "cargo": exp.get("cargo"),
                        "fecha_inicio": exp.get("fecha_inicio"),
                        "fecha_fin": exp.get("fecha_fin"),
                        "descripcion": exp.get("descripcion"),
                        "responsabilidades": exp.get("responsabilidades", []),
                        "logros": exp.get("logros", []),
                        "tecnologias": exp.get("tecnologias", []),
                    }
                    for exp in experience_structured
                ],
                "formacion_academica": education_structured,
                "habilidades_tecnicas": software_for_structure,
                "habilidades_blandas": di_result.get("strengths") or [],
                "idiomas": languages_structured,
                "certificaciones": di_result.get("certifications") or [],
                "proyectos": di_result.get("projects") or [],
                "resumen_profesional": resumen_profesional,
                "intereses": di_result.get("interests") or [],
                "voluntariado": di_result.get("volunteer") or [],
            }

            logger.info("Analizando estructura del CV con datos combinados...")
            analysis = analyze_cv_structure_ai(cv_data_for_structure)
            logger.info("Analisis estructural completado (Document Intelligence + PyMuPDF/OCR)")

            raw_segments: List[str] = []
            if text.strip():
                raw_segments.append(text.strip())
            if di_raw_text and di_raw_text.strip() not in raw_segments:
                raw_segments.append(di_raw_text.strip())
            combined_raw_text = "\n\n".join(raw_segments).strip()

            exp_payload = di_result.get("experience")
            if not isinstance(exp_payload, list) or not exp_payload:
                exp_payload = experience_structured

            edu_payload = di_result.get("education")
            if not isinstance(edu_payload, list) or not edu_payload:
                edu_payload = education_structured

            lang_payload = di_result.get("languages")
            if not isinstance(lang_payload, list) or not lang_payload:
                lang_payload = languages_structured

            software_payload = di_result.get("software")
            if not isinstance(software_payload, list) or not software_payload:
                software_payload = [item["herramienta"] for item in software_for_structure]

            result_payload = {
                "summary": di_result.get("summary"),
                "strengths": di_result.get("strengths") or [],
                "weaknesses": di_result.get("weaknesses") or [],
                "feedback": di_result.get("feedback"),
                # Stars: intentar de DI, luego del análisis local, luego defaults
                "stars": di_result.get("stars") or analysis.get("stars") or _default_stars(),
                "experience": exp_payload,
                "education": edu_payload,
                "languages": lang_payload,
                "software": software_payload,
                "contact": merged_contact,
                "raw_text": (combined_raw_text or candidate_text or di_raw_text or "")[:10000],
                "raw_text_excerpt": (combined_raw_text or candidate_text or di_raw_text or "")[:1000],
                "analysis": analysis,
                "cv_info": cv_info,
                "full_cv_data": cv_data_for_structure,
                "processing_metadata": processing_metadata,
                "raw_text_sources": {
                    "py_mupdf_ocr": text,
                    "document_intelligence": di_raw_text,
                },
                "document_intelligence_used": True,
            }

            try:
                logger.info(
                    "CV extraído (DI+OCR) → contacto: name=%s email=%s phone=%s loc=%s | exp=%d edu=%d idiomas=%d tools=%d",
                    merged_contact.get("name") or merged_contact.get("nombre") or "",
                    (merged_contact.get("emails") or [""])[0],
                    (merged_contact.get("phones") or [""])[0],
                    merged_contact.get("location") or "",
                    len(experience_structured),
                    len(education_structured),
                    len(languages_structured),
                    len(software_items),
                )
            except Exception:
                pass

            result_payload["full_raw_text"] = combined_raw_text
            logger.info("Análisis de CV completado combinando Document Intelligence y PyMuPDF/OCR")
            return result_payload

        # Si Document Intelligence no está disponible o falló, usar el método tradicional
        logger.info("Aplicando método tradicional de extracción y análisis...")

        if not candidate_text.strip():
            logger.error("No se pudo extraer texto del PDF")
            return {
                "error": "No se pudo extraer texto del PDF. El archivo puede estar corrupto o ser una imagen sin texto.",
                "cv_info": {},
                "analysis": {},
                "raw_text": "",
                "processing_metadata": processing_metadata,
                "document_intelligence_used": False,
            }

        logger.info("Texto extraído: %s caracteres", len(candidate_text))
        logger.debug("Primeros 200 caracteres: %s...", candidate_text[:200])

        logger.info("Extrayendo información de contacto...")
        contact = extract_contact_info_enhanced(candidate_text)
        logger.info("Contacto extraído: %s", contact)

        logger.info("Analizando CV con IA heurística...")
        cv_data = analyze_cv_with_ai(candidate_text)

        if "error" in cv_data:
            logger.warning("Error en análisis con IA: %s", cv_data['error'])
            cv_data = {
                "contacto": contact,
                "experiencia_laboral": [],
                "formacion_academica": [],
                "habilidades_tecnicas": [],
                "habilidades_blandas": [],
                "idiomas": [],
                "proyectos": [],
            }
        else:
            logger.info("Análisis con IA completado exitosamente")

        logger.info("Analizando estructura del CV (método tradicional)...")
        analysis = analyze_cv_structure_ai(cv_data)
        logger.info("Análisis estructural completado")

        cv_info = {
            "contacto": cv_data.get("contacto", {}),
            "software": [
                {
                    "name": skill.get("herramienta", ""),
                    "level": skill.get("nivel", "No especificado"),
                }
                for skill in cv_data.get("habilidades_tecnicas", [])
                if isinstance(skill, dict) and skill.get("herramienta")
            ],
            "idiomas": [
                f"{lang.get('idioma', '')} ({lang.get('nivel', '')})".strip()
                for lang in cv_data.get("idiomas", [])
            ],
            "perfil": cv_data.get("resumen_profesional", ""),
            "experiencia": cv_data.get("experiencia_laboral", []),
            "educacion": cv_data.get("formacion_academica", []),
            "habilidades": cv_data.get("habilidades_blandas", []),
            "proyectos": cv_data.get("proyectos", []),
        }

        try:
            contact_log = cv_info.get("contacto") or {}
            logger.info(
                "CV extraído (heurístico) → contacto: name=%s email=%s phone=%s loc=%s | exp=%d edu=%d idiomas=%d tools=%d",
                contact_log.get("nombre") or "",
                contact_log.get("email") or "",
                contact_log.get("telefono") or "",
                contact_log.get("ubicacion") or "",
                len(cv_info.get("experiencia") or []),
                len(cv_info.get("educacion") or []),
                len(cv_info.get("idiomas") or []),
                len(cv_info.get("software") or []),
            )
        except Exception:
            pass

        logger.info("Análisis de CV completado con método tradicional")
        logger.info("Análisis de CV completado con método tradicional")

        return {
            "cv_info": cv_info,
            "analysis": analysis,
            "raw_text": candidate_text[:1000],
            "full_raw_text": candidate_text,
            "full_cv_data": cv_data,
            "processing_metadata": processing_metadata,
            "document_intelligence_used": False,
        }

    except Exception as e:  # pragma: no cover - errores inesperados
        import traceback
        logger.exception("Error analizando CV: %s", e)
        return {
            "error": f"Error al procesar el PDF: {str(e)}",
            "cv_info": {},
            "analysis": {},
            "raw_text": "",
            "processing_metadata": processing_metadata,
            "document_intelligence_used": False,
        }

if __name__ == "__main__":
    # Para testing directo
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        with open(pdf_path, 'rb') as f:
            pdf_buffer = f.read()
        result = extract_pdf_info(pdf_buffer)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Uso: python cv_analyzer.py <ruta_al_pdf>") 
