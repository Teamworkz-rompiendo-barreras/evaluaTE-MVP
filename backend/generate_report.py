# backend/generate_report.py
# -*- coding: utf-8 -*-

from __future__ import annotations
import json
import re
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

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
except ImportError:
    from new_report_schema import NewReportSchema, convert_old_format_to_new, create_default_report, ImprovementArea

import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai_configured = False
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        genai_configured = True
    except ImportError:
        pass

logger = logging.getLogger(__name__)

LLM_SUCCESS_COUNT = 0
LLM_FALLBACK_COUNT = 0

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
    "closing": re.compile(r"^\s*13\)\s*FRASE\s+FINAL\s*$", re.IGNORECASE),
}

def _split_sections(prompt: str) -> Dict[str, List[str]]:
    lines = prompt.splitlines()
    buckets: Dict[str, List[str]] = {k: [] for k in SECTION_HEADERS.keys()}
    current_key: str | None = None
    for raw in lines:
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
    parsed: List[Dict[str, Any]] = []
    scores: List[int] = []
    if not isinstance(lines, list):
        return [], 0
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
            if score < 0 or score > 100:
                score = max(0, min(100, score))
            parsed.append({"skill": skill, "score": score, "level": level})
            scores.append(score)
        except (ValueError, AttributeError):
            continue
    if not scores:
        return [], 0
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
    text = "\n".join([ln.rstrip() for ln in lines]).strip()
    return re.sub(r"\n{3,}", "\n\n", text) if text else ""

def _extract_list_from_lines(lines: List[str]) -> List[str]:
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
    "structure": "El CV contiene secciones básicas.",
    "coherence": "Falta de detalles o consistencia en la presentación.",
    "key_info": "No se incluyen logros cuantificables o KPIs.",
    "clarity": "Ausencia de verbos de acción; la información es general.",
    "style": "Revisar formato estructural.",
}

_DEFAULT_CORRECTIONS = [
    "Añadir logros cuantificables en cada experiencia.",
    "Incluir perfil de LinkedIn.",
    "Homogeneizar el formato de fechas.",
    "Utilizar bullets y verbos de acción.",
]

_DEFAULT_REORDERING = [
    "Colocar el perfil profesional al inicio.",
    "Agrupar la experiencia profesional antes de la formación.",
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

    def _pick_list(primary_key: str, detailed_key: str, nested_key: str = "") -> list:
        candidates = []
        p_val = cv_data.get(primary_key)
        if isinstance(p_val, list) and p_val: candidates.append(p_val)
        d_val = cv_data.get(detailed_key)
        if isinstance(d_val, list) and d_val: candidates.append(d_val)
        target = nested_key or primary_key
        for root in ("cv_structured", "cv_analysis_structured", "cv_info"):
            container = cv_data.get(root)
            if isinstance(container, dict):
                sub_keys = [target]
                if target == "experience": sub_keys.append("experiencia")
                if target == "education": sub_keys.append("educacion")
                if target == "languages": sub_keys.append("idiomas")
                if target == "software": sub_keys.append("tools")
                for k in sub_keys:
                    val = container.get(k)
                    if isinstance(val, list) and val:
                        candidates.append(val)
        for cand_list in candidates:
            cleaned = []
            for v in cand_list:
                if isinstance(v, str):
                    s = v.lower().strip()
                    if s in ("mejorable", "regular", "bueno", "excelente", "no consta", "no especificado", "ver cv", "none", "n/a"):
                        continue
                    if len(s) < 3:
                        continue
                    cleaned.append(v)
                elif isinstance(v, dict):
                    is_placeholder = False
                    for key_check in ["empresa", "company", "title", "cargo", "institucion", "institution", "idioma", "language"]:
                        val_check = v.get(key_check)
                        if isinstance(val_check, str):
                            chk = val_check.lower().strip()
                            if chk in ("mejorable", "regular", "bueno", "excelente", "no consta", "no especificado", "ver cv", "none", "n/a"):
                                is_placeholder = True
                                break
                    if not is_placeholder:
                        cleaned.append(v)
                else:
                    cleaned.append(v)
            if cleaned:
                return cleaned
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

    candidate_name = ""
    if isinstance(cv_data.get("contact"), dict):
        candidate_name = cv_data["contact"].get("name") or cv_data["contact"].get("nombre") or ""
    if not candidate_name:
        candidate_name = cv_data.get("candidate") or ""

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
        "feedback": feedback or "CV procesado.",
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
    if location: job_preferences["location"] = location
    has_cert = candidate.get("hasDisabilityCertificate")
    if has_cert is None: has_cert = job_preferences.get("hasDisabilityCert")
    if has_cert is not None: job_preferences["hasDisabilityCert"] = bool(has_cert)
    work_mode = job_preferences.get("workMode") or job_preferences.get("work_mode")
    if work_mode: job_preferences["workMode"] = work_mode
    desired = job_preferences.get("desired_roles") or job_preferences.get("areas") or []
    if not isinstance(desired, list): desired = [desired]
    job_preferences["desired_roles"] = desired
    job_preferences["areas"] = desired
    if "preferred_platforms" not in job_preferences and job_preferences.get("platforms"):
        job_preferences["preferred_platforms"] = job_preferences.get("platforms")
    if "seniority" not in job_preferences and candidate.get("seniority"):
        job_preferences["seniority"] = candidate.get("seniority")
    return job_preferences

def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    if not text: return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict): return parsed
    except Exception: pass
    try:
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1 and last > first:
            candidate = text[first : last + 1]
            parsed = json.loads(candidate)
            if isinstance(parsed, dict): return parsed
    except Exception: return None
    return None

