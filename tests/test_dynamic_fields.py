import os
import sys

# Ensure backend module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from new_report_schema import create_default_report, create_frontend_compatible_data


def test_default_report_uses_inputs_for_sections():
    cv_analysis = {
        "corrections": ["Añadir logros cuantificables"],
        "reordering_suggestions": ["Mover educación al final"],
        "software": ["Python", "Excel"],
    }
    job_preferences = {
        "areas": ["Data Scientist"],
        "workMode": "remoto",
        "seniority": "Senior",
        "preferred_platforms": ["LinkedIn", "Indeed"],
    }
    report = create_default_report("Tester", [], cv_analysis, job_preferences)
    assert report.improvement_areas[0].area == "Añadir logros cuantificables"
    assert report.action_plan.short_term[0] == "Explorar oportunidades en Data Scientist"
    assert report.job_search_advice.recommended_platforms == ["LinkedIn", "Indeed"]
    assert report.useful_tools.productivity == ["Python", "Excel"]
    assert report.useful_tools.accessibility == ["Microsoft Immersive Reader", "Grammarly", "ColorZilla"]
    assert report.suggested_roles[0].role == "Data Scientist"
    assert any("Python" in item for item in report.cv_details.tools)


def test_frontend_data_uses_inputs_for_sections():
    cv_analysis = {
        "corrections": ["Añadir logros cuantificables"],
        "reordering_suggestions": ["Mover educación al final"],
        "software": ["Python", "Excel"],
    }
    job_preferences = {
        "areas": ["Data Scientist"],
        "workMode": "remoto",
        "seniority": "Senior",
        "preferred_platforms": ["LinkedIn", "Indeed"],
    }
    data = create_frontend_compatible_data("Tester", [], cv_analysis, job_preferences)
    assert data["improvement_areas"][0]["area"] == "Añadir logros cuantificables"
    assert data["action_plan"]["short_term"][0] == "Explorar oportunidades en Data Scientist"
    assert data["job_search_advice"]["recommended_platforms"] == ["LinkedIn", "Indeed"]
    assert data["useful_tools"]["productivity"] == ["Python", "Excel"]
    assert data["useful_tools"]["accessibility"] == ["Microsoft Immersive Reader", "Grammarly", "ColorZilla"]
    assert data["suggested_roles"][0]["role"] == "Data Scientist"
    assert data["cv_details"]["tools"] == ["Python", "Excel"]
