#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
deterministic_report.py

Generador de informes de empleabilidad SIN IA generativa: construye el mismo
contrato de datos que el pipeline de Gemini (ver `backend/new_report_schema.py`
-- Chunk1Base + Chunk2Competencias + Chunk3Accion) usando únicamente:

- Heurísticas deterministas sobre el CV (`backend/cv_structure_analyzer.py`:
  regex + puntuación por reglas, sin LLM).
- Los resultados estructurados de los minijuegos (`softSkills`).
- Las preferencias laborales indicadas por el candidato.

Es el motor usado cuando `ENABLE_AI_REPORT` está desactivado (por defecto) o
cuando el intento de IA falla, para garantizar que el informe SIEMPRE se
genera, al instante, sin depender de cuotas ni disponibilidad de terceros.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

try:
    from backend.cv_structure_analyzer import (
        analyze_cv_structure_from_bytes,
        extract_contact_info,
        SECTION_PATTERNS,
    )
except ImportError:
    from cv_structure_analyzer import (
        analyze_cv_structure_from_bytes,
        extract_contact_info,
        SECTION_PATTERNS,
    )

_ANY_SECTION_HEADER_RE = re.compile(
    "|".join(f"(?:{pat})" for pat in SECTION_PATTERNS.values()), re.IGNORECASE
)

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {
    "español": "Español", "castellano": "Español",
    "inglés": "Inglés", "ingles": "Inglés",
    "francés": "Francés", "frances": "Francés",
    "alemán": "Alemán", "aleman": "Alemán",
    "portugués": "Portugués", "portugues": "Portugués",
    "italiano": "Italiano",
    "catalán": "Catalán", "catalan": "Catalán",
    "euskera": "Euskera", "gallego": "Gallego",
    "chino": "Chino", "mandarín": "Chino", "mandarin": "Chino",
    "árabe": "Árabe", "arabe": "Árabe",
}

LEVEL_PATTERN = re.compile(
    r"\b(nativ[oa]|c2|c1|b2|b1|a2|a1|fluid[oa]|avanzad[oa]|intermedi[oa]|básic[oa]|basic[oa]|alto|medio|bajo)\b",
    re.IGNORECASE,
)

TOOL_KEYWORDS = [
    "Excel", "Word", "PowerPoint", "Outlook", "Access", "Google Sheets", "Google Docs",
    "Photoshop", "Illustrator", "InDesign", "Premiere", "After Effects", "Figma", "Canva",
    "AutoCAD", "SolidWorks", "SAP", "Salesforce", "CRM", "WordPress", "Shopify",
    "Python", "Java", "JavaScript", "SQL", "HTML", "CSS", "React",
    "Power BI", "Tableau", "QuickBooks", "Contaplus", "Sage",
    "Zendesk", "HubSpot", "Mailchimp", "SEO", "Google Analytics", "Google Ads",
    "TPV", "PRL", "Manipulador de alimentos", "Carnet de conducir", "Carretilla elevadora",
]

WORK_MODE_TEXT = {
    "remoto": "entornos 100% remotos, con buena conexión a internet y autonomía para organizar el propio tiempo",
    "presencial": "entornos presenciales, con contacto directo con el equipo y rutinas estructuradas",
    "híbrido": "un esquema híbrido que combine trabajo presencial y remoto según la tarea",
    "hibrido": "un esquema híbrido que combine trabajo presencial y remoto según la tarea",
}


def _detect_languages(text: str) -> List[str]:
    if not text:
        return []
    found: Dict[str, str] = {}
    for alias, canon in LANGUAGE_NAMES.items():
        if canon in found:
            continue
        m = re.search(rf"\b{re.escape(alias)}\b", text, re.IGNORECASE)
        if not m:
            continue
        # El nivel suele ir DESPUÉS del idioma dentro del mismo fragmento
        # ("Inglés B2", "Francés básico") -- se acota al mismo trozo (hasta
        # la siguiente coma/salto de línea/punto) para no capturar el nivel
        # de un idioma distinto mencionado justo antes en la misma frase.
        tail = text[m.end(): m.end() + 40]
        stop = re.search(r"[,\n;.]", tail)
        forward_window = tail[: stop.start()] if stop else tail
        level_m = LEVEL_PATTERN.search(forward_window)
        found[canon] = f"{canon} ({level_m.group(0).capitalize()})" if level_m else canon
    return list(found.values())[:6]


def _detect_tools(text: str) -> List[str]:
    if not text:
        return []
    found = []
    for tool in TOOL_KEYWORDS:
        if re.search(rf"\b{re.escape(tool)}\b", text, re.IGNORECASE):
            found.append(tool)
    return found[:12]


