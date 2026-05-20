from app.cv_pipeline.scoring import compute_cv_analysis


def test_scoring_dimensions_and_overall_present():
    cv = {
        "experience": [{}, {}],
        "education": [{}],
        "languages": [{}, {}],
        "skills": ["Python", "Git", "Docker"],
        "contact": {"emails": ["x@y.com"], "phones": [], "location": "Madrid", "linkedin": "https://linkedin.com/in/test"},
        "summary": "Perfil profesional",
        "sections": {"experience": [{}, {}]},
    }
    res = compute_cv_analysis(cv)
    assert "dimensions" in res and isinstance(res["dimensions"], list)
    assert len(res["dimensions"]) == 6
    assert res.get("overall", {}).get("score") is not None


