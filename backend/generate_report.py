# generate_report.py
# -*- coding: utf-8 -*-
"""
Generador de informe IA _determinista_ y robusto a partir del prompt de back-end.
No requiere claves ni servicios externos. Devuelve un diccionario compatible con
`NewReportSchema`, es decir, con claves como `personal_data`,
`cv_analysis`, `action_plan`, etc., más el campo `employability_score`.
"""

from __future__ import annotations
import json
import re
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

# Importar la nueva configuración de prompts
try:
    from prompt_config import PromptConfig
except ImportError:
    PromptConfig = None

try:
    from backend.new_report_schema import (
        NewReportSchema,
        convert_old_format_to_new,
        create_default_report,
        ImprovementArea,
    )
except ImportError:  # pragma: no cover - fallback cuando se ejecuta dentro de backend/
    from new_report_schema import NewReportSchema, convert_old_format_to_new, create_default_report, ImprovementArea

# Cliente Azure OpenAI compartido con el analizador de CV
try:
    from backend.cv_analyzer import client as azure_client, DEPLOYMENT as AZURE_DEPLOYMENT
except Exception:  # pragma: no cover - evitar fallo cuando no hay cliente
    try:
        from cv_analyzer import client as azure_client, DEPLOYMENT as AZURE_DEPLOYMENT
    except Exception:
        azure_client = None
        AZURE_DEPLOYMENT = None

logger = logging.getLogger(__name__)

# Métricas básicas de uso LLM
LLM_SUCCESS_COUNT = 0
LLM_FALLBACK_COUNT = 0

# ----------------------------
# Utilidades de parsing seguro
# ----------------------------

_SOFT_LINE = re.compile(
    r"^\s*-\s*(?P<skill>[^:]+):\s*(?P<score>\d{1,3})\s*/\s*100"
    r"(?:\s*\((?P<level>[^)]+)\))?\s*$",
    flags=re.IGNORECASE,
)

SECTION_HEADERS = {
    "resumen": re.compile(r"^\s*1\)\s*RESUMEN\s+EJECUTIVO\s*$", re.IGNORECASE),
    "soft": re.compile(r"^\s*2\)\s*SOFT\s+SKILLS\s*$", re.IGNORECASE),
    "cv": re.compile(r"^\s*3\)\s*CV\s+ANALIZADO\s*$", re.IGNORECASE),
    "prefs": re.compile(r"^\s*4\)\s*PREFERENCIAS\s+LABORALES\s*$", re.IGNORECASE),
    "games": re.compile(r"^\s*5\)\s*JUEGOS\s+COMPLETADOS\s*$", re.IGNORECASE),
    # ignoramos 6..12 si existen
    "closing": re.compile(r"^\s*13\)\s*FRASE\s+FINAL\s*$", re.IGNORECASE),
}

def _split_sections(prompt: str) -> Dict[str, List[str]]:
    """
    Divide el prompt por secciones numeradas que esperamos (1..5 y 13).
    Devuelve map {clave: [lineas]} sin los encabezados.
    """
    lines = prompt.splitlines()
    buckets: Dict[str, List[str]] = {k: [] for k in SECTION_HEADERS.keys()}

    current_key: str | None = None
    for raw in lines:
        # Detecta encabezado
        hit = None
        for key, rx in SECTION_HEADERS.items():
            if rx.match(raw):
                current_key = key
                hit = True
                break
        if hit:
            continue

        if current_key:
            buckets[current_key].append(raw)

    return buckets

def _parse_soft_skills(lines: List[str]) -> Tuple[List[Dict[str, Any]], int]:
    """
    Extrae soft skills en el formato
    "- Comunicación: 85/100 (Avanzado)"
    Devuelve (lista, media_entera_0_100)
    """
    parsed: List[Dict[str, Any]] = []
    scores: List[int] = []
    
    # Validar que lines sea una lista
    if not isinstance(lines, list):
        return [], 0
    
    # Procesar cada línea
    for ln in lines:
        if not isinstance(ln, str):
            continue
        
        try:
            m = _SOFT_LINE.match(ln.strip())
            if not m:
                continue
            
            skill = m.group("skill").strip()
            score = int(m.group("score"))
            level = (m.group("level") or "").strip() or None
            
            # Validar y acotar score a 0..100
            if score < 0 or score > 100:
                score = max(0, min(100, score))
            
            parsed.append({"skill": skill, "score": score, "level": level})
            scores.append(score)
            
        except (ValueError, AttributeError) as e:
            # Si hay error en el parsing, continuar con la siguiente línea
            continue
    
    # Si no se encontraron soft skills, devolver lista vacía
    if not scores:
        return [], 0
    
    # Calcular promedio de forma segura
    try:
        avg = int(round(sum(scores) / len(scores)))
    except (ZeroDivisionError, TypeError):
        avg = 0
    
    return parsed, avg

def _score_to_level(score: int) -> str:
    if score >= 75:
        return "Alto"
    if score >= 50:
        return "Medio"
    return "Bajo"

def _clean_join(lines: List[str]) -> str:
    # Junta líneas, eliminando múltiples blancos
    text = "\n".join([ln.rstrip() for ln in lines]).strip()
    return re.sub(r"\n{3,}", "\n\n", text) if text else ""

def _extract_list_from_lines(lines: List[str]) -> List[str]:
    """
    Extrae lista de elementos de líneas que empiezan con "- " o "* "
    """
    out = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        m = re.match(r"^[-*]\s*(.+)$", ln)
        if m:
            out.append(m.group(1).strip())
    return out


