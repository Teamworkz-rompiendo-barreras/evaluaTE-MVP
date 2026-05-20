import os
import io
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def _make_pdf_bytes() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("Helvetica", 12)
    c.drawString(50, 800, "Nombre: Test User")
    c.drawString(50, 780, "Email: test.user@example.com")
    c.drawString(50, 760, "Teléfono: +34 600 111 222")
    c.drawString(50, 740, "Experiencia: 2021-2023 Data Entry")
    c.save()
    return buf.getvalue()


def test_analyze_cv_di_normalization_if_available():
    # Usa servidor local
    base = os.getenv("BASE_URL", "http://localhost:8080")
    # Comprobar salud
    hr = requests.get(f"{base}/health", timeout=10)
    if hr.status_code != 200:
        raise AssertionError("Backend no disponible en /health")

    pdf_bytes = _make_pdf_bytes()
    files = {"file": ("cv.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    r = requests.post(f"{base}/api/pdf/analyze-cv", files=files, timeout=60)
    assert r.status_code == 200
    data = r.json()

    # Validar presencia de flag y estructura mínima
    assert "document_intelligence_used" in data
    assert "candidate" in data
    assert isinstance(data.get("contact"), dict)
    assert "experience_detailed" in data
    assert "education_detailed" in data


