from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from market_recon.rag.models import SourceDocument
from market_recon.rag.pipeline import load_normalized_jsonl_documents, source_record_to_document
from market_recon.sources.schema import NormalizedRecord


def test_source_document_metadata_cannot_override_canonical_provenance():
    document = SourceDocument(
        "doc:1", "Real title", "body", "SEC", "https://sec.gov/real", "10-K",
        metadata={"source_url": "https://evil.example/override", "title": "Fake title"},
    )
    with pytest.raises(ValueError, match="canonical provenance"):
        document.to_payload()


def test_normalized_record_to_rag_document_preserves_authoritative_fields():
    record = NormalizedRecord(
        record_id="sec:1", source_id="sec_edgar", collection="sec_filings", record_type="sec_filing",
        source_name="SEC EDGAR", source_url="https://www.sec.gov/Archives/filing", retrieved_at=datetime.now(timezone.utc).isoformat(),
        data={"title": "Example 10-K", "text": "Public filing text."}, published_at="2026-01-01",
        ticker="TEST", cik="0000000001", metadata={"accession_number": "0001"},
    )
    document = source_record_to_document(record)
    payload = document.to_payload()
    assert payload["source_url"] == record.source_url
    assert payload["title"] == "Example 10-K"
    assert payload["record_id"] == "sec:1"
    assert payload["provider_metadata"] == {"accession_number": "0001"}


def test_normalized_jsonl_loader_rejects_non_text_records(tmp_path: Path):
    record = NormalizedRecord(
        "fred:CPI:2026-01-01", "fred", "fred_macro", "economic_observation", "FRED",
        "https://fred.stlouisfed.org/series/CPI", "2026-01-02T00:00:00Z", {"value": "2.5"},
    )
    path = tmp_path / "records.jsonl"
    import json
    path.write_text(json.dumps(record.to_dict()) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no non-empty textual"):
        load_normalized_jsonl_documents(path)
