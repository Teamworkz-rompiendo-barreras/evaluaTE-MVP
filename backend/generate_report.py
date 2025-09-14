# generate_report.py
# -*- coding: utf-8 -*-
"""
Generador de informe IA _determinista_ y robusto a partir del prompt de back-end.
No requiere claves ni servicios externos. Siempre devuelve un dict con:
{
  "report": {...},
  "recommendations": [...],
  "level": "Bajo|Medio|Alto",
  "employabilityScore": int
}
"""

from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Tuple

# Importar la nueva configuración de prompts
try:
    from prompt_config import PromptConfig
except ImportError:
    PromptConfig = None

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

def _generate_modern_report(candidate_data: dict, soft_skills_data: list, cv_data: dict, 
                           job_preferences_data: dict, employability_score: int, level: str, 
                           completed_games: list) -> Dict[str, Any]:
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
                                          completed_games: list) -> Dict[str, Any]:
    """
    Genera una respuesta estructurada basada en los datos disponibles
    """
    # Preparar datos personales
    personal_data = {
        "name": candidate_data.get("fullName", "No consta"),
        "location": candidate_data.get("location", "No consta"),
        "email": candidate_data.get("email", "No consta"),
        "phone": candidate_data.get("phone", "No especificado"),
        "disability_certificate": "Sí" if candidate_data.get("hasDisabilityCertificate") else "No"
    }
    
    # Preparar resumen del perfil
    profile_summary = f"Perfil {level.lower()} con puntuación de empleabilidad {employability_score}/100. "
    if soft_skills_data:
        avg_score = sum(s.get("score", 0) for s in soft_skills_data) / len(soft_skills_data)
        profile_summary += f"Soft skills evaluadas con puntuación media de {int(avg_score)}/100."
    
    # Preparar resumen del CV
    cv_summary = "La información del CV no está disponible debido a limitaciones técnicas en la extracción de datos."
    if cv_data.get("rawText"):
        cv_summary = "CV analizado con información disponible para evaluación."
    
    # Preparar fortalezas
    strengths = []
    if soft_skills_data:
        for skill in soft_skills_data:
            if skill.get("score", 0) >= 70:
                strengths.append(f"{skill.get('skill', '')} - Puntuación alta ({skill.get('score')}/100)")
    
    if not strengths:
        strengths = ["Potencial de desarrollo profesional", "Disposición para el aprendizaje", "Adaptabilidad"]
    
    # Preparar áreas de mejora
    improvement_areas = []
    if soft_skills_data:
        for skill in soft_skills_data:
            if skill.get("score", 0) < 50:
                improvement_areas.append(f"{skill.get('skill', '')} - Oportunidad de mejora ({skill.get('score')}/100)")
    
    if not improvement_areas:
        improvement_areas = ["Desarrollo de competencias específicas", "Elaboración del CV", "Definición de objetivos profesionales"]
    
    # Preparar diagnóstico del CV - usar datos reales si están disponibles
    cv_analysis_data = cv_data.get("analysis_json", {}) if isinstance(cv_data, dict) else {}
    
    # Usar datos reales del análisis del CV si están disponibles, sino usar valores por defecto
    cv_diagnosis = {
        "structure_score": cv_analysis_data.get("structure_score", 3),
        "coherence_score": cv_analysis_data.get("coherence_score", 2),
        "key_info_score": cv_analysis_data.get("key_info_score", 2),
        "clarity_score": cv_analysis_data.get("clarity_score", 2),
        "spelling_style_score": cv_analysis_data.get("spelling_style_score", 3),
        "evidence": cv_analysis_data.get("evidence", {
            "structure": "El CV contiene secciones básicas (experiencia, educación, idiomas, herramientas, contacto), pero no se detalla el orden ni la jerarquía de la información.",
            "coherence": "Falta de detalles sobre fechas, empresas y funciones específicas; no se observa consistencia en la presentación.",
            "key_info": "No se incluyen logros cuantificables, KPIs ni enlaces a perfiles profesionales.",
            "clarity": "Ausencia de bullets claros y verbos de acción; la información es general y poco específica.",
            "style": "No se pueden evaluar tildes ni formato debido a la falta de texto raw, pero la estructura detectada es básica."
        }),
        "corrections": cv_analysis_data.get("corrections", [
            "Añadir logros cuantificables y KPIs en cada experiencia.",
            "Incluir enlaces a LinkedIn u otros perfiles profesionales.",
            "Homogeneizar el formato de fechas y ubicaciones.",
            "Utilizar bullets y verbos de acción claros.",
            "Revisar ortografía y formato general."
        ]),
        "reordering_suggestions": cv_analysis_data.get("reordering_suggestions", [
            "Colocar el perfil profesional al inicio.",
            "Agrupar la experiencia profesional antes de la formación.",
            "Incluir una sección específica de habilidades técnicas y soft skills."
        ]),
        "observations": cv_analysis_data.get("observations", [
            "Estructura: El CV contiene secciones básicas (experiencia, educación, idiomas, herramientas, contacto), pero no se detalla el orden ni la jerarquía de la información.",
            "Claridad: Ausencia de bullets claros y verbos de acción; la información es general y poco específica.",
            "Coherencia: Falta de detalles sobre fechas, empresas y funciones específicas; no se observa consistencia en la presentación.",
            "Información clave: No se incluyen logros cuantificables, KPIs ni enlaces a perfiles profesionales.",
            "Ortografía y estilo: No se pueden evaluar tildes ni formato debido a la falta de texto raw, pero la estructura detectada es básica."
        ])
    }
    
    # Preparar roles sugeridos
    suggested_roles = [
        "Asistente administrativo/a - Rol de entrada con potencial de desarrollo (Junior, Remoto: Sí)",
        "Auxiliar de soporte técnico - Posición para desarrollar competencias tecnológicas (Junior, Remoto: Sí)",
        "Operario/a de servicios generales - Para perfiles en desarrollo (Junior, Remoto: No)"
    ]
    
    # Preparar plan de acción
    action_plan = {
        "corto_plazo": [
            "Elaborar CV actualizado en los próximos 15 días",
            "Definir objetivos profesionales en 2 semanas",
            "Inscribirse en curso de soft skills en 30 días"
        ],
        "medio_plazo": [
            "Actualizar CV para cada oferta en 2 meses",
            "Participar en networking en 3 meses",
            "Solicitar feedback profesional"
        ],
        "largo_plazo": [
            "Desarrollar competencias técnicas en 6 meses",
            "Explorar oportunidades de prácticas",
            "Mantener aprendizaje continuo"
        ]
    }
    
    # Preparar consejos de búsqueda
    job_search_advice = {
        "cv_optimization": [
            "Usar formato claro y profesional",
            "Incluir logros cuantificables",
            "Revisar ortografía antes de enviar"
        ],
        "letters_portfolio": "Preparar carta de presentación adaptable",
        "recommended_platforms": ["InfoJobs", "LinkedIn", "Indeed", "Portal Empléate"],
        "networking": "Participar en grupos profesionales online",
        "interview_tips": "Preparar respuestas frecuentes y practicar presentación"
    }
    
    # Preparar herramientas útiles
    useful_tools = {
        "productividad": [{"name": "Trello", "description": "", "url": ""}, {"name": "Google Calendar", "description": "", "url": ""}],
        "busqueda": [{"name": "LinkedIn", "description": "", "url": ""}, {"name": "InfoJobs", "description": "", "url": ""}],
        "aprendizaje": [{"name": "Coursera", "description": "", "url": ""}, {"name": "edX", "description": "", "url": ""}, {"name": "Google Actívate", "description": "", "url": ""}],
        "accesibilidad": [{"name": "Microsoft Immersive Reader", "description": "", "url": ""}, {"name": "Grammarly", "description": "", "url": ""}]
    }

    # -----------------------------
    # Normalización para UI (cv_analysis)
    # -----------------------------

    def _fmt_dates(start: str | None, end: str | None) -> str:
        start = (start or "").strip()
        end = (end or "").strip()
        if start and end:
            return f"{start} – {end}"
        return start or end or ""

    def _map_experience_for_ui(items: list) -> list:
        out = []
        for it in items or []:
            if not isinstance(it, dict):
                # admitir cadenas sueltas
                out.append({"title": str(it), "company": "", "dates": "", "summary": ""})
                continue
            title = it.get("title") or it.get("cargo") or it.get("position") or "Experiencia"
            company = it.get("company") or it.get("empresa") or it.get("organization") or it.get("organisation") or ""
            dates = _fmt_dates(it.get("start_date") or it.get("fecha_inicio"), it.get("end_date") or it.get("fecha_fin"))
            # construir resumen
            partes = []
            desc = it.get("description") or it.get("descripcion")
            if isinstance(desc, str) and desc.strip():
                partes.append(desc.strip())
            for key in ("responsabilidades", "logros", "tecnologias"):
                val = it.get(key)
                if isinstance(val, list) and val:
                    partes.append("; ".join(str(x) for x in val if x))
            summary = "; ".join([p for p in partes if p])
            out.append({"title": title, "company": company, "dates": dates, "summary": summary})
        return out

    def _map_education_for_ui(items: list) -> list:
        out = []
        for it in items or []:
            if not isinstance(it, dict):
                out.append({"degree": str(it), "center": "", "year": ""})
                continue
            degree = it.get("degree") or it.get("titulo") or it.get("title") or "Formación"
            center = it.get("institution") or it.get("institucion") or it.get("school") or ""
            year = it.get("end_date") or it.get("fecha_fin") or it.get("start_date") or it.get("fecha_inicio") or ""
            out.append({"degree": degree, "center": center, "year": year})
        return out
    
    # Construir objeto report con el shape esperado por el frontend
    report_obj: Dict[str, Any] = {
        "personal_data": personal_data,
        "resumen_ejecutivo": f"El informe analiza la empleabilidad de {personal_data['name']}, quien presenta un perfil {level.lower()} con puntuación {employability_score}/100. Se identifican fortalezas y áreas de mejora para potenciar el acceso al mercado laboral.",
        "soft_skills": soft_skills_data,
        "cv_analysis": {
            # Adaptado al formato de la UI
            "experience": _map_experience_for_ui(cv_data.get("experience") or []),
            "education": _map_education_for_ui(cv_data.get("education") or []),
            "languages": cv_data.get("languages") or [],
            "software": cv_data.get("software") or [],
            "contact": cv_data.get("contact") or {},
            # Estrellas opcionales para el bloque visual
            "stars": {
                "formato": cv_diagnosis.get("structure_score"),
                "claridad": cv_diagnosis.get("clarity_score"),
                "coherencia": cv_diagnosis.get("coherence_score"),
                "informacion_clave": cv_diagnosis.get("key_info_score"),
                "ortografia": cv_diagnosis.get("spelling_style_score"),
            },
            # Incluir analysis_json completo para el frontend
            "analysis_json": {
                "structure_score": cv_diagnosis.get("structure_score"),
                "clarity_score": cv_diagnosis.get("clarity_score"),
                "coherence_score": cv_diagnosis.get("coherence_score"),
                "key_info_score": cv_diagnosis.get("key_info_score"),
                "spelling_style_score": cv_diagnosis.get("spelling_style_score"),
                "evidence": cv_diagnosis.get("evidence", {}),
                "corrections": cv_diagnosis.get("corrections", []),
                "reordering_suggestions": cv_diagnosis.get("reordering_suggestions", []),
                "observations": cv_diagnosis.get("observations", [])
            }
        },
        "improvement_areas": [
            {"area": a, "score": 0} for a in improvement_areas
        ],
        "environments": [
            "Entorno inclusivo y flexible",
            "Equipos con acompañamiento profesional",
        ],
        "suggested_roles": [
            {"role": "Asistente administrativo/a", "seniority": "Junior", "remote_viable": True, "reason": "perfil en desarrollo con potencial"},
            {"role": "Auxiliar de soporte", "seniority": "Junior", "remote_viable": True, "reason": "competencias transferibles"},
        ],
        "action_plan": {
            "short_term": action_plan.get("corto_plazo", []),
            "medium_term": action_plan.get("medio_plazo", []),
            "long_term": action_plan.get("largo_plazo", []),
        },
        "job_search_advice": {
            "tips": job_search_advice.get("cv_optimization", []),
            "ats_keywords": ["data entry", "calidad de datos", "Excel"],
        },
        "tools": {
            "productivity": ["Excel", "Google Sheets", "Notion/Airtable"],
            "job_search": ["LinkedIn", "Indeed"],
            "learning": ["Coursera", "Udemy"],
        },
        "completed_games": completed_games,
        "frase_final": "Cada paso en tu desarrollo profesional suma. Mantén una actitud proactiva y confía en tu potencial.",
    }

    return {
        "report": report_obj,
        "recommendations": {
            "datos_personales": personal_data,
            "resumen_perfil": profile_summary,
            "resumen_cv": cv_summary,
            "fortalezas_clave": strengths,
            "areas_mejora": improvement_areas,
            "diagnostico_cv": cv_diagnosis,
            "entornos_ideales": "Entorno inclusivo con acompañamiento profesional y flexibilidad",
            "roles_sugeridos": suggested_roles,
            "plan_accion": action_plan,
            "consejos_busqueda": job_search_advice,
            "herramientas_utiles": useful_tools,
            "juegos_completados": completed_games,
            "frase_final": "Cada paso en tu desarrollo profesional suma. Mantén una actitud proactiva y confía en tu potencial.",
        },
        "employabilityScore": employability_score,
        "level": level,
        "summary": f"El informe analiza la empleabilidad de {personal_data['name']}, quien presenta un perfil {level.lower()} con puntuación {employability_score}/100.",
    }

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
        # Fallback ultra seguro
        return {
            "report": {
                "resumen_ejecutivo": "No se recibió información suficiente.",
                "soft_skills": [],
                "cv_analizado": "Sin análisis.",
                "preferencias_laborales": "No especificadas.",
                "juegos_completados": [],
                "frase_final": "Define un objetivo profesional y comienza por acciones concretas la próxima semana.",
            },
            "recommendations": [],
            "level": "Bajo",
            "employabilityScore": 0,
        }

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
                job_preferences_data = {
                    "desired_roles": jp_raw.get("areas") or [],
                    "desired_sectors": [],
                    "work_mode": jp_raw.get("workMode") or jp_raw.get("work_mode") or "",
                }

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
            )
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
            return modern_report
            
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

    # Puntuación global basada en las soft skills
    employability = int(soft_avg)

    return {
        "report": report,
        "recommendations": recs,
        "level": nivel,
        "employabilityScore": employability,
    }
