# backend/pdf_service.py
import os
import math
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple
from datetime import date
import unicodedata

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors

try:
    from new_report_schema import NewReportSchema
except ImportError:
    from backend.new_report_schema import NewReportSchema

# --- Colores (Tema Oscuro) ---
BG_COLOR = colors.HexColor("#171923")  # Deep Dark Blue/Slate
TEXT_COLOR = colors.white
ACCENT_COLOR = colors.HexColor("#4299E1") # Blue
BOX_BG_COLOR = colors.HexColor("#A0AEC0") # For badges (light grey) - wait, images show dark badges?
# Image analysis: Background is clearly dark (#171923 or similar). Text is white/light grey.
# Radar chart background is dark.
# Global score badge is dark grey/black with white text.

# --- Helpers de Dibujo ---

def _draw_background(c: canvas.Canvas):
    """Pinta el fondo completo de la página."""
    c.saveState()
    c.setFillColor(BG_COLOR)
    c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    c.restoreState()

def _draw_text(c: canvas.Canvas, x: float, y: float, text: str, font="Helvetica", size=10, color=TEXT_COLOR):
    """Dibuja texto simple."""
    c.saveState()
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, text)
    c.restoreState()

def _draw_centered_text(c: canvas.Canvas, x: float, y: float, text: str, font="Helvetica", size=10, color=TEXT_COLOR):
    c.saveState()
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawCentredString(x, y, text)
    c.restoreState()

def _draw_wrapped_text(c: canvas.Canvas, x: float, y: float, text: str, max_width: float, leading: float = 12, font="Helvetica", size=10, color=TEXT_COLOR) -> float:
    """Dibuja texto multilínea."""
    if not text:
        return y
    c.saveState()
    c.setFillColor(color)
    c.setFont(font, size)
    
    lines: List[str] = []
    for raw_line in text.split("\n"):
        words = raw_line.split(" ")
        line = ""
        for w in words:
            test = f"{line} {w}".strip()
            if c.stringWidth(test, font, size) <= max_width:
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
    c.restoreState()
    return y

def _draw_bulleted_list(c: canvas.Canvas, x: float, y: float, items: List[Any], max_width: float, leading: float = 14) -> float:
    """Renderiza lista con viñetas."""
    if not items:
        return y
    for it in items:
        if not it:
            continue
        # Convertir a string si es dict
        txt = ""
        if isinstance(it, str):
            txt = it
        elif isinstance(it, dict):
            # Lógica heurística para diccionarios
            labels = [str(it.get(k)) for k in ["name", "skill", "role", "title", "language", "empresa"] if it.get(k)]
            txt = " - ".join(labels) if labels else str(it)
        
        y = _draw_wrapped_text(c, x, y, f"• {txt}", max_width, leading, font="Helvetica", size=10)
    return y

# --- Radar Chart (Customizado para Dark Mode) ---
def _draw_radar_chart(c: canvas.Canvas, center_x: float, center_y: float, radius: float, data: List[Dict[str, Any]]) -> None:
    if not data:
        return
    # Top 10 skills standard
    pairs = []
    for item in data:
        lbl = item.get("skill") or item.get("name") or ""
        scr = item.get("score") or 0
        try:
            scr = float(scr)
        except:
            scr = 0
        pairs.append((lbl, max(0, min(100, scr))))
    
    n = len(pairs)
    if n < 3: return

    # Ejes y anillos (Gris claro)
    c.saveState()
    c.setStrokeColor(colors.grey)
    c.setLineWidth(0.5)
    
    # 5 Niveles
    for i in range(1, 6):
        r = radius * (i/5)
        # Dibujar polígono
        p = c.beginPath()
        for j in range(n):
            ang = (j / n) * 2 * math.pi - (math.pi / 2)
            x = center_x + r * math.cos(ang)
            y = center_y + r * math.sin(ang)
            if j == 0: p.moveTo(x, y)
            else: p.lineTo(x, y)
        p.close()
        c.drawPath(p, stroke=1, fill=0)

    # Ejes radiales
    for j in range(n):
        ang = (j / n) * 2 * math.pi - (math.pi / 2)
        x = center_x + radius * math.cos(ang)
        y = center_y + radius * math.sin(ang)
        c.line(center_x, center_y, x, y)
        
        # Etiquetas
        lbl_x = center_x + (radius + 15) * math.cos(ang)
        lbl_y = center_y + (radius + 10) * math.sin(ang)
        
        # Ajuste de alineación según cuadrante
        align = "diferente"
        # Usar drawCentredString por simplicidad
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 8)
        # Dividir etiquetas largas
        palabras = pairs[j][0].split(" ")
        if len(palabras) > 2:
            lbl_txt1 = " ".join(palabras[:2])
            lbl_txt2 = " ".join(palabras[2:])
            c.drawCentredString(lbl_x, lbl_y + 4, lbl_txt1)
            c.drawCentredString(lbl_x, lbl_y - 4, lbl_txt2)
        else:
            c.drawCentredString(lbl_x, lbl_y, pairs[j][0])

    # Datos (Relleno azul transparente)
    c.setStrokeColor(ACCENT_COLOR)
    c.setLineWidth(2)
    c.setFillColor(colors.Color(0.26, 0.6, 0.88, alpha=0.3)) # #4299E1 con alpha
    
    p = c.beginPath()
    first_pt = None
    for j in range(n):
        val = pairs[j][1]
        r = radius * (val / 100.0)
        ang = (j / n) * 2 * math.pi - (math.pi / 2)
        x = center_x + r * math.cos(ang)
        y = center_y + r * math.sin(ang)
        if j == 0:
            p.moveTo(x, y)
            first_pt = (x, y)
        else:
            p.lineTo(x, y)
        
        # Puntito
        c.circle(x, y, 3, stroke=0, fill=1) # Dibuja puntos azules en los vértices
        
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()

