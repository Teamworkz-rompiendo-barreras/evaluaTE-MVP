# backend/test_main.py

import pytest
import requests
import json
from main import app
import uvicorn
import threading
import time

# Función para iniciar el servidor en un hilo
def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

@pytest.fixture(scope="session", autouse=True)
def setup_server():
    """Inicia el servidor antes de los tests"""
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Esperar a que el servidor inicie
    yield
    # El servidor se detendrá automáticamente cuando termine el proceso

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
    """Test del endpoint raíz"""
    response = requests.get("http://127.0.0.1:8001/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Bienvenida/o a EvaluaTE MVP"

def test_log_scene_decision(sample_soft_skills):
    """Test del endpoint de logging de escenas"""
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

    response = requests.post("http://127.0.0.1:8001/api/logs/scene", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_log_game_complete(sample_soft_skills):
    """Test del endpoint de completado de juegos"""
    payload = {
        "sceneId": 3,
        "decisions": sample_soft_skills,
        "completed": True,
        "timestamp": "2025-06-10T12:00:00Z"
    }

    response = requests.post("http://127.0.0.1:8001/api/logs/game-complete", json=payload)
    assert response.status_code == 200
    assert "success" in response.json()
    assert response.json()["success"] is True

def test_generate_report(sample_user_data, sample_cv_analysis, sample_soft_skills):
    """Test del endpoint de generación de reportes"""
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
                "easyReadingMode": False,
                "audioAssistiveMode": False,
                "showPictograms": False,
                "contrastLevel": "normal"
            }
        },
        "completedGames": [1, 2, 3],
        "logs": []
    }

    response = requests.post("http://127.0.0.1:8001/api/logs/report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert "recommendations" in data
    assert "employabilityScore" in data
    assert "level" in data

def test_upload_cv(tmp_path):
    """Test del endpoint de subida de CV"""
    # Crear un archivo PDF simulado
    cv_file = tmp_path / "test_cv.pdf"
    cv_file.write_text("Contenido simulado del CV")
    
    with open(cv_file, 'rb') as f:
        files = {'file': ('test_cv.pdf', f, 'application/pdf')}
        response = requests.post("http://127.0.0.1:8001/api/upload-cv", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "size" in data
    assert "pages" in data

def test_analyze_cv(tmp_path):
    """Test del endpoint de análisis de CV"""
    # Crear un archivo PDF simulado
    cv_file = tmp_path / "test_cv.pdf"
    cv_file.write_text("Contenido simulado del CV")
    
    with open(cv_file, 'rb') as f:
        files = {'file': ('test_cv.pdf', f, 'application/pdf')}
        data = {
            'userId': 'test-user',
            'fullName': 'Test User',
            'softSkills': json.dumps([{"skill": "Comunicación", "level": "Alto", "confidence": 0.8}]),
            'jobPreferences': json.dumps({"areas": ["Desarrollo"], "needs": []}),
            'completedGames': json.dumps([1, 2])
        }
        response = requests.post("http://127.0.0.1:8001/api/pdf/analyze-cv", files=files, data=data)
    
    assert response.status_code == 200
    data = response.json()
    assert "strengths" in data
    assert "weaknesses" in data
    assert "feedback" in data

def test_evaluate_softskills(sample_soft_skills):
    """Test de evaluación de soft skills"""
    # Simular evaluación de habilidades blandas
    high_skills = [skill for skill in sample_soft_skills if skill["level"] == "Alto"]
    medium_skills = [skill for skill in sample_soft_skills if skill["level"] == "Medio"]
    low_skills = [skill for skill in sample_soft_skills if skill["level"] == "Bajo"]
    
    assert len(high_skills) == 1
    assert len(medium_skills) == 1
    assert len(low_skills) == 1

def test_get_recommendations(sample_user_data, sample_cv_analysis, sample_soft_skills):
    """Test de generación de recomendaciones"""
    # Simular generación de recomendaciones
    roles = []
    resources = ["Platzi", "Microsoft Learn"]
    improvements = []
    next_steps = []

    if any(skill["level"] == "Alto" for skill in sample_soft_skills):
        roles.append("Desarrollador frontend")
        roles.append("Soporte técnico")

    if sample_cv_analysis and sample_cv_analysis["weaknesses"]:
        improvements.extend(sample_cv_analysis["weaknesses"])

    next_steps.append("Completar todos los juegos")
    next_steps.append("Actualizar tu CV")
    next_steps.append("Revisar tus preferencias")

    assert len(roles) > 0
    assert len(resources) > 0
    assert len(improvements) > 0
    assert len(next_steps) > 0

def test_full_flow(sample_user_data, sample_cv_file, sample_soft_skills):
    """Test del flujo completo de la aplicación"""
    # 1. Test del endpoint raíz
    response = requests.get("http://127.0.0.1:8001/")
    assert response.status_code == 200

    # 2. Test de logging de escena
    scene_payload = {
        "sceneId": 1,
        "decisions": sample_soft_skills,
        "totalSteps": 5,
        "totalTime": 300,
        "averageConfidence": 0.67,
        "emotionalTrend": ["positivo"],
        "accessibilityUsed": False
    }
    response = requests.post("http://127.0.0.1:8001/api/logs/scene", json=scene_payload)
    assert response.status_code == 200

    # 3. Test de generación de reporte
    report_payload = {
        "userId": "test-user-flow",
        "fullName": f"{sample_user_data['nombre']} {sample_user_data['apellidos']}",
        "softSkills": sample_soft_skills,
        "jobPreferences": {
            "areas": [sample_user_data["puesto"]],
            "needs": [],
            "workMode": sample_user_data["jornada"],
            "availability": sample_user_data["disponibilidad"],
            "willingToRelocate": False,
            "hasDisabilityCert": False
        },
        "completedGames": [1],
        "logs": []
    }
    response = requests.post("http://127.0.0.1:8001/api/logs/report", json=report_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "employabilityScore" in data
    assert "level" in data
    assert "recommendations" in data