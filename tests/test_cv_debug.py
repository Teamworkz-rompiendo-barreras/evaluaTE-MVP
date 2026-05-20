import io
import json
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_debug_endpoint_empty_file():
    response = client.post("/api/debug/cv-data", files={"file": ("empty.pdf", b"")})
    assert response.status_code == 400
    assert response.json()["detail"] == "Archivo vacío"

def test_debug_endpoint_success(monkeypatch):
    # Mock extract_pdf_info to return a sample payload
    sample_payload = {"cv_info": {"contacto": {}}, "error": None}
    async def mock_extract_pdf_info(pdf_bytes):
        return sample_payload
    monkeypatch.setattr("backend.main.extract_pdf_info", mock_extract_pdf_info)
    fake_pdf = b"%PDF-1.4 fake content"
    response = client.post("/api/debug/cv-data", files={"file": ("sample.pdf", fake_pdf)})
    assert response.status_code == 200
    assert response.json() == sample_payload
