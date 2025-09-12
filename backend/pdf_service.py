# backend/pdf_service.py
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple
from datetime import date
import math

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors

# Helpers
def _draw_wrapped_text(c: canvas.Canvas, x: float, y: float, text: str, max_width: float, leading: float = 12) -> float:
    """
    Dibuja texto multilínea simple; devuelve la coordenada Y final.
    """
    if not text:
        return y
    lines: List[str] = []
    for raw_line in text.split("\n"):
        words = raw_line.split(" ")
        line = ""
        for w in words:
            test = f"{line} {w}".strip()
            if c.stringWidth(test) <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y

# Renderiza una lista con viñetas; cada item puede ser str o dict (con claves comunes)
def _draw_bulleted_list(
    c: canvas.Canvas,
    x: float,
    y: float,
    items: List[Any],
    max_width: float,
    leading: float = 12,
) -> float:
    if not items:
        return y
    for it in items:
        if it is None:
            continue
        if isinstance(it, dict):
            # Intentar construir una línea legible a partir de claves comunes
            label_parts: List[str] = []
            for k in ("title", "degree", "role", "area", "name", "label"):
                v = it.get(k)
                if v:
                    label_parts.append(str(v))
                    break
            # info secundaria
            secondary: List[str] = []
            for k in ("company", "center", "year", "seniority", "reason"):
                v = it.get(k)
                if v:
                    secondary.append(str(v))
            line = " • " + (" ".join(label_parts) if label_parts else str(it))
            if secondary:
                line += " — " + ", ".join(secondary)
            y = _draw_wrapped_text(c, x, y, line, max_width, leading)
        else:
            y = _draw_wrapped_text(c, x, y, f"• {str(it)}", max_width, leading)
    return y

# Crea una nueva página si falta espacio
def _ensure_space(c: canvas.Canvas, y: float, needed: float, margin_top: float, margin_bottom: float) -> float:
    if y - needed < margin_bottom:
        c.showPage()
        c.setFont("Helvetica", 10)
        return A4[1] - margin_top
    return y

# Radar simple para soft skills (0..100)
def _draw_radar_chart(
    c: canvas.Canvas,
    center_x: float,
    center_y: float,
    radius: float,
    data: List[Dict[str, Any]],
    levels: int = 5,
    label_color = colors.grey,
) -> None:
    if not data:
        return
    # Normalizar a pares (label, score)
    pairs: List[Tuple[str, float]] = []
    for item in data:
        if isinstance(item, dict):
            label = str(item.get("skill") or item.get("name") or item.get("label") or "").strip()
            try:
                score = float(item.get("score"))
            except Exception:
                score = 0.0
            if label:
                pairs.append((label, max(0.0, min(100.0, score))))
        elif isinstance(item, str):
            pairs.append((item, 50.0))
    if not pairs:
        return
    n = len(pairs)
    # Ejes y anillos
    c.setStrokeColor(colors.grey)
    c.setLineWidth(0.6)
    for lvl in range(1, levels + 1):
        r = radius * (lvl / levels)
        # Polígono concéntrico
        pts: List[Tuple[float, float]] = []
        for i in range(n):
            angle = (i / n) * 6.283185307179586  # 2*pi
            x = center_x + r * math.cos(angle - 1.57079632679)  # rotar 90º
            y = center_y + r * math.sin(angle - 1.57079632679)
            pts.append((x, y))
        # Dibujar
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            c.line(x1, y1, x2, y2)
    # Ejes y etiquetas
    c.setStrokeColor(colors.lightgrey)
    for i, (label, _score) in enumerate(pairs):
        angle = (i / n) * 6.283185307179586
        x2 = center_x + radius * math.cos(angle - 1.57079632679)
        y2 = center_y + radius * math.sin(angle - 1.57079632679)
        c.line(center_x, center_y, x2, y2)
        # Etiqueta
        lx = center_x + (radius + 6 * mm) * math.cos(angle - 1.57079632679)
        ly = center_y + (radius + 6 * mm) * math.sin(angle - 1.57079632679)
        c.setFillColor(label_color)
        c.setFont("Helvetica", 8)
        c.drawCentredString(lx, ly, label[:22])
    # Polígono de datos
    c.setFillColorRGB(0.2, 0.45, 0.85, alpha=0.25)
    c.setStrokeColorRGB(0.2, 0.45, 0.85)
    c.setLineWidth(1.2)
    first: Optional[Tuple[float, float]] = None
    prev: Optional[Tuple[float, float]] = None
    for i, (_label, score) in enumerate(pairs):
        r = radius * (score / 100.0)
        angle = (i / n) * 6.283185307179586
        x = center_x + r * math.cos(angle - 1.57079632679)
        y = center_y + r * math.sin(angle - 1.57079632679)
        if prev is not None:
            c.line(prev[0], prev[1], x, y)
        else:
            first = (x, y)
        prev = (x, y)
    if prev and first:
        c.line(prev[0], prev[1], first[0], first[1])
    # Puntos
    c.setFillColorRGB(0.2, 0.45, 0.85)
    for i, (_label, score) in enumerate(pairs):
        r = radius * (score / 100.0)
        angle = (i / n) * 6.283185307179586
        x = center_x + r * math.cos(angle - 1.57079632679)
        y = center_y + r * math.sin(angle - 1.57079632679)
        c.circle(x, y, 1.6, stroke=0, fill=1)

