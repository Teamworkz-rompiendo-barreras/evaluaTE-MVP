import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from new_report_schema import create_frontend_compatible_data, create_default_report


def test_create_frontend_compatible_data_maps_inputs():
    soft_skills = [{"skill": "Comunicación", "score": 88}]
    cv_analysis = {"structure": "excelente", "feedback": "bien"}
    job_preferences = {"workMode": "remoto"}

    data = create_frontend_compatible_data("Tester", soft_skills, cv_analysis, job_preferences)

    assert data["softSkills"][0]["skill"] == "Comunicación"
    assert data["cv_analysis"]["structure"] == "excelente"
    assert data["job_preferences"]["workMode"] == "remoto"


def test_create_default_report_uses_inputs():
    soft_skills = [{"name": "Liderazgo"}]
    cv_analysis = {
        "structure_score": 4,
        "coherence_score": 3,
        "evidence": {
            "structure": "Buena",
            "coherence": "Correcta",
            "key_info": "",
            "clarity": "",
            "style": "",
        },
    }
    job_preferences = {"location": "Madrid", "workMode": "remoto"}

    report = create_default_report("Tester", soft_skills, cv_analysis, job_preferences)

    assert "Liderazgo" in report.strengths
    assert report.cv_analysis.structure_score == 4
    assert report.personal_data.location == "Madrid"
    assert "remoto" in report.ideal_work_environment.lower()
