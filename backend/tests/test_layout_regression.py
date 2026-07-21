import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from pdf_service import create_employability_pdf

try:
    from report_generator import render_informe_estructurado  # type: ignore
    _report_generator_import_error: Exception | None = None
except Exception as exc:  # pragma: no cover - defensive import guard
    render_informe_estructurado = None  # type: ignore
    _report_generator_import_error = exc


def test_pdf_service_uses_new_cv_analysis_fields():
    payload = {
        "fullName": "Tester",
        "summary": "Resumen",
        "personal_data": {
            "name": "Tester",
            "location": "Ciudad",
            "email": "tester@example.com",
            "phone": "123456789",
            "disability_certificate": "No",
        },
        "profile_summary": "Perfil",
        "cv_summary": "CV",
        "strengths": [],
        "soft_skills": [],
        "improvement_areas": [
            {"area": "Área", "reason": "", "suggested_action": "Acción"},
        ],
        "cv_analysis": {
            "structure_score": 5,
            "clarity_score": 4,
            "coherence_score": 3,
            "key_info_score": 2,
            "style_score": 1,
        },
        "ideal_work_environment": "",
        "suggested_roles": [],
        "action_plan": {"short_term": [], "medium_term": [], "long_term": []},
        "job_search_advice": {
            "cv_optimization": [],
            "letters_portfolio": "",
            "recommended_platforms": [],
            "networking": "",
            "interview_tips": "",
        },
        "useful_tools": {
            "productivity": [],
            "job_search": [],
            "learning": [],
            "accessibility": [],
        },
        "employability_score": 80,
        "completed_games": [],
        "final_message": "Mensaje",
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


def test_pdf_includes_extended_sections():
    payload = {
        "fullName": "Tester",
        "summary": "Resumen",
        "personal_data": {
            "name": "Tester",
        },
        "cv_analysis": {
            "structure_score": 5,
            "clarity_score": 4,
            "coherence_score": 3,
            "key_info_score": 2,
            "style_score": 1,
        },
        "ideal_work_environment": "Ambientes colaborativos y flexibles con foco en impacto.",
        "job_search_advice": {
            "cv_optimization": "Ajusta tu CV con logros medibles.",
            "letters_portfolio": "Actualiza tu portfolio con proyectos recientes.",
            "recommended_platforms": ["LinkedIn", "Indeed"],
            "networking": "Participa en comunidades y eventos del sector.",
            "interview_tips": "Practica respuestas con el método STAR.",
        },
        "useful_tools": {
            "productivity": ["Notion", "Trello"],
            "job_search": ["LinkedIn Jobs", "Indeed Alerts"],
            "learning": ["Coursera"],
            "accessibility": ["Be My Eyes"],
        },
        "completed_games": [
            "Juego de estrategia laboral",
            {"name": "Simulación de entrevistas", "insight": "Practicar respuestas"},
        ],
        "final_message": "¡Mucho éxito en tu búsqueda!",
    }

    pdf_bytes = create_employability_pdf(payload)
    text = pdf_bytes.decode("latin1")

    assert "Entornos de trabajo ideales" in text
    assert "Ambientes colaborativos y flexibles" in text

    assert "Consejos de b\\372squeda de empleo" in text
    assert "CV: Ajusta tu CV con logros medibles." in text
    assert "Plataformas: LinkedIn, Indeed" in text
    assert "Networking: Participa en comunidades y eventos del sector." in text

    assert "Herramientas \\372tiles" in text
    assert "Productividad: Notion, Trello" in text
    assert "B\\372squeda de empleo: LinkedIn Jobs, Indeed Alerts" in text
    assert "Aprendizaje: Coursera" in text
    assert "Accesibilidad: Be My Eyes" in text

    assert "Juegos completados" in text
    assert "Juego de estrategia laboral" in text
    assert "Simulaci\\363n de entrevistas: Practicar respuestas" in text

    assert "Mensaje final" in text
    assert "\\241Mucho \\351xito en tu b\\372squeda!" in text


def test_report_generator_uses_new_cv_analysis_fields():
    if render_informe_estructurado is None:
        pytest.skip(f"No se pudo importar report_generator: {_report_generator_import_error}")

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
        "cv_details": {"experience": ["Experiencia reciente"], "education": [], "languages": [], "tools": []},
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
    assert "Experiencia reciente" in text