_DEFAULT_EVIDENCE = {
    "structure": (
        "El CV contiene secciones básicas (experiencia, educación, idiomas, herramientas, contacto), "
        "pero no se detalla el orden ni la jerarquía de la información."
    ),
    "coherence": (
        "Falta de detalles sobre fechas, empresas y funciones específicas; no se observa consistencia en la presentación."
    ),
    "key_info": "No se incluyen logros cuantificables, KPIs ni enlaces a perfiles profesionales.",
    "clarity": "Ausencia de bullets claros y verbos de acción; la información es general y poco específica.",
    "style": "No se pueden evaluar tildes ni formato debido a la falta de texto raw, pero la estructura detectada es básica.",
}

_DEFAULT_CORRECTIONS = [
    "Añadir logros cuantificables y KPIs en cada experiencia.",
    "Incluir enlaces a LinkedIn u otros perfiles profesionales.",
    "Homogeneizar el formato de fechas y ubicaciones.",
    "Utilizar bullets y verbos de acción claros.",
    "Revisar ortografía y formato general.",
]

_DEFAULT_REORDERING = [
    "Colocar el perfil profesional al inicio.",
    "Agrupar la experiencia profesional antes de la formación.",
    "Incluir una sección específica de habilidades técnicas y soft skills.",
]


