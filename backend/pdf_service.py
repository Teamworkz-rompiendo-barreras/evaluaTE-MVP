# backend/pdf_service.py
"""
Generación de PDF del informe de empleabilidad.

Sustituye al renderizado con Playwright/Chromium (incompatible con el
runtime serverless de Vercel: no se puede empaquetar ni lanzar un
navegador completo dentro de una función). En su lugar, el PDF se
construye directamente a partir del JSON estructurado del informe con
reportlab (librería pura Python, sin binarios externos).

Paleta de color: la misma definida como marca en
`nuevo-frontend/tailwind.config.js` (verde Teamworkz), ya auditada para
accesibilidad -- todos los ratios de contraste indicados ahí (>=4.5:1 sobre
blanco) se mantienen aquí. No usar ningún color que no venga de esa paleta.
"""
import logging
import re
from datetime import datetime
from io import BytesIO
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Paleta de marca (azul EvalúaTE, la misma que usa ResultadosPage.tsx) --
# reportlab's mini-XML de <font color="..."> exige "#RRGGBB" o un nombre --
# Color.hexval() devuelve "0x..." y rompe el parseo, así que se guardan
# también las cadenas hex tal cual para usarlas dentro de <font>.
PRIMARY_HEX = "#374BA6"      # Azul principal (igual que ResultadosPage.tsx)
SECONDARY_HEX = "#2d3f96"    # Azul oscuro (hover de btn-primary en index.css)
ACCENT_HEX = "#2a3b8c"       # Azul más oscuro (active de btn-primary en index.css)
WARNING_HEX = "#b45309"      # 4.8:1 sobre blanco
ERROR_HEX = "#b91c1c"        # 5.9:1 sobre blanco
INFO_HEX = "#0369a1"         # 5.8:1 sobre blanco

PRIMARY = colors.HexColor(PRIMARY_HEX)
SECONDARY = colors.HexColor(SECONDARY_HEX)
ACCENT = colors.HexColor(ACCENT_HEX)
NEUTRAL_LIGHT = colors.HexColor("#F9F9F9")
NEUTRAL = colors.HexColor("#EAEAEA")
NEUTRAL_DARK = colors.HexColor("#1f2937")   # 15:1 sobre blanco
WARNING = colors.HexColor(WARNING_HEX)
ERROR = colors.HexColor(ERROR_HEX)
INFO = colors.HexColor(INFO_HEX)
WHITE = colors.white

BRAND_COLOR = PRIMARY  # alias retrocompatible

_styles = getSampleStyleSheet()
_styles.add(ParagraphStyle(
    name="CoverTitle", parent=_styles["Title"], textColor=WHITE, fontSize=22,
    leading=26, alignment=TA_LEFT, spaceAfter=2,
))
_styles.add(ParagraphStyle(
    name="CoverName", parent=_styles["Normal"], textColor=WHITE, fontSize=13,
    leading=16, alignment=TA_LEFT, spaceAfter=2,
))
_styles.add(ParagraphStyle(
    name="CoverMeta", parent=_styles["Normal"], textColor=colors.HexColor("#d1fae5"),
    fontSize=9, alignment=TA_LEFT,
))
_styles.add(ParagraphStyle(
    name="CoverScoreNumber", parent=_styles["Normal"], textColor=WHITE, fontSize=30,
    leading=32, alignment=TA_CENTER, fontName="Helvetica-Bold",
))
_styles.add(ParagraphStyle(
    name="CoverScoreLabel", parent=_styles["Normal"], textColor=colors.HexColor("#d1fae5"),
    fontSize=7.5, alignment=TA_CENTER, spaceBefore=2,
))
_styles.add(ParagraphStyle(
    name="ReportSubtitle", parent=_styles["Normal"], textColor=NEUTRAL_DARK, fontSize=10, spaceAfter=16,
))
_styles.add(ParagraphStyle(
    name="SectionBarTitle", parent=_styles["Heading2"], textColor=PRIMARY, fontSize=13.5,
    spaceBefore=0, spaceAfter=0, leading=16,
))
_styles.add(ParagraphStyle(
    name="SubSection", parent=_styles["Heading3"], textColor=NEUTRAL_DARK, fontSize=11,
    spaceBefore=8, spaceAfter=4,
))
_styles.add(ParagraphStyle(
    name="CardMeta", parent=_styles["Normal"], textColor=colors.HexColor("#4b5563"), fontSize=9,
    spaceAfter=2,
))
_styles.add(ParagraphStyle(
    name="Body", parent=_styles["Normal"], alignment=TA_LEFT, spaceAfter=6, leading=14, fontSize=10,
))
_styles.add(ParagraphStyle(
    name="BulletBody", parent=_styles["Normal"], leading=13, fontSize=10,
))
_styles.add(ParagraphStyle(
    name="FinalMessage", parent=_styles["Normal"], textColor=WHITE, fontSize=11.5,
    leading=17, alignment=TA_LEFT, fontName="Helvetica-BoldOblique",
))
_styles.add(ParagraphStyle(
    name="FinalMessageTitle", parent=_styles["Normal"], textColor=WHITE, fontSize=13.5,
    leading=16, fontName="Helvetica-Bold",
))
_styles.add(ParagraphStyle(
    name="FooterText", parent=_styles["Normal"], textColor=colors.HexColor("#6b7280"), fontSize=8,
))

