# backend/pdf_service.py 
import io
import os
from typing import List, Dict, Any, Optional
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, KeepTogether, PageTemplate, Frame, PageBreak
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.pdfgen import canvas

try:
    from backend.new_report_schema import NewReportSchema
except ImportError:
    from new_report_schema import NewReportSchema

# --- CONFIGURACIÓN CORPORATIVA ---
COLOR_PRIMARY = colors.HexColor("#0f172a") # Slate 900
COLOR_ACCENT = colors.HexColor("#38bdf8")  # Sky 400
COLOR_P2 = colors.HexColor("#374BA6")      # Corporate Blue
COLOR_BG_BOX = colors.HexColor("#E6F0FF")  # Light Blue Box
COLOR_TEXT_MAIN = colors.HexColor("#1e293b")
COLOR_TEXT_LIGHT = colors.HexColor("#64748b")
COLOR_WHITE = colors.white

def create_drawing(data: List[Dict[str, Any]], width=150, height=150):
    """Genera el gráfico Radar vectorial (SpiderChart)."""
    d = Drawing(width, height)
    chart = SpiderChart()
    chart.x = (width - chart.width) / 2 
    chart.y = (height - chart.height) / 2 
    chart.width = width * 0.7
    chart.height = height * 0.7
    
    # Procesar datos (top 6 skills)
    sorted_data = sorted(data, key=lambda x: x.get('score', 0), reverse=True)[:6]
    
    if not sorted_data:
        sorted_data = [{"skill": "General", "score": 50}]

    labels = [d.get('skill', '')[:12] for d in sorted_data]
    data_points = [d.get('score', 0) for d in sorted_data]
    
    chart.data = [data_points]
    chart.labels = labels
    chart.strands[0].strokeColor = COLOR_ACCENT
    chart.strands[0].fillColor = colors.Color(55/255, 75/255, 166/255, alpha=0.4) 
    chart.strands[0].strokeWidth = 2
    
    chart.spokes.strokeColor = colors.HexColor("#cbd5e1")
    chart.strandLabels.fontName = "Helvetica"
    chart.strandLabels.fontSize = 8
    
    d.add(chart)
    return d

def header_footer(canvas, doc):
    """Template para Cabecera y Pie de Página en todas las páginas."""
    canvas.saveState()
    
    # Cabecera
    canvas.setFont("Helvetica-Bold", 14)
    canvas.setFillColor(COLOR_P2)
    canvas.drawString(20*mm, A4[1] - 15*mm, "Teamworkz")
    
    # Título alternativo en cabecera
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(COLOR_TEXT_LIGHT)
    canvas.drawRightString(A4[0] - 20*mm, A4[1] - 15*mm, "Informe de Empleabilidad 360°")
    
    # Línea separadora header
    canvas.setStrokeColor(colors.HexColor("#e2e8f0"))
    canvas.line(20*mm, A4[1] - 18*mm, A4[0] - 20*mm, A4[1] - 18*mm)
    
    # Pie de Página
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(COLOR_TEXT_LIGHT)
    canvas.drawString(20*mm, 10*mm, f"Generado el {date.today().strftime('%d/%m/%Y')}")
    canvas.drawRightString(A4[0] - 20*mm, 10*mm, f"Página {doc.page}")
    
    canvas.restoreState()

