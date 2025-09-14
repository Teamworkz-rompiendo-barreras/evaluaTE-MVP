import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from new_report_schema import CvAnalysis, CvEvidence


def test_cv_analysis_list_independence():
    evidence1 = CvEvidence(structure="", coherence="", key_info="", clarity="", style="")
    evidence2 = CvEvidence(structure="", coherence="", key_info="", clarity="", style="")
    cv1 = CvAnalysis(
        structure_score=1,
        coherence_score=1,
        key_info_score=1,
        clarity_score=1,
        style_score=1,
        evidence=evidence1,
    )
    cv2 = CvAnalysis(
        structure_score=2,
        coherence_score=2,
        key_info_score=2,
        clarity_score=2,
        style_score=2,
        evidence=evidence2,
    )

    cv1.corrections.append("fix1")
    cv1.reordering_suggestions.append("reorder1")
    cv1.observations.append("obs1")
    cv1.actions.append("act1")

    assert cv2.corrections == []
    assert cv2.reordering_suggestions == []
    assert cv2.observations == []
    assert cv2.actions == []

    cv2.corrections.append("fix2")
    cv2.reordering_suggestions.append("reorder2")
    cv2.observations.append("obs2")
    cv2.actions.append("act2")

    assert cv1.corrections == ["fix1"]
    assert cv2.corrections == ["fix2"]
    assert cv1.reordering_suggestions == ["reorder1"]
    assert cv2.reordering_suggestions == ["reorder2"]
    assert cv1.observations == ["obs1"]
    assert cv2.observations == ["obs2"]
    assert cv1.actions == ["act1"]
    assert cv2.actions == ["act2"]