CARD_PADDING = 10


# Mini-lenguaje de marcado que este módulo inserta a propósito (negrita,
# saltos de línea y color de texto) dentro de las cadenas que construye. Se
# "protegen" estas etiquetas exactas ANTES de escapar el resto del texto
# (que viene de JSON de IA o del motor determinista, texto plano de
# terceros) y se restauran después -- así no hace falta ir añadiendo una
# etiqueta nueva cada vez que aparece un caso roto, y cualquier otro
# `<`/`>` que venga en texto de terceros (nombre del candidato, contenido
# del CV...) se sigue escapando con seguridad.
_ALLOWED_TAGS_RE = re.compile(r'</?b>|<br\s*/?>|</font>|<font\s+[^<>]{1,60}>')


def _p(text: Any, style: str = "Body"):
    """Paragraph seguro: castea a str, protege el mini-marcado permitido
    (ver _ALLOWED_TAGS_RE) y escapa todo lo demás."""
    raw = "" if text is None else str(text)

    stashed: list = []

    def _stash(match: "re.Match[str]") -> str:
        stashed.append(match.group(0))
        return f"\x00{len(stashed) - 1}\x00"

    placeheld = _ALLOWED_TAGS_RE.sub(_stash, raw)
    safe_text = placeheld.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for i, tag in enumerate(stashed):
        safe_text = safe_text.replace(f"\x00{i}\x00", tag)

    return Paragraph(safe_text, _styles[style])


def _bullets(items: list, style: str = "BulletBody"):
    if not items:
        return None
    return ListFlowable(
        [ListItem(_p(item, style), leftIndent=6) for item in items if item],
        bulletType="bullet",
        start="•",
        leftIndent=14,
        bulletColor=SECONDARY,
    )


def _section_title(text: str):
    """Título de sección con una barra de color a la izquierda (el mismo
    lenguaje visual que `.report-section-title::before` en la web)."""
    bar_table = Table(
        [["", _p(text, "SectionBarTitle")]],
        colWidths=[0.14 * cm, None],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), ACCENT),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 0),
            ("LEFTPADDING", (1, 0), (1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]),
    )
    return KeepTogether([Spacer(1, 6), bar_table, Spacer(1, 10)])


def _card(flowables: list, bg=NEUTRAL_LIGHT, border=NEUTRAL, border_left: Optional[Any] = None):
    """Envuelve una lista de flowables en una tarjeta con fondo y borde,
    replicando el estilo `.role-card` / `.improvement-card` de la web."""
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.75, border),
        ("LEFTPADDING", (0, 0), (-1, -1), CARD_PADDING),
        ("RIGHTPADDING", (0, 0), (-1, -1), CARD_PADDING),
        ("TOPPADDING", (0, 0), (-1, -1), CARD_PADDING),
        ("BOTTOMPADDING", (0, 0), (-1, -1), CARD_PADDING),
    ]
    if border_left is not None:
        style_cmds.append(("LINEBEFORE", (0, 0), (0, -1), 3, border_left))
    table = Table([[flowables]], colWidths=[None], style=TableStyle(style_cmds))
    return KeepTogether([table, Spacer(1, 8)])


_DEMAND_HEX = {"ALTA": SECONDARY_HEX, "MEDIA-ALTA": SECONDARY_HEX, "MEDIA": WARNING_HEX, "BAJA": "#6b7280"}


