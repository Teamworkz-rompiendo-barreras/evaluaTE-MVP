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
    Espera un dict con:
    {
      "fullName": str,
      "cvAnalysis": {...},
      "report": {...}  # salida de la IA (generate_report)
    }
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    margin_x = 20 * mm
    y = height - 20 * mm
    line_w = width - 40 * mm

    title = f"Informe de Empleabilidad"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin_x, y, title)
    y -= 16

    full_name = payload.get("fullName") or payload.get("userId") or ""
    c.setFont("Helvetica", 11)
    y = _draw_wrapped_text(c, margin_x, y, f"Nombre: {full_name}", line_w, leading=14)
    y -= 4

    report: Dict[str, Any] = payload.get("report") or {}
    cv: Dict[str, Any] = payload.get("cvAnalysis") or {}

    # Resumen
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Resumen ejecutivo")
    y -= 14
    c.setFont("Helvetica", 10)
    y = _draw_wrapped_text(c, margin_x, y, report.get("summary") or "", line_w)

    # CV: estrellas
    stars = (cv.get("stars") or report.get("cv_analysis", {}).get("stars") or {})
    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Diagnóstico del CV")
    y -= 14
    c.setFont("Helvetica", 10)
    y = _draw_wrapped_text(c, margin_x, y, f"Formato: {_stars(stars.get('formato'))}", line_w)
    y = _draw_wrapped_text(c, margin_x, y, f"Claridad: {_stars(stars.get('claridad'))}", line_w)
    y = _draw_wrapped_text(c, margin_x, y, f"Coherencia: {_stars(stars.get('coherencia'))}", line_w)
    y = _draw_wrapped_text(c, margin_x, y, f"Información clave: {_stars(stars.get('informacion_clave'))}", line_w)
    y = _draw_wrapped_text(c, margin_x, y, f"Ortografía: {_stars(stars.get('ortografia'))}", line_w)

    # Fortalezas y Áreas de mejora
    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Fortalezas")
    y -= 14
    c.setFont("Helvetica", 10)
    for s in report.get("strengths", []):
        y = _draw_wrapped_text(c, margin_x, y, f"• {s}", line_w)
    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y, "Áreas de mejora")
    y -= 14
    c.setFont("Helvetica", 10)
    for s in report.get("improvement_areas", []):
        y = _draw_wrapped_text(c, margin_x, y, f"• {s}", line_w)

    # Roles sugeridos
    roles = report.get("suggested_roles", [])
    if roles:
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Roles sugeridos")
        y -= 14
        c.setFont("Helvetica", 10)
        for r in roles:
            linea = f"• {r.get('role')} — {r.get('seniority')} — Remoto: {r.get('remote_viable')}"
            y = _draw_wrapped_text(c, margin_x, y, linea, line_w)
            if r.get("reason"):
                y = _draw_wrapped_text(c, margin_x+8, y, f"   Razón: {r.get('reason')}", line_w-8)

    # Plan de acción (si cabe en 1 página)
    plan = report.get("action_plan") or {}
    bloques = [
        ("Corto plazo (0–30 días)", plan.get("short_term", [])),
        ("Medio plazo (1–3 meses)", plan.get("mid_term", [])),
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

    # Mensaje final
    if report.get("final_message"):
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Mensaje final")
        y -= 14
        c.setFont("Helvetica", 10)
        y = _draw_wrapped_text(c, margin_x, y, report["final_message"], line_w)

    c.showPage()
    c.save()
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
