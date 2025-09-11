import os
import sys

# Ensure backend module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from new_report_schema import create_default_report, create_frontend_compatible_data


def test_create_default_report_missing_job_preferences():
    report = create_default_report(
        full_name="Test User",
        soft_skills=[],
        cv_analysis={},
        job_preferences={}
    )
    assert report.personal_data.location == "No especificado"
    assert report.personal_data.disability_certificate == "No"


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