# --- Normalización Soft Skills ---
ALL_SOFT_SKILLS = [
    "Pensamiento analítico", "Toma de decisiones", "Liderazgo", "Creatividad",
    "Influencia social", "Curiosidad y aprendizaje", "Resiliencia y flexibilidad",
    "Autoconciencia", "Empatía", "Pensamiento Crítico"
]

def _normalize_soft_skills(raw_data: List[Any]) -> List[Dict[str, Any]]:
    # Crea lista fija de 10 skills, mapeando lo que venga
    # Simplificado: si viene dict con name/skill, busca match fuzzy o exacto
    mapping = {k.lower(): k for k in ALL_SOFT_SKILLS}
    scores = {k: 0 for k in ALL_SOFT_SKILLS}
    
    for item in raw_data:
        if isinstance(item, dict):
            nm = str(item.get("skill") or item.get("name") or "").lower()
            val = item.get("score") or 0
            # Intentar buscar en mapping
            for k in mapping:
                if k in nm or nm in k:
                    scores[mapping[k]] = int(val)
    
    return [{"skill": k, "score": v} for k, v in scores.items()]


def create_employability_pdf(report: NewReportSchema) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    margin = 25 * mm
    printable_w = w - 2 * margin
    
    # Datos
    rep_dict = report.dict()
    soft_skills = _normalize_soft_skills(rep_dict.get("soft_skills") or [])
    
    # --- PÁGINA 1: Portada / Radar ---
    _draw_background(c)
    
    # Header
    # Logo text "Teamworkz" (simulado con texto dorado/amarillo)
    _draw_centered_text(c, w/2, h - 30 * mm, "Teamworkz", font="Helvetica-Bold", size=14, color=colors.HexColor("#F6E05E"))
    _draw_centered_text(c, w/2, h - 35 * mm, "ROMPIENDO BARRERAS", font="Helvetica", size=8, color=colors.HexColor("#F6E05E"))
    
    # Título Grande
    _draw_centered_text(c, w/2, h - 50 * mm, "Informe de Empleabilidad", font="Helvetica-Bold", size=24)
    
    # Nombre
    full_name = report.personal_data.name or "Usuario"
    _draw_centered_text(c, w/2, h - 60 * mm, full_name, font="Helvetica-Bold", size=16, color=colors.lightgrey)
    
    # Fecha
    _draw_centered_text(c, w/2, h - 68 * mm, date.today().strftime("%d/%m/%Y"), font="Helvetica", size=12, color=colors.grey)
    
    # Sección Mapa de Habilidades
    y_radar = h - 110 * mm
    _draw_text(c, margin, y_radar + 20, "Mapa de habilidades", font="Helvetica-Bold", size=16)
    
    # Radar Chart
    radar_center_y = y_radar - 60
    radar_radius = 45 * mm
    # Ajustar centro X un poco a la izquierda para dejar espacio a la lista
    radar_center_x = margin + radar_radius + 10
    
    _draw_radar_chart(c, radar_center_x, radar_center_y, radar_radius, soft_skills)
    
    # Lista de puntuaciones (a la derecha del radar)
    list_x = radar_center_x + radar_radius + 30
    list_y = y_radar
    
    _draw_text(c, list_x, list_y, "Resumen de puntuaciones:", font="Helvetica-Bold", size=10)
    list_y -= 15
    for sk in soft_skills:
        sc = sk["score"]
        color = colors.white
        if sc > 70: color = colors.HexColor("#68D391") # Green
        elif sc < 40: color = colors.HexColor("#FC8181") # Red
        
        _draw_text(c, list_x, list_y, f"{sk['skill']}: {sc}%", font="Helvetica", size=9, color=color)
        list_y -= 12
        
    # Puntaje Global (Abajo a la derecha)
    glob_score = int(report.employability_score or 0)
    badge_x = w - margin - 50
    badge_y = margin + 20
    # Circulo o Rectangulo redondeado
    c.setFillColor(colors.HexColor("#2D3748"))
    c.roundRect(badge_x, badge_y, 40, 25, 10, fill=1, stroke=0)
    _draw_centered_text(c, badge_x + 20, badge_y + 8, f"{glob_score}%", font="Helvetica-Bold", size=12)
    
    c.showPage()
    
    # --- PÁGINA 2: Resumen, Datos, CV ---
    _draw_background(c)
    y = h - margin - 20
    
    # Resumen Ejecutivo (White box inverted? No, just text is fine or maybe a card look)
    # User image shows clean text on whitebg... wait. 
    # IF USER WANTS DARK THEME, I stick to dark.
    # Title
    _draw_text(c, margin, y, "Resumen ejecutivo", font="Helvetica-Bold", size=20)
    y -= 10
    c.setStrokeColor(colors.grey)
    c.line(margin, y, w-margin, y)
    y -= 20
    
    profile_summary = report.profile_summary or "No hay resumen disponible."
    y = _draw_wrapped_text(c, margin, y, profile_summary, printable_w, size=11, leading=16)
    
    y -= 30
    
    # Datos personales
    _draw_text(c, margin, y, "Datos personales", font="Helvetica-Bold", size=20)
    y -= 10
    c.line(margin, y, w-margin, y)
    y -= 20
    
    pd = report.personal_data
    datos = [
        f"Nombre: {pd.name}",
        f"Ubicación: {pd.location}",
        f"Email: {pd.email}",
        f"Teléfono: {pd.phone}",
        f"LinkedIn: {pd.linkedin or 'No especificado'}"
    ]
    y = _draw_bulleted_list(c, margin, y, datos, printable_w)
    
    y -= 30
    
    # Resumen del CV
    _draw_text(c, margin, y, "Resumen del CV", font="Helvetica-Bold", size=20)
    y -= 10
    c.line(margin, y, w-margin, y)
    y -= 20
    
    _draw_text(c, margin, y, "Experiencia (selección)", font="Helvetica-Bold", size=12)
    y -= 15
    cv_dets = report.cv_details or {}
    exps = cv_dets.get("experience") or []
    y = _draw_bulleted_list(c, margin, y, exps[:5], printable_w) # Limit to 5
    
    # Badge (Global Score again usually on every page bottom right)
    badge_x = w - margin - 40
    badge_y = margin
    c.setFillColor(colors.HexColor("#2D3748"))
    c.roundRect(badge_x, badge_y, 35, 20, 8, fill=1, stroke=0)
    _draw_centered_text(c, badge_x + 17.5, badge_y + 6, f"{glob_score}%", font="Helvetica-Bold", size=10)
    
    c.showPage()
    
    # --- PÁGINA 3: Áreas de mejora ---
    _draw_background(c)
    y = h - margin - 20
    
    _draw_text(c, margin, y, "Áreas de mejora priorizadas", font="Helvetica-Bold", size=20)
    y -= 10
    c.line(margin, y, w-margin, y)
    y -= 20
    
    # Listado con acción
    imps = rep_dict.get("improvement_areas") or []
    if not imps:
        # Fallback to soft skills < 50
        imps = [{"name": s["skill"], "score": s["score"], "action": "Definir plan de práctica diaria."} for s in soft_skills if s["score"] < 60]
    
    for item in imps:
        nm = ""
        act = ""
        sc = ""
        if isinstance(item, dict):
            nm = item.get("area") or item.get("name") or "Área"
            act = item.get("suggested_action") or item.get("action") or ""
            sc = item.get("score")
        else:
            nm = str(item)
            
        # Draw block
        _draw_text(c, margin, y, f"• {nm}: ({sc}/100)", font="Helvetica-Bold", size=11)
        y -= 15
        if act:
            y = _draw_wrapped_text(c, margin + 10, y, f"Acción: {act}", printable_w - 10, size=10)
        y -= 15
        
    c.showPage()
    
    # --- PÁGINA 4: Fortalezas y Detalles ---
    _draw_background(c)
    y = h - margin - 20
    
    _draw_text(c, margin, y, "Fortalezas clave", font="Helvetica-Bold", size=20)
    y -= 10
    c.line(margin, y, w-margin, y)
    y -= 20
    
    strs = rep_dict.get("strengths") or []
    y = _draw_bulleted_list(c, margin, y, strs, printable_w)
    
    y -= 30
    _draw_text(c, margin, y, "Herramientas / Software", font="Helvetica-Bold", size=16)
    y -= 15
    tools = cv_dets.get("tools") or []
    y = _draw_bulleted_list(c, margin, y, tools, printable_w)
    
    c.showPage()
    
    return buf.getvalue()