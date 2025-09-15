import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from report_generator import render_informe_estructurado


def _base_report() -> dict:
    return {
        "summary": "Resumen",
        "personal_data": {
            "name": "Tester",
            "location": "Ciudad",
            "email": "tester@example.com",
            "phone": "123456789",
            "disability_certificate": "No",
        },
        "profile_summary": "Perfil",
        "cv_summary": "CV con información relevante.",
        "strengths": [],
        "improvement_areas": [],
        "cv_analysis": {
            "structure_score": 3,
            "clarity_score": 3,
            "coherence_score": 3,
            "key_info_score": 3,
            "style_score": 3,
        },
        "ideal_work_environment": "",
        "suggested_roles": [],
        "action_plan": {},
        "job_search_advice": {},
        "useful_tools": {},
        "completed_games": [],
        "final_message": "",
    }


def test_render_informe_includes_cv_detail_lists():
    report = _base_report()
    report["cv_analysis"].update(
        experience=[
            {
                "title": "Desarrollador",
                "company": "Tech Corp",
                "start_date": "2020",
                "end_date": "2022",
            },
            "Proyecto freelance",
        ],
        education=[
            {
                "degree": "Ingeniería Informática",
                "institution": "Universidad Estatal",
                "start_date": "2015",
                "end_date": "2019",
            }
        ],
        languages=[
            {"language": "Inglés", "level": "Avanzado"},
            "Español nativo",
        ],
        software=[
            {"name": "Python", "level": "Avanzado"},
            "Git",
        ],
    )

    text = render_informe_estructurado(report)

    assert "\nExperiencia" in text
    assert "- Desarrollador — Tech Corp — 2020 - 2022" in text
    assert "- Proyecto freelance" in text
    assert "\nEducación" in text
    assert "- Ingeniería Informática — Universidad Estatal — 2015 - 2019" in text
    assert "\nIdiomas" in text
    assert "- Inglés — Avanzado" in text
    assert "- Español nativo" in text
    assert "\nSoftware" in text
    assert "- Python — Avanzado" in text
    assert "- Git" in text


def test_render_informe_handles_empty_cv_lists():
    report = _base_report()
    report["cv_analysis"].update(
        experience=[],
        education=[],
        languages=[],
        software=[],
    )

    text = render_informe_estructurado(report)

    assert "\nExperiencia" in text
    assert "- No se registró experiencia disponible." in text
    assert "\nEducación" in text
    assert "- No se registró formación educativa disponible." in text
    assert "\nIdiomas" in text
    assert "- No se registraron idiomas." in text
    assert "\nSoftware" in text
    assert "- No se registraron herramientas destacadas." in text
