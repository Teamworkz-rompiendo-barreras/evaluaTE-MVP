"""Regresión del motor de informes SIN IA (backend/deterministic_report.py).

Este motor es el que genera el informe por defecto (ENABLE_AI_REPORT no
está activado): debe funcionar siempre, sin red, sin claves de API y sin
lanzar excepciones, produciendo una estructura compatible con
backend/new_report_schema.py (Chunk1Base + Chunk2Competencias + Chunk3Accion)
y con lo que consume backend/pdf_service.py para el PDF exportable.
"""
from io import BytesIO

from reportlab.pdfgen import canvas

from backend.deterministic_report import generate_deterministic_report

REQUIRED_TOP_LEVEL_FIELDS = [
    "datos_personales", "resumen_ejecutivo", "puntuacion_global", "interpretacion_global",
    "analisis_cv", "perfil_competencias", "fortalezas_principales", "areas_mejora",
    "resultados_juegos", "entornos_ideales", "roles_recomendados", "plan_accion",
    "estrategia_busqueda", "herramientas_recomendadas", "recomendaciones_personalizadas",
    "recursos_adicionales", "mensaje_final",
]


def _build_sample_pdf() -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf)
    lines = [
        "Juan Perez Garcia",
        "juan.perez@example.com",
        "+34 600 123 456",
        "linkedin.com/in/juanperez",
        "",
        "PERFIL",
        "Profesional con experiencia en atencion al cliente y logistica.",
        "",
        "EXPERIENCIA",
        "- Mozo de almacen en LogiSA, 2019-2022",
        "- Atencion al cliente en TiendaXYZ, 2022-2024",
        "",
        "EDUCACION",
        "- Grado Medio en Gestion Administrativa, 2018",
        "",
        "IDIOMAS",
        "Ingles B2, Frances basico",
        "",
        "HABILIDADES",
        "Excel, Word, SAP, Photoshop",
    ]
    y = 800
    for ln in lines:
        c.drawString(50, y, ln)
        y -= 18
    c.save()
    return buf.getvalue()


def _sample_games_data():
    return {
        "softSkills": [
            {"skill": "Toma de decisiones", "score": 85, "level": "Alto", "confidence": 0.9},
            {"skill": "Pensamiento analitico", "score": 40, "level": "Bajo", "confidence": 0.8},
            {"skill": "Comunicacion", "score": 65, "level": "Medio", "confidence": 0.7},
        ],
        "completedGames": ["decision-making", "analytical-thinking"],
    }


def _sample_prefs_data():
    return {
        "areas": ["Logistica", "Atencion al cliente"],
        "needs": ["Entorno tranquilo"],
        "workMode": "presencial",
        "willingToRelocate": False,
        "hasDisabilityCert": True,
        "email": "juan.perez@example.com",
        "whatsapp": "+34600123456",
    }


def test_generates_all_required_fields_with_a_real_pdf():
    report = generate_deterministic_report(
        pdf_bytes=_build_sample_pdf(),
        games_data=_sample_games_data(),
        prefs_data=_sample_prefs_data(),
        employability_score=72,
        candidate_name="Juan Perez",
    )
    missing = [k for k in REQUIRED_TOP_LEVEL_FIELDS if k not in report]
    assert not missing, f"Faltan campos: {missing}"
    assert report["generado_sin_ia"] is True


def test_valoraciones_and_scores_are_within_schema_bounds():
    report = generate_deterministic_report(
        pdf_bytes=_build_sample_pdf(),
        games_data=_sample_games_data(),
        prefs_data=_sample_prefs_data(),
        employability_score=72,
        candidate_name="Juan Perez",
    )
    valoraciones = report["analisis_cv"]["valoraciones"]
    for k, v in valoraciones.items():
        assert 1 <= v <= 5, f"valoracion {k} fuera de rango 1-5: {v}"
    assert 0 <= report["analisis_cv"]["ats_compatibilidad"] <= 100
    assert 0 <= report["puntuacion_global"] <= 100
    for comp in report["perfil_competencias"][0]["competencias"]:
        assert 0 <= comp["puntuacion"] <= 100


def test_section_extraction_does_not_bleed_into_next_section():
    report = generate_deterministic_report(
        pdf_bytes=_build_sample_pdf(),
        games_data=_sample_games_data(),
        prefs_data=_sample_prefs_data(),
        employability_score=72,
        candidate_name="Juan Perez",
    )
    experiencia = " ".join(report["analisis_cv"]["experiencia"])
    assert "EDUCACION" not in experiencia
    assert "LogiSA" in experiencia


def test_language_level_is_not_borrowed_from_a_different_language():
    report = generate_deterministic_report(
        pdf_bytes=_build_sample_pdf(),
        games_data=_sample_games_data(),
        prefs_data=_sample_prefs_data(),
        employability_score=72,
        candidate_name="Juan Perez",
    )
    idiomas = {i.split(" (")[0]: i for i in report["analisis_cv"]["idiomas"]}
    assert "(B2)" in idiomas.get("Inglés", "")
    assert "(B2)" not in idiomas.get("Francés", "")


def test_never_crashes_on_empty_or_corrupt_pdf():
    for pdf_bytes in (b"", b"not a real pdf", b"%PDF-1.4 corrupt"):
        report = generate_deterministic_report(
            pdf_bytes=pdf_bytes,
            games_data={},
            prefs_data={},
            employability_score=200,  # fuera de rango a propósito
            candidate_name="",
        )
        missing = [k for k in REQUIRED_TOP_LEVEL_FIELDS if k not in report]
        assert not missing, f"Faltan campos con PDF inválido: {missing}"
        assert 0 <= report["puntuacion_global"] <= 100


def test_plan_accion_has_three_items_per_horizon():
    report = generate_deterministic_report(
        pdf_bytes=_build_sample_pdf(),
        games_data=_sample_games_data(),
        prefs_data=_sample_prefs_data(),
        employability_score=72,
        candidate_name="Juan Perez",
    )
    plan = report["plan_accion"]
    assert len(plan["dias_30"]) == 3
    assert len(plan["dias_60"]) == 3
    assert len(plan["dias_90"]) == 3
