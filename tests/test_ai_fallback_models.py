import backend.cv_analyzer as cv_analyzer


def test_supported_gemini_fallback_chain_excludes_invalid_preview_models():
    assert "gemini-3.6-flash" not in cv_analyzer.FALLBACK_MODELS
    assert "gemini-1.5-flash" in cv_analyzer.FALLBACK_MODELS
    assert any(model.startswith("gemini-2") for model in cv_analyzer.FALLBACK_MODELS)
    assert all(model in cv_analyzer.SUPPORTED_GEMINI_MODELS for model in cv_analyzer.FALLBACK_MODELS)


def test_fallback_chain_keeps_groq_as_recovery_after_gemini_exhaustion():
    assert "openai/gpt-oss-120b" in cv_analyzer._generate_chunk_via_groq.__code__.co_consts
    assert cv_analyzer.FALLBACK_MODELS


def test_backoff_budget_is_short_and_not_excessive():
    assert cv_analyzer.MAX_RETRIES_PER_MODEL <= 1
    assert max(cv_analyzer.RATE_LIMIT_BACKOFF_SECONDS) <= 0.75
    assert max(cv_analyzer.STAGGER_DELAY_SECONDS) <= 1.0