def create_employability_pdf(report: NewReportSchema) -> bytes:
    """Función principal que genera el PDF usando Platypus."""
    buffer = io.BytesIO()
    
    # Configurar documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=25*mm,
        bottomMargin=20*mm
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo Título Principal
    style_title = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=COLOR_P2,
        alignment=TA_CENTER,
        spaceAfter=15*mm
    )
    
    # Estilo H2 (Secciones) - CORREGIDO BORDER PADDING
    style_h2 = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=COLOR_PRIMARY,
        spaceBefore=10*mm,
        spaceAfter=5*mm,
        borderPadding=4,
        borderColor=COLOR_ACCENT,
        borderWidth=0
    )
    
    # Estilo Normal
    style_normal = ParagraphStyle(
        'NormalCustom',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COLOR_TEXT_MAIN,
        leading=14,
        alignment=TA_JUSTIFY
    )
    
    # Estilo Caja Azul (Mensaje Final)
    style_blue_box = ParagraphStyle(
        'BlueBox',
        parent=styles['Normal'],
        fontSize=11,
        textColor=COLOR_P2,
        backColor=COLOR_BG_BOX,
        borderColor=COLOR_P2,
        borderWidth=1,
        borderPadding=15,
        alignment=TA_CENTER,
        leading=16,
        spaceBefore=10*mm
    )

    story = []
    
    # --- PÁGINA 1: PORTADA / DASHBOARD ---
    story.append(Paragraph("PERFIL DE COMPETENCIAS PROFESIONALES", style_title))
    
    # Datos Personales (Tabla)
    p_data = [
        [f"NOMBRE: {report.datos_personales.nombre}", f"UBICACIÓN: {report.datos_personales.ubicacion}"],
        [f"EMAIL: {report.datos_personales.email or 'No consta'}", f"TELÉFONO: {report.datos_personales.telefono or 'No consta'}"]
    ]
    t_personal = Table(p_data, colWidths=[90*mm, 80*mm])
    t_personal.setStyle(TableStyle([
        ('TEXTCOLOR', (0,0), (-1,-1), COLOR_TEXT_MAIN),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
    ]))
    story.append(t_personal)
    story.append(Spacer(1, 10*mm))
    
    # Score y Nivel
    score = report.employability_score or 0
    story.append(Paragraph(f"<b>PUNTUACIÓN DE EMPLEABILIDAD: {score}/100</b>", 
                           ParagraphStyle('Score', parent=style_normal, alignment=TA_CENTER, textColor=COLOR_ACCENT, fontSize=14)))
    story.append(Spacer(1, 10*mm))

    # Dos columnas: Radar (Izq) y Resumen (Der)
    radar = create_drawing(report.soft_skills or [], width=150, height=150)
    resumen_text = Paragraph(f"<b>RESUMEN EJECUTIVO:</b><br/><br/>{report.resumen_ejecutivo}", style_normal)
    
    t_summary = Table([[radar, resumen_text]], colWidths=[60*mm, 110*mm])
    t_summary.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 15*mm))
    
    # Entornos Ideales
    story.append(Paragraph("ENTORNOS DE TRABAJO IDEALES", style_h2))
    for env in report.entornos_ideales:
        story.append(Paragraph(f"• {env}", style_normal))
    
    # --- PÁGINA 2: ANÁLISIS DETALLADO ---
    story.append(Paragraph("ANÁLISIS FODA PERSONALIZADO", style_h2))
    
    # Fortalezas
    story.append(Paragraph("<b>FORTALEZAS CLAVE</b>", style_normal))
    for f in report.analisis_foda.fortalezas_clave:
        story.append(Paragraph(f"• {f}", style_normal))
    story.append(Spacer(1, 5*mm))
    
    # Áreas de Mejora
    story.append(Paragraph("<b>ÁREAS DE MEJORA PRIORITARIAS</b>", style_normal))
    for idx, area in enumerate(report.analisis_foda.areas_mejora):
        story.append(Paragraph(f"{idx+1}. {area}", style_normal))
    story.append(Spacer(1, 10*mm))
    
    # Análisis CV
    story.append(KeepTogether([
        Paragraph("ANÁLISIS TÉCNICO DEL CV", style_h2),
        Paragraph(report.analisis_detallado_cv, style_normal)
    ]))
    story.append(Spacer(1, 10*mm))
    
    # Roles Sugeridos (Tabla)
    story.append(Paragraph("ROLES SUGERIDOS", style_h2))
    
    roles_data = [["ROL", "AJUSTE", "JUSTIFICACIÓN"]]
    for r in report.roles_sugeridos:
        roles_data.append([
            Paragraph(r.rol, style_normal),
            r.ajuste,
            Paragraph(r.justificacion, style_normal)
        ])
        
    t_roles = Table(roles_data, colWidths=[40*mm, 25*mm, 105*mm])
    t_roles.setStyle(TableStyle([
        ('TEXTCOLOR', (0,0), (-1,0), COLOR_WHITE),
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY), 
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f5f9")]),
    ]))
    story.append(t_roles)
    
    story.append(PageBreak())
    
    # --- PÁGINA 3: PLAN DE ACCIÓN ---
    story.append(Paragraph("PLAN DE ACCIÓN ESTRATÉGICO", style_h2))
    
    # Pasos
    p_steps = [Paragraph(f"✅ {paso}", style_normal) for paso in report.plan_accion.pasos]
    story.append(Paragraph("<b>PASOS CLAVE:</b>", style_normal))
    for p in p_steps:
        story.append(p)
     
    story.append(Spacer(1, 5*mm))
    
    # Herramientas
    story.append(Paragraph(f"<b>HERRAMIENTAS:</b> {', '.join(report.plan_accion.herramientas)}", style_normal))
    story.append(Spacer(1, 5*mm))
    
    # Kit Búsqueda
    story.append(Paragraph("KIT DE BÚSQUEDA", style_h2))
    
    story.append(Paragraph("<b>TITULAR LINKEDIN SUGERIDO:</b>", style_normal))
    story.append(Paragraph(report.kit_busqueda.frases_linkedin.get("titular", ""), 
                           ParagraphStyle('Italic', parent=style_normal, fontName='Helvetica-Oblique')))
    story.append(Spacer(1, 5*mm))
    
    story.append(Paragraph("<b>EXTRACTO (ACERCA DE):</b>", style_normal))
    story.append(Paragraph(report.kit_busqueda.frases_linkedin.get("acerca_de", ""), 
                           ParagraphStyle('Italic', parent=style_normal, fontName='Helvetica-Oblique')))
    
    story.append(Spacer(1, 15*mm))
    
    # Mensaje Final (Blue Box)
    story.append(KeepTogether([
        Paragraph(report.mensaje_final_azul, style_blue_box)
    ]))

    # Generar PDF
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    
    return buffer.getvalue()