def _validate_report_json(data: Dict[str, Any], fallback: NewReportSchema) -> Optional[NewReportSchema]:
    if not isinstance(data, dict): return None
    try:
        if "summary" in data: del data["summary"]
        merged = fallback.dict()
        merged.update(data)
        if "cv_summary" in merged and "cv_analysis_summary" not in merged:
            merged["cv_analysis_summary"] = merged["cv_summary"]
            del merged["cv_summary"]
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
    global LLM_SUCCESS_COUNT, LLM_FALLBACK_COUNT
    request_id = str(uuid.uuid4())

    fallback_report = _generate_structured_response_from_data(
        candidate_data, soft_skills_data, cv_data,
        job_preferences_data, employability_score, level, completed_games
    )

    try:
        if PromptConfig is None: raise ImportError("PromptConfig no disponible")
        languages_data = cv_data.get("languages", []) if isinstance(cv_data, dict) else []
        diag_block_source = {}
        if isinstance(cv_data, dict):
            for key in ("analysis_json", "cv_analysis_structured", "diagnostico_cv", "analysis"):
                candidate = cv_data.get(key)
                if isinstance(candidate, dict) and candidate:
                    diag_block_source = candidate
                    break

        analysis_block = ""
        try: analysis_block = PromptConfig.make_cv_analysis_block(diag_block_source, cv_data)
        except Exception: analysis_block = ""

        full_text = cv_data.get("full_raw_text") or cv_data.get("rawText") or cv_data.get("raw_text") or ""
        
        # FIX IA: Extraer el nombre prioritario desde los datos del formulario frontend
        force_candidate_name = candidate_data.get("fullName") or candidate_data.get("name") or "Usuario"

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
            full_raw_text=full_text,
        )
        
        prompt += f"\n\nINSTRUCCIÓN CRÍTICA: Eres un orientador laboral dirigiéndote al candidato '{force_candidate_name}'. NUNCA uses plantillas genéricas o corchetes. Evalúa basándote en la información real extraída."

        if genai_configured:
            model = genai.GenerativeModel(
                model_name="gemini-flash-latest",
                system_instruction=PromptConfig.get_system_prompt()
            )
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.15,
                    max_output_tokens=2200,
                    response_mime_type="application/json"
                )
            )
            parsed = _extract_json_from_text(response.text if response else "")
            candidate_schema = _validate_report_json(parsed, fallback_report) if isinstance(parsed, dict) else None
            if candidate_schema: return candidate_schema
        else:
            pass
    except Exception as e:
        pass
    return fallback_report

