# backend/generate_report_test.py

import pytest
from httpx import AsyncClient

def test_generate_report_success(client, sample_user_data, sample_soft_skills):
    payload = {
        "userId": "user-ester-2025",
        "fullName": f"{sample_user_data['firstName']} {sample_user_data['lastName']}",
        "softSkills": sample_soft_skills,
        "jobPreferences": {
            "areas": sample_user_data["jobPreferences"],
            "needs": ["Horario flexible", "Acceso remoto"],
            "workMode": sample_user_data["workMode"],
            "availability": sample_user_data["availability"],
            "willingToRelocate": sample_user_data["willingToRelocate"],
            "hasDisabilityCert": sample_user_data["hasDisabilityCert"]
        },
        "cvAnalysis": {
            "score": 62,
            "strengths": ["Formato claro", "Experiencia relevante"],
            "weaknesses": ["Falta objetivos profesionales"]
        },
        "completedGames": [1, 2, 3, 4, 5],
        "logs": [
            {
                "sceneId": 1,
                "decisions": [
                    {
                        "optionText": "Opción A",
                        "isCorrect": True,
                        "skillImpacts": {"Toma de decisiones": 0.9},
                        "timestamp": "2025-06-10T12:00:00Z"
                    }
                ],
                "accessibilityUsed": True
            }
        ]
    }

    response = client.post("/api/logs/report", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "report" in data
    assert "employabilityScore" in data["report"]
    assert "level" in data["report"]
    assert "recommendations" in data

    # Verifica puntaje y nivel
    score = data["report"]["employabilityScore"]
    level = data["report"]["level"]

    assert isinstance(score, int)
    assert level in ["Baja empleabilidad", "Empleabilidad media", "Alta empleabilidad"]

    # Nivel alto si > 80
    if score >= 80:
        assert level == "Alta empleabilidad"
    elif score >= 50:
        assert level == "Empleabilidad media"
    else:
        assert level == "Baja empleabilidad"

    # Recomendaciones personalizadas
    recommendations = data["recommendations"]
    assert len(recommendations["roles"]) >= 1
    assert len(recommendations["nextSteps"]) >= 1