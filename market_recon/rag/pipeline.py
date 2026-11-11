from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from market_recon.sources.schema import NormalizedRecord

from .chunking import chunk_document
from .embeddings import SentenceTransformerEmbedder
from .models import SourceDocument
from .store import QdrantKnowledgeBase


def source_record_to_document(record: NormalizedRecord) -> SourceDocument:
    """Convert a normalized record with textual content into a provenance-safe RAG document.

    Structured-only observations (for example one FRED numeric datum) are not prose documents
    and must remain in structured storage rather than being embedded as fabricated narratives.
    """
    data = record.data
    text = data.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"Record {record.record_id!r} has no non-empty textual data['text'] for RAG indexing")
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        title = f"{record.record_type}: {record.entity_name or record.ticker or record.record_id}"
    metadata = {
        "record_id": record.record_id,
        "source_id": record.source_id,
        "collection": record.collection,
        "record_type": record.record_type,
        "observed_at": record.observed_at,
        "entity_id": record.entity_id,
        "entity_name": record.entity_name,
        "license_status": record.license_status,
        "provider_metadata": record.metadata,
    }
    return SourceDocument(
        document_id=record.record_id,
        title=title,
        text=text,
        source_name=record.source_name,
        source_url=record.source_url,
        document_type=record.record_type,
        published_at=record.published_at,
        retrieved_at=record.retrieved_at,
        ticker=record.ticker,
        cik=record.cik,
        metadata=metadata,
    )


def ingest_documents(documents: list[SourceDocument], store: QdrantKnowledgeBase, chunk_size: int = 1200, overlap: int = 180) -> int:
    chunks = [chunk for document in documents for chunk in chunk_document(document, chunk_size, overlap)]
    return store.upsert(chunks)


def load_jsonl_documents(path: str | Path) -> list[SourceDocument]:
    """Load legacy RAG JSONL documents containing document_id/title/text/source fields."""
    documents = []
    with Path(path).open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            row: dict[str, Any] = json.loads(line)
            documents.append(SourceDocument(
                document_id=str(row.get("document_id") or f"local-{line_number}"),
                title=str(row["title"]),
                text=str(row["text"]),
                source_name=str(row["source_name"]),
                source_url=str(row["source_url"]),
                document_type=str(row["document_type"]),
                published_at=row.get("published_at"),
                retrieved_at=row.get("retrieved_at") or datetime.now(timezone.utc).isoformat(),
                ticker=row.get("ticker"),
                cik=row.get("cik"),
                metadata=row.get("metadata", {}),
            ))
    return documents


def load_normalized_jsonl_documents(path: str | Path) -> list[SourceDocument]:
    """Load adapter `NormalizedRecord` JSONL and convert only text-bearing records to RAG docs."""
    documents: list[SourceDocument] = []
    with Path(path).open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            row: dict[str, Any] = json.loads(line)
            record = NormalizedRecord(**row)
            documents.append(source_record_to_document(record))
    return documents


def create_store(model_name: str, qdrant_path: str, qdrant_url: str | None = None, api_key: str | None = None) -> QdrantKnowledgeBase:
    embedder = SentenceTransformerEmbedder(model_name)
    return QdrantKnowledgeBase(embedder, path=qdrant_path, url=qdrant_url, api_key=api_key)
