from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from market_recon.intelligence.models import PublicSignal
from market_recon.sources.schema import NormalizedRecord


def test_normalized_record_parses_shared_contract():
    path = Path(__file__).parent.parent / "contracts" / "record_contract.json"
    with path.open("r", encoding="utf-8") as stream:
        raw = json.load(stream)

    raw.pop("version", None)
    record = NormalizedRecord(**raw)
    assert record.record_id == "rec:sec:0000320193:20241101"
    assert record.source_id == "sec"
    assert record.collection == "filings"
    assert record.record_type == "10-K"
    assert record.ticker == "AAPL"
    assert record.license_status == "public_domain"
    assert "supply chain" in record.data["text"]
    assert record.metadata["primary_document_fetched"] is True


def test_public_signal_model_parses_shared_contract():
    path = Path(__file__).parent.parent / "contracts" / "signal_contract.json"
    with path.open("r", encoding="utf-8") as stream:
        raw = json.load(stream)

    raw.pop("version", None)
    raw.pop("category", None)
    raw["observed_on"] = date.fromisoformat(raw["observed_on"])
    signal = PublicSignal(**raw)
    assert signal.signal_id == "sig:sec:aapl:shipping_delay:20260201"
    assert signal.entity_id == "entity:sec:cik:0000320193"
    assert signal.kind == "shipping_delay"
    assert signal.direction == "negative"
    assert signal.metric_value == -14.5
    assert signal.confidence == 0.95
