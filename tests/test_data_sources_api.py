from __future__ import annotations

from datetime import date
from unittest.mock import Mock

import pytest

from market_recon.data_sources_api import FredClient, USASpendingClient


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self.body


def test_fred_observations_keep_source_and_query_params():
    session = Mock()
    session.get.return_value = FakeResponse({"observations": [{"date": "2026-01-01", "value": "2.5"}]})
    records = FredClient("test-key", session=session).observations(
        "CPIAUCSL", start_date=date(2025, 1, 1), end_date=date(2026, 1, 1)
    )
    assert records[0].record_id == "fred:CPIAUCSL:2026-01-01"
    assert records[0].data["value"] == "2.5"
    assert records[0].source_url.endswith("/CPIAUCSL")
    assert session.get.call_args.kwargs["timeout"] > 0
    assert session.get.call_args.kwargs["params"]["api_key"] == "test-key"


def test_fred_validates_key_dates_and_limit():
    with pytest.raises(ValueError):
        FredClient("")
    client = FredClient("key", session=Mock())
    with pytest.raises(ValueError):
        client.observations("GDP", start_date=date(2026, 1, 2), end_date=date(2026, 1, 1))
    with pytest.raises(ValueError):
        client.observations("GDP", limit=0)


def test_usaspending_awards_are_normalized_and_cited():
    session = Mock()
    session.post.return_value = FakeResponse({"results": [{"Award ID": "ABC123", "Recipient Name": "Example", "Award Amount": 1000}]})
    records = USASpendingClient(session=session).search_awards(start_date=date(2025, 1, 1), end_date=date(2025, 12, 31))
    assert records[0].record_id == "usaspending:ABC123"
    assert records[0].source_url.endswith("/ABC123")
    assert session.post.call_args.kwargs["timeout"] > 0


def test_usaspending_validates_bounds():
    with pytest.raises(ValueError):
        USASpendingClient(session=Mock()).search_awards(start_date=date(2026, 1, 2), end_date=date(2026, 1, 1))


def test_fred_missing_value_sentinel_normalizes_to_none():
    session = Mock()
    session.get.return_value = FakeResponse({"observations": [
        {"date": "2026-01-01", "value": "."},
        {"date": "2026-01-02", "value": "2.5"},
    ]})
    records = FredClient("key", session=session).observations("DGS10")
    assert records[0].data["value"] is None
    assert records[1].data["value"] == "2.5"
    assert records[0].source_id == "fred"
    assert records[0].collection == "fred_macro"
    assert records[0].license_status == "fred_api_terms_review_required"
