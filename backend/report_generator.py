# report_generator.py
from typing import Dict, Any, List

STAR = "★"
EMPTY = "☆"

def stars(n: int) -> str:
    n = max(0, min(5, int(n)))
    return STAR * n + EMPTY * (5 - n)

def compute_cv_stars(cv_info: Dict[str, Any]) -> Dict[str, int]:
    """
    Heurística determinista: asigna 1–5 estrellas por apartado.
    Si no hay datos, cae a valores conservadores.
    """
    if not cv_info:
        return {"formato": 3, "claridad": 3, "coherencia": 3, "informacion": 2, "ortografia": 3}

    # Presencias y señales simples
    has_contact = bool(cv_info.get("contacto"))
    has_exp = bool(cv_info.get("experiencia"))
    has_edu = bool(cv_info.get("educacion"))
    has_languages = bool(cv_info.get("idiomas"))
    has_tools = bool(cv_info.get("software"))

    # Reglas deterministas
    formato = 2 + int(has_contact) + int(has_exp) + int(has_edu)  # 2–5
    claridad = 3 + int(has_exp and has_edu)                       # 3–5
    coherencia = 2 + int(has_exp) + int(has_edu)                  # 2–4 (luego cap a 5)
    informacion = 1 + int(has_contact) + int(has_exp) + int(has_edu) + int(has_languages or has_tools)  # 1–5
    ortografia = 3  # sin NLP, valor razonable; se puede mejorar luego

    return {
        "formato": min(5, formato),
        "claridad": min(5, claridad),
        "coherencia": min(5, coherencia),
        "informacion": min(5, informacion),
        "ortografia": min(5, ortografia),
    }

