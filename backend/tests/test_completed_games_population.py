import os
import sys

from typing import List


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from generate_report import _generate_structured_response_from_data  # type: ignore
from new_report_schema import create_default_report  # type: ignore


def test_completed_games_default_and_payload_roundtrip() -> None:
    """Ensure completed_games defaults to [] and reflects provided values."""

    default_report = create_default_report("Tester", [], {}, {})
    assert default_report.completed_games == []

    sample_games: List[object] = [
        "Juego de lógica",
        {"name": "Desafío de memoria"},
        {"title": "Simulador de entrevista"},
    ]

    structured_report = _generate_structured_response_from_data(
        candidate_data={"fullName": "Tester"},
        soft_skills_data=[],
        cv_data={},
        job_preferences_data={},
        employability_score=0,
        level="",
        completed_games=sample_games,
    )

    assert structured_report.completed_games == [
        "Juego de lógica",
        "Desafío de memoria",
        "Simulador de entrevista",
    ]
