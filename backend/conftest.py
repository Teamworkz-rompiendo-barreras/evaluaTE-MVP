# backend/conftest.py

import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_user_data():
    return {
        "firstName": "Ester",
        "lastName": "Pérez",
        "email": "ester@example.com",
        "whatsapp": "987654321",
        "jobPreferences": ["Desarrollo web", "UX"],
        "workMode": "remoto",
        "availability": "mañana",
        "willingToRelocate": False,
        "hasDisabilityCert": True,
        "accessibilitySettings": {
            "easyReadingMode": True,
            "audioAssistiveMode": False,
            "showPictograms": True,
            "contrastLevel": "alto"
        }
    }

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

@pytest.fixture
def sample_game_logs():
    return [
        {
            "sceneId": 1,
            "decisions": [
                {
                    "optionText": "Respondes de inmediato",
                    "isCorrect": True,
                    "skillImpacts": {"Toma de decisiones": 0.9},
                    "timestamp": "2025-06-10T12:00:00Z"
                }
            ],
            "totalSteps": 5,
            "totalTime": 300,
            "averageConfidence": 0.67,
            "emotionalTrend": ["positivo", "neutro"],
            "accessibilityUsed": True
        },
        {
            "sceneId": 2,
            "decisions": [
                {
                    "optionText": "Organizas según prioridad",
                    "isCorrect": True,
                    "skillImpacts": {"Resolución de problemas": 0.8},
                    "timestamp": "2025-06-10T12:01:00Z"
                }
            ],
            "totalSteps": 5,
            "totalTime": 300,
            "averageConfidence": 0.8,
            "emotionalTrend": ["positivo", "positivo"],
            "accessibilityUsed": False
        }
    ]