# backend/test_main.py

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def sample_user_data():
    return {
        "nombre": "Ester",
        "apellidos": "Pérez",
        "email": "ester@example.com",
        "whatsapp": "987654321",
        "discapacidad": "",
        "tipo": "",
        "puesto": "Desarrollador frontend",
        "jornada": "remoto",
        "disponibilidad": "mañana",
        "traslado": "false"
    }

@pytest.fixture
def sample_cv_file(tmp_path):
    cv_file = tmp_path / "cv.pdf"
    cv_file.write_text("Contenido simulado del CV")
    return cv_file

@pytest.fixture
def sample_soft_skills():
    return [
        {"skill": "Toma de decisiones", "level": "Alto", "confidence": 0.9},
        {"skill": "Resolución de problemas", "level": "Medio", "confidence": 0.65},
        {"skill": "Gestión emocional", "level": "Bajo", "confidence": 0.4}
    ]

@pytest.fixture
def sample_cv_analysis():
    return {
        "score": 62,
        "strengths": ["Formato claro", "Experiencia relevante"],
        "weaknesses": ["Falta objetivos profesionales"],
        "feedback": "Tu CV muestra experiencia, pero necesita mayor claridad"
    }

def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Bienvenida/o a EvaluaTE MVP"

def test_log_scene_decision(sample_soft_skills):
    payload = {
        "sceneId": 1,
        "decisions": sample_soft_skills,
        "totalSteps": 5,
        "totalTime": 300,
        "averageConfidence": 0.67,
        "emotionalTrend": ["positivo", "neutro"],
        "accessibilityUsed": True,
        "accessibilitySettings": {
            "easyReadingMode": True,
            "audioAssistiveMode": False,
            "showPictograms": True,
            "contrastLevel": "alto"
        }
    }

    response = client.post("/api/logs/scene", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_log_game_complete(sample_soft_skills):
    payload = {
        "sceneId": 3,
        "decisions": sample_soft_skills,
        "completed": True,
        "timestamp": "2025-06-10T12:00:00Z"
    }

    response = client.post("/api/logs/game-complete", json=payload)
    assert response.status_code == 200
    assert "success" in response.json()
    assert response.json()["success"] is True

def test_generate_report(sample_user_data, sample_cv_analysis, sample_soft_skills):
    payload = {
        "userId": "user-ester-2025",
        "fullName": f"{sample_user_data['nombre']} {sample_user_data['apellidos']}",
        "softSkills": sample_soft_skills,
        "cvAnalysis": sample_cv_analysis,
        "jobPreferences": {
            "areas": [sample_user_data["puesto"]],
            "needs": ["Horario flexible", "Acceso remoto"],
            "workMode": sample_user_data["jornada"],
            "availability": sample_user_data["disponibilidad"],
            "willingToRelocate": sample_user_data["traslado"].lower() == "true",
            "hasDisabilityCert": False,
            "accessibilitySettings": {
                "easyReadingMode": True,
                "audioAssistiveMode": False,
                "showPictograms": True,
                "contrastLevel": "alto"
            }
        },
        "completedGames": [1, 2, 3, 4, 5],
        "logs": [{
            "sceneId": 1,
            "decisions": sample_soft_skills,
            "totalSteps": 5,
            "totalTime": 300,
            "averageConfidence": 0.67,
            "emotionalTrend": ["positivo", "neutro"],
            "accessibilityUsed": True
        }]
    }

    response = client.post("/api/logs/report", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "report" in data
    assert "employabilityScore" in data["report"]
    assert "level" in data["report"]
    assert "recommendations" in data
    assert len(data["recommendations"]["roles"]) >= 1

def test_upload_cv(tmp_path):
    cv_file = tmp_path / "cv.pdf"
    cv_file.write_text("Este es un CV de prueba")

    with open(cv_file, "rb") as f:
        files = {"file": ("cv.pdf", f.read(), "application/pdf")}
        response = client.post("/api/upload-cv", files=files)

    assert response.status_code == 200
    assert "filename" in response.json()
    assert response.json()["filename"] == "cv.pdf"

def test_analyze_cv(tmp_path):
    cv_file = tmp_path / "cv.pdf"
    cv_file.write_text("Este es un CV de prueba")

    with open(cv_file, "rb") as f:
        files = {"file": ("cv.pdf", f.read(), "application/pdf")}
        response = client.post("/api/analyze-cv", files=files)

    assert response.status_code == 200
    data = response.json()

    assert "score" in data
    assert isinstance(data["score"], int)
    assert data["score"] >= 0 and data["score"] <= 100

    assert "strengths" in data
    assert isinstance(data["strengths"], list)

    assert "weaknesses" in data
    assert isinstance(data["weaknesses"], list)

def test_evaluate_softskills(sample_soft_skills):
    response = client.post("/api/evaluate/skills", json={"skills": sample_soft_skills})
    assert response.status_code == 200

    data = response.json()
    assert "summary" in data
    assert "averageConfidence" in data
    assert data["averageConfidence"] >= 0.4
    assert data["averageConfidence"] <= 0.9

def test_get_recommendations(sample_user_data, sample_cv_analysis, sample_soft_skills):
    payload = {
        "softSkills": sample_soft_skills,
        "cvAnalysis": sample_cv_analysis,
        "preferences": {
            "areas": [sample_user_data["puesto"]],
            "needs": ["Horario flexible", "Acceso remoto"],
            "workMode": sample_user_data["jornada"],
            "availability": sample_user_data["disponibilidad"],
            "willingToRelocate": sample_user_data["traslado"].lower() == "true",
            "hasDisabilityCert": False
        }
    }

    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "roles" in data["recommendations"]
    assert "resources" in data["recommendaciones"]
    assert "nextSteps" in data["recommendaciones"]

def test_full_flow(sample_user_data, sample_cv_file, sample_soft_skills):
    """Test completo del flujo desde registro → juego → informe"""

    # Paso 1: Registro de usuario
    user_response = client.post("/api/register/contact", json={
        "firstName": sample_user_data["nombre"],
        "lastName": sample_user_data["apellidos"],
        "email": sample_user_data["email"],
        "whatsapp": sample_user_data["whatsapp"]
    })
    assert user_response.status_code == 200

    # Paso 2: Subida de CV
    with open(sample_cv_file, "rb") as f:
        files = {"file": ("cv.pdf", f.read(), "application/pdf")}
        upload_response = client.post("/api/upload-cv", files=files)
    assert upload_response.status_code == 200

    # Paso 3: Evaluación del CV
    analyze_response = client.post("/api/analyze-cv", json={"filename": "cv.pdf"})
    assert analyze_response.status_code == 200

    # Paso 4: Completar minijuegos
    for game_id in range(1, 6):
        log_response = client.post("/api/logs/scene", json={
            "sceneId": game_id,
            "decisions": sample_soft_skills,
            "accessibilityUsed": True
        })
        assert log_response.status_code == 200

    # Paso 5: Generar informe final
    report_response = client.post("/api/logs/report", json={
        "userId": "user-ester-2025",
        "fullName": f"{sample_user_data['nombre']} {sample_user_data['apellidos']}",
        "softSkills": sample_soft_skills,
        "cvAnalysis": sample_cv_analysis,
        "completedGames": list(range(1, 6)),
        "logs": [{
            "sceneId": id,
            "decisions": sample_soft_skills,
            "accessibilityUsed": True
        } for id in range(1, 6)]
    })

    assert report_response.status_code == 200
    data = report_response.json()

    assert "report" in data
    assert "employabilityScore" in data["report"]
    assert "level" in data["report"]
    assert "recommendations" in data