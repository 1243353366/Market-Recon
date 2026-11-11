from __future__ import annotations

from datetime import date

import pytest

from market_recon.intelligence.models import PublicSignal


def make_signal(**overrides):
    fields = {
        "signal_id": "signal-1", "entity_id": "CIK0000000001", "entity_name": "Example Co",
        "kind": "package_activity", "direction": "positive", "observed_on": date(2026, 1, 1),
        "summary": "Public package download count increased against baseline.", "source_name": "Registry",
        "source_url": "https://example.org/source", "baseline": "prior 30-day count",
    }
    fields.update(overrides)
    return PublicSignal(**fields)


def test_engineering_and_regulatory_categories_are_supported():
    assert make_signal(kind="package_activity").kind == "package_activity"
    assert make_signal(kind="regulatory_comment").kind == "regulatory_comment"
    assert make_signal(kind="permit_activity").kind == "permit_activity"


def test_invalid_direction_and_non_finite_measurements_are_rejected():
    with pytest.raises(ValueError, match="direction"):
        make_signal(direction="bullish")
    with pytest.raises(ValueError, match="finite"):
        make_signal(confidence=float("nan"))
    with pytest.raises(ValueError, match="finite"):
        make_signal(metric_value=float("inf"))


def test_source_name_is_required():
    with pytest.raises(ValueError, match="source name"):
        make_signal(source_name="")
