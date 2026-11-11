from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .chunking import chunk_document
from .embeddings import SentenceTransformerEmbedder
from .models import SourceDocument
from .store import QdrantKnowledgeBase


def ingest_documents(documents: list[SourceDocument], store: QdrantKnowledgeBase, chunk_size: int = 1200, overlap: int = 180) -> int:
    chunks = [chunk for document in documents for chunk in chunk_document(document, chunk_size, overlap)]
    return store.upsert(chunks)


def load_jsonl_documents(path: str | Path) -> list[SourceDocument]:
    """Load normalized public source documents from JSONL for arbitrary source adapters."""
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


def create_store(model_name: str, qdrant_path: str, qdrant_url: str | None = None, api_key: str | None = None) -> QdrantKnowledgeBase:
    embedder = SentenceTransformerEmbedder(model_name)
    return QdrantKnowledgeBase(embedder, path=qdrant_path, url=qdrant_url, api_key=api_key)
