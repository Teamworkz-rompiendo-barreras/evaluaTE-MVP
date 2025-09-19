# generate_report.py
# -*- coding: utf-8 -*-
"""
Generador de informe IA _determinista_ y robusto a partir del prompt de back-end.
No requiere claves ni servicios externos. Devuelve un diccionario compatible con
`NewReportSchema`, es decir, con claves como `summary`, `personal_data`,
`cv_analysis`, `action_plan`, etc., más el campo `employability_score`.
"""

from __future__ import annotations
import json
import re
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
    )
except ImportError:  # pragma: no cover - fallback cuando se ejecuta dentro de backend/
    from new_report_schema import NewReportSchema, convert_old_format_to_new, create_default_report

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

    summary = ""
    for key in ("summary", "perfil", "profile_summary"):
        if isinstance(analysis, dict) and analysis.get(key):
            summary = str(analysis.get(key))
            break
    if not summary:
        summary = str(cv_data.get("summary") or "")

    corrections = _coerce_str_list((analysis or {}).get("corrections")) or _DEFAULT_CORRECTIONS
    reordering = _coerce_str_list((analysis or {}).get("reordering_suggestions")) or _DEFAULT_REORDERING

    evidence = {
        "structure": str(evidence_src.get("structure") or _DEFAULT_EVIDENCE["structure"]),
        "coherence": str(evidence_src.get("coherence") or _DEFAULT_EVIDENCE["coherence"]),
        "key_info": str(evidence_src.get("key_info") or _DEFAULT_EVIDENCE["key_info"]),
        "clarity": str(evidence_src.get("clarity") or _DEFAULT_EVIDENCE["clarity"]),
        "style": str(evidence_src.get("style") or _DEFAULT_EVIDENCE["style"]),
    }

    experience = cv_data.get("experience") or cv_data.get("experience_detailed") or []
    education = cv_data.get("education") or cv_data.get("education_detailed") or []
    languages = cv_data.get("languages") or cv_data.get("languages_detailed") or cv_data.get("idiomas") or []
    software = cv_data.get("software") or cv_data.get("skills") or []

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
        "summary": summary or "Perfil profesional con potencial de desarrollo.",
        "experience": experience,
        "education": education,
        "software": software,
        "languages": languages,
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

def _generate_modern_report(candidate_data: dict, soft_skills_data: list, cv_data: dict,
                           job_preferences_data: dict, employability_score: int, level: str,
                           completed_games: list) -> Optional[NewReportSchema]:
    """
    Genera un informe moderno y completo usando la nueva lógica de PromptConfig
    """
    try:
        if PromptConfig is None:
            raise ImportError("PromptConfig no disponible")
        
        # Preparar datos para el prompt moderno
        languages_data = cv_data.get("languages", [])
        
        # Generar el prompt usando la nueva configuración
        prompt = PromptConfig.get_employability_report_prompt(
            candidate_data=candidate_data,
            soft_skills_data=soft_skills_data,
            cv_data=cv_data,
            job_preferences_data=job_preferences_data,
            employability_score=employability_score,
            level=level,
            completed_games=completed_games,
            languages_data=languages_data
        )
        
        # Aquí normalmente se enviaría a OpenAI, pero como es local, generamos una respuesta estructurada
        # basada en los datos disponibles
        return _generate_structured_response_from_data(
            candidate_data, soft_skills_data, cv_data,
            job_preferences_data, employability_score, level, completed_games
        )

    except Exception as e:
        # Fallback a la lógica antigua si hay error
        return None

def _generate_structured_response_from_data(candidate_data: dict, soft_skills_data: list,
                                          cv_data: dict, job_preferences_data: dict,
                                          employability_score: int, level: str,
                                          completed_games: list) -> NewReportSchema:
    """Genera un ``NewReportSchema`` consistente a partir de los datos normalizados."""

    full_name = str(candidate_data.get("fullName") or "Usuario").strip() or "Usuario"
    normalized_soft_skills = _normalize_soft_skills(soft_skills_data or [])
    cv_payload = _build_cv_analysis_payload(cv_data or {})
    job_pref_payload = _build_job_preferences_payload(candidate_data, job_preferences_data or {})

    safe_score = max(0, min(100, int(employability_score or 0)))
    level_label = level or _score_to_level(safe_score)

    # Preparar resumen y feedback antes de crear el reporte base
    highlighted = ", ".join([s["skill"] for s in normalized_soft_skills[:3] if s.get("skill")])
    profile_parts = [f"Perfil {level_label.lower()} con puntuación de empleabilidad {safe_score}/100."]
    if highlighted:
        profile_parts.append(f"Destacan habilidades como {highlighted}.")
    if cv_payload.get("summary"):
        profile_parts.append(str(cv_payload.get("summary")))
    cv_payload["summary"] = " ".join(part.strip() for part in profile_parts if part).strip()

    cv_feedback = cv_payload.get("feedback") or ""
    if not cv_feedback:
        cv_feedback = (
            "CV con información básica disponible. Se recomienda enriquecerlo con más "
            "detalles sobre proyectos y logros específicos."
        )
    cv_payload["feedback"] = cv_feedback

    report = create_default_report(full_name, normalized_soft_skills, cv_payload, job_pref_payload)

    report.summary = (
        f"Informe de empleabilidad para {full_name}. Puntuación global {safe_score}/100 ({level_label})."
    )

    personal = report.personal_data
    personal.name = full_name
    if candidate_data.get("location"):
        personal.location = str(candidate_data.get("location"))
    if candidate_data.get("email"):
        personal.email = str(candidate_data.get("email"))
    if candidate_data.get("phone"):
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

    report.final_message = (
        f"{full_name}, tu nivel de empleabilidad actual es {level_label.lower()}. "
        "Aplica el plan de acción priorizado y mantén una rutina de aprendizaje continuo "
        "para acelerar tus oportunidades laborales."
    )

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
        fallback_report.summary = "No se recibió información suficiente."
        fallback_report.profile_summary = "No se recibió información suficiente."
        fallback_report.cv_summary = "Sin análisis disponible."
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

            # Datos del candidato
            full_name = str(data.get("fullName") or data.get("userId") or "Usuario")
            candidate_data = {
                "fullName": full_name,
                "location": (data.get("location") or "No consta"),
                "email": (data.get("email") or "No consta"),
                "phone": (data.get("phone") or "No especificado"),
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
            cv_raw = data.get("cvAnalysis") or {}
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