def _lines_from_section(sections: Dict[str, Any], key: str, limit: int = 6) -> List[str]:
    block = sections.get(key)
    if not block:
        return []
    raw_lines = str(block).splitlines()
    # Descarta la primera línea si es solo el encabezado de la sección (p.ej. "EXPERIENCIA")
    if raw_lines and len(raw_lines[0].split()) <= 3:
        raw_lines = raw_lines[1:]

    lines: List[str] = []
    for ln in raw_lines:
        clean = ln.strip(" \t•-·")
        if len(clean) <= 3:
            continue
        # El bloque se extrae hasta el siguiente salto doble; si el PDF no
        # separa secciones con línea en blanco, cortar en cuanto aparezca
        # el encabezado de OTRA sección para no arrastrar su contenido.
        if _ANY_SECTION_HEADER_RE.match(clean):
            break
        lines.append(clean)
    return lines[:limit]


def _tier_label(score: int) -> str:
    if score >= 80:
        return "Alto"
    if score >= 55:
        return "Medio"
    return "Bajo"


def _build_analisis_cv(review: Dict[str, Any], text: str, sections: Dict[str, Any]) -> Dict[str, Any]:
    scores = review.get("scores", {}) or {}
    fmt = scores.get("format", {}) or {}
    cla = scores.get("clarity", {}) or {}
    coh = scores.get("coherence", {}) or {}
    key = scores.get("key_information", {}) or {}
    spe = scores.get("spelling", {}) or {}

    valoraciones = {
        "formato": int(fmt.get("stars", 3) or 3),
        "claridad": int(cla.get("stars", 3) or 3),
        "coherencia": int(coh.get("stars", 3) or 3),
        "info_clave": int(key.get("stars", 3) or 3),
        "ortografia": int(spe.get("stars", 3) or 3),
    }

    dim_labels = {
        "formato": ("estructura y formato", fmt),
        "claridad": ("claridad de redacción", cla),
        "coherencia": ("coherencia cronológica", coh),
        "info_clave": ("información clave aportada", key),
        "ortografia": ("ortografía y estilo", spe),
    }

    puntos_fuertes: List[str] = []
    aspectos_mejorar: List[str] = []
    for dim, (label, data) in dim_labels.items():
        stars = valoraciones[dim]
        expl = str(data.get("explanation") or "").strip()
        if stars >= 4:
            puntos_fuertes.append(f"Buen nivel de {label}. {expl}".strip())
        elif stars <= 2:
            aspectos_mejorar.append(f"Necesita reforzar {label}. {expl}".strip())

    if not puntos_fuertes:
        puntos_fuertes.append(
            "El CV cubre la información básica esperada para un primer diagnóstico automático."
        )
    if not aspectos_mejorar:
        aspectos_mejorar.append(
            "No se han detectado carencias críticas en el análisis automático; aun así, una revisión manual siempre suma."
        )

    experiencia = _lines_from_section(sections, "experience") or [
        "No se detectó una sección de experiencia claramente encabezada en el documento."
    ]
    formacion = _lines_from_section(sections, "education") or [
        "No se detectó una sección de formación claramente encabezada en el documento."
    ]
    idiomas = _detect_languages(text) or ["No se especifican idiomas en el documento."]
    software = _detect_tools(text) or ["No se detectaron herramientas o software específicos mencionados textualmente."]

    ats_score = int(round((fmt.get("score", 60) or 60) * 0.4 + (key.get("score", 60) or 60) * 0.6))
    ats_score = max(0, min(100, ats_score))
    email_found = bool(re.search(r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}", text or ""))
    ats_explicacion = (
        "Compatibilidad estimada con lectores automáticos (ATS) a partir de la cobertura de secciones "
        f"({'contacto detectado en el documento' if email_found else 'sin contacto claro detectado en el documento'}) "
        "y del formato general. Es una estimación heurística basada en reglas, no una lectura semántica del contenido."
    )

    return {
        "resumen": (
            "Análisis automático (sin IA) generado a partir de la estructura del documento: "
            f"formato {valoraciones['formato']}/5, claridad {valoraciones['claridad']}/5, "
            f"coherencia {valoraciones['coherencia']}/5, información clave {valoraciones['info_clave']}/5 "
            f"y ortografía {valoraciones['ortografia']}/5."
        ),
        "experiencia": experiencia,
        "formacion": formacion,
        "idiomas": idiomas,
        "software": software,
        "valoraciones": valoraciones,
        "puntos_fuertes": puntos_fuertes,
        "aspectos_mejorar": aspectos_mejorar,
        "ats_compatibilidad": ats_score,
        "ats_explicacion": ats_explicacion,
    }


def _build_competencias(soft_skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    competencias = []
    for s in soft_skills:
        nombre = str(s.get("skill") or "Competencia").strip()
        try:
            score = int(round(float(s.get("score", 0) or 0)))
        except (TypeError, ValueError):
            score = 0
        score = max(0, min(100, score))
        nivel = str(s.get("level") or _tier_label(score)).capitalize()
        competencias.append({
            "nombre": nombre,
            "puntuacion": score,
            "nivel": nivel,
            "explicacion": (
                f"En las dinámicas evaluativas de EvalúaTE obtuvo una puntuación de {score}/100 en {nombre.lower()}, "
                f"un nivel {nivel.lower()}. Esto se traduce en el día a día laboral en cómo afronta situaciones que "
                "requieren esta competencia, y aporta valor especialmente en entornos donde se pone a prueba."
            ),
        })

    perfil_competencias = (
        [{"categoria": "Competencias evaluadas en los minijuegos", "competencias": competencias}]
        if competencias else []
    )

    ranked = sorted(competencias, key=lambda c: c["puntuacion"], reverse=True)
    fuertes = [c for c in ranked if c["puntuacion"] >= 70][:3] or ranked[:1]
    debiles = [c for c in ranked if c["puntuacion"] < 60][-3:] or ranked[-1:]

    fortalezas_principales = [
        {
            "nombre": c["nombre"].upper(),
            "explicacion_practica": (
                f"Con {c['puntuacion']}/100 en las pruebas de {c['nombre'].lower()}, este es uno de los puntos más "
                "sólidos del perfil evaluado. Es una fortaleza demostrada con datos de comportamiento, no solo "
                "autopercibida, y conviene mencionarla activamente en procesos de selección."
            ),
        }
        for c in fuertes
    ]

    areas_mejora = [
        {
            "nombre": c["nombre"].upper(),
            "porque_afecta": (
                f"La puntuación de {c['puntuacion']}/100 en {c['nombre'].lower()} indica un margen de mejora real. "
                "Si el objetivo profesional exige esta competencia de forma frecuente, puede ser motivo de descarte "
                "en procesos de selección exigentes si no se trabaja de forma activa."
            ),
            "como_mejorar": "PLAN DE CAPACITACIÓN INMEDIATA:",
            "acciones_concretas": [
                f"Buscar un curso corto o recurso gratuito centrado específicamente en {c['nombre'].lower()}.",
                "Practicar la competencia en situaciones reales o simuladas (voluntariado, proyectos personales, "
                "rol-play) al menos una vez por semana.",
                "Pedir feedback explícito sobre esta competencia a un mentor, formador o responsable de Teamworkz.",
            ],
        }
        for c in debiles
    ]

    resultados_juegos = [
        {
            "juego": c["nombre"],
            "que_mide": f"DIMENSIÓN: {c['nombre']} — capacidad evaluada mediante escenarios simulados dentro de EvalúaTE.",
            "resultado": f"{c['puntuacion']}/100 ({c['nivel']})",
            "interpretacion": (
                f"Mapeo Psicométrico: una puntuación de {c['puntuacion']}/100 sitúa al candidato en un nivel "
                f"{c['nivel'].lower()} en esta dimensión, consistente con su comportamiento durante la dinámica evaluada."
            ),
            "aplicacion_entrevista": (
                "Transferencia a Entrevista: puede argumentar este resultado citando ejemplos concretos de su "
                f"experiencia donde haya demostrado {c['nombre'].lower()}, respaldando la puntuación obtenida."
            ),
        }
        for c in competencias
    ]

    return {
        "perfil_competencias": perfil_competencias,
        "fortalezas_principales": fortalezas_principales,
        "areas_mejora": areas_mejora,
        "resultados_juegos": resultados_juegos,
    }


def _build_accion(job_prefs: Dict[str, Any], puntuacion_global: int) -> Dict[str, Any]:
    areas = [a for a in (job_prefs.get("areas") or []) if isinstance(a, str) and a.strip()] or ["su área profesional de interés"]
    needs = [n for n in (job_prefs.get("needs") or []) if isinstance(n, str) and n.strip()]
    work_mode = str(job_prefs.get("workMode") or job_prefs.get("work_mode") or "").lower()

    entornos_ideales = [
        f"Puestos dentro de {areas[0]}, alineados con el interés declarado por el candidato.",
        WORK_MODE_TEXT.get(work_mode, "un entorno de trabajo flexible que se pueda adaptar según necesidad").capitalize(),
    ]
    if needs:
        entornos_ideales.append("Entornos que contemplen: " + "; ".join(needs[:3]) + ".")
    entornos_ideales.append(
        "Equipos con procesos claros, feedback frecuente y acompañamiento durante la incorporación."
    )

    roles_recomendados = []
    for area in areas[:2]:
        demanda = "ALTA" if puntuacion_global >= 70 else "MEDIA"
        roles_recomendados.append({
            "titulo": f"Perfil junior/operativo en {area}",
            "nivel": "Junior" if puntuacion_global < 70 else "Mid-level",
            "modalidad": work_mode.capitalize() if work_mode else "A definir según la oferta",
            "por_que_encaja": (
                f"Justificación de encaje temporal: el candidato ha mostrado interés explícito en {area} y una "
                f"puntuación global de empleabilidad de {puntuacion_global}/100 en la evaluación de EvalúaTE, "
                "un punto de partida razonable para posiciones de entrada en este ámbito."
            ),
            "demanda_laboral": demanda,
        })

    dias_30 = [
        "Actualizar y pulir el CV incorporando los puntos fuertes detectados en este informe.",
        f"Enviar activamente candidaturas a ofertas relacionadas con {areas[0]}, al menos 3-5 por semana.",
        "Preparar un guion breve de 2-3 minutos para presentarse en entrevistas, apoyado en los resultados de este informe.",
    ]
    dias_60 = [
        "Completar una formación corta o certificación gratuita relacionada con las áreas de mejora detectadas.",
        "Actualizar el perfil de LinkedIn (o portfolio, según el sector) con la experiencia y competencias reales.",
        "Contactar activamente con la red de Teamworkz y otras entidades de intermediación laboral especializadas.",
    ]
    dias_90 = [
        "Realizar al menos una simulación de entrevista con feedback de un tercero.",
        "Revisar y ajustar la estrategia de búsqueda según los resultados obtenidos hasta el momento.",
        "Consolidar los aprendizajes del proceso en un documento de seguimiento personal.",
    ]

    estrategia_busqueda = [
        f"Priorizar portales y empresas especializadas en {areas[0]} y en empleo inclusivo/con apoyo.",
        "Activar la red de contactos personal y profesional explicando de forma clara el objetivo laboral.",
        "Hacer seguimiento de cada candidatura enviada (fecha, empresa, estado) para no perder oportunidades.",
        "Adaptar el CV y la carta de presentación a cada oferta relevante, destacando las competencias mejor puntuadas.",
        "Participar en ferias de empleo, jornadas de intermediación laboral o eventos del sector de interés.",
    ]

    herramientas_recomendadas = [
        {"nombre": "LinkedIn", "para_que_sirve": "Visibilidad profesional, red de contactos y acceso a ofertas del sector."},
        {"nombre": "Portales de empleo especializados", "para_que_sirve": "Búsqueda activa y postulación a ofertas relacionadas con el área de interés."},
        {"nombre": "Canva", "para_que_sirve": "Diseñar un CV visualmente claro y profesional sin necesidad de conocimientos de diseño."},
    ]

    recomendaciones_personalizadas = [
        f"Enfocar la búsqueda inicial en {areas[0]}, donde el candidato ha mostrado mayor interés.",
        "Apoyarse en las fortalezas detectadas en la evaluación al preparar entrevistas.",
        "Trabajar de forma activa, aunque progresiva, las áreas de mejora señaladas en este informe.",
        "Mantener actualizado el CV con logros concretos y medibles a medida que se generen.",
        "Pedir apoyo a Teamworkz u otras entidades de intermediación si el proceso se estanca más de 4-6 semanas.",
    ]

    recursos_adicionales = [
        {
            "nombre": f"Formación online gratuita relacionada con {areas[0]}",
            "tipo": "FORMACIÓN HABILITANTE",
            "descripcion": f"Refuerza la empleabilidad en {areas[0]}, el área de mayor interés declarada por el candidato.",
        },
        {
            "nombre": "Curso corto de preparación de entrevistas de trabajo",
            "tipo": "DESARROLLO DE HABILIDAD ESPECÍFICA",
            "descripcion": "Ayuda a transformar los resultados de este informe en argumentos sólidos durante un proceso de selección.",
        },
    ]

    if puntuacion_global >= 70:
        nivel_txt = "un nivel de empleabilidad sólido"
    elif puntuacion_global >= 45:
        nivel_txt = "un nivel de empleabilidad en desarrollo"
    else:
        nivel_txt = "un punto de partida que requiere trabajo constante"

    mensaje_final = (
        "Este informe se ha generado de forma 100% automática, sin intervención de un modelo de IA generativa, "
        "a partir de tus respuestas, tus resultados en los minijuegos y un análisis heurístico de tu CV. "
        f"Con una puntuación global de {puntuacion_global}/100, el perfil evaluado muestra {nivel_txt}. "
        "Usa las fortalezas señaladas como argumento en tus candidaturas y trabaja las áreas de mejora de forma "
        "constante: la empleabilidad es un proceso, no un veredicto único."
    )

    return {
        "entornos_ideales": entornos_ideales[:4],
        "roles_recomendados": roles_recomendados,
        "plan_accion": {"dias_30": dias_30, "dias_60": dias_60, "dias_90": dias_90},
        "estrategia_busqueda": estrategia_busqueda,
        "herramientas_recomendadas": herramientas_recomendadas,
        "recomendaciones_personalizadas": recomendaciones_personalizadas,
        "recursos_adicionales": recursos_adicionales,
        "mensaje_final": mensaje_final,
    }


def generate_deterministic_report(
    pdf_bytes: bytes,
    games_data: Dict[str, Any],
    prefs_data: Dict[str, Any],
    employability_score: int,
    candidate_name: str = "Candidato",
) -> Dict[str, Any]:
    """Genera el informe completo SIN IA: heurísticas deterministas sobre el
    CV (regex + puntuación por reglas) + datos estructurados de los
    minijuegos y las preferencias. Nunca lanza excepción, nunca depende de
    una API externa, y siempre devuelve una estructura completa."""
    try:
        cv_result = analyze_cv_structure_from_bytes(pdf_bytes or b"")
    except Exception as e:
        logger.warning(f"Fallo heurístico analizando el CV, se usa revisión neutra: {e}")
        cv_result = {"review": {"scores": {}}, "text": "", "sections": {}}

    review = cv_result.get("review") or {}
    text = cv_result.get("text") or ""
    sections = cv_result.get("sections") or {}

    contacto = extract_contact_info(text) if text else {}

    job_prefs = prefs_data if isinstance(prefs_data, dict) else {}

    soft_skills_raw = games_data.get("softSkills") if isinstance(games_data, dict) else None
    soft_skills = [s for s in (soft_skills_raw or []) if isinstance(s, dict) and s.get("skill")]
    if not soft_skills:
        soft_skills = [{"skill": "Adaptabilidad", "score": 60, "level": "Medio"}]

    datos_personales = {
        "Nombre": str(candidate_name or contacto.get("nombre") or "Candidato/a"),
        "Ubicacion": str(job_prefs.get("location") or "No especificada"),
        "Email": str(job_prefs.get("email") or contacto.get("email") or "No especificado"),
        "Telefono": str(job_prefs.get("whatsapp") or job_prefs.get("phone") or contacto.get("telefono") or "No especificado"),
        "LinkedIn": str(contacto.get("linkedin") or "No especificado"),
    }

    analisis_cv = _build_analisis_cv(review, text, sections)
    competencias_info = _build_competencias(soft_skills)

    try:
        puntuacion_global = int(employability_score)
    except (TypeError, ValueError):
        puntuacion_global = 60
    puntuacion_global = max(0, min(100, puntuacion_global))

    interpretacion_global = (
        f"Puntuación global de {puntuacion_global}/100, calculada a partir del promedio de las competencias "
        "evaluadas en los minijuegos (ver detalle en 'Resultados de las Evaluaciones'). Es un indicador "
        "orientativo, no un veredicto definitivo sobre la empleabilidad del candidato."
    )
    resumen_ejecutivo = (
        f"Informe generado automáticamente (sin IA generativa) para {datos_personales['Nombre']}. "
        "Combina el análisis heurístico del CV aportado con los resultados de los minijuegos de EvalúaTE "
        "y las preferencias laborales indicadas, para ofrecer una fotografía objetiva y reproducible del "
        "perfil evaluado, sin depender de servicios externos de inteligencia artificial."
    )

    accion = _build_accion(job_prefs, puntuacion_global)

    report = {
        "datos_personales": datos_personales,
        "resumen_ejecutivo": resumen_ejecutivo,
        "puntuacion_global": puntuacion_global,
        "interpretacion_global": interpretacion_global,
        "analisis_cv": analisis_cv,
        "perfil_competencias": competencias_info["perfil_competencias"],
        "fortalezas_principales": competencias_info["fortalezas_principales"],
        "areas_mejora": competencias_info["areas_mejora"],
        "resultados_juegos": competencias_info["resultados_juegos"],
        **accion,
        "generado_sin_ia": True,
    }
    return report
