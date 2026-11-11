from __future__ import annotations

import pytest

from benchmark.scoring import BenchmarkError, score_review_cases


def test_perfect_predictions_score_100_including_no_bug_case() -> None:
    cases = [
        {"id": "clean", "expected_finding_ids": [], "severity_by_id": {}},
        {"id": "bug", "expected_finding_ids": ["x"], "severity_by_id": {"x": "medium"}},
    ]
    predictions = {
        "clean": {"finding_ids": [], "explanation_score": 1},
        "bug": {"finding_ids": ["x"], "severity_by_id": {"x": "medium"}, "fix_passed": True, "regression_free": True, "explanation_score": 1},
    }
    result = score_review_cases(cases, predictions)
    assert result["score_out_of_100"] == 100
    assert result["precision"] == result["recall"] == 1


def test_false_positive_on_known_good_case_is_penalized() -> None:
    result = score_review_cases(
        [{"id": "clean", "expected_finding_ids": []}],
        {"clean": {"finding_ids": ["invented"]}},
    )
    assert result["precision"] == 0
    assert result["score_out_of_100"] < 20


def test_duplicate_case_ids_rejected() -> None:
    with pytest.raises(BenchmarkError):
        score_review_cases([{"id": "x"}, {"id": "x"}], {})
