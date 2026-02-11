# backend/pdf_service.py
import math
from datetime import date
from io import BytesIO
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

try:
    from backend.new_report_schema import NewReportSchema
except ImportError:
    from new_report_schema import NewReportSchema

# --- Configuración de Estilo (Tema Oscuro Profesional) ---
BG_COLOR = colors.HexColor("#0f172a")     # Slate 900 (Fondo principal)
CARD_BG_COLOR = colors.HexColor("#1e293b") # Slate 800 (Fondo tarjetas)
TEXT_PRIMARY = colors.white
TEXT_SECONDARY = colors.HexColor("#94a3b8") # Slate 400
ACCENT_COLOR = colors.HexColor("#38_bdf8")  # Sky 400 (Azul claro vibrante)
GOLD_COLOR = colors.HexColor("#facc15")     # Yellow 400
SUCCESS_COLOR = colors.HexColor("#4ade80")
WARNING_COLOR = colors.HexColor("#fbbf24")
DANGER_COLOR = colors.HexColor("#f87171")

MARGIN = 20 * mm
PAGE_W, PAGE_H = A4

def _draw_background(c: canvas.Canvas):
    c.saveState()
    c.setFillColor(BG_COLOR)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    
    # Decoración sutil (header bar)
    c.setFillColor(colors.HexColor("#1e293b"))
    c.rect(0, PAGE_H - 18*mm, PAGE_W, 18*mm, stroke=0, fill=1)
    
    # Footer bar
    c.rect(0, 0, PAGE_W, 12*mm, stroke=0, fill=1)
    c.restoreState()

def _draw_header(c: canvas.Canvas, title: str = "INFORME DE EMPLEABILIDAD"):
    c.saveState()
    # Logo text
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(TEXT_PRIMARY)
    c.drawString(MARGIN, PAGE_H - 12*mm, "Teamworkz")
    
    c.setFont("Helvetica", 12)
    c.setFillColor(TEXT_SECONDARY)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 12*mm, title)
    c.restoreState()

def _draw_footer(c: canvas.Canvas, page_num: int):
    c.saveState()
    c.setFont("Helvetica", 9)
    c.setFillColor(TEXT_SECONDARY)
    c.drawString(MARGIN, 5*mm, f"Generado el {date.today().strftime('%d/%m/%Y')}")
    c.drawRightString(PAGE_W - MARGIN, 5*mm, f"Página {page_num}")
    c.restoreState()

def _draw_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: Optional[str] = None):
    """Dibuja un fondo tipo tarjeta redondeada."""
    c.saveState()
    c.setFillColor(CARD_BG_COLOR)
    # roundRect(x, y, width, height, radius)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=0)
    
    if title:
        c.setFillColor(ACCENT_COLOR) # Título en acento
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + 5*mm, y + h - 8*mm, title.upper())
        # Línea separadora
        c.setStrokeColor(colors.HexColor("#334155"))
        c.setLineWidth(1)
        c.line(x + 5*mm, y + h - 11*mm, x + w - 5*mm, y + h - 11*mm)
    
    c.restoreState()

def _wrapped_text(c: canvas.Canvas, text: str, x: float, y: float, max_w: float, 
                  font="Helvetica", size=10, color=TEXT_SECONDARY, leading=14) -> float:
    """Dibuja texto multilínea y retorna la nueva posición Y."""
    if not text: return y
    
    # Usar Paragraph para mejor manejo de texto
    estilos = getSampleStyleSheet()
    estilo = ParagraphStyle(
        'Custom',
        parent=estilos['Normal'],
        fontName=font,
        fontSize=size,
        textColor=color,
        leading=leading,
        alignment=TA_LEFT
    )
    
    p = Paragraph(text.replace("\n", "<br/>"), estilo)
    w, h = p.wrap(max_w, PAGE_H) # Altura disponible arbitraria grande
    p.drawOn(c, x, y - h)
    return y - h