def _generate_structured_response_from_data(candidate_data: dict, soft_skills_data: list,
                                          cv_data: dict, job_preferences_data: dict,
                                          employability_score: int, level: str,
                                          completed_games: list) -> NewReportSchema:
    # FIX IA: Fallback Name sin "Candidato Anonimizado"
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

    base_score = 0
    try: base_score = int(round(float(employability_score or 0)))
    except Exception: base_score = 0
    if (base_score == 0 or not isinstance(base_score, int)) and normalized_soft_skills:
        try:
            avg_soft = int(round(sum(s.get("score", 0) for s in normalized_soft_skills) / len(normalized_soft_skills)))
            base_score = max(0, min(100, avg_soft))
        except Exception: base_score = 0
    base_score = max(0, min(100, base_score))

    cv_boost = min(20, exp_count * 4 + edu_count * 2 + min(lang_count * 2, 8) + (5 if tools_count else 0))
    games_boost = min(10, len(completed_games or []) * 2)
    prefs_boost = 5 if (job_pref_payload.get("areas") or job_pref_payload.get("workMode") or job_pref_payload.get("work_mode")) else 0
    safe_score = max(0, min(100, base_score + cv_boost + games_boost + prefs_boost))
    if cv_missing and safe_score > 40: safe_score = 40
    level_label = level or _score_to_level(safe_score)

    sorted_skills = sorted(normalized_soft_skills, key=lambda x: x.get("score", 0), reverse=True)
    top_skills = [s["skill"] for s in sorted_skills[:4] if s.get("skill")]
    weak_skills_data = sorted(normalized_soft_skills, key=lambda x: x.get("score", 0))[:2]
    improvement_strs = []
    for ws in weak_skills_data:
        nm = ws.get("skill")
        if nm: improvement_strs.append(f"{nm} - Oportunidad de mejora")

    areas_pref = [str(a) for a in job_pref_payload.get("areas", []) if a]
    work_mode = str(job_pref_payload.get("workMode") or job_pref_payload.get("work_mode") or "").strip()

    summary_sentences: List[str] = []
    intro_part = f"Profesional con experiencia," if exp_count > 0 else "Profesional en búsqueda de nuevas oportunidades,"

    skills_text = ""
    if top_skills:
        skills_text = top_skills[0] if len(top_skills) == 1 else ", ".join(top_skills[:-1]) + " y " + top_skills[-1]
        summary_sentences.append(f"{intro_part} {full_name} destaca por su capacidad de {skills_text}.")
    else:
        summary_sentences.append(f"{intro_part} {full_name} presenta un perfil con potencial de desarrollo.")

    roles_text = f"con especial interés en roles {areas_pref[0] if len(areas_pref) == 1 else ', '.join(areas_pref[:-1]) + ' y ' + areas_pref[-1]}" if areas_pref else "con interés en desarrollar su carrera"
    env_text = f" en entornos {work_mode}" if work_mode else ""
    summary_sentences.append(f"Su propuesta de valor reside en la combinación de habilidades técnicas y soft skills, {roles_text}{env_text}.")
    summary_sentences.append("Su perfil es adecuado para entornos que valoren la autonomía, la organización y el aprendizaje continuo.")
    
    if improvement_strs:
        summary_sentences.append(f"Áreas a potenciar: {improvement_strs[0] if len(improvement_strs) == 1 else ' y '.join(improvement_strs)}.")
    if cv_missing:
        summary_sentences.append("Sugerencia: Sube tu CV para un diagnóstico más completo.")

    narrative_summary = " ".join(summary_sentences).strip()

    if not cv_payload.get("summary"): cv_payload["summary"] = narrative_summary

    if cv_missing:
        cv_payload["structure_score"] = 1
        cv_payload["coherence_score"] = 1
        cv_payload["key_info_score"] = 1
        cv_payload["clarity_score"] = 1
        cv_payload["style_score"] = 1
        cv_payload["evidence"] = {
            "structure": "Sube tu CV para recibir tu evaluación de estructura.",
            "coherence": "No evaluado.",
            "key_info": "No evaluado.",
            "clarity": "No evaluado.",
            "style": "No evaluado.",
        }
        cv_payload["corrections"] = ["Sube un CV con fechas y funciones."]
        cv_payload["reordering_suggestions"] = ["Ordena la experiencia cronológicamente."]
        cv_payload["feedback"] = "Añade un documento para completar tu diagnóstico."

    cv_payload["feedback"] = cv_payload.get("feedback") or "CV procesado."
    cv_payload["candidate"] = full_name
    contact = cv_payload.get("contact") if isinstance(cv_payload.get("contact"), dict) else {}
    if not contact: contact = {}
    if not contact.get("emails") and candidate_data.get("email"): contact["emails"] = [candidate_data.get("email")]
    if not contact.get("phones") and candidate_data.get("phone"): contact["phones"] = [candidate_data.get("phone")]
    if not contact.get("location") and candidate_data.get("location"): contact["location"] = candidate_data.get("location")
    cv_payload["contact"] = contact

    def _stringify_list(items: Any) -> List[Dict[str, Any]]:
        if not items: return []
        out: List[Dict[str, Any]] = []
        for it in items:
            if it is None: continue
            if isinstance(it, str):
                txt = it.strip()
                if txt: out.append({"title": txt, "detail": txt})
            elif isinstance(it, dict):
                candidate: Dict[str, Any] = {}
                for k, alias in (("title", "title"), ("cargo", "title"), ("company", "subtitle"), ("empresa", "subtitle"), ("period", "period"), ("description", "detail")):
                    if k in it and it.get(k): candidate.setdefault(alias, str(it.get(k)))
                if not candidate: candidate = {k: str(v) for k, v in it.items() if v is not None}
                out.append(candidate)
            else: out.append({"title": str(it), "detail": str(it)})
        return out

    cv_payload["cv_details"] = {
        "experience": _stringify_list(cv_payload.get("experience") or cv_payload.get("experience_detailed")),
        "education": _stringify_list(cv_payload.get("education") or cv_payload.get("education_detailed")),
        "languages": _stringify_list(cv_payload.get("languages")),
        "tools": _stringify_list(cv_payload.get("software") or cv_payload.get("skills")),
    }

    report = create_default_report(full_name, normalized_soft_skills, cv_payload, job_pref_payload)
    if cv_payload.get("cv_details"): report.cv_details = cv_payload.get("cv_details")
    else: report.cv_details = {}

    simple_summary = f"Perfil {level_label.lower()}."
    cv_summary_parts: list[str] = []
    if exp_count: cv_summary_parts.append(f"Experiencia: {exp_count} registros.")
    if edu_count: cv_summary_parts.append(f"Formación: {edu_count} registros.")
    if lang_count: cv_summary_parts.append(f"Idiomas detectados: {lang_count}.")
    if tools_count: cv_summary_parts.append(f"Herramientas: {tools_count}.")
    if cv_missing: cv_summary_parts.append("Añade un CV para análisis de métricas.")

    report.cv_analysis_summary = " ".join([simple_summary] + cv_summary_parts).strip() or "Evaluación lista."
    if "summary" in cv_payload: del cv_payload["summary"]

    personal = report.personal_data
    cv_contact = cv_payload.get("contact") if isinstance(cv_payload.get("contact"), dict) else {}
    personal.name = cv_contact.get("name") or cv_contact.get("nombre") or full_name
    if cv_contact.get("location"): personal.location = str(cv_contact.get("location"))
    elif candidate_data.get("location"): personal.location = str(candidate_data.get("location"))
    if cv_contact.get("emails"): personal.email = str(cv_contact.get("emails")[0])
    elif candidate_data.get("email"): personal.email = str(candidate_data.get("email"))
    if cv_contact.get("phones"): personal.phone = str(cv_contact.get("phones")[0])
    elif candidate_data.get("phone"): personal.phone = str(candidate_data.get("phone"))
    has_cert = candidate_data.get("hasDisabilityCertificate")
    if has_cert is None: has_cert = job_pref_payload.get("hasDisabilityCert")
    if has_cert is not None: personal.disability_certificate = "Sí" if has_cert else "No"
    report.personal_data = personal

    if normalized_soft_skills:
        report.soft_skills = normalized_soft_skills
        report.strengths = [s["skill"] for s in normalized_soft_skills if s.get("skill")]

    report.employability_score = safe_score

    if cv_missing:
        try:
            report.improvement_areas.insert(0, ImprovementArea(area="Subir CV", reason="Datos ausentes", suggested_action="Añade tu PDF."))
        except Exception: pass

    games_list: List[str] = []
    for game in completed_games or []:
        if isinstance(game, dict):
            name = game.get("name") or game.get("title")
            if name: games_list.append(str(name)); continue
        if game: games_list.append(str(game))
    report.completed_games = games_list

    preferred_platforms = job_pref_payload.get("preferred_platforms") or []
    if preferred_platforms: report.job_search_advice.recommended_platforms = [str(p) for p in preferred_platforms if p]

    work_mode = job_pref_payload.get("workMode")
    areas = job_pref_payload.get("areas") or []
    ideal_parts = []
    if work_mode: ideal_parts.append(f"Modalidad: {work_mode}")
    if areas: ideal_parts.append("Sectores: " + ", ".join(str(a) for a in areas if a))
    if ideal_parts: report.ideal_work_environment = ". ".join(ideal_parts)

    report.final_message = f"{full_name}, nivel {safe_score}/100. Avanza con el plan."
    return report

