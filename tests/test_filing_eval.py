from __future__ import annotations

from benchmark.filing_eval import evaluate_filing_corpus


def test_filing_change_corpus_benchmark_metrics():
    report = evaluate_filing_corpus()
    assert report.total_cases >= 10
    assert report.hard_negatives_count >= 5
    assert report.hard_negatives_passed == report.hard_negatives_count, (
        f"Hard negatives failed: {report.hard_negatives_passed}/{report.hard_negatives_count}"
    )
    assert report.overall_precision >= 0.95
    assert report.overall_recall >= 0.90
    assert report.overall_f1 >= 0.90
    for category, metric in report.category_metrics.items():
        assert metric.precision >= 0.90
        assert metric.recall >= 0.85
