import os
import requests


def test_generate_pdf_endpoint_returns_pdf_bytes():
    base = os.getenv("BASE_URL", "http://localhost:8080")
    payload = {
        "fullName": "Test User",
        "summary": "Resumen",
        "personal_data": {
            "name": "Test User",
            "location": "Ciudad",
            "email": "user@example.com",
            "phone": "123",
            "disability_certificate": "No",
        },
        "profile_summary": "Perfil",
        "cv_summary": "CV",
        "strengths": ["Comunicación"],
        "soft_skills": [{"skill": "Comunicación", "score": 80}],
        "improvement_areas": [
            {"area": "Área", "reason": "", "suggested_action": "Acción"}
        ],
        "cv_analysis": {
            "structure_score": 4,
            "clarity_score": 4,
            "coherence_score": 3,
            "key_info_score": 3,
            "style_score": 2,
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
        "employability_score": 75,
        "completed_games": [],
        "final_message": "Mensaje",
    }
    r = requests.post(f"{base}/api/pdf/generate-report", json=payload, timeout=30)
    assert r.status_code == 200
    assert r.headers.get("content-type") == "application/pdf"
    assert r.content and len(r.content) > 100