def _stars(val: Optional[int]) -> str:
    n = int(val or 0)
    if n < 0: n = 0
    if n > 5: n = 5
    return "★" * n + "☆" * (5 - n)

def create_employability_pdf(payload: Dict[str, Any]) -> bytes:
    """
    Construye un PDF multi-sección con datos REALES del payload.
    - Usa, si existen: report.personal_data, report.cv_analysis, report.strengths,
      report.improvement_areas, report.suggested_roles, report.action_plan,
      report.job_search_advice, report.tools, report.completed_games.
    - Acepta además: softSkills, jobPreferences, completedGames, cvAnalysis.
    """
    if not isinstance(payload, dict):
        raise ValueError("Payload debe ser un diccionario")

    # ---------- Extracción de datos robusta ----------
    report_data = {}
    cv_data = {}
    soft_skills = []
    job_prefs = payload.get("jobPreferences") or {}
    completed_games = payload.get("completedGames") or []
    if isinstance(payload.get("summary"), str) and isinstance(payload.get("personal_data"), dict):
        report_data = payload
        cv_data = report_data.get("cv_analysis") or {}
    else:
        report_data = payload.get("report") or {}
        cv_data = payload.get("cvAnalysis") or report_data.get("cv_analysis") or {}
    if not isinstance(report_data, dict):
        report_data = {}
    if not isinstance(cv_data, dict):
        cv_data = {}
    soft_skills = payload.get("softSkills") or report_data.get("soft_skills") or []
    if not isinstance(soft_skills, list):
        soft_skills = []

    # Datos personales básicos
    full_name = (
        payload.get("fullName")
        or (report_data.get("personal_data") or {}).get("name")
        or payload.get("userId")
        or "Usuario"
    )
    personal = report_data.get("personal_data") or {}
    if not isinstance(personal, dict):
        personal = {}
    # Enriquecer con contacto del CV si falta
    contact = (cv_data.get("contact") if isinstance(cv_data, dict) else {}) or {}
    if isinstance(contact, dict):
        if not personal.get("email") and isinstance(contact.get("emails"), list) and contact.get("emails"):
            personal["email"] = contact.get("emails")[0]
        if not personal.get("phone") and isinstance(contact.get("phones"), list) and contact.get("phones"):
            personal["phone"] = contact.get("phones")[0]
        if not personal.get("location") and isinstance(contact.get("location"), str):
            personal["location"] = contact.get("location")

    # Puntuación global
    global_score = int(payload.get("employabilityScore") or report_data.get("employabilityScore") or 0)

    # ---------- Render PDF ----------
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=0)
    width, height = A4
    margin_x = 20 * mm
    margin_top = 20 * mm
    margin_bottom = 18 * mm
    y = height - margin_top
    line_w = width - 2 * margin_x

    # Cabecera
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin_x, y, "Informe de Empleabilidad")
    y -= 16
    c.setFont("Helvetica", 10)
    today = date.today().strftime("%d/%m/%Y")
    y = _draw_wrapped_text(c, margin_x, y, f"Nombre: {full_name}", line_w, leading=14)
    y = _draw_wrapped_text(c, margin_x, y, f"Fecha: {today}", line_w, leading=12)
    y -= 6

    # Bloque: Mapa de habilidades (radar) + resumen de puntuaciones + puntaje global
    import math  # local import para evitar dependencia global si no se usa
    chart_radius = 45 * mm
    center_x = margin_x + chart_radius + 5 * mm
    center_y = y - chart_radius - 4 * mm
    # Título
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Mapa de habilidades")
    y -= 14
    # Radar
    try:
        _draw_radar_chart(c, center_x, center_y, chart_radius, soft_skills)
    except Exception:
        pass
    # Resumen de soft skills a la derecha
    c.setFont("Helvetica", 9)
    col_x = center_x + chart_radius + 14 * mm
    y_list_top = y - 4
    y2 = y_list_top
    if soft_skills:
        top_list = []
        for it in soft_skills:
            if isinstance(it, dict):
                nm = str(it.get("skill") or it.get("name") or "").strip()
                sc = it.get("score")
                try:
                    sc_int = int(sc)
                except Exception:
                    sc_int = 0
                if nm:
                    top_list.append(f"{nm}: {sc_int}/100")
        y2 = _draw_wrapped_text(c, col_x, y2, "Resumen de puntuaciones:", width - col_x - margin_x, leading=12)
        c.setFont("Helvetica", 9)
        for ln in top_list[:12]:
            y2 = _draw_wrapped_text(c, col_x, y2, f"• {ln}", width - col_x - margin_x, leading=12)

    # Burbuja de score global (si existe)
    if global_score:
        badge_x = width - margin_x - 22 * mm
        badge_y = center_y - chart_radius + 8 * mm
        c.setFillColorRGB(0.15, 0.18, 0.22)
        c.roundRect(badge_x, badge_y, 22 * mm, 12 * mm, 6, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 9)
        c.drawCentredString(badge_x + 11 * mm, badge_y + 4, f"{global_score}%")
        c.setFillColor(colors.black)

    y = center_y - chart_radius - 8 * mm
    y = _ensure_space(c, y, 30 * mm, margin_top, margin_bottom)

    # Página 2: Resumen ejecutivo, Datos personales, Resumen del CV
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Resumen ejecutivo")
    y -= 14
    c.setFont("Helvetica", 10)
    y = _draw_wrapped_text(c, margin_x, y, report_data.get("summary") or report_data.get("resumen_ejecutivo") or "", line_w)

    y -= 6
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Datos personales")
    y -= 14
    c.setFont("Helvetica", 10)
    pd_lines: List[str] = []
    if personal.get("name") or full_name:
        pd_lines.append(f"Nombre: {personal.get('name') or full_name}")
    if personal.get("location"):
        pd_lines.append(f"Ubicación: {personal.get('location')}")
    if personal.get("email"):
        pd_lines.append(f"Email: {personal.get('email')}")
    if personal.get("phone"):
        pd_lines.append(f"Teléfono: {personal.get('phone')}")
    y = _draw_bulleted_list(c, margin_x, y, pd_lines, line_w)

    # Resumen del CV (experiencia/educación/idiomas/software)
    y = _ensure_space(c, y, 40 * mm, margin_top, margin_bottom)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Resumen del CV")
    y -= 14
    c.setFont("Helvetica", 10)
    # Experiencia
    y = _draw_wrapped_text(c, margin_x, y, "Experiencia (selección)", line_w)
    xp = (cv_data.get("experience") or cv_data.get("experience_detailed") or [])
    y = _draw_bulleted_list(c, margin_x, y, xp[:8], line_w)
    # Educación
    y -= 6
    y = _draw_wrapped_text(c, margin_x, y, "Formación (selección)", line_w)
    edu = cv_data.get("education") or cv_data.get("education_detailed") or []
    y = _draw_bulleted_list(c, margin_x, y, edu[:8], line_w)
    # Idiomas
    langs = cv_data.get("languages") or []
    if langs:
        y -= 6
        y = _draw_wrapped_text(c, margin_x, y, "Idiomas", line_w)
        items = []
        for it in langs:
            if isinstance(it, dict):
                nm = it.get("name") or it.get("language") or "Idioma"
                lvl = it.get("level") or it.get("nivel") or ""
                items.append(f"{nm} — {lvl}".strip(" —"))
            else:
                items.append(str(it))
        y = _draw_bulleted_list(c, margin_x, y, items, line_w)
    # Software / herramientas
    sw = cv_data.get("software") or cv_data.get("skills") or []
    if sw:
        y -= 6
        y = _draw_wrapped_text(c, margin_x, y, "Herramientas/Software", line_w)
        y = _draw_bulleted_list(c, margin_x, y, sw[:12], line_w)

    # Página 3: Áreas de mejora priorizadas
    y = _ensure_space(c, y, 60 * mm, margin_top, margin_bottom)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Áreas de mejora priorizadas")
    y -= 14
    c.setFont("Helvetica", 10)
    improvements = report_data.get("improvement_areas") or []
    formatted_improvements: List[str] = []
    for it in improvements:
        if isinstance(it, dict):
            label = it.get("area") or it.get("name") or str(it)
            action = it.get("suggested_action") or it.get("action") or ""
            score = it.get("score")
            line = f"{label}"
            if isinstance(score, int):
                line += f": ({score}/100)"
            if action:
                line += f". Acción: {action}"
            formatted_improvements.append(line)
        else:
            formatted_improvements.append(str(it))
    if not formatted_improvements and isinstance(soft_skills, list):
        for it in soft_skills:
            if isinstance(it, dict):
                try:
                    sc = int(it.get("score") or 0)
                except Exception:
                    sc = 0
                if sc <= 50:
                    formatted_improvements.append(f"{it.get('skill') or it.get('name')}: ({sc}/100). Acción: Definir un micro-plan de mejora")
    y = _draw_bulleted_list(c, margin_x, y, formatted_improvements[:12], line_w)

    # Página 4: Entornos ideales, Roles sugeridos, Plan de acción
    y = _ensure_space(c, y, 80 * mm, margin_top, margin_bottom)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Entornos de trabajo ideales")
    y -= 14
    c.setFont("Helvetica", 10)
    env_txt = ""
    if isinstance(report_data.get("environments"), list) and report_data.get("environments"):
        env_txt = ", ".join(str(x) for x in report_data.get("environments") if x)
    elif isinstance(job_prefs, dict):
        wm = job_prefs.get("workMode") or job_prefs.get("work_mode") or ""
        roles = job_prefs.get("areas") or job_prefs.get("desired_roles") or []
        env_txt = f"Modalidad preferida: {wm}. Áreas/roles de interés: {', '.join(roles) if roles else 'No especificado'}."
    y = _draw_wrapped_text(c, margin_x, y, env_txt, line_w)

    # Roles sugeridos
    roles = report_data.get("suggested_roles") or []
    if roles:
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Roles sugeridos")
        y -= 14
        c.setFont("Helvetica", 10)
        pretty_roles: List[str] = []
        for r in roles:
            if isinstance(r, dict):
                line = f"{r.get('role')} — {r.get('seniority')} — 100% remoto" if r.get('remote_viable') else f"{r.get('role')} — {r.get('seniority')}"
                if r.get("reason"):
                    line += f". Razón: {r.get('reason')}"
                pretty_roles.append(line)
            else:
                pretty_roles.append(str(r))
        y = _draw_bulleted_list(c, margin_x, y, pretty_roles, line_w)

    # Plan de acción
    plan = report_data.get("action_plan") or {}
    bloques = [
        ("Corto plazo (0-30 días)", plan.get("short_term", [])),
        ("Medio plazo (1-3 meses)", plan.get("mid_term", []) or plan.get("medium_term", [])),
        ("Largo plazo (3-6+ meses)", plan.get("long_term", [])),
    ]
    for titulo, items in bloques:
        if not items:
            continue
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, titulo)
        y -= 14
        c.setFont("Helvetica", 10)
        y = _draw_bulleted_list(c, margin_x, y, items, line_w)

    # Página 5: Estrategias de búsqueda + Minijuegos + Herramientas
    y = _ensure_space(c, y, 90 * mm, margin_top, margin_bottom)
    advice = report_data.get("job_search_advice") or {}
    if advice:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Estrategias de búsqueda de empleo")
        y -= 14
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin_x, y, "Optimización del CV")
        y -= 12
        c.setFont("Helvetica", 10)
        y = _draw_bulleted_list(c, margin_x, y, advice.get("cv_optimization") or advice.get("tips") or [], line_w)
        if advice.get("letters_portfolio"):
            y -= 6
            c.setFont("Helvetica-Bold", 11)
            c.drawString(margin_x, y, "Cartas y portfolio/casos")
            y -= 12
            c.setFont("Helvetica", 10)
            y = _draw_wrapped_text(c, margin_x, y, str(advice.get("letters_portfolio")), line_w)
        if advice.get("recommended_platforms"):
            y -= 6
            c.setFont("Helvetica-Bold", 11)
            c.drawString(margin_x, y, "Plataformas")
            y -= 12
            c.setFont("Helvetica", 10)
            y = _draw_bulleted_list(c, margin_x, y, advice.get("recommended_platforms"), line_w)
        if advice.get("networking"):
            y -= 6
            c.setFont("Helvetica-Bold", 11)
            c.drawString(margin_x, y, "Networking dirigido")
            y -= 12
            c.setFont("Helvetica", 10)
            y = _draw_wrapped_text(c, margin_x, y, str(advice.get("networking")), line_w)

    # Minijuegos completados
    games = completed_games or report_data.get("completed_games") or []
    if games:
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Resultados de minijuegos")
        y -= 14
        c.setFont("Helvetica", 10)
        pretty_games: List[str] = []
        for g in games:
            if isinstance(g, dict):
                nm = g.get("name") or g.get("id") or "Juego"
                score = g.get("score")
                if score is not None:
                    pretty_games.append(f"{nm}: {score}")
                else:
                    pretty_games.append(str(nm))
            else:
                pretty_games.append(str(g))
        y = _draw_bulleted_list(c, margin_x, y, pretty_games, line_w)

    # Herramientas útiles
    tools = report_data.get("tools") or {}
    if tools:
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Herramientas útiles")
        y -= 14
        c.setFont("Helvetica", 10)
        for title, items in tools.items():
            c.setFont("Helvetica-Bold", 10)
            y = _draw_wrapped_text(c, margin_x, y, title.capitalize(), line_w)
            c.setFont("Helvetica", 10)
            y = _draw_bulleted_list(c, margin_x, y, items, line_w)

    # Página final: Mensaje
    msg = report_data.get("final_message") or report_data.get("frase_final")
    if msg:
        y = _ensure_space(c, y, 40 * mm, margin_top, margin_bottom)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Mensaje final")
        y -= 14
        c.setFont("Helvetica", 10)
        y = _draw_wrapped_text(c, margin_x, y, str(msg), line_w)

    c.showPage()
    c.save()
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes