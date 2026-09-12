# backend/pdf_service.py
"""
Generación de PDF del informe de empleabilidad.

Sustituye al renderizado con Playwright/Chromium (incompatible con el
runtime serverless de Vercel: no se puede empaquetar ni lanzar un
navegador completo dentro de una función). En su lugar, el PDF se
construye directamente a partir del JSON estructurado del informe con
reportlab (librería pura Python, sin binarios externos).
"""
import logging
from io import BytesIO
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
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

BRAND_COLOR = colors.HexColor("#2148C0")
MUTED_COLOR = colors.HexColor("#555555")

_styles = getSampleStyleSheet()
_styles.add(ParagraphStyle(name="ReportTitle", parent=_styles["Title"], textColor=BRAND_COLOR, spaceAfter=4))
_styles.add(ParagraphStyle(name="ReportSubtitle", parent=_styles["Normal"], textColor=MUTED_COLOR, fontSize=10, spaceAfter=16))
_styles.add(ParagraphStyle(name="Section", parent=_styles["Heading2"], textColor=BRAND_COLOR, spaceBefore=14, spaceAfter=6))
_styles.add(ParagraphStyle(name="SubSection", parent=_styles["Heading3"], spaceBefore=8, spaceAfter=4))
_styles.add(ParagraphStyle(name="Body", parent=_styles["Normal"], alignment=TA_LEFT, spaceAfter=6, leading=14))
_styles.add(ParagraphStyle(name="BulletBody", parent=_styles["Normal"], leading=13))


def _p(text: Any, style: str = "Body"):
    """Paragraph seguro: castea a str y escapa el contenido (viene de JSON de
    IA o del motor determinista, texto plano de terceros). Las llamadas de
    este módulo insertan `<b>...</b>` a propósito para negrita (ver más abajo)
    -- se restauran esas dos etiquetas exactas tras el escapado para que
    reportlab las interprete, sin dejar de escapar cualquier otro `<`/`>`."""
    safe_text = "" if text is None else str(text)
    safe_text = safe_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_text = safe_text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    return Paragraph(safe_text, _styles[style])


def _bullets(items: list, style: str = "BulletBody"):
    if not items:
        return None
    return ListFlowable(
        [ListItem(_p(item, style), leftIndent=6) for item in items if item],
        bulletType="bullet",
        start="•",
        leftIndent=14,
    )


def _section_title(text: str):
    return _p(text, "Section")


def build_report_pdf(report: dict, candidate_name: str = "Candidato") -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title=f"Informe de Empleabilidad - {candidate_name}",
    )

    story = []

    story.append(_p("Informe de Empleabilidad", "ReportTitle"))
    story.append(_p(f"Candidato/a: {candidate_name}", "ReportSubtitle"))

    puntuacion = report.get("puntuacion_global")
    if puntuacion is not None:
        story.append(_p(f"Puntuación global: {puntuacion}/100", "SubSection"))
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
            rows = [["Formato", "Claridad", "Coherencia", "Info. clave", "Ortografía"]]
            rows.append([str(valoraciones.get(k, "-")) for k in ("formato", "claridad", "coherencia", "info_clave", "ortografia")])
            table = Table(rows, hAlign="LEFT", colWidths=[3.2 * cm] * 5)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(Spacer(1, 4))
            story.append(table)
            story.append(Spacer(1, 8))

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
            story.append(_p(f"Compatibilidad ATS: {analisis_cv['ats_compatibilidad']}/100", "SubSection"))
            if analisis_cv.get("ats_explicacion"):
                story.append(_p(analisis_cv["ats_explicacion"]))

    perfil_competencias = report.get("perfil_competencias") or []
    if perfil_competencias:
        story.append(_section_title("Perfil de Competencias"))
        for categoria in perfil_competencias:
            story.append(_p(categoria.get("categoria", ""), "SubSection"))
            for comp in categoria.get("competencias", []) or []:
                linea = f"<b>{comp.get('nombre', '')}</b> — {comp.get('puntuacion', '-')}/100 ({comp.get('nivel', '')})"
                story.append(_p(linea))
                if comp.get("explicacion"):
                    story.append(_p(comp["explicacion"], "BulletBody"))

    fortalezas = report.get("fortalezas_principales") or []
    if fortalezas:
        story.append(_section_title("Fortalezas Principales"))
        for f in fortalezas:
            story.append(_p(f.get("nombre", ""), "SubSection"))
            if f.get("explicacion_practica"):
                story.append(_p(f["explicacion_practica"]))

    areas_mejora = report.get("areas_mejora") or []
    if areas_mejora:
        story.append(_section_title("Áreas de Mejora"))
        for a in areas_mejora:
            story.append(_p(a.get("nombre", ""), "SubSection"))
            if a.get("porque_afecta"):
                story.append(_p(a["porque_afecta"]))
            if a.get("como_mejorar"):
                story.append(_p(f"<b>{a['como_mejorar']}</b>"))
            acciones = _bullets(a.get("acciones_concretas"))
            if acciones:
                story.append(acciones)

    resultados_juegos = report.get("resultados_juegos") or []
    if resultados_juegos:
        story.append(_section_title("Resultados de las Evaluaciones"))
        for r in resultados_juegos:
            story.append(_p(r.get("juego", ""), "SubSection"))
            for campo in ("que_mide", "resultado", "interpretacion", "aplicacion_entrevista"):
                if r.get(campo):
                    story.append(_p(r[campo], "BulletBody"))

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
            story.append(_p(titulo, "SubSection"))
            if rol.get("por_que_encaja"):
                story.append(_p(rol["por_que_encaja"]))
            if rol.get("demanda_laboral"):
                story.append(_p(f"Demanda laboral: {rol['demanda_laboral']}", "BulletBody"))

    plan_accion = report.get("plan_accion") or {}
    if plan_accion:
        story.append(_section_title("Plan de Acción"))
        for label, key in (("Próximos 30 días", "dias_30"), ("Próximos 60 días", "dias_60"), ("Próximos 90 días", "dias_90")):
            items = plan_accion.get(key)
            if items:
                story.append(_p(label, "SubSection"))
                bullets = _bullets(items)
                if bullets:
                    story.append(bullets)

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
        story.append(_section_title("Mensaje Final"))
        story.append(_p(report["mensaje_final"]))

    doc.build(story)
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
