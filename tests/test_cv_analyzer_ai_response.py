import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

import cv_analyzer  # noqa: E402


class DummyAzureClient:
    def __init__(self, content: str):
        dummy_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=lambda *_, **__: dummy_response)
        )


def test_analyze_cv_with_ai_parses_wrapped_json(monkeypatch: pytest.MonkeyPatch):
    expected_payload = {
        "contacto": {
            "nombre": "Juan Pérez",
            "email": "juan@example.com",
            "telefono": "",
            "ubicacion": "",
            "linkedin": "",
            "portfolio": "",
        },
        "experiencia_laboral": [],
        "formacion_academica": [],
        "habilidades_tecnicas": [],
        "habilidades_blandas": [],
        "idiomas": [],
        "certificaciones": [],
        "proyectos": [],
        "logros": [],
        "intereses": [],
    }

    azure_response = """```json
{json_payload}
```""".format(json_payload=json.dumps(expected_payload))

    monkeypatch.setattr(cv_analyzer, "client", DummyAzureClient(azure_response))
    monkeypatch.setattr(cv_analyzer, "DEPLOYMENT", "dummy-deployment")

    fallback_called = []

    def fake_fallback(_: str):
        fallback_called.append(True)
        return {"fallback": True}

    monkeypatch.setattr(cv_analyzer, "extract_basic_cv_data_from_text", fake_fallback)

    result = cv_analyzer.analyze_cv_with_ai("Contenido del CV de prueba")

    assert result == expected_payload
    assert fallback_called == []
