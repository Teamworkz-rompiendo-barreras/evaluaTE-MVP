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
    
    # Preparar diagnóstico del CV
    cv_diagnosis = {
        "structure_score": 1,
        "coherence_score": 1,
        "key_info_score": 1,
        "clarity_score": 1,
        "spelling_style_score": 1,
        "evidence": {
            "structure": "No hay información del CV para evaluar la estructura.",
            "coherence": "No hay información del CV para evaluar la coherencia.",
            "key_info": "No hay información del CV para evaluar la información clave.",
            "clarity": "No hay información del CV para evaluar la claridad.",
            "style": "No hay información del CV para evaluar la ortografía y estilo."
        },
        "corrections": [
            "Elaborar un CV estructurado y completo",
            "Incluir información clave y logros medibles",
            "Revisar ortografía y formato"
        ],
        "reordering_suggestions": [
            "Iniciar con resumen profesional",
            "Seguir con experiencia y formación",
            "Finalizar con habilidades y contacto"
        ]
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
    
    # Construir el informe completo
    report = {
        "resumen_ejecutivo": f"El informe analiza la empleabilidad de {personal_data['name']}, quien presenta un perfil {level.lower()} con puntuación {employability_score}/100. Se identifican fortalezas y áreas de mejora para potenciar el acceso al mercado laboral.",
        "employabilityScore": employability_score,
        "level": level,
        "recommendations": [
            "Prioriza 3 vacantes objetivo y adapta tu CV",
            "Refuerza tu perfil profesional",
            "Participa en formaciones de soft skills"
        ],
        "report": {
            "resumen_ejecutivo": f"El informe analiza la empleabilidad de {personal_data['name']}, quien presenta un perfil {level.lower()} con puntuación {employability_score}/100. Se identifican fortalezas y áreas de mejora para potenciar el acceso al mercado laboral.",
            "employabilityScore": employability_score,
            "level": level,
            "recommendations": [
                "Prioriza 3 vacantes objetivo y adapta tu CV",
                "Refuerza tu perfil profesional",
                "Participa en formaciones de soft skills"
            ]
        }
    }
    
    # Construir las recomendaciones completas
    recommendations = {
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
        "resumen_ejecutivo": f"El informe analiza la empleabilidad de {personal_data['name']}, quien presenta un perfil {level.lower()} con puntuación {employability_score}/100.",
        "analisis_perfil": profile_summary,
        "evaluacion_cv": f"Estructura {cv_diagnosis['structure_score']}/5, Coherencia {cv_diagnosis['coherence_score']}/5, Información clave {cv_diagnosis['key_info_score']}/5, Claridad {cv_diagnosis['clarity_score']}/5, Ortografía/estilo {cv_diagnosis['spelling_style_score']}/5",
        "profile_analysis": profile_summary,
        "strengths_analysis": "\n".join([f"- {s}" for s in strengths]),
        "improvement_areas": "\n".join([f"- {a}" for a in improvement_areas]),
        "cv_analysis": f"Estructura {cv_diagnosis['structure_score']}/5, Coherencia {cv_diagnosis['coherence_score']}/5, Información clave {cv_diagnosis['key_info_score']}/5, Claridad {cv_diagnosis['clarity_score']}/5, Ortografía/estilo {cv_diagnosis['spelling_style_score']}/5",
        "job_suggestions": "\n".join([f"- {r}" for r in suggested_roles]),
        "next_steps": action_plan,
        "resources": [{"name": tool["name"], "description": tool["description"], "url": tool["url"]} for category in useful_tools.values() for tool in category]
    }
    
    return {
        "report": report,
        "recommendations": recommendations,
        "employabilityScore": employability_score,
        "level": level,
        "summary": f"El informe analiza la empleabilidad de {personal_data['name']}, quien presenta un perfil {level.lower()} con puntuación {employability_score}/100.",
        "createdAt": "2025-08-23T10:58:09.926249"
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

    # Si por error llega un dict (no debería, pero lo soportamos)
    if isinstance(prompt, dict):
        # Intentamos serializarlo y continuar, para mantener una salida homogénea.
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
