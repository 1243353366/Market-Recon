from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from market_recon.sources.filing_intelligence import _RULES, _evaluate_match

CATEGORIES = tuple(rule[0] for rule in _RULES)


@dataclass(frozen=True)
class CategoryMetric:
    category: str
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class EvaluationReport:
    version: str
    total_cases: int
    hard_negatives_count: int
    hard_negatives_passed: int
    overall_precision: float
    overall_recall: float
    overall_f1: float
    category_metrics: dict[str, CategoryMetric]
    mismatches: list[dict[str, Any]]


def evaluate_filing_corpus(corpus_path: str | Path | None = None) -> EvaluationReport:
    """Evaluate filing change classification rules against the versioned labeled corpus."""
    path = Path(corpus_path) if corpus_path else Path(__file__).parent / "filing_change_corpus.json"
    with path.open("r", encoding="utf-8") as stream:
        data = json.load(stream)

    version = data.get("version", "unknown")
    cases = data.get("cases", [])

    counts = {
        cat: {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
        for cat in CATEGORIES
    }

    mismatches: list[dict[str, Any]] = []
    hard_negatives_count = 0
    hard_negatives_passed = 0

    for case in cases:
        case_id = case["id"]
        section = case["section"]
        text = case["text"]
        expected = set(case["expected_categories"])
        is_hard_neg = case.get("is_hard_negative", False)

        predicted: set[str] = set()
        match_details: dict[str, str] = {}
        for category in CATEGORIES:
            matched, phrase, hint, reason = _evaluate_match(category, section, text)
            if matched:
                predicted.add(category)
                match_details[category] = reason

        if is_hard_neg:
            hard_negatives_count += 1
            if not predicted:
                hard_negatives_passed += 1

        for category in CATEGORIES:
            is_expected = category in expected
            is_predicted = category in predicted

            if is_expected and is_predicted:
                counts[category]["tp"] += 1
            elif not is_expected and is_predicted:
                counts[category]["fp"] += 1
            elif is_expected and not is_predicted:
                counts[category]["fn"] += 1
            else:
                counts[category]["tn"] += 1

        if predicted != expected:
            mismatches.append({
                "case_id": case_id,
                "section": section,
                "text": text,
                "expected": sorted(expected),
                "predicted": sorted(predicted),
                "details": match_details,
            })

    category_metrics: dict[str, CategoryMetric] = {}
    total_tp = sum(c["tp"] for c in counts.values())
    total_fp = sum(c["fp"] for c in counts.values())
    total_fn = sum(c["fn"] for c in counts.values())

    for cat in CATEGORIES:
        tp = counts[cat]["tp"]
        fp = counts[cat]["fp"]
        fn = counts[cat]["fn"]
        tn = counts[cat]["tn"]

        prec = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else (1.0 if fp == 0 else 0.0)
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        category_metrics[cat] = CategoryMetric(
            category=cat,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            true_negatives=tn,
            precision=round(prec, 4),
            recall=round(rec, 4),
            f1=round(f1, 4),
        )

    overall_prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 1.0
    overall_rec = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 1.0
    overall_f1 = (2 * overall_prec * overall_rec) / (overall_prec + overall_rec) if (overall_prec + overall_rec) > 0 else 0.0

    return EvaluationReport(
        version=version,
        total_cases=len(cases),
        hard_negatives_count=hard_negatives_count,
        hard_negatives_passed=hard_negatives_passed,
        overall_precision=round(overall_prec, 4),
        overall_recall=round(overall_rec, 4),
        overall_f1=round(overall_f1, 4),
        category_metrics=category_metrics,
        mismatches=mismatches,
    )


if __name__ == "__main__":
    report = evaluate_filing_corpus()
    print(f"Filing Classification Benchmark (v{report.version})")
    print(f"Cases: {report.total_cases} | Hard Negatives: {report.hard_negatives_passed}/{report.hard_negatives_count} passed")
    print(f"Overall Precision: {report.overall_precision:.2%} | Recall: {report.overall_recall:.2%} | F1: {report.overall_f1:.2%}")
    for cat, metric in report.category_metrics.items():
        print(f"  {cat:22s} P={metric.precision:.2%} R={metric.recall:.2%} F1={metric.f1:.2%}")
    if report.mismatches:
        print("\nMismatches:")
        for m in report.mismatches:
            print(" ", m)
