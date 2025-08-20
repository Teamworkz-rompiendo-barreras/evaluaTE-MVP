import os
import pytest


def test_extract_native_importable():
    try:
        from app.cv_pipeline.extract import _extract_native  # type: ignore
    except Exception as e:
        pytest.fail(f"No se pudo importar extractor nativo: {e}")


