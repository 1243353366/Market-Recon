from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


class BenchmarkError(ValueError):
    pass


def score_review_cases(cases: list[dict[str, Any]], predictions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Score explicit benchmark annotations; missing/invalid outputs receive no credit.

    Each prediction contains finding_ids, severity_by_id, fix_passed, regression_free,
    and explanation_score (0..1). Correctness is judged against case annotations, not
    the model's own confidence or verbosity.
    """
    if not cases:
        raise BenchmarkError("Benchmark has no cases")
    known_ids = [case.get("id") for case in cases]
    if any(not isinstance(case_id, str) or not case_id for case_id in known_ids) or len(set(known_ids)) != len(known_ids):
        raise BenchmarkError("Cases require unique non-empty string ids")

    tp = fp = fn = 0
    severity_correct = severity_total = 0
    fix_total = fix_passed = regression_passed = regression_total = 0
    explanations: list[float] = []
    case_results = []

    for case in cases:
        case_id = case["id"]
        expected = set(case.get("expected_finding_ids", []))
        prediction = predictions.get(case_id, {})
        found = set(prediction.get("finding_ids", []))
        case_tp = len(expected & found)
        case_fp = len(found - expected)
        case_fn = len(expected - found)
        tp += case_tp
        fp += case_fp
        fn += case_fn
        expected_severity = case.get("severity_by_id", {})
        predicted_severity = prediction.get("severity_by_id", {})
        for finding_id in expected & found:
            severity_total += 1
            severity_correct += int(expected_severity.get(finding_id) == predicted_severity.get(finding_id))
        if expected:
            fix_total += 1
            fix_passed += int(prediction.get("fix_passed") is True)
            regression_total += 1
            regression_passed += int(prediction.get("regression_free") is True)
        explanation = prediction.get("explanation_score", 0)
        if isinstance(explanation, (int, float)) and math.isfinite(explanation):
            explanations.append(max(0.0, min(1.0, float(explanation))))
        case_results.append({"case_id": case_id, "true_positive": case_tp, "false_positive": case_fp, "false_negative": case_fn})

    precision = tp / (tp + fp) if tp + fp else (1.0 if fn == 0 else 0.0)
    recall = tp / (tp + fn) if tp + fn else 1.0
    detection_score = 20 * (2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    false_positive_score = 20 * precision
    severity_score = 10 * severity_correct / severity_total if severity_total else 0.0
    fix_score = 25 * fix_passed / fix_total if fix_total else 0.0
    regression_score = 25 * regression_passed / regression_total if regression_total else 0.0
    explanation_score = 5 * sum(explanations) / len(explanations) if explanations else 0.0
    # The published taxonomy weights detection 20, precision 20, remediation 25,
    # regression resistance 25, explanation 10. Severity is reported separately,
    # not double-counted: explanation's 10 points include a rubric for severity.
    explanation_score *= 2
    total = detection_score + false_positive_score + fix_score + regression_score + explanation_score
    return {
        "score_out_of_100": round(total, 2),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "severity_accuracy": round(severity_correct / severity_total, 4) if severity_total else None,
        "components": {
            "detection_f1_20": round(detection_score, 2),
            "false_positive_resistance_20": round(false_positive_score, 2),
            "fix_correctness_25": round(fix_score, 2),
            "regression_resistance_25": round(regression_score, 2),
            "explanation_quality_10": round(explanation_score, 2),
        },
        "cases": case_results,
    }


def load_cases(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise BenchmarkError("Benchmark file must contain a JSON list")
    return data