def _normalize_soft_skills(soft_skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for skill in soft_skills or []:
        if not isinstance(skill, dict):
            continue
        name = (skill.get("skill") or skill.get("name") or "").strip()
        if not name:
            continue
        score_raw = skill.get("score")
        try:
            score = int(round(float(score_raw)))
        except (TypeError, ValueError):
            score = 0
        score = max(0, min(100, score))
        normalized.append({"skill": name, "score": score})
    return normalized


def _parse_star_value(value: Any) -> Optional[int]:
    if isinstance(value, (int, float)):
        num = int(round(float(value)))
        return max(1, min(5, num))
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        star_count = stripped.count("★")
        if star_count:
            return max(1, min(5, star_count))
        try:
            # Permitir formatos "3/5" o "4"
            digits = re.findall(r"\d+", stripped)
            if digits:
                num = int(digits[0])
                return max(1, min(5, num))
        except (TypeError, ValueError):
            return None
    return None


def _extract_score(analysis: Dict[str, Any], stars: Dict[str, Any], keys: List[str], fallback: int = 3) -> int:
    for key in keys:
        if not isinstance(analysis, dict):
            break
        if key in analysis:
            parsed = _parse_star_value(analysis.get(key))
            if parsed is not None:
                return parsed
        # También probar con sufijo _score si no estaba explícito
        if not key.endswith("_score") and isinstance(analysis, dict):
            alt_key = f"{key}_score"
            if alt_key in analysis:
                parsed = _parse_star_value(analysis.get(alt_key))
                if parsed is not None:
                    return parsed
    if isinstance(stars, dict):
        for key in keys:
            if key in stars:
                parsed = _parse_star_value(stars.get(key))
                if parsed is not None:
                    return parsed
            # admitir claves con guiones bajos ↔ camelCase
            alt = key.replace("_", "")
            if alt in stars:
                parsed = _parse_star_value(stars.get(alt))
                if parsed is not None:
                    return parsed
    return fallback


def _coerce_str_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    if value is None:
        return []
    return [str(value)]


def _build_cv_analysis_payload(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(cv_data, dict):
        cv_data = {}

    def _pick_list(primary_key: str, detailed_key: str) -> list:
        primary_val = cv_data.get(primary_key)
        detailed_val = cv_data.get(detailed_key)
        if isinstance(primary_val, list) and primary_val:
            return primary_val
        if isinstance(detailed_val, list) and detailed_val:
            return detailed_val
        return []

    analysis_candidates: List[Dict[str, Any]] = []
    for key in ("analysis_json", "cv_analysis_structured", "analysis", "diagnostico_cv"):
        val = cv_data.get(key)
        if isinstance(val, dict) and val:
            analysis_candidates.append(val)

    analysis = analysis_candidates[0] if analysis_candidates else {}

    stars: Dict[str, Any] = {}
    star_candidates = []
    if isinstance(analysis, dict) and isinstance(analysis.get("stars"), dict):
        star_candidates.append(analysis.get("stars") or {})
    for key in ("stars", "cv_analysis_structured"):
        val = cv_data.get(key)
        if isinstance(val, dict):
            if key == "cv_analysis_structured" and isinstance(val.get("stars"), dict):
                star_candidates.append(val.get("stars") or {})
            else:
                star_candidates.append(val)
    for candidate in star_candidates:
        if candidate:
            stars = candidate
            break

    structure_score = _extract_score(analysis, stars, ["structure_score", "structure", "formato", "estructura"], 3)
    clarity_score = _extract_score(analysis, stars, ["clarity_score", "clarity", "claridad"], 3)
    coherence_score = _extract_score(analysis, stars, ["coherence_score", "coherence", "coherencia"], 3)
    key_info_score = _extract_score(analysis, stars, ["key_info_score", "key_info", "informacion_clave", "información_clave"], 3)
    style_score = _extract_score(analysis, stars, ["style_score", "spelling_style_score", "style", "ortografia", "ortografía"], 3)

    evidence_src = {}
    if isinstance(analysis, dict) and isinstance(analysis.get("evidence"), dict):
        evidence_src = analysis.get("evidence") or {}

    feedback = ""
    for key in ("feedback", "resumen", "resume"):
        if isinstance(analysis, dict) and analysis.get(key):
            feedback = str(analysis.get(key))
            break
    if not feedback:
        feedback = str(cv_data.get("feedback") or "")

    corrections = _coerce_str_list((analysis or {}).get("corrections")) or _DEFAULT_CORRECTIONS
    reordering = _coerce_str_list((analysis or {}).get("reordering_suggestions")) or _DEFAULT_REORDERING

    evidence = {
        "structure": str(evidence_src.get("structure") or _DEFAULT_EVIDENCE["structure"]),
        "coherence": str(evidence_src.get("coherence") or _DEFAULT_EVIDENCE["coherence"]),
        "key_info": str(evidence_src.get("key_info") or _DEFAULT_EVIDENCE["key_info"]),
        "clarity": str(evidence_src.get("clarity") or _DEFAULT_EVIDENCE["clarity"]),
        "style": str(evidence_src.get("style") or _DEFAULT_EVIDENCE["style"]),
    }

    experience = _pick_list("experience", "experience_detailed")
    education = _pick_list("education", "education_detailed")
    languages = _pick_list("languages", "languages_detailed") or cv_data.get("idiomas") or []
    software = _pick_list("software", "skills")
    courses = _pick_list("courses", "courses_detailed") or cv_data.get("cursos") or []
    certifications = _pick_list("certifications", "certifications_detailed") or cv_data.get("certificaciones") or []
    volunteering = _pick_list("volunteering", "volunteering_detailed") or cv_data.get("voluntariado") or []
    projects = _pick_list("projects", "projects_detailed") or cv_data.get("proyectos") or []
    aptitudes = _pick_list("aptitudes", "aptitudes_detailed") or cv_data.get("aptitudes") or cv_data.get("skills") or []

    # Preferir nombre desde contacto si existe
    candidate_name = ""
    if isinstance(cv_data.get("contact"), dict):
        candidate_name = cv_data["contact"].get("name") or cv_data["contact"].get("nombre") or ""
    if not candidate_name:
        candidate_name = cv_data.get("candidate") or ""

    # Contacto directo desde el CV (prioritario frente a la app)
    contact = {}
    if isinstance(cv_data.get("contact"), dict):
        contact = {
            "emails": cv_data["contact"].get("emails") or [],
            "phones": cv_data["contact"].get("phones") or [],
            "location": cv_data["contact"].get("location") or "",
            "name": cv_data["contact"].get("name") or cv_data["contact"].get("nombre") or "",
            "linkedin": cv_data["contact"].get("linkedin") or "",
        }

    return {
        "structure_score": structure_score,
        "coherence_score": coherence_score,
        "key_info_score": key_info_score,
        "clarity_score": clarity_score,
        "style_score": style_score,
        "evidence": evidence,
        "corrections": corrections,
        "reordering_suggestions": reordering,
        "feedback": feedback or "CV con información básica disponible.",
        "experience": experience,
        "education": education,
        "software": software,
        "languages": languages,
        "candidate": candidate_name,
        "contact": contact,
        "courses": courses,
        "certifications": certifications,
        "volunteering": volunteering,
        "projects": projects,
        "aptitudes": aptitudes,
    }


def _build_job_preferences_payload(candidate: Dict[str, Any], job_preferences: Dict[str, Any]) -> Dict[str, Any]:
    job_preferences = job_preferences.copy() if isinstance(job_preferences, dict) else {}

    location = candidate.get("location") or job_preferences.get("location") or ""
    if location:
        job_preferences["location"] = location

    has_cert = candidate.get("hasDisabilityCertificate")
    if has_cert is None:
        has_cert = job_preferences.get("hasDisabilityCert")
    if has_cert is not None:
        job_preferences["hasDisabilityCert"] = bool(has_cert)

    work_mode = job_preferences.get("workMode") or job_preferences.get("work_mode")
    if work_mode:
        job_preferences["workMode"] = work_mode

    desired = job_preferences.get("desired_roles") or job_preferences.get("areas") or []
    if not isinstance(desired, list):
        desired = [desired]
    job_preferences["desired_roles"] = desired
    job_preferences["areas"] = desired

    if "preferred_platforms" not in job_preferences and job_preferences.get("platforms"):
        job_preferences["preferred_platforms"] = job_preferences.get("platforms")

    if "seniority" not in job_preferences and candidate.get("seniority"):
        job_preferences["seniority"] = candidate.get("seniority")

    return job_preferences


def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extrae un JSON válido de un texto, tolerando ruido alrededor."""
    if not text:
        return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    try:
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1 and last > first:
            candidate = text[first : last + 1]
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
    except Exception:
        return None
    return None


def _validate_report_json(data: Dict[str, Any], fallback: NewReportSchema) -> Optional[NewReportSchema]:
    """
    Combina la respuesta del modelo con el fallback y valida contra NewReportSchema.
    Devuelve None si no cumple el esquema.
    """
    if not isinstance(data, dict):
        return None
    try:
        # El campo 'summary' fue eliminado del esquema; si llega, se ignora
        if "summary" in data:
            del data["summary"]

        merged = fallback.dict()
        merged.update(data)

        # Compatibilidad: mapear cv_summary → cv_analysis_summary si el LLM usó el nombre antiguo
        if "cv_summary" in merged and "cv_analysis_summary" not in merged:
            merged["cv_analysis_summary"] = merged["cv_summary"]
            del merged["cv_summary"]

        # Normalizar job_search_advice a listas si el modelo devolvió strings
        jsa = merged.get("job_search_advice", {}) or {}
        if isinstance(jsa, dict):
            for k in ("letters_portfolio", "networking", "interview_tips"):
                if k in jsa and isinstance(jsa[k], str):
                    jsa[k] = [jsa[k]] if jsa[k] else []
            merged["job_search_advice"] = jsa
        return NewReportSchema(**merged)
    except Exception as exc:
        logger.warning("Respuesta LLM no cumple esquema: %s", exc)
        return None

def _generate_modern_report(candidate_data: dict, soft_skills_data: list, cv_data: dict,
                           job_preferences_data: dict, employability_score: int, level: str,
                           completed_games: list) -> Optional[NewReportSchema]:
    """
    Genera un informe moderno y completo usando la nueva lógica de PromptConfig
    """
    global LLM_SUCCESS_COUNT, LLM_FALLBACK_COUNT
    request_id = str(uuid.uuid4())

    fallback_report = _generate_structured_response_from_data(
        candidate_data, soft_skills_data, cv_data,
        job_preferences_data, employability_score, level, completed_games
    )

    try:
        if PromptConfig is None:
            raise ImportError("PromptConfig no disponible")

        languages_data = cv_data.get("languages", []) if isinstance(cv_data, dict) else []
        diag_block_source = {}
        if isinstance(cv_data, dict):
            for key in ("analysis_json", "cv_analysis_structured", "diagnostico_cv", "analysis"):
                candidate = cv_data.get(key)
                if isinstance(candidate, dict) and candidate:
                    diag_block_source = candidate
                    break

        analysis_block = ""
        try:
            analysis_block = PromptConfig.make_cv_analysis_block(diag_block_source, cv_data)
        except Exception:
            analysis_block = ""

        prompt = PromptConfig.get_employability_report_prompt(
            candidate_data=candidate_data,
            soft_skills_data=soft_skills_data,
            cv_data=cv_data,
            job_preferences_data=job_preferences_data,
            employability_score=employability_score,
            level=level,
            completed_games=completed_games,
            languages_data=languages_data,
            analysis_block=analysis_block,
        )

        # Usar Azure OpenAI si está configurado
        if azure_client and AZURE_DEPLOYMENT:
            logger.info(
                "LLM request start",
                extra={
                    "request_id": request_id,
                    "deployment": AZURE_DEPLOYMENT,
                    "source": "generate_report",
                    "cv_has_text": bool(cv_data.get("rawText") if isinstance(cv_data, dict) else False),
                },
            )
            response = azure_client.chat.completions.create(
                model=AZURE_DEPLOYMENT,
                temperature=0.15,
                max_tokens=2200,
                messages=[
                    {"role": "system", "content": PromptConfig.get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content if response and response.choices else ""
            parsed = _extract_json_from_text(content)
            candidate_schema = _validate_report_json(parsed, fallback_report) if isinstance(parsed, dict) else None
            if candidate_schema:
                LLM_SUCCESS_COUNT += 1
                logger.info(
                    "LLM request success",
                    extra={"request_id": request_id, "deployment": AZURE_DEPLOYMENT, "status": "ok"},
                )
                return candidate_schema
            LLM_FALLBACK_COUNT += 1
            logger.warning(
                "LLM JSON inválido; se usa fallback",
                extra={"request_id": request_id, "deployment": AZURE_DEPLOYMENT, "status": "invalid_json"},
            )
        else:
            logger.info(
                "Azure OpenAI no configurado; se usa respuesta determinista",
                extra={"request_id": request_id, "status": "no_llm"},
            )

    except Exception as e:
        # Fallback a la lógica determinista si hay error
        LLM_FALLBACK_COUNT += 1
        logger.warning(
            "Error generando informe con LLM, usando fallback determinista",
            extra={"request_id": request_id, "error": str(e)},
        )

    return fallback_report

def _generate_structured_response_from_data(candidate_data: dict, soft_skills_data: list,
                                          cv_data: dict, job_preferences_data: dict,
                                          employability_score: int, level: str,
                                          completed_games: list) -> NewReportSchema:
    """Genera un ``NewReportSchema`` consistente a partir de los datos normalizados."""

    full_name = str(candidate_data.get("fullName") or "Usuario").strip() or "Usuario"
    normalized_soft_skills = _normalize_soft_skills(soft_skills_data or [])
    cv_payload = _build_cv_analysis_payload(cv_data or {})
    job_pref_payload = _build_job_preferences_payload(candidate_data, job_preferences_data or {})

    raw_text = ""
    if isinstance(cv_data, dict):
        raw_text = cv_data.get("rawText") or cv_data.get("raw_text") or ""

    exp_count = len(cv_payload.get("experience") or cv_payload.get("experience_detailed") or [])
    edu_count = len(cv_payload.get("education") or cv_payload.get("education_detailed") or [])
    lang_count = len(cv_payload.get("languages") or [])
    tools_count = len(cv_payload.get("software") or cv_payload.get("skills") or [])
    cv_missing = not any([exp_count, edu_count, lang_count, tools_count]) and not raw_text

    # Garantizar puntaje aunque no venga employability_score
    base_score = 0
    try:
        base_score = int(round(float(employability_score or 0)))
    except Exception:
        base_score = 0
    if (base_score == 0 or not isinstance(base_score, int)) and normalized_soft_skills:
        try:
            avg_soft = int(round(sum(s.get("score", 0) for s in normalized_soft_skills) / len(normalized_soft_skills)))
            base_score = max(0, min(100, avg_soft))
        except Exception:
            base_score = 0
    base_score = max(0, min(100, base_score))

    cv_boost = min(20, exp_count * 4 + edu_count * 2 + min(lang_count * 2, 8) + (5 if tools_count else 0))
    games_boost = min(10, len(completed_games or []) * 2)
    prefs_boost = 5 if (job_pref_payload.get("areas") or job_pref_payload.get("workMode") or job_pref_payload.get("work_mode")) else 0
    safe_score = max(0, min(100, base_score + cv_boost + games_boost + prefs_boost))
    if cv_missing and safe_score > 40:
        safe_score = 40  # limitar cuando no hay CV
    level_label = level or _score_to_level(safe_score)

    # Preparar resumen y feedback antes de crear el reporte base
    highlighted = ", ".join([s["skill"] for s in normalized_soft_skills[:3] if s.get("skill")])
    profile_parts = [f"Perfil {level_label.lower()} con puntuación de empleabilidad {safe_score}/100."]
    if highlighted:
        profile_parts.append(f"Destacan habilidades como {highlighted}.")
    if cv_payload.get("summary"):
        profile_parts.append(str(cv_payload.get("summary")))
    cv_payload["summary"] = " ".join(part.strip() for part in profile_parts if part).strip()

    if cv_missing:
        cv_payload["structure_score"] = 1
        cv_payload["coherence_score"] = 1
        cv_payload["key_info_score"] = 1
        cv_payload["clarity_score"] = 1
        cv_payload["style_score"] = 1
        cv_payload["evidence"] = {
            "structure": "No hay información del CV disponible para evaluar la estructura.",
            "coherence": "No hay información del CV disponible para evaluar la coherencia.",
            "key_info": "No hay información del CV disponible para evaluar la información clave.",
            "clarity": "No hay información del CV disponible para evaluar la claridad.",
            "style": "No hay información del CV disponible para evaluar ortografía y estilo.",
        }
        cv_payload["corrections"] = [
            "Sube un CV en PDF legible con fechas, funciones y logros medibles.",
            "Añade enlaces de contacto (email, LinkedIn) visibles en la cabecera.",
            "Incluye 3-5 logros cuantificados en tus experiencias más recientes.",
        ]
        cv_payload["reordering_suggestions"] = [
            "Coloca un resumen profesional inicial con especialidad y sector objetivo.",
            "Ordena la experiencia de la más reciente a la más antigua con fechas completas.",
            "Añade una sección de herramientas/idiomas con nivel.",
        ]
        cv_payload["feedback"] = "No hay información del CV disponible para evaluar; añade un PDF legible para un análisis completo."

    cv_feedback = cv_payload.get("feedback") or ""
    if not cv_feedback:
        cv_feedback = (
            "CV con información básica disponible. Se recomienda enriquecerlo con más "
            "detalles sobre proyectos y logros específicos."
        )
    cv_payload["feedback"] = cv_feedback

    # Enriquecer contacto priorizando SIEMPRE los datos del CV; solo usar candidato como último recurso
    cv_payload["candidate"] = full_name
    contact = cv_payload.get("contact") if isinstance(cv_payload.get("contact"), dict) else {}
    if not contact:
        contact = {}
    if not contact.get("emails") and candidate_data.get("email"):
        contact["emails"] = [candidate_data.get("email")]
    if not contact.get("phones") and candidate_data.get("phone"):
        contact["phones"] = [candidate_data.get("phone")]
    if not contact.get("location") and candidate_data.get("location"):
        contact["location"] = candidate_data.get("location")
    cv_payload["contact"] = contact

    # Construir cv_details como lista de dicts básicos para CvItem
    def _stringify_list(items: Any) -> List[Dict[str, Any]]:
        if not items:
            return []
        out: List[Dict[str, Any]] = []
        for it in items:
            if it is None:
                continue
            if isinstance(it, str):
                txt = it.strip()
                if txt:
                    out.append({"title": txt, "detail": txt})
            elif isinstance(it, dict):
                candidate: Dict[str, Any] = {}
                for k, alias in (
                    ("title", "title"),
                    ("cargo", "title"),
                    ("position", "title"),
                    ("role", "title"),
                    ("puesto", "title"),
                    ("company", "subtitle"),
                    ("empresa", "subtitle"),
                    ("organization", "subtitle"),
                    ("organizacion", "subtitle"),
                    ("institution", "subtitle"),
                    ("institucion", "subtitle"),
                    ("school", "subtitle"),
                    ("period", "period"),
                    ("duration", "period"),
                    ("start_date", "period"),
                    ("fecha_inicio", "period"),
                    ("end_date", "period"),
                    ("fecha_fin", "period"),
                    ("description", "detail"),
                    ("descripcion", "detail"),
                    ("degree", "level"),
                    ("titulo", "level"),
                    ("program", "level"),
                    ("area", "level"),
                    ("language", "title"),
                    ("level", "level"),
                    ("certification", "detail"),
                    ("tool", "title"),
                    ("technology", "title"),
                    ("software", "title"),
                    ("category", "detail"),
                ):
                    if k in it and it.get(k):
                        candidate.setdefault(alias, str(it.get(k)))
                # fallback: if empty, keep raw
                if not candidate:
                    candidate = {k: str(v) for k, v in it.items() if v is not None}
                out.append(candidate)
            else:
                out.append({"title": str(it), "detail": str(it)})
        return out

    cv_payload["cv_details"] = {
        "experience": _stringify_list(cv_payload.get("experience") or cv_payload.get("experience_detailed")),
        "education": _stringify_list(cv_payload.get("education") or cv_payload.get("education_detailed")),
        "languages": _stringify_list(cv_payload.get("languages")),
        "tools": _stringify_list(cv_payload.get("software") or cv_payload.get("skills")),
    }

    report = create_default_report(full_name, normalized_soft_skills, cv_payload, job_pref_payload)

    # Resumen ejecutivo enriquecido con preferencias, soft skills y CV
    top_skills = [s["skill"] for s in normalized_soft_skills[:2] if s.get("skill")]
    areas_pref = [str(a) for a in job_pref_payload.get("areas", []) if a]
    work_mode = str(job_pref_payload.get("workMode") or job_pref_payload.get("work_mode") or "").strip()
    exp_count = len(cv_payload.get("experience") or cv_payload.get("experience_detailed") or [])
    edu_count = len(cv_payload.get("education") or cv_payload.get("education_detailed") or [])
    games_count = len(completed_games or [])

    # profile_summary = resumen ejecutivo principal
    profile_parts: list[str] = [
        f"Informe de empleabilidad para {full_name}. Puntuación global {safe_score}/100 ({level_label})."
    ]
    if areas_pref:
        profile_parts.append(f"Orientado a roles en {', '.join(areas_pref)}.")
    if top_skills:
        profile_parts.append(f"Fortalezas destacadas: {', '.join(top_skills)}.")
    if work_mode:
        profile_parts.append(f"Preferencia de modalidad: {work_mode}.")
    if exp_count or edu_count:
        profile_parts.append(f"CV con {exp_count} experiencias y {edu_count} formaciones registradas.")
    if games_count:
        profile_parts.append(f"Resultados de {games_count} minijuego(s) integrados.")
    if cv_missing:
        profile_parts.append("No se encontró texto del CV; sube un PDF legible para un diagnóstico completo.")
    report.profile_summary = " ".join(profile_parts).strip()

    # cv_analysis_summary = resumen del CV
    cv_summary_parts: list[str] = []
    if exp_count:
        cv_summary_parts.append(f"Experiencia: {exp_count} registros.")
    if edu_count:
        cv_summary_parts.append(f"Formación: {edu_count} registros.")
    if lang_count:
        cv_summary_parts.append(f"Idiomas detectados: {lang_count}.")
    if tools_count:
        cv_summary_parts.append(f"Herramientas/tecnologías: {tools_count}.")
    if cv_missing:
        cv_summary_parts.append("No hay texto del CV; añade un PDF con fechas, funciones y logros cuantificados.")
    cv_analysis_summary_src = str(cv_payload.get("summary") or "").strip()
    report.cv_analysis_summary = " ".join([cv_analysis_summary_src] + cv_summary_parts).strip() or "Análisis del CV no disponible."

    # Eliminar campo summary del payload para evitar confusión
    if "summary" in cv_payload:
        del cv_payload["summary"]

    personal = report.personal_data
    # Datos personales: priorizar contacto del CV
    cv_contact = cv_payload.get("contact") if isinstance(cv_payload.get("contact"), dict) else {}
    personal.name = cv_contact.get("name") or cv_contact.get("nombre") or full_name
    if cv_contact.get("location"):
        personal.location = str(cv_contact.get("location"))
    elif candidate_data.get("location"):
        personal.location = str(candidate_data.get("location"))
    if cv_contact.get("emails"):
        personal.email = str(cv_contact.get("emails")[0])
    elif candidate_data.get("email"):
        personal.email = str(candidate_data.get("email"))
    if cv_contact.get("phones"):
        personal.phone = str(cv_contact.get("phones")[0])
    elif candidate_data.get("phone"):
        personal.phone = str(candidate_data.get("phone"))
    has_cert = candidate_data.get("hasDisabilityCertificate")
    if has_cert is None:
        has_cert = job_pref_payload.get("hasDisabilityCert")
    if has_cert is not None:
        personal.disability_certificate = "Sí" if has_cert else "No"
    report.personal_data = personal

    if normalized_soft_skills:
        report.soft_skills = normalized_soft_skills
        report.strengths = [s["skill"] for s in normalized_soft_skills if s.get("skill")]

    report.employability_score = safe_score

    if cv_missing:
        try:
            report.improvement_areas.insert(
                0,
                ImprovementArea(
                    area="Completar CV",
                    reason="No se recibió texto ni secciones del CV",
                    suggested_action="Sube un PDF legible con fechas, funciones y logros cuantificados para un diagnóstico completo.",
                ),
            )
        except Exception:
            pass

    games_list: List[str] = []
    for game in completed_games or []:
        if isinstance(game, dict):
            name = game.get("name") or game.get("title")
            if name:
                games_list.append(str(name))
                continue
        if game:
            games_list.append(str(game))
    report.completed_games = games_list

    preferred_platforms = job_pref_payload.get("preferred_platforms") or []
    if preferred_platforms:
        report.job_search_advice.recommended_platforms = [str(p) for p in preferred_platforms if p]

    work_mode = job_pref_payload.get("workMode")
    areas = job_pref_payload.get("areas") or []
    ideal_parts = []
    if work_mode:
        ideal_parts.append(f"Modalidad preferida: {work_mode}")
    if areas:
        ideal_parts.append("Áreas de interés: " + ", ".join(str(a) for a in areas if a))
    if ideal_parts:
        report.ideal_work_environment = ". ".join(ideal_parts)

    cierre = (
        f"{full_name}, tu nivel de empleabilidad actual es {safe_score}/100. "
        "Sigue el plan de acción priorizado y mantén una rutina de aprendizaje continuo."
    )
    if cv_missing:
        cierre += " Sube tu CV en PDF para que podamos ofrecerte un diagnóstico más preciso."
    report.final_message = cierre

    return report

# ----------------------------
# Núcleo público
# ----------------------------

def generar_informe(prompt: str | Dict[str, Any]) -> Dict[str, Any]:
    """
    Entrada: prompt (str) tal y como lo construye main.build_prompt(...)
    Salida: dict conforme a la UI/PDF.

    Nunca devuelve None. Nunca accede a .get() sobre valores no dict.
    """
    if prompt is None:
        fallback_report = create_default_report("Usuario", [], {}, {})
        fallback_report.profile_summary = "No se recibió información suficiente."
        fallback_report.cv_analysis_summary = "Sin análisis disponible."
        fallback_report.soft_skills = []
        fallback_report.strengths = []
        fallback_report.improvement_areas = []
        fallback_report.employability_score = 0
        fallback_report.completed_games = []
        fallback_report.final_message = (
            "Define un objetivo profesional y comienza por acciones concretas la próxima semana."
        )
        return fallback_report.dict()

    # Si llega un dict (payload estructurado del frontend), mapearlo directamente
    if isinstance(prompt, dict):
        try:
            data: Dict[str, Any] = prompt

            # Datos del candidato (con fallback a datos del CV para el nombre)
            full_name_raw = data.get("fullName") or data.get("userId") or ""
            cv_raw_for_name = data.get("cvAnalysis") or {}
            cv_structured_for_name = cv_raw_for_name.get("cv_structured") or {}
            cv_contact_for_name = cv_raw_for_name.get("contact") or cv_structured_for_name.get("contact") or {}
            cv_candidate_name = cv_structured_for_name.get("candidate") or cv_contact_for_name.get("name") or cv_contact_for_name.get("nombre") or ""
            full_name = str(cv_candidate_name or full_name_raw or "Usuario").strip() or "Usuario"

            # Datos del candidato priorizando siempre el contacto del CV
            candidate_data = {
                "fullName": full_name,
                "location": cv_contact_for_name.get("location")
                or data.get("location")
                or "No consta",
                "email": (cv_contact_for_name.get("emails") or [None])[0]
                or data.get("email")
                or "No consta",
                "phone": (cv_contact_for_name.get("phones") or [None])[0]
                or data.get("phone")
                or "No especificado",
                "hasDisabilityCertificate": bool((data.get("jobPreferences") or {}).get("hasDisabilityCert"))
            }

            # Soft skills
            soft_skills_raw = data.get("softSkills") or []
            soft_skills_data: List[Dict[str, Any]] = []
            scores: List[int] = []
            if isinstance(soft_skills_raw, list):
                for it in soft_skills_raw:
                    if not isinstance(it, dict):
                        continue
                    skill = (it.get("skill") or it.get("name") or "").strip()
                    try:
                        score = int(it.get("score") or 0)
                    except Exception:
                        score = 0
                    level = it.get("level") or None
                    soft_skills_data.append({"skill": skill, "score": score, "level": level})
                    scores.append(score)
            soft_avg = int(round(sum(scores) / len(scores))) if scores else 0

            provided_score = data.get("employabilityScore")
            if provided_score is None:
                provided_score = data.get("employability_score")

            override_score = None
            for key in ("employabilityScoreOverride", "employability_score_override"):
                candidate = data.get(key)
                if isinstance(candidate, str):
                    candidate = candidate.strip()
                if candidate in (None, "", []):
                    continue
                override_score = candidate
                break

            if override_score is not None:
                try:
                    soft_avg = int(round(float(override_score)))
                except (TypeError, ValueError):
                    pass
            elif not scores and provided_score not in (None, "", []):
                try:
                    soft_avg = int(round(float(provided_score)))
                except (TypeError, ValueError):
                    pass

            soft_avg = max(0, min(100, soft_avg))
            nivel = _score_to_level(soft_avg)

            # CV data (tomar lo disponible)
            # Aceptar ambas convenciones de clave para cvAnalysis
            cv_raw = data.get("cvAnalysis") or data.get("cv_analysis") or {}
            cv_data = {}
            if isinstance(cv_raw, dict):
                contact_raw = cv_raw.get("contact") or {}
                emails = contact_raw.get("emails") if isinstance(contact_raw, dict) else None
                phones = contact_raw.get("phones") if isinstance(contact_raw, dict) else None
                loc = contact_raw.get("location") if isinstance(contact_raw, dict) else None
                emails = emails if isinstance(emails, list) else ([] if emails is None else [str(emails)])
                phones = phones if isinstance(phones, list) else ([] if phones is None else [str(phones)])
                loc = loc if isinstance(loc, str) else None

                if not candidate_data.get("email") or candidate_data["email"] == "No consta":
                    candidate_data["email"] = (emails[0] if emails else "No consta")
                if not candidate_data.get("phone") or candidate_data["phone"] == "No especificado":
                    candidate_data["phone"] = (phones[0] if phones else "No especificado")
                if (not candidate_data.get("location") or candidate_data["location"] == "No consta") and loc:
                    candidate_data["location"] = loc

                # Extraer herramientas/software con múltiples estrategias de fallback
                structured = cv_raw.get("cv_structured") or {}
                structured_skills = structured.get("skills") or []

                software_list = (
                    cv_raw.get("software")
                    or cv_raw.get("skills")
                    or structured_skills
                    or []
                )

                analysis_json = (
                    cv_raw.get("analysis_json")
                    or cv_raw.get("cv_analysis_structured")
                    or cv_raw.get("analysis")
                    or {}
                )

                cv_data = {
                    "rawText": cv_raw.get("raw_text") or "",
                    "languages": cv_raw.get("languages") or [],
                    "experience": cv_raw.get("experience_detailed") or cv_raw.get("experience") or [],
                    "education": cv_raw.get("education_detailed") or cv_raw.get("education") or [],
                    "skills": cv_raw.get("skills") or structured_skills or [],
                    "software": software_list,
                    "contact": {
                        "emails": emails,
                        "phones": phones,
                        "location": loc,
                        "name": cv_raw.get("candidate") or cv_structured_for_name.get("candidate") or "",
                    },
                    "analysis_json": analysis_json,
                }

            # Preferencias laborales
            jp_raw = data.get("jobPreferences") or {}
            job_preferences_data = {}
            if isinstance(jp_raw, dict):
                work_mode = jp_raw.get("workMode") or jp_raw.get("work_mode") or ""
                desired = jp_raw.get("areas") or jp_raw.get("desired_roles") or []
                if not isinstance(desired, list):
                    desired = [desired]
                preferred_platforms = (
                    jp_raw.get("preferred_platforms")
                    or jp_raw.get("preferredPlatforms")
                    or jp_raw.get("platforms")
                    or []
                )
                if not isinstance(preferred_platforms, list):
                    preferred_platforms = [preferred_platforms]
                job_preferences_data = {
                    "areas": desired,
                    "desired_roles": desired,
                    "workMode": work_mode,
                    "work_mode": work_mode,
                    "preferred_platforms": preferred_platforms,
                    "seniority": jp_raw.get("seniority") or jp_raw.get("level"),
                    "location": jp_raw.get("location"),
                    "hasDisabilityCert": jp_raw.get("hasDisabilityCert"),
                }
                if jp_raw.get("seniority"):
                    candidate_data["seniority"] = jp_raw.get("seniority")

            completed_games = data.get("completedGames") or []
            if not isinstance(completed_games, list):
                completed_games = []

            # Generar respuesta estructurada determinista a partir del payload
            return _generate_structured_response_from_data(
                candidate_data,
                soft_skills_data,
                cv_data,
                job_preferences_data,
                soft_avg,
                nivel,
                completed_games,
            ).dict()
        except Exception:
            # Fallback: serializar a texto y seguir con la lógica basada en prompt
            prompt = json.dumps(prompt, ensure_ascii=False)

    # INTENTAR USAR LA NUEVA LÓGICA MODERNA
    try:
        # Extraer datos del prompt para usar la nueva lógica
        # Buscar información del candidato
        m_name = re.search(r"(?im)^\s*Nombre\s*:\s*(.+?)\s*$", prompt)
        nombre = m_name.group(1).strip() if m_name else "Usuario"
        
        # Extraer soft skills del prompt
        soft_list, soft_avg = _parse_soft_skills(prompt.splitlines())
        nivel = _score_to_level(soft_avg)
        
        # Preparar datos para la nueva lógica
        candidate_data = {
            "fullName": nombre,
            "location": "No consta",
            "email": "No consta", 
            "phone": "No especificado",
            "hasDisabilityCertificate": False
        }
        
        # Preparar datos del CV (simulados por ahora)
        cv_data = {
            "rawText": prompt,
            "languages": [],
            "diagnostico_cv": {
                "structure_score": 1,
                "clarity_score": 1,
                "coherence_score": 1,
                "key_info_score": 1,
                "spelling_style_score": 1
            }
        }
        
        # Preparar preferencias laborales
        job_preferences_data = {
            "desired_roles": [],
            "desired_sectors": []
        }
        
        # Intentar generar informe moderno
        modern_report = _generate_modern_report(
            candidate_data, soft_list, cv_data, 
            job_preferences_data, soft_avg, nivel, []
        )
        
        if modern_report:
            return modern_report.dict()
            
    except Exception as e:
        # Si falla la nueva lógica, continuar con la antigua
        pass

    # FALLBACK A LA LÓGICA ANTIGUA (mantiene compatibilidad)
    # Parseo de secciones
    sec = _split_sections(prompt)

    # 1) Resumen + nombre si está en la línea siguiente
    resumen_text = _clean_join(sec.get("resumen", []))
    # intenta rescatar "Nombre: X" si existe en el prompt original
    m_name = re.search(r"(?im)^\s*Nombre\s*:\s*(.+?)\s*$", prompt)
    nombre = m_name.group(1).strip() if m_name else None
    if nombre and "Nombre:" not in resumen_text:
        resumen_text = ("Nombre: " + nombre + "\n" + resumen_text).strip()

    # 2) Soft skills
    soft_list, soft_avg = _parse_soft_skills(sec.get("soft", []))
    nivel = _score_to_level(soft_avg)

    # 3) CV analizado (bloque entero tal cual lo generó el back, si existe)
    cv_text = _clean_join(sec.get("cv", [])) or "CV ANALIZADO\n- No se pudo recuperar el detalle."

    # 4) Preferencias laborales
    prefs_text = _clean_join(sec.get("prefs", [])) or "PREFERENCIAS LABORALES\n- No especificadas."

    # 5) Juegos completados
    games = _extract_list_from_lines(sec.get("games", []))
    # Si vino "- No consta", dejamos lista vacía
    games = [] if any("no consta" in (g or "").lower() for g in games) else games

    # 13) Frase final
    cierre = _clean_join(sec.get("closing", [])) or \
        "Mantén una búsqueda activa, actualiza tu CV con logros medibles y crea una rutina semanal de networking."

    # Recomendaciones básicas derivadas del contenido
    recs: List[str] = []
    if soft_avg < 50:
        recs.append("Refuerza las competencias con cursos breves y práctica guiada (p.ej., comunicación y trabajo en equipo).")
    if "CV ANALIZADO" in cv_text and "No se ha podido" in cv_text:
        recs.append("Sube un CV en PDF legible y con fechas, funciones y logros concretos (STAR).")
    if not games:
        recs.append("Completa los juegos de evaluación para enriquecer tu perfil de soft skills.")
    if not recs:
        recs = [
            "Prioriza 3 vacantes objetivo y adapta tu CV con logros cuantificables.",
            "Refuerza tu perfil de LinkedIn y pide 2-3 recomendaciones recientes.",
        ]

    # Construcción del informe
    report: Dict[str, Any] = {
        "resumen_ejecutivo": resumen_text or "Sin resumen disponible.",
        "soft_skills": soft_list,                     # lista [{skill, score, level?}]
        "cv_analizado": cv_text,                      # bloque multilínea
        "preferencias_laborales": prefs_text,         # bloque multilínea
        "juegos_completados": games,                  # lista de textos
        "frase_final": cierre,                        # cierre breve
    }

    if nombre:
        report["fullName"] = nombre

    # Puntuación global basada en las soft skills
    employability = int(soft_avg)
    legacy_payload = {
        "report": report,
        "recommendations": recs,
        "employabilityScore": employability,
    }

    return convert_old_format_to_new(legacy_payload).dict()
