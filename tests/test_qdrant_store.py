"""Real Qdrant (local mode) round-trip: the indexing path the workflow tests fake out."""
from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

import pytest

from market_recon.rag.chunking import chunk_document
from market_recon.rag.models import SourceDocument
from market_recon.rag.store import QdrantKnowledgeBase


class StubEmbedder:
    dimension = 16

    def _vector(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in text.lower().split():
            vector[sum(map(ord, token)) % self.dimension] += 1.0
        norm = sum(value * value for value in vector) ** 0.5 or 1.0
        return [value / norm for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


def document(body: str = "Supplier concentration risk could disrupt production.") -> SourceDocument:
    return SourceDocument(
        document_id="doc-1",
        title="Example 10-K Item 1A",
        text=body,
        source_name="SEC EDGAR",
        source_url="https://www.sec.gov/Archives/example",
        document_type="10-K",
        published_at="2026-02-01",
        retrieved_at="2026-02-02T00:00:00+00:00",
        ticker="DEMO",
        cik="0001234567",
        metadata={"accession_number": "0000-00-000001"},
    )


def store_for(tmp_path: Path) -> QdrantKnowledgeBase:
    return QdrantKnowledgeBase(StubEmbedder(), collection_name="filings", path=str(tmp_path / "qdrant"))


def test_generated_chunk_ids_are_uuid_shaped() -> None:
    for chunk in chunk_document(document()):
        parsed = uuid.UUID(chunk.chunk_id)
        assert str(parsed) == chunk.chunk_id


def test_upsert_and_retrieve_chunks(tmp_path: Path) -> None:
    store = store_for(tmp_path)
    chunks = chunk_document(document())
    assert len(chunks) == 1

    assert store.upsert(chunks) == 1

    points, _ = store.client.scroll("filings", limit=100, with_payload=True)
    assert len(points) == 1
    assert str(points[0].id) == chunks[0].chunk_id
    assert points[0].payload["document_id"] == "doc-1"
    assert points[0].payload["source_url"] == "https://www.sec.gov/Archives/example"


def test_repeated_ingestion_is_idempotent(tmp_path: Path) -> None:
    store = store_for(tmp_path)
    first = [chunk.chunk_id for chunk in chunk_document(document())]
    second = [chunk.chunk_id for chunk in chunk_document(document())]
    assert first == second

    store.upsert(chunk_document(document()))
    store.upsert(chunk_document(document()))
    points, _ = store.client.scroll("filings", limit=100)
    assert len(points) == len(first)


def test_chunk_point_id_is_stable_and_distinct() -> None:
    from market_recon.rag.chunking import chunk_point_id

    assert chunk_point_id("a:0:prefix") == chunk_point_id("a:0:prefix")
    assert chunk_point_id("a:0:prefix") != chunk_point_id("a:1:prefix")


def test_hex_digest_ids_are_rejected_before_the_call(tmp_path: Path) -> None:
    store = store_for(tmp_path)
    chunk = chunk_document(document())[0]
    broken = type(chunk)(chunk_id=hashlib.sha256(b"key").hexdigest(), document_id=chunk.document_id, text=chunk.text,
                        chunk_index=chunk.chunk_index, metadata=chunk.metadata)
    with pytest.raises(ValueError, match="not a Qdrant point ID"):
        store.upsert([broken])


def test_search_returns_the_cited_chunk(tmp_path: Path) -> None:
    store = store_for(tmp_path)
    store.upsert(chunk_document(document()))
    hits = store.search("supplier concentration risk", limit=3)
    assert hits
    assert hits[0].document_id == "doc-1"
    assert hits[0].metadata["source_url"] == "https://www.sec.gov/Archives/example"
