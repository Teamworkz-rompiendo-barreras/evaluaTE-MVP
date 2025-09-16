# backend/pdf_service.py
from io import BytesIO
from typing import Any, Dict, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

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

def _stars(val: Optional[int]) -> str:
    n = int(val or 0)
    if n < 0: n = 0
    if n > 5: n = 5
    return "★" * n + "☆" * (5 - n)

def create_employability_pdf(payload: Dict[str, Any]) -> bytes:
    """
    Construye un PDF con los campos clave del informe IA + CV.
    Puede recibir directamente un diccionario compatible con `NewReportSchema`
    (claves `summary`, `personal_data`, `cv_analysis`, etc.) o el formato legado
    `{ "report": {...}, "cvAnalysis": {...} }`.
    """
    # Validar payload
    if not isinstance(payload, dict):
        raise ValueError("Payload debe ser un diccionario")
    
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=0)
    width, height = A4

    margin_x = 20 * mm
    y = height - 20 * mm
    line_w = width - 40 * mm

    title = f"Informe de Empleabilidad"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin_x, y, title)
    y -= 16

    # Determinar si el payload ya viene en el nuevo formato
    report_data: Dict[str, Any] = {}
    cv_data: Dict[str, Any] = {}
    if isinstance(payload, dict):
        if isinstance(payload.get("summary"), str) and isinstance(payload.get("personal_data"), dict):
            report_data = payload
            cv_data = payload.get("cv_analysis") if isinstance(payload.get("cv_analysis"), dict) else {}
        else:
            report_candidate = payload.get("report")
            if isinstance(report_candidate, dict):
                report_data = report_candidate
            cv_candidate = payload.get("cvAnalysis")
            if isinstance(cv_candidate, dict):
                cv_data = cv_candidate

    if not isinstance(report_data, dict):
        report_data = {}
    if not isinstance(cv_data, dict):
        cv_data = {}

    legacy_recs = payload.get("recommendations") if isinstance(payload.get("recommendations"), dict) else {}
    if not report_data.get("summary"):
        legacy_summary = report_data.get("resumen_ejecutivo") or legacy_recs.get("resumen_perfil")
        if legacy_summary:
            report_data["summary"] = legacy_summary
    if not report_data.get("strengths"):
        rec_strengths = legacy_recs.get("fortalezas_clave") if isinstance(legacy_recs, dict) else None
        if isinstance(rec_strengths, list):
            report_data["strengths"] = [str(item) for item in rec_strengths]
        elif isinstance(report_data.get("soft_skills"), list):
            report_data["strengths"] = [
                str(item.get("skill") or item.get("name") or item)
                for item in report_data.get("soft_skills")
                if item
            ]
    if not report_data.get("final_message"):
        legacy_message = report_data.get("frase_final") or (legacy_recs.get("frase_final") if isinstance(legacy_recs, dict) else None)
        if legacy_message:
            report_data["final_message"] = legacy_message

    personal = report_data.get("personal_data") if isinstance(report_data.get("personal_data"), dict) else {}
    full_name = str(payload.get("fullName") or personal.get("name") or "Usuario")

    c.setFont("Helvetica", 11)
    y = _draw_wrapped_text(c, margin_x, y, f"Nombre: {full_name}", line_w, leading=14)
    if personal:
        if personal.get("location"):
            y = _draw_wrapped_text(c, margin_x, y, f"Ubicación: {personal.get('location')}", line_w, leading=14)
        if personal.get("email"):
            y = _draw_wrapped_text(c, margin_x, y, f"Email: {personal.get('email')}", line_w, leading=14)
        if personal.get("phone"):
            y = _draw_wrapped_text(c, margin_x, y, f"Teléfono: {personal.get('phone')}", line_w, leading=14)
    y -= 4

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Resumen ejecutivo")
    y -= 14
    c.setFont("Helvetica", 10)
    y = _draw_wrapped_text(c, margin_x, y, report_data.get("summary") or "", line_w)

    cv_analysis = report_data.get("cv_analysis") or cv_data
    if not isinstance(cv_analysis, dict):
        cv_analysis = {}
    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Diagnóstico del CV")
    y -= 14
    c.setFont("Helvetica", 10)
    y = _draw_wrapped_text(c, margin_x, y, f"Estructura: {_stars(cv_analysis.get('structure_score'))}", line_w)
    y = _draw_wrapped_text(c, margin_x, y, f"Claridad: {_stars(cv_analysis.get('clarity_score'))}", line_w)
    y = _draw_wrapped_text(c, margin_x, y, f"Coherencia: {_stars(cv_analysis.get('coherence_score'))}", line_w)
    y = _draw_wrapped_text(c, margin_x, y, f"Información clave: {_stars(cv_analysis.get('key_info_score'))}", line_w)
    y = _draw_wrapped_text(c, margin_x, y, f"Estilo: {_stars(cv_analysis.get('style_score'))}", line_w)

    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Fortalezas")
    y -= 14
    c.setFont("Helvetica", 10)
    for strength in report_data.get("strengths", []) or []:
        y = _draw_wrapped_text(c, margin_x, y, f"• {strength}", line_w)

    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Áreas de mejora")
    y -= 14
    c.setFont("Helvetica", 10)
    for area in report_data.get("improvement_areas", []) or []:
        if isinstance(area, dict):
            label = area.get("area") or ""
            action = area.get("suggested_action") or ""
            line = label if not action else f"{label}: {action}"
            y = _draw_wrapped_text(c, margin_x, y, f"• {line}", line_w)
        else:
            y = _draw_wrapped_text(c, margin_x, y, f"• {area}", line_w)

    roles = report_data.get("suggested_roles", []) or []
    if roles:
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Roles sugeridos")
        y -= 14
        c.setFont("Helvetica", 10)
        for role in roles:
            if isinstance(role, dict):
                linea = f"• {role.get('role')} — {role.get('seniority')} — Remoto: {role.get('remote_viable')}"
                y = _draw_wrapped_text(c, margin_x, y, linea, line_w)
                if role.get("reason"):
                    y = _draw_wrapped_text(c, margin_x + 8, y, f"   Razón: {role.get('reason')}", line_w - 8)
            else:
                y = _draw_wrapped_text(c, margin_x, y, f"• {role}", line_w)

    plan = report_data.get("action_plan") or {}
    bloques = [
        ("Corto plazo (0–30 días)", plan.get("short_term", [])),
        ("Medio plazo (1–3 meses)", plan.get("medium_term", [])),
        ("Largo plazo (3–6+ meses)", plan.get("long_term", [])),
    ]
    for titulo, items in bloques:
        if not items:
            continue
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, titulo)
        y -= 14
        c.setFont("Helvetica", 10)
        for it in items:
            y = _draw_wrapped_text(c, margin_x, y, f"• {it}", line_w)

    ideal_env = report_data.get("ideal_work_environment")
    if ideal_env:
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Entornos de trabajo ideales")
        y -= 14
        c.setFont("Helvetica", 10)
        y = _draw_wrapped_text(c, margin_x, y, str(ideal_env), line_w)

    job_advice = report_data.get("job_search_advice")
    advice_lines: List[str] = []
    if isinstance(job_advice, dict):
        def _fmt(value: Any) -> str:
            if isinstance(value, (list, tuple, set)):
                return ", ".join(str(v) for v in value if v)
            return str(value)

        if job_advice.get("cv_optimization"):
            advice_lines.append(f"• CV: {_fmt(job_advice.get('cv_optimization'))}")
        if job_advice.get("letters_portfolio"):
            advice_lines.append(f"• Cartas/portfolio: {_fmt(job_advice.get('letters_portfolio'))}")
        if job_advice.get("recommended_platforms"):
            advice_lines.append(
                f"• Plataformas: {_fmt(job_advice.get('recommended_platforms'))}"
            )
        if job_advice.get("networking"):
            advice_lines.append(f"• Networking: {_fmt(job_advice.get('networking'))}")
        if job_advice.get("interview_tips"):
            advice_lines.append(f"• Entrevistas: {_fmt(job_advice.get('interview_tips'))}")

    if advice_lines:
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Consejos de búsqueda de empleo")
        y -= 14
        c.setFont("Helvetica", 10)
        for line in advice_lines:
            y = _draw_wrapped_text(c, margin_x, y, line, line_w)

    tools = report_data.get("useful_tools")
    tool_lines: List[str] = []
    if isinstance(tools, dict):
        labels = {
            "productivity": "Productividad",
            "job_search": "Búsqueda de empleo",
            "learning": "Aprendizaje",
            "accessibility": "Accesibilidad",
        }

        def _fmt_tools(val: Any) -> str:
            if isinstance(val, (list, tuple, set)):
                return ", ".join(str(v) for v in val if v)
            return str(val)

        for key, label in labels.items():
            value = tools.get(key)
            if value:
                tool_lines.append(f"• {label}: {_fmt_tools(value)}")

    if tool_lines:
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Herramientas útiles")
        y -= 14
        c.setFont("Helvetica", 10)
        for line in tool_lines:
            y = _draw_wrapped_text(c, margin_x, y, line, line_w)

    games = report_data.get("completed_games")
    if games:
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Juegos completados")
        y -= 14
        c.setFont("Helvetica", 10)
        for game in games:
            if isinstance(game, dict):
                nombre = game.get("name") or game.get("title") or ""
                detalle = game.get("insight") or game.get("summary") or ""
                base = nombre
                if detalle:
                    base = f"{nombre}: {detalle}" if nombre else detalle
                if base:
                    y = _draw_wrapped_text(c, margin_x, y, f"• {base}", line_w)
            else:
                y = _draw_wrapped_text(c, margin_x, y, f"• {game}", line_w)

    if report_data.get("final_message"):
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Mensaje final")
        y -= 14
        c.setFont("Helvetica", 10)
        y = _draw_wrapped_text(c, margin_x, y, report_data.get("final_message"), line_w)

    c.showPage()
    c.save()
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
