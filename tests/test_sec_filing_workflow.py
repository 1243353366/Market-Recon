from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from market_recon.rag.models import DocumentChunk, SourceDocument
from market_recon.sources.sec_filing_workflow import FilingVersionStore, SecFilingWorkflow


class FakeClient:
    def __init__(self, documents):
        self.documents = documents

    def recent_filings(self, ticker, forms, limit):
        return [doc for doc in self.documents if doc.document_type in forms][:limit]


class FakeIndex:
    def __init__(self):
        self.chunks: list[DocumentChunk] = []

    def upsert(self, chunks, batch_size=64):
        self.chunks.extend(chunks)
        return len(chunks)


def doc(document_id: str, filing_date: str, body: str) -> SourceDocument:
    text = f"PART I\nITEM 1A. RISK FACTORS\n{body}\nPART II\nITEM 7. MANAGEMENT DISCUSSION\nRevenue was stable."
    return SourceDocument(document_id, "Example 10-K", text, "SEC EDGAR", f"https://www.sec.gov/Archives/{document_id}", "10-K", filing_date, datetime.now(timezone.utc).isoformat(), "TEST", "000123", {"accession_number": document_id})


def test_filing_workflow_fetches_parses_chunks_indexes_and_compares(tmp_path: Path):
    client = FakeClient([
        doc("old", "2025-02-01", "The company faces supplier concentration risk."),
        doc("new", "2026-02-01", "A new cybersecurity risk could adversely affect operations."),
    ])
    index = FakeIndex()
    versions = FilingVersionStore(tmp_path / "filings.sqlite")
    workflow = SecFilingWorkflow(client, index, versions)
    first = workflow.ingest("TEST", "10-K", limit=1)
    assert first.documents == first.sections == first.chunks_indexed == 1
    second = workflow.ingest("TEST", "10-K", limit=2)
    assert second.documents == 2
    assert second.chunks_indexed >= 2
    assert all(chunk.metadata.get("section") for chunk in index.chunks)
    report = workflow.compare_latest("TEST", "10-K")
    changes = report["changes"]["risks"]
    assert len(changes) == 2
    assert changes[0]["before_url"].startswith("https://")
    assert changes[0]["after_url"].startswith("https://")
    assert "heuristic" in changes[0]["explanation"]


def test_compare_requires_two_filing_versions(tmp_path: Path):
    versions = FilingVersionStore(tmp_path / "filings.sqlite")
    workflow = SecFilingWorkflow(FakeClient([]), FakeIndex(), versions)
    try:
        workflow.compare_latest("TEST")
    except LookupError as exc:
        assert "at least two" in str(exc)
    else:
        raise AssertionError("Expected missing-version error")
