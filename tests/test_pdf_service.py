"""Regresion del PDF exportable (backend/pdf_service.py).

Bug real detectado en sesion: build_report_pdf() insertaba <b>, <font ...>
y <br/> a proposito para dar formato, pero _p() escapaba TODAS las
etiquetas del texto -- salian como texto literal ("<font color=...>...")
en vez de negrita/color/salto de linea real. Estos tests fijan que el
marcado permitido se interpreta y que cualquier otro '<'/'>' de texto de
terceros se sigue escapando (sin romper el parser de reportlab).
"""
from io import BytesIO

from pypdf import PdfReader

from backend.deterministic_report import generate_deterministic_report
from backend.pdf_service import build_report_pdf


def _sample_report():
    return generate_deterministic_report(
        pdf_bytes=b"",
        games_data={"softSkills": [
            {"skill": "Toma de decisiones", "score": 85, "level": "Alto"},
            {"skill": "Comunicacion", "score": 45, "level": "Bajo"},
        ]},
        prefs_data={"areas": ["Maquilladora"], "workMode": "remoto", "email": "a@example.com"},
        employability_score=68,
        candidate_name="Laura",
    )


def _extract_text(pdf_bytes: bytes) -> str:
    return "\n".join(p.extract_text() or "" for p in PdfReader(BytesIO(pdf_bytes)).pages)


def test_builds_valid_pdf_without_raising():
    pdf_bytes = build_report_pdf(_sample_report(), "Laura")
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 1000


def test_allowed_markup_tags_never_leak_as_literal_text():
    text = _extract_text(build_report_pdf(_sample_report(), "Laura"))
    for literal in ("<b>", "</b>", "<font", "</font>", "<br"):
        assert literal not in text, f"'{literal}' salió como texto literal en el PDF"


def test_untrusted_looking_text_is_still_escaped_safely():
    """Un candidato podria (sin querer) tener '<algo>' en el nombre de un
    area o similar. reportlab no debe interpretarlo como una etiqueta real
    (lo que rompería el parser, como pasaba con <font> antes de la
    proteccion) -- debe generarse el PDF sin excepción y el texto debe
    seguir siendo legible tal cual (como texto plano, no como marcado)."""
    report = generate_deterministic_report(
        pdf_bytes=b"",
        games_data={"softSkills": [{"skill": "Comunicacion", "score": 60, "level": "Medio"}]},
        prefs_data={"areas": ["<script>Ventas</script> & Marketing"], "workMode": "presencial"},
        employability_score=60,
        candidate_name="Ana <Test>",
    )
    pdf_bytes = build_report_pdf(report, "Ana <Test>")  # no debe lanzar
    assert pdf_bytes[:4] == b"%PDF"
    text = _extract_text(pdf_bytes)
    assert "Ventas" in text
    assert "Marketing" in text


def test_coherence_warning_reaches_the_pdf_text():
    text = _extract_text(build_report_pdf(_sample_report(), "Laura"))
    assert "presencia física" in text or "presencial" in text.lower()
