import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from pdf_service import create_employability_pdf
from report_generator import render_informe_estructurado


def test_pdf_service_uses_new_cv_analysis_fields():
    payload = {
        "fullName": "Tester",
        "report": {
            "summary": "Resumen",
            "strengths": [],
            "improvement_areas": ["Área"],
            "cv_analysis": {
                "structure_score": 5,
                "clarity_score": 4,
                "coherence_score": 3,
                "key_info_score": 2,
                "style_score": 1,
            },
            "action_plan": {},
        },
    }
    pdf_bytes = create_employability_pdf(payload)
    text = pdf_bytes.decode("latin1")
    assert "Estructura:" in text
    assert "Claridad:" in text
    assert "Coherencia:" in text
    assert "Informaci\\363n clave" in text
    assert "Estilo:" in text
    assert "Formato:" not in text
    assert "Ortografía:" not in text


def test_report_generator_uses_new_cv_analysis_fields():
    report = {
        "summary": "Resumen",
        "personal_data": {
            "name": "Tester",
            "location": "Ciudad",
            "email": "t@example.com",
            "phone": "123",
            "disability_certificate": "No",
        },
        "profile_summary": "Perfil",
        "cv_summary": "CV",
        "strengths": ["F1"],
        "improvement_areas": [{"area": "A1", "suggested_action": "Hacer algo"}],
        "cv_analysis": {
            "structure_score": 5,
            "clarity_score": 4,
            "coherence_score": 3,
            "key_info_score": 2,
            "style_score": 1,
        },
        "ideal_work_environment": "",
        "suggested_roles": [],
        "action_plan": {},
        "job_search_advice": {},
        "useful_tools": {},
        "completed_games": [],
        "final_message": "",
    }
    text = render_informe_estructurado(report)
    assert "Estructura:" in text
    assert "Claridad:" in text
    assert "Coherencia:" in text
    assert "Información clave:" in text
    assert "Estilo:" in text
    assert "Formato" not in text
    assert "Ortografía" not in text

