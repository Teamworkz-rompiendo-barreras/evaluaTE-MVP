import os
import sys

# Ensure backend module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from new_report_schema import create_default_report, create_frontend_compatible_data, convert_old_format_to_new


def test_create_default_report_missing_job_preferences():
    report = create_default_report(
        full_name="Test User",
        soft_skills=[],
        cv_analysis={},
        job_preferences={}
    )
    assert report.personal_data.location == "No especificado"
    assert report.personal_data.disability_certificate == "No"
    assert isinstance(report.soft_skills, list)
    assert len(report.soft_skills) > 0
    assert isinstance(report.employability_score, int)
    assert isinstance(report.cv_details.experience, list)
    assert isinstance(report.cv_details.languages, list)


def test_create_frontend_compatible_data_missing_cv_analysis():
    data = create_frontend_compatible_data(
        full_name="Test User",
        soft_skills=[],
        cv_analysis={},
        job_preferences={}
    )
    cv_data = data["cv_analysis"]
    assert cv_data["structure"] == "regular"
    assert cv_data["coherence"] == "regular"
    assert cv_data["feedback"] == "CV analizado con limitaciones"
    assert "softSkills" in data
    assert isinstance(data["softSkills"], list)
    assert len(data["softSkills"]) > 0


def test_create_default_report_reflects_inputs():
    soft_skills = [{"skill": "Comunicación", "score": 80}]
    cv_analysis = {
        "structure_score": 5,
        "coherence_score": 4,
        "key_info_score": 3,
        "clarity_score": 2,
        "style_score": 1,
        "evidence": {
            "structure": "bien",
            "coherence": "buena",
            "key_info": "completa",
            "clarity": "clara",
            "style": "moderno",
        },
        "experience": [{"title": "Analista", "company": "ACME"}],
        "education": [{"degree": "Grado", "institution": "Uni"}],
        "languages": [{"name": "Inglés", "level": "B2"}],
        "software": [{"name": "Python"}],
    }
    job_preferences = {
        "location": "Madrid",
        "hasDisabilityCert": True,
        "workMode": "remoto",
        "areas": ["Analista"],
        "seniority": "Senior",
    }
    report = create_default_report("Tester", soft_skills, cv_analysis, job_preferences)
    assert report.soft_skills[0]["skill"] == "Comunicación"
    assert report.cv_analysis.structure_score == 5
    assert report.cv_analysis.evidence.structure == "bien"
    assert report.personal_data.location == "Madrid"
    assert report.suggested_roles[0].role == "Analista"
    assert report.suggested_roles[0].remote_viable is True
    assert report.employability_score == 80
    assert any("Analista" in item for item in report.cv_details.experience)
    assert "### Experiencia destacada" in report.cv_summary


def test_convert_old_format_to_new_employability_score():
    old = {
        "report": {},
        "recommendations": [],
        "employabilityScore": 55,
    }
    new = convert_old_format_to_new(old)
    assert new.employability_score == 55


def test_create_frontend_compatible_data_reflects_inputs():
    soft_skills = [{"skill": "Comunicación", "score": 80}]
    cv_analysis = {
        "structure": "excelente",
        "coherence": "buena",
        "feedback": "Gran CV",
        "summary": "Buen resumen",
        "experience": [{"title": "Proyecto X"}],
        "education": [{"degree": "Universidad"}],
        "software": ["Python"],
        "languages": [{"name": "Inglés", "level": "C1"}],
    }
    job_preferences = {"workMode": "remoto", "areas": ["Analista"]}
    data = create_frontend_compatible_data("Tester", soft_skills, cv_analysis, job_preferences)
    assert data["softSkills"][0]["skill"] == "Comunicación"
    assert data["cv_analysis"]["structure"] == "excelente"
    assert data["cv_analysis"]["experience"][0]["title"] == "Proyecto X"
    assert data["suggested_roles"][0]["role"] == "Analista"
    assert data["suggested_roles"][0]["remote_viable"] is True
    assert data["cv_details"]["experience"][0].startswith("Proyecto X")
    assert "Inglés" in data["cv_details"]["languages"][0]