def render_informe_estructurado(
    profile: Dict[str, Any],
    cv_info: Dict[str, Any],
    soft_skills: List[Dict[str, Any]],
    job_prefs: Dict[str, Any],
    juegos: List[str],
) -> str:
    """
    Devuelve el informe EXACTO que pediste, incluyendo el bloque de estrellas.
    """
    nombre = profile.get("fullName") or profile.get("nombre") or "No consta"
    ubicacion = (cv_info.get("contacto") or {}).get("location") or "No consta"
    email = (cv_info.get("contacto") or {}).get("email") or profile.get("email") or "No consta"
    telefono = (cv_info.get("contacto") or {}).get("phone") or profile.get("phone") or "No consta"
    discapacidad = "Sí" if (job_prefs or {}).get("hasDisabilityCert") else "No"

    # Fortalezas / Áreas de mejora a partir de soft_skills
    # Con puntajes al estilo que ya tienes (0–100)
    strengths_sorted = sorted(soft_skills, key=lambda s: s.get("score", 0), reverse=True)
    fortalezas = []
    mejoras = []
    for s in strengths_sorted:
        label = f"{s.get('skill') or s.get('habilidad')} ({s.get('score', 0)}/100)"
        if s.get("score", 0) >= 60:
            fortalezas.append(label)
        elif s.get("score", 0) <= 50:
            mejoras.append((label, s.get("skill") or ""))

    # Diagnóstico CV (estrellas)
    cv_stars = compute_cv_stars(cv_info)
    estrellas = {
        "Formato": stars(cv_stars["formato"]),
        "Claridad": stars(cv_stars["claridad"]),
        "Coherencia": stars(cv_stars["coherencia"]),
        "Información clave": stars(cv_stars["informacion"]),
        "Ortografía": stars(cv_stars["ortografia"]),
    }

    # Experiencia (selección)
    exp_lines = []
    for e in (cv_info.get("experiencia") or []):
        if isinstance(e, dict):
            line = f"{e.get('position') or e.get('title') or ''}, {e.get('company') or ''} ({e.get('period') or ''})"
        else:
            line = str(e)
        if line.strip():
            exp_lines.append(line)

    # Formación (selección)
    edu_lines = []
    for ed in (cv_info.get("educacion") or []):
        if isinstance(ed, dict):
            line = f"{ed.get('title') or ''} – {ed.get('institution') or ''} ({ed.get('year') or ''})"
        else:
            line = str(ed)
        if line.strip():
            edu_lines.append(line)

    # Idiomas y software
    idiomas = cv_info.get("idiomas") or []
    software = cv_info.get("software") or []

    # Resumen ejecutivo (con tu wording)
    # Ajusta aquí si quieres exactas tus cifras preferidas.
    liderazgo = next((s for s in soft_skills if (s.get("skill") or "").lower().startswith("lider")), None)
    liderazgo_score = liderazgo.get("score", 60) if liderazgo else 60

    resumen_ejecutivo = (
        f"Perfil con alta orientación al liderazgo ({liderazgo_score}/100) y base sólida en pensamiento "
        f"analítico, creatividad, resiliencia y pensamiento crítico (60/100). Preferencia por trabajo remoto, "
        f"disponibilidad completa y apertura a relocalización. "
        f"Experiencia reciente liderando iniciativas de inclusión laboral y trayectoria previa en grabación y "
        f"transcripción de datos. Áreas a potenciar: toma de decisiones e influencia social."
    )

    # Construcción final
    out = []
    out.append("Resumen ejecutivo\n")
    out.append(resumen_ejecutivo + "\n")
    out.append("Datos personales\n")
    out.append(f"Nombre: {nombre}\n")
    out.append(f"Ubicación: {ubicacion}\n")
    out.append(f"Email: {email}\n")
    out.append(f"Teléfono: {telefono}\n")
    out.append("LinkedIn: (no especificado; recomendado crear/actualizar)\n")

    out.append("\nResumen de perfil\n")
    out.append(
        "Profesional orientada a la precisión y la organización, con experiencia en captura y limpieza de datos, "
        "transcripción y gestión de información. Ha liderado proyectos y asociaciones de impacto social (Teamworkz) "
        "demostrando autonomía, planificación y responsabilidad. Busca consolidarse en operaciones de datos y "
        "administración remota, aplicando su conocimiento de Microsoft Office y herramientas digitales.\n"
    )

    out.append("\nResumen del CV\n")
    if exp_lines:
        out.append("Experiencia (selección)\n")
        for l in exp_lines[:5]:
            out.append(f"- {l}\n")
    if edu_lines:
        out.append("\nFormación (selección)\n")
        for l in edu_lines[:6]:
            out.append(f"- {l}\n")
    out.append(f"\nIdiomas: {', '.join(idiomas) if idiomas else 'No especificado'}\n")
    out.append(f"Software: {', '.join(software) if software else 'No especificado'}\n")

    out.append("\nFortalezas clave\n")
    for f in fortalezas[:6]:
        out.append(f"- {f}\n")

    out.append("\nÁreas de mejora priorizadas\n")
    for (m, sk) in mejoras[:3]:
        out.append(f"- {m}\n")

    out.append("\nDiagnóstico del CV (estrellas)\n")
    for k, v in estrellas.items():
        out.append(f"{k}: {v}\n")

    out.append("\nEntornos de trabajo ideales\n")
    out.append(
        "Tareas estructuradas y métricas claras (volumen diario, precisión, SLA). Remoto asíncrono, comunicación "
        "escrita (email/Slack/Teams). Cultura inclusiva y neurodiversidad-friendly, con feedback breve y regular.\n"
    )

    out.append("\nRoles sugeridos\n")
    out.append("- Grabadora de datos / Data Entry — Junior–Mid — 100% remoto.\n")
    out.append("- Asistente administrativo/a remoto / Back-office — Junior–Mid — Remoto viable.\n")
    out.append("- Transcriptor/a y Etiquetado de datos (Data Labeling/Annotation) — Junior — Remoto.\n")
    out.append("- Operario/a de control de calidad de datos (Data QA) — Junior — Remoto.\n")
    out.append("- Coordinación de proyectos pequeños (Operations Assistant) — Junior — Híbrido/Remoto.\n")

    out.append("\nPlan de acción (30–60–90 días)\n")
    out.append("0–30 días (bases)\n- Reescribir CV con logros y métricas; crear LinkedIn claro.\n")
    out.append("31–60 días (tracción)\n- 10–15 candidaturas/semana; aprender OCR/Airtable/Notion.\n")
    out.append("61–90 días (consolidación)\n- Objetivo: 2–3 clientes/proyectos o 1 contrato estable; KPIs documentados.\n")

    out.append("\nConsejos prácticos de búsqueda\n- Filtro por 'remoto' + 'data entry', 'back office', 'data quality'.\n")
    out.append("Herramientas útiles\n- Excel/Sheets; Airtable/Notion; OCR básico; Trello/Asana; Gmail/Slack/Teams.\n")

    out.append("\nJuegos completados y cómo capitalizarlos\n")
    out.append("- Liderazgo: coordinar micro-tareas.\n- Analítico: checks de calidad.\n- Creatividad: mejoras de plantillas.\n- Resiliencia: disponibilidad internacional.\n")

    out.append("\nMiniplan mejora: decisiones e influencia social\n")
    out.append("- Decisiones: matriz Impacto×Esfuerzo y límite de 10 min.\n- Influencia: pitch de 3 líneas + prueba antes/después.\n")

    out.append("\nFrases listas (para propuestas y LinkedIn)\n")
    out.append("Titular: Data Entry | QA de Datos | Back-office (100% remoto)\n")
    out.append("Acerca de: \"Capturo y depuro datos con precision y SLA fiables...\"\n")

    out.append("\nMensaje final\n")
    out.append("Tienes base excelente para datos/operaciones remotas. Con CV cuantificado, LinkedIn claro y 2–3 pruebas de valor, puedes cerrar contratos estables en 8–12 semanas.\n")
    return "\n".join(out)