def generar_informe(prompt: str | Dict[str, Any]) -> Dict[str, Any]:
    if prompt is None:
        fallback_report = create_default_report("Usuario", [], {}, {})
        fallback_report.profile_summary = "Faltan datos."
        return fallback_report.dict()

    if isinstance(prompt, dict):
        try:
            data: Dict[str, Any] = prompt
            full_name = str(data.get("fullName") or data.get("userId") or "Usuario").strip() or "Usuario"
            candidate_data = {"fullName": full_name, "email": data.get("email"), "phone": data.get("phone")}
            soft_skills_data = data.get("softSkills") or []
            return _generate_structured_response_from_data(candidate_data, soft_skills_data, {}, {}, 50, "Medio", []).dict()
        except Exception:
            prompt = json.dumps(prompt, ensure_ascii=False)

    try:
        m_name = re.search(r"(?im)^\s*Nombre\s*:\s*(.+?)\s*$", prompt)
        nombre = m_name.group(1).strip() if m_name else "Usuario"
        soft_list, soft_avg = _parse_soft_skills(prompt.splitlines())
        nivel = _score_to_level(soft_avg)
        candidate_data = {"fullName": nombre, "location": "No consta", "email": "No consta", "phone": "No especificado", "hasDisabilityCertificate": False}
        cv_data = {"rawText": prompt, "languages": []}
        job_preferences_data = {"desired_roles": [], "desired_sectors": []}
        modern_report = _generate_modern_report(candidate_data, soft_list, cv_data, job_preferences_data, soft_avg, nivel, [])
        if modern_report: return modern_report.dict()
    except Exception:
        pass

    return _generate_structured_response_from_data({"fullName": "Usuario"}, [], {}, {}, 50, "Medio", []).dict()