def _demand_badge_text(value: str) -> str:
    hex_color = _DEMAND_HEX.get(str(value or "").upper(), "#6b7280")
    return f'Demanda laboral: <font color="{hex_color}"><b>{value}</b></font>'


def _cover_band(report: dict, candidate_name: str) -> Table:
    puntuacion = report.get("puntuacion_global")
    fecha = datetime.now().strftime("%d/%m/%Y")

    left_block = [
        _p("EVALÚATE · TEAMWORKZ", "CoverMeta"),
        Spacer(1, 4),
        _p("Informe de Empleabilidad", "CoverTitle"),
        _p(f"Candidato/a: {candidate_name}", "CoverName"),
        Spacer(1, 4),
        _p(f"Generado el {fecha} · Informe automático sin intervención de IA generativa", "CoverMeta"),
    ]

    if puntuacion is not None:
        right_block = [
            _p(f"{puntuacion}", "CoverScoreNumber"),
            _p("PUNTUACIÓN<br/>GLOBAL /100", "CoverScoreLabel"),
        ]
    else:
        right_block = [Spacer(1, 1)]

    band = Table(
        [[left_block, right_block]],
        colWidths=[12.5 * cm, 4.5 * cm],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("LEFTPADDING", (0, 0), (0, 0), 16),
            ("RIGHTPADDING", (0, 0), (0, 0), 8),
            ("LEFTPADDING", (1, 0), (1, 0), 8),
            ("RIGHTPADDING", (1, 0), (1, 0), 16),
            ("TOPPADDING", (0, 0), (-1, -1), 18),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
            ("LINEAFTER", (0, 0), (0, 0), 1, colors.HexColor("#ffffff33")),
        ]),
    )
    return band


_PERSONAL_DATA_LABELS = {
    "Nombre": "Nombre", "Ubicacion": "Ubicación", "Email": "Email",
    "Telefono": "Teléfono", "LinkedIn": "LinkedIn",
}


def _personal_data_table(datos: dict) -> Optional[Table]:
    if not datos:
        return None
    pares = [(k, v) for k, v in datos.items() if v]
    if not pares:
        return None
    rows = []
    for i in range(0, len(pares), 2):
        row = []
        for k, v in pares[i:i + 2]:
            label = _PERSONAL_DATA_LABELS.get(k, str(k))
            row.append([_p(f'<font size="7" color="#6b7280"><b>{label.upper()}</b></font><br/>{v}', "CardMeta")])
        if len(row) == 1:
            row.append("")
        rows.append(row)
    return Table(
        rows,
        colWidths=[8.5 * cm, 8.5 * cm],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), NEUTRAL_LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.5, NEUTRAL),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, NEUTRAL),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]),
    )


def _cv_scores_table(valoraciones: dict) -> Table:
    # Se evita el glifo de estrella (★/☆): no está garantizado en la
    # codificación WinAnsi de las fuentes base de reportlab/PDF y, aunque se
    # viera bien, un lector de pantalla no lo interpreta de forma fiable.
    # "N/5" en texto + puntos rellenos/vacíos (el mismo carácter de viñeta
    # "•" ya usado en las listas) es accesible y no depende de un glifo raro.
    labels = [("formato", "Formato"), ("claridad", "Claridad"), ("coherencia", "Coherencia"),
              ("info_clave", "Info. clave"), ("ortografia", "Ortografía")]
    header = [_p(f'<font color="#ffffff"><b>{lbl}</b></font>', "CardMeta") for _, lbl in labels]
    values = []
    for k, _ in labels:
        n = max(0, min(5, int(valoraciones.get(k, 0) or 0)))
        dots = ("•" * n) + ("·" * (5 - n))
        color = SECONDARY_HEX if n >= 4 else (WARNING_HEX if n == 3 else ERROR_HEX)
        values.append(_p(
            f'<font size="8" color="{color}">{dots}</font><br/>'
            f'<font size="11" color="{color}"><b>{n}/5</b></font>',
            "CardMeta",
        ))
    table = Table(
        [header, values],
        colWidths=[3.4 * cm] * 5,
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("BACKGROUND", (0, 1), (-1, 1), NEUTRAL_LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.5, NEUTRAL),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, NEUTRAL),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]),
    )
    return table


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(NEUTRAL)
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(2 * cm, 1.1 * cm, "EvalúaTE · Teamworkz")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Página {doc.page}")
    canvas.restoreState()


