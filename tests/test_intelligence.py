from __future__ import annotations

from datetime import date, timedelta

import pytest

from market_recon.intelligence.divergence import find_cross_signal_divergences
from market_recon.intelligence.models import PublicSignal


def signal(signal_id: str, kind: str, direction: str, day: date) -> PublicSignal:
    return PublicSignal(
        signal_id=signal_id,
        entity_id="CIK0000000001",
        entity_name="Example Co",
        kind=kind,  # type: ignore[arg-type]
        direction=direction,  # type: ignore[arg-type]
        observed_on=day,
        summary=f"{kind} changed",
        source_name="Public test source",
        source_url="https://example.org/evidence",
    )


def test_divergence_requires_both_directions_and_distinct_signal_kinds() -> None:
    today = date(2026, 1, 1)
    observations = [
        signal("a", "management_demand_commentary", "negative", today),
        signal("b", "hiring_activity", "positive", today),
    ]
    results = find_cross_signal_divergences(observations, as_of=today)
    assert len(results) == 1
    assert results[0].positive_signal_count == results[0].negative_signal_count == 1
    assert "not evidence of deception" in results[0].interpretation


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
