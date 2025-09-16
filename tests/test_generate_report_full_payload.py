import os
import sys
from typing import Dict, List

import pytest

# Ensure backend modules are importable when tests are run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from generate_report import generar_informe  # type: ignore
from new_report_schema import NewReportSchema  # type: ignore


@pytest.fixture
def sample_job_preferences() -> Dict[str, object]:
    return {
        "workMode": "Híbrido",
        "areas": ["Analista de Datos", "Business Intelligence"],
        "preferredPlatforms": ["LinkedIn", "InfoJobs"],
        "seniority": "Semi Senior",
        "location": "Sevilla",
        "hasDisabilityCert": True,
    }


@pytest.fixture
def sample_completed_games() -> List[str]:
    return [
        "Juego de lógica completado",
        "Simulación de entrevista completada",
    ]


@pytest.fixture
def sample_cv_analysis() -> Dict[str, object]:
    return {
        "contact": {
            "emails": ["maria@example.com"],
            "phones": ["+34 600 111 222"],
            "location": "Sevilla",
        },
        "experience_detailed": [
            {
                "title": "Analista de Datos",
                "company": "Analytics Corp",
                "description": "Responsable de tableros de control y métricas de negocio.",
            }
        ],
        "education_detailed": [
            {
                "degree": "Grado en Estadística",
                "institution": "Universidad de Sevilla",
            }
        ],
        "languages": [
            {"name": "Inglés", "level": "B2"},
            {"name": "Español", "level": "Nativo"},
        ],
        "software": ["Python", "SQL", "Tableau"],
        "analysis_json": {
            "structure_score": 5,
            "coherence_score": 4,
            "key_info_score": 5,
            "clarity_score": 4,
            "style_score": 3,
            "feedback": "CV con buen nivel de detalle y logros medibles.",
            "summary": "Profesional enfocada en analítica avanzada.",
            "corrections": [
                "Añadir ejemplos adicionales de impacto en proyectos de datos.",
            ],
            "reordering_suggestions": [
                "Destacar certificaciones técnicas al inicio del CV.",
            ],
            "evidence": {
                "structure": "La estructura sigue un orden cronológico claro.",
                "coherence": "La narrativa del CV es consistente con los roles descritos.",
                "key_info": "Incluye métricas relevantes para evaluar el impacto.",
                "clarity": "La redacción es concisa y directa.",
                "style": "Uso adecuado de formato profesional.",
            },
        },
    }


def test_generar_informe_with_complete_payload(
    sample_job_preferences: Dict[str, object],
    sample_completed_games: List[str],
    sample_cv_analysis: Dict[str, object],
) -> None:
    payload = {
        "fullName": "María García",
        "location": "Sevilla",
        "email": "maria@example.com",
        "phone": "+34 600 111 222",
        "softSkills": [
            {"skill": "Comunicación", "score": 82, "level": "Avanzado"},
            {"skill": "Pensamiento analítico", "score": 78},
        ],
        "employabilityScore": 81,
        "cvAnalysis": sample_cv_analysis,
        "jobPreferences": sample_job_preferences,
        "completedGames": sample_completed_games,
    }

    raw_report = generar_informe(payload)
    report = NewReportSchema.model_validate(raw_report)

    # Job preference data is surfaced in multiple sections
    assert report.personal_data.location == sample_job_preferences["location"]
    assert report.personal_data.disability_certificate == "Sí"
    for area in sample_job_preferences["areas"]:
        assert area in report.ideal_work_environment
    assert sample_job_preferences["workMode"] in report.ideal_work_environment
    assert report.job_search_advice.recommended_platforms == sample_job_preferences["preferredPlatforms"]
    assert report.job_preferences.areas == sample_job_preferences["areas"]
    assert report.job_preferences.work_mode == sample_job_preferences["workMode"]
    assert report.job_preferences.preferred_platforms == sample_job_preferences["preferredPlatforms"]
    assert report.job_preferences.seniority == sample_job_preferences["seniority"]
    assert report.job_preferences.location == sample_job_preferences["location"]
    assert report.job_preferences.has_disability_cert is True

    # CV analysis information is mapped into the structured report
    assert report.cv_analysis.structure_score == sample_cv_analysis["analysis_json"]["structure_score"]
    assert report.cv_analysis.evidence.structure == sample_cv_analysis["analysis_json"]["evidence"]["structure"]
    assert report.cv_analysis.corrections[0] == sample_cv_analysis["analysis_json"]["corrections"][0]
    assert any("Analista de Datos" in entry for entry in report.cv_details.experience)
    assert "### Experiencia destacada" in report.cv_summary

    # Completed games are preserved in the response
    assert report.completed_games == sample_completed_games
