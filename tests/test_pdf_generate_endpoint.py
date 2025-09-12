import os
import requests


def test_generate_pdf_endpoint_returns_pdf_bytes():
    base = os.getenv("BASE_URL", "http://localhost:8080")
    payload = {"fullName": "Test User", "report": {"summary": "Resumen"}, "cvAnalysis": {}}
    r = requests.post(f"{base}/api/pdf/generate-report", json=payload, timeout=30)
    assert r.status_code == 200
    assert r.headers.get("content-type") == "application/pdf"
    assert r.content and len(r.content) > 100


