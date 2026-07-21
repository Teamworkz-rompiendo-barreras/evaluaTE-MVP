from app.cv_pipeline.quality import cv_quality_ok


def test_quality_gate_basic_fail():
    ok, reason = cv_quality_ok({"char_count": 100, "experience": [], "education": [], "contact": {}})
    assert ok is False
    assert "Extracción insuficiente" in reason


def test_quality_gate_no_contact():
    ok, reason = cv_quality_ok({"char_count": 1200, "experience": [], "education": [], "contact": {}})
    assert ok is False
    assert "No se detectó ningún dato de contacto" in reason


def test_quality_gate_ok():
    ok, reason = cv_quality_ok({"char_count": 1500, "experience": [1], "education": [], "contact": {"emails": ["a@b.com"]}})
    assert ok is True
    assert reason == ""