def build_report_pdf(report: dict, candidate_name: str = "Candidato") -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=2.2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title=f"Informe de Empleabilidad - {candidate_name}",
    )

    story: list = []

    story.append(_cover_band(report, candidate_name))
    story.append(Spacer(1, 16))

    datos_personales = report.get("datos_personales") or {}
    personal_table = _personal_data_table(datos_personales)
    if personal_table:
        story.append(personal_table)
        story.append(Spacer(1, 12))

    if report.get("interpretacion_global"):
        story.append(_p(report["interpretacion_global"]))
    if report.get("resumen_ejecutivo"):
        story.append(_section_title("Resumen Ejecutivo"))
        story.append(_p(report["resumen_ejecutivo"]))

    analisis_cv = report.get("analisis_cv") or {}
    if analisis_cv:
        story.append(_section_title("Análisis del CV"))
        if analisis_cv.get("resumen"):
            story.append(_p(analisis_cv["resumen"]))

        valoraciones = analisis_cv.get("valoraciones") or {}
        if valoraciones:
            story.append(Spacer(1, 4))
            story.append(_cv_scores_table(valoraciones))
            story.append(Spacer(1, 10))

        for label, key in (
            ("Experiencia", "experiencia"), ("Formación", "formacion"),
            ("Idiomas", "idiomas"), ("Software", "software"),
            ("Puntos fuertes", "puntos_fuertes"), ("Aspectos a mejorar", "aspectos_mejorar"),
        ):
            items = analisis_cv.get(key)
            if items:
                story.append(_p(label, "SubSection"))
                bullets = _bullets(items)
                if bullets:
                    story.append(bullets)

        if analisis_cv.get("ats_compatibilidad") is not None:
            story.append(_p(f"Compatibilidad ATS: <b>{analisis_cv['ats_compatibilidad']}/100</b>", "SubSection"))
            if analisis_cv.get("ats_explicacion"):
                story.append(_p(analisis_cv["ats_explicacion"]))

    perfil_competencias = report.get("perfil_competencias") or []
    if perfil_competencias:
        story.append(_section_title("Perfil de Competencias"))
        for categoria in perfil_competencias:
            story.append(_p(categoria.get("categoria", ""), "SubSection"))
            for comp in categoria.get("competencias", []) or []:
                linea = f"<b>{comp.get('nombre', '')}</b> — {comp.get('puntuacion', '-')}/100 ({comp.get('nivel', '')})"
                card_content = [_p(linea, "CardMeta")]
                if comp.get("explicacion"):
                    card_content.append(_p(comp["explicacion"], "BulletBody"))
                story.append(_card(card_content, bg=NEUTRAL_LIGHT, border=NEUTRAL, border_left=SECONDARY))

    fortalezas = report.get("fortalezas_principales") or []
    if fortalezas:
        story.append(_section_title("Fortalezas Principales"))
        for f in fortalezas:
            card_content = [_p(f.get("nombre", ""), "SubSection")]
            if f.get("explicacion_practica"):
                card_content.append(_p(f["explicacion_practica"], "BulletBody"))
            story.append(_card(card_content, bg=colors.HexColor("#f0fdf4"), border=colors.HexColor("#bbf7d0"), border_left=SECONDARY))

    areas_mejora = report.get("areas_mejora") or []
    if areas_mejora:
        story.append(_section_title("Áreas de Mejora"))
        for a in areas_mejora:
            card_content = [_p(a.get("nombre", ""), "SubSection")]
            if a.get("porque_afecta"):
                card_content.append(_p(a["porque_afecta"], "BulletBody"))
            if a.get("como_mejorar"):
                card_content.append(_p(f"<b>{a['como_mejorar']}</b>", "BulletBody"))
            acciones = _bullets(a.get("acciones_concretas"))
            if acciones:
                card_content.append(acciones)
            story.append(_card(card_content, bg=colors.HexColor("#fffbeb"), border=colors.HexColor("#fde68a"), border_left=WARNING))

    resultados_juegos = report.get("resultados_juegos") or []
    if resultados_juegos:
        story.append(_section_title("Resultados de las Evaluaciones"))
        for r in resultados_juegos:
            card_content = [_p(r.get("juego", ""), "SubSection")]
            for campo in ("que_mide", "resultado", "interpretacion", "aplicacion_entrevista"):
                if r.get(campo):
                    card_content.append(_p(r[campo], "BulletBody"))
            story.append(_card(card_content, bg=NEUTRAL_LIGHT, border=NEUTRAL, border_left=INFO))

    entornos = report.get("entornos_ideales") or []
    if entornos:
        story.append(_section_title("Entornos de Trabajo Ideales"))
        bullets = _bullets(entornos)
        if bullets:
            story.append(bullets)

    roles = report.get("roles_recomendados") or []
    if roles:
        story.append(_section_title("Roles Recomendados"))
        for rol in roles:
            titulo = f"{rol.get('titulo', '')} — {rol.get('nivel', '')} ({rol.get('modalidad', '')})"
            card_content = [_p(titulo, "SubSection")]
            if rol.get("por_que_encaja"):
                card_content.append(_p(rol["por_que_encaja"], "BulletBody"))
            if rol.get("demanda_laboral"):
                card_content.append(_p(_demand_badge_text(rol["demanda_laboral"]), "BulletBody"))
            story.append(_card(card_content, bg=NEUTRAL_LIGHT, border=NEUTRAL, border_left=PRIMARY))

    plan_accion = report.get("plan_accion") or {}
    if plan_accion:
        story.append(_section_title("Plan de Acción"))
        phase_colors = {
            "dias_30": (colors.HexColor("#ecfdf5"), colors.HexColor("#6ee7b7"), SECONDARY_HEX, SECONDARY),
            "dias_60": (colors.HexColor("#eff6ff"), colors.HexColor("#93c5fd"), INFO_HEX, INFO),
            "dias_90": (colors.HexColor("#f5f3ff"), colors.HexColor("#c4b5fd"), "#7c3aed", colors.HexColor("#7c3aed")),
        }
        for label, key in (("Próximos 30 días", "dias_30"), ("Próximos 60 días", "dias_60"), ("Próximos 90 días", "dias_90")):
            items = plan_accion.get(key)
            if items:
                bg, border, accent_hex, accent = phase_colors[key]
                card_content = [_p(f'<font color="{accent_hex}"><b>{label.upper()}</b></font>', "CardMeta")]
                bullets = _bullets(items)
                if bullets:
                    card_content.append(bullets)
                story.append(_card(card_content, bg=bg, border=border, border_left=accent))

    estrategia = report.get("estrategia_busqueda") or []
    if estrategia:
        story.append(_section_title("Estrategia de Búsqueda"))
        bullets = _bullets(estrategia)
        if bullets:
            story.append(bullets)

    herramientas = report.get("herramientas_recomendadas") or []
    if herramientas:
        story.append(_section_title("Herramientas Recomendadas"))
        for h in herramientas:
            story.append(_p(f"<b>{h.get('nombre', '')}</b>: {h.get('para_que_sirve', '')}", "BulletBody"))

    recomendaciones = report.get("recomendaciones_personalizadas") or []
    if recomendaciones:
        story.append(_section_title("Recomendaciones Personalizadas"))
        bullets = _bullets(recomendaciones)
        if bullets:
            story.append(bullets)

    recursos = report.get("recursos_adicionales") or []
    if recursos:
        story.append(_section_title("Recursos Adicionales"))
        for rec in recursos:
            story.append(_p(f"<b>{rec.get('nombre', '')}</b> ({rec.get('tipo', '')})", "BulletBody"))
            if rec.get("descripcion"):
                story.append(_p(rec["descripcion"], "BulletBody"))

    if report.get("mensaje_final"):
        story.append(PageBreak())
        story.append(_card(
            [_p("VEREDICTO DE ORIENTACIÓN", "FinalMessageTitle"), Spacer(1, 8),
             _p(report["mensaje_final"], "FinalMessage")],
            bg=PRIMARY, border=PRIMARY,
        ))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()


@router.post("/api/export-pdf")
async def export_pdf(request: Request):
    try:
        body = await request.json()
    except Exception as json_err:
        logger.error(f"Fallo al parsear el JSON de export-pdf: {json_err}")
        raise HTTPException(status_code=400, detail="Payload corrupto")

    report = body.get("report")
    candidate_name = body.get("candidate_name") or "Candidato"

    if not report or not isinstance(report, dict):
        raise HTTPException(status_code=400, detail="No se proporcionó el informe a exportar")

    try:
        pdf_bytes = build_report_pdf(report, candidate_name)
    except Exception as e:
        logger.exception(f"Fallo generando PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Fallo de generación de PDF: {str(e)}")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Informe_EvaluaTE_{candidate_name.replace(' ', '_')}.pdf"}
    )
