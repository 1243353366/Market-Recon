from __future__ import annotations

from datetime import date, timedelta

import pytest

from market_recon.intelligence.divergence import find_cross_signal_divergences
from market_recon.intelligence.models import PublicSignal


def signal(signal_id: str, kind: str, direction: str, day: date, entity_name: str = "Example Co", source_name: str = "Public test source") -> PublicSignal:
    return PublicSignal(
        signal_id=signal_id,
        entity_id="CIK0000000001",
        entity_name=entity_name,
        kind=kind,  # type: ignore[arg-type]
        direction=direction,  # type: ignore[arg-type]
        observed_on=day,
        summary=f"{kind} changed",
        source_name=source_name,
        source_url="https://example.org/evidence",
    )


def test_divergence_requires_both_directions_and_distinct_signal_kinds() -> None:
    today = date(2026, 1, 1)
    observations = [
        signal("a", "management_demand_commentary", "negative", today, source_name="SEC 10-K"),
        signal("b", "hiring_activity", "positive", today, source_name="Bureau of Labor Statistics"),
    ]
    results = find_cross_signal_divergences(observations, as_of=today)
    assert len(results) == 1
    assert results[0].positive_signal_count == results[0].negative_signal_count == 1
    assert "not evidence of deception" in results[0].interpretation
    assert results[0].distinct_kind_count == 2
    assert results[0].distinct_source_count == 2
    assert results[0].divergence_caveat is None


def test_out_of_window_and_unknown_signals_do_not_create_divergence() -> None:
    today = date(2026, 1, 1)
    observations = [
        signal("old", "management_demand_commentary", "negative", today - timedelta(days=121)),
        signal("unknown", "hiring_activity", "unknown", today),
    ]
    assert find_cross_signal_divergences(observations, as_of=today) == []


def test_invalid_window_rejected() -> None:
    with pytest.raises(ValueError):
        find_cross_signal_divergences([], as_of=date.today(), window_days=0)


def test_signal_requires_citable_https_provenance() -> None:
    with pytest.raises(ValueError):
        PublicSignal("x", "cik", "Company", "hiring_activity", "positive", date.today(), "x", "Source", "http://example.org")  # type: ignore[arg-type]


def test_signal_validates_field_types_and_raises_value_error_not_attribute_error() -> None:
    today = date.today()

    with pytest.raises(ValueError, match="source_name"):
        PublicSignal("sig1", "CIK1", "Corp", "hiring_activity", "positive", today, "summary", None, "https://example.com")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="source_name"):
        PublicSignal("sig1", "CIK1", "Corp", "hiring_activity", "positive", today, "summary", 12345, "https://example.com")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="source_url"):
        PublicSignal("sig1", "CIK1", "Corp", "hiring_activity", "positive", today, "summary", "Source", 123)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="signal_id"):
        PublicSignal(None, "CIK1", "Corp", "hiring_activity", "positive", today, "summary", "Source", "https://example.com")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="entity_id"):
        PublicSignal("sig1", None, "Corp", "hiring_activity", "positive", today, "summary", "Source", "https://example.com")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="entity_name"):
        PublicSignal("sig1", "CIK1", None, "hiring_activity", "positive", today, "summary", "Source", "https://example.com")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="summary"):
        PublicSignal("sig1", "CIK1", "Corp", "hiring_activity", "positive", today, None, "Source", "https://example.com")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="metric_name"):
        PublicSignal("sig1", "CIK1", "Corp", "hiring_activity", "positive", today, "summary", "Source", "https://example.com", metric_name=999)  # type: ignore[arg-type]


def test_divergence_deduplicates_duplicate_signal_ids() -> None:
    today = date(2026, 1, 1)
    sig_pos = signal("sig_pos_1", "hiring_activity", "positive", today)
    sig_neg = signal("sig_neg_1", "management_demand_commentary", "negative", today)

    # Ingest the exact same positive signal 5 times and negative signal 3 times
    observations = [sig_pos, sig_pos, sig_pos, sig_pos, sig_pos, sig_neg, sig_neg, sig_neg]
    results = find_cross_signal_divergences(observations, as_of=today)

    assert len(results) == 1
    assert results[0].positive_signal_count == 1
    assert results[0].negative_signal_count == 1
    assert len(results[0].signals) == 2


def test_divergence_uses_latest_entity_name_across_time() -> None:
    today = date(2026, 1, 1)
    older_day = date(2025, 11, 1)

    sig_old = signal("sig_1", "management_demand_commentary", "negative", older_day, entity_name="Old Name Inc")
    sig_new = signal("sig_2", "hiring_activity", "positive", today, entity_name="Rebranded Modern Corp")

    results = find_cross_signal_divergences([sig_old, sig_new], as_of=today)
    assert len(results) == 1
    assert results[0].entity_name == "Rebranded Modern Corp"


def test_divergence_identifies_single_source_and_heterogeneous_baselines() -> None:
    today = date(2026, 1, 1)
    sig1 = PublicSignal(
        signal_id="s1",
        entity_id="E1",
        entity_name="SingleSource Corp",
        kind="hiring_activity",
        direction="positive",
        observed_on=today,
        summary="Headcount expanded",
        source_name="Company Press Release",
        source_url="https://example.com/pr",
        baseline="YoY",
    )
    sig2 = PublicSignal(
        signal_id="s2",
        entity_id="E1",
        entity_name="SingleSource Corp",
        kind="shipping_delay",
        direction="negative",
        observed_on=today,
        summary="Shipment delays reported",
        source_name="Company Press Release",
        source_url="https://example.com/pr",
        baseline="Sequential QoQ",
    )

    results = find_cross_signal_divergences([sig1, sig2], as_of=today)
    assert len(results) == 1
    assert results[0].distinct_source_count == 1
    assert results[0].divergence_caveat is not None
    assert "single source" in results[0].divergence_caveat
    assert "heterogeneous baselines" in results[0].divergence_caveat