def _draw_skill_bar(c: canvas.Canvas, x: float, y: float, w: float, name: str, score: int):
    c.saveState()
    h = 6*mm
    
    # Nombre
    c.setFont("Helvetica", 9)
    c.setFillColor(TEXT_PRIMARY)
    c.drawString(x, y + 2*mm, name)
    
    # Barra fondo
    bar_x = x + 50*mm
    bar_w = w - 60*mm
    c.setFillColor(colors.HexColor("#334155"))
    c.roundRect(bar_x, y, bar_w, h, 3, fill=1, stroke=0)
    
    # Barra progreso
    progress = max(0, min(100, score))
    fill_w = bar_w * (progress / 100)
    
    # Color según score
    fill_color = SUCCESS_COLOR if score >= 75 else (WARNING_COLOR if score >= 50 else DANGER_COLOR)
    c.setFillColor(fill_color)
    c.roundRect(bar_x, y, fill_w, h, 3, fill=1, stroke=0)
    
    # Texto score
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(TEXT_PRIMARY)
    c.drawRightString(bar_x + bar_w + 8*mm, y + 1.5*mm, f"{score}%")
    
    c.restoreState()

def draw_radar_chart(c, data: List[Dict[str, Any]], cx, cy, radius=50):
    """Dibuja un gráfico de radar hexagonal."""
    if not data: return
    
    # Asegurar que hay datos
    if len(data) < 3: return
    
    # Limitar a top 6 para limpieza visual
    if not isinstance(data, list): data = list(data)
    sorted_data = sorted(data, key=lambda x: x.get("score", 0), reverse=True)
    data = sorted_data[:6]
    n = len(data)
    angle_step = 2 * math.pi / n
    
    c.saveState()
    
    # Ejes y fondo
    c.setStrokeColor(colors.HexColor("#475569"))
    c.setLineWidth(0.5)
    
    # Anillos concéntricos (20%, 40%, 60%, 80%, 100%)
    for i in range(1, 6):
        level_r = radius * (i/5)
        path = c.beginPath()
        for j in range(n):
            ang = j * angle_step - math.pi/2
            px = cx + level_r * math.cos(ang)
            py = cy + level_r * math.sin(ang)
            if j == 0: path.moveTo(px, py)
            else: path.lineTo(px, py)
        path.close()
        c.drawPath(path, stroke=1, fill=0)
    
    # Ejes radiales y etiquetas
    c.setFont("Helvetica", 7)
    c.setFillColor(TEXT_SECONDARY)
    
    value_points = []
    
    for j in range(n):
        ang = j * angle_step - math.pi/2
        
        # Eje
        end_x = cx + radius * math.cos(ang)
        end_y = cy + radius * math.sin(ang)
        c.line(cx, cy, end_x, end_y)
        
        # Etiqueta
        lbl_r = radius + 12
        lbl_x = cx + lbl_r * math.cos(ang)
        lbl_y = cy + lbl_r * math.sin(ang)
        
        # Ajuste alineación
        align = TA_CENTER
        item = data[j]
        c.saveState() # Para texto
        # Simple drawString centrado manual
        c.drawCentredString(lbl_x, lbl_y, item.get("skill", "")[:15])
        c.restoreState()
        
        # Punto de valor
        score = item.get("score", 0)
        val_r = radius * (score / 100)
        val_x = cx + val_r * math.cos(ang)
        val_y = cy + val_r * math.sin(ang)
        value_points.append((val_x, val_y))
        
    # Polígono de valores
    if value_points:
        path = c.beginPath()
        # Ensure value_points is indexable
        vp_list = list(value_points)
        path.moveTo(vp_list[0][0], vp_list[0][1])
        for p in vp_list[1:]:
            path.lineTo(p[0], p[1])
        path.close()
        
        # Relleno semi-transparente
        c.setFillColor(colors.Color(56/255, 189/255, 248/255, alpha=0.4)) # Sky 400 with alpha
        c.setStrokeColor(ACCENT_COLOR)
        c.setLineWidth(2)
        c.drawPath(path, fill=1, stroke=1)
        
        # Puntos
        c.setFillColor(ACCENT_COLOR)
        for p in value_points:
            c.circle(p[0], p[1], 2, fill=1, stroke=0)
            
    c.restoreState()


def create_employability_pdf(report: NewReportSchema) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setTitle(f"Informe Empleabilidad - {report.personal_data.name}")
    
    # --- PÁGINA 1: Dashboard Principal ---
    _draw_background(c)
    _draw_header(c)
    
    # Título Principal
    y_cursor = PAGE_H - 40*mm
    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(PAGE_W/2, y_cursor, "PERFIL DE COMPETENCIAS PROFESIONALES")
    
    # Datos Candidato (Tarjeta Superior)
    y_cursor -= 15*mm
    card_h = 45*mm
    _draw_card(c, MARGIN, y_cursor - card_h, PAGE_W - 2*MARGIN, card_h, "DATOS PERSONALES")
    
    # Contenido Datos
    content_y = y_cursor - 18*mm
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(TEXT_PRIMARY)
    c.drawString(MARGIN + 10*mm, content_y, report.personal_data.name)
    
    c.setFont("Helvetica", 10)
    c.setFillColor(TEXT_SECONDARY)
    # Columna 1
    c.drawString(MARGIN + 10*mm, content_y - 8*mm, f"📍 {report.personal_data.location}")
    c.drawString(MARGIN + 10*mm, content_y - 14*mm, f"📧 {report.personal_data.email}")
    # Columna 2
    c.drawString(PAGE_W/2, content_y - 8*mm, f"📞 {report.personal_data.phone}")
    c.drawString(PAGE_W/2, content_y - 14*mm, f"🔗 {report.personal_data.linkedin or 'No disponible'}")
    
    # Score Global (Badge)
    score = report.employability_score or 75
    score_color = SUCCESS_COLOR if score >= 70 else (WARNING_COLOR if score >= 50 else DANGER_COLOR)
    c.setFillColor(score_color)
    c.circle(PAGE_W - MARGIN - 25*mm, y_cursor - 22*mm, 18*mm, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(PAGE_W - MARGIN - 25*mm, y_cursor - 20*mm, f"{score}%")
    c.setFont("Helvetica", 7)
    c.drawCentredString(PAGE_W - MARGIN - 25*mm, y_cursor - 28*mm, "EMPLEABILIDAD")
    
    y_cursor -= (card_h + 10*mm)
    
    # Resumen Perfil
    summary_h = 35*mm
    _draw_card(c, MARGIN, y_cursor - summary_h, PAGE_W - 2*MARGIN, summary_h, "RESUMEN EJECUTIVO")
    _wrapped_text(c, report.profile_summary, MARGIN + 5*mm, y_cursor - 15*mm, PAGE_W - 2*MARGIN - 10*mm)
    
    y_cursor -= (summary_h + 10*mm)
    
    # Dos columnas: Radar (Izq) y Soft Skills (Der)
    col_w = (PAGE_W - 2*MARGIN - 10*mm) / 2
    chart_h = 80*mm
    
    # Tarjeta Izq: Radar
    _draw_card(c, MARGIN, y_cursor - chart_h, col_w, chart_h, "MAPA DE HABILIDADES")
    # Centro del radar relativo a la tarjeta
    rx = MARGIN + col_w/2
    ry = y_cursor - chart_h/2 - 5*mm
    draw_radar_chart(c, report.soft_skills or [], rx, ry, 25*mm)
    
    # Tarjeta Der: Top Skills
    _draw_card(c, MARGIN + col_w + 10*mm, y_cursor - chart_h, col_w, chart_h, "COMPETENCIAS CLAVE")
    
    skill_y = y_cursor - 18*mm
    # Ordenar y tomar top 5
    soft_skills: List[Dict[str, Any]] = report.soft_skills or []
    if not isinstance(soft_skills, list): soft_skills = list(soft_skills)
    sorted_skills = sorted(soft_skills, key=lambda x: x.get("score", 0), reverse=True)
    top_skills = sorted_skills[:5]
    for sk in top_skills:
        _draw_skill_bar(c, MARGIN + col_w + 15*mm, skill_y, col_w - 10*mm, sk.get("skill", "")[:20], sk.get("score", 0))
        skill_y -= 12*mm
        
    _draw_footer(c, 1)
    c.showPage()
    
    # --- PÁGINA 2: Diagnóstico y Análisis CV ---
    _draw_background(c)
    _draw_header(c)
    y_cursor = PAGE_H - 30*mm
    
    _draw_card(c, MARGIN, y_cursor - 70*mm, PAGE_W - 2*MARGIN, 70*mm, "ANÁLISIS TÉCNICO DEM CV")
    
    # Scores del análisis (Estrellas / Barras)
    an = report.cv_analysis
    metrics = [
        ("Estructura", an.structure_score),
        ("Claridad", an.clarity_score),
        ("Contenido", an.key_info_score),
        ("Coherencia", an.coherence_score),
        ("Estilo", an.style_score),
    ]
    
    met_y = y_cursor - 20*mm
    col_gap = 60*mm
    for i, (label, val) in enumerate(metrics):
        # Dibujar estrellas
        x_pos = MARGIN + 10*mm + (i % 2) * 90*mm 
        y_pos = met_y - (i // 2) * 15*mm
        
        c.setFillColor(TEXT_PRIMARY)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_pos, y_pos, f"{label}:")
        
        # Estrellas de 5 ptos
        for st in range(5):
            sx = x_pos + 25*mm + st*5*mm
            c.setFillColor(GOLD_COLOR if st < val else colors.HexColor("#475569"))
            c.circle(sx, y_pos + 1*mm, 1.5*mm, fill=1, stroke=0)
            
    # Feedback texto
    feed_y = met_y - 45*mm
    c.setFillColor(TEXT_SECONDARY)
    c.setFont("Helvetica-Oblique", 9)
    # Usamos cv_summary como feedback general o evidence
    feedback_text = f"Observaciones: {report.cv_summary[:300]}..."
    _wrapped_text(c, feedback_text, MARGIN + 10*mm, feed_y, PAGE_W - 2*MARGIN - 20*mm)

    y_cursor -= (80*mm)
    
    # Áreas de Mejora
    improve_h = 100*mm
    _draw_card(c, MARGIN, y_cursor - improve_h, PAGE_W - 2*MARGIN, improve_h, "ÁREAS DE MEJORA PRIORITARIAS")
    
    im_y = y_cursor - 20*mm
    for item in report.improvement_areas[:4]: # Max 4
        c.setFillColor(DANGER_COLOR)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN + 10*mm, im_y, f"• {item.area}")
        
        new_y = _wrapped_text(c, f"Acción: {item.suggested_action}", MARGIN + 15*mm, im_y - 5*mm, PAGE_W - 2*MARGIN - 30*mm, size=9)
        im_y = new_y - 8*mm
        
    _draw_footer(c, 2)
    c.showPage()
    
    # --- PÁGINA 3: Plan de Acción y Roles ---
    _draw_background(c)
    _draw_header(c)
    y_cursor = PAGE_H - 30*mm
    
    # Roles Sugeridos
    roles_h = 60*mm
    _draw_card(c, MARGIN, y_cursor - roles_h, PAGE_W - 2*MARGIN, roles_h, "ROLES RECOMENDADOS")
    
    r_y = y_cursor - 20*mm
    for role in report.suggested_roles[:3]:
        c.setFillColor(ACCENT_COLOR)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN + 10*mm, r_y, f"Role: {role.role} ({role.seniority})")
        
        c.setFillColor(TEXT_SECONDARY)
        c.setFont("Helvetica", 9)
        c.drawRightString(PAGE_W - MARGIN - 10*mm, r_y, "Remoto: Sí" if role.remote_viable else "Remoto: No")
        
        new_y = _wrapped_text(c, role.reason, MARGIN + 10*mm, r_y - 5*mm, PAGE_W - 2*MARGIN - 20*mm, size=9)
        r_y = new_y - 8*mm
        
    y_cursor -= (roles_h + 10*mm)
    
    # Plan de Acción
    plan_h = 120*mm
    _draw_card(c, MARGIN, y_cursor - plan_h, PAGE_W - 2*MARGIN, plan_h, "PLAN DE ACCIÓN (30-60-90 DÍAS)")
    
    p_y = y_cursor - 15*mm
    
    # 3 Columnas conceptuales o bloques apilados
    periods = [
        ("CORTO PLAZO (0-30 Días)", report.action_plan.short_term),
        ("MEDIO PLAZO (30-60 Días)", report.action_plan.medium_term),
        ("LARGO PLAZO (60-90+ Días)", report.action_plan.long_term),
    ]
    
    for title, items in periods:
        c.setFillColor(TEXT_PRIMARY)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN + 10*mm, p_y, title)
        p_y -= 5*mm
        
        for it in items[:3]: # Limit 3 bullet points
            p_y = _wrapped_text(c, f"• {it}", MARGIN + 15*mm, p_y, PAGE_W - 2*MARGIN - 30*mm, size=9)
            p_y -= 2*mm
        p_y -= 5*mm

    _draw_footer(c, 3)
    c.showPage()
    
    c.save()
    return buffer.getvalue()