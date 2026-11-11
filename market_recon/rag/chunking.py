from __future__ import annotations

import hashlib
import uuid

from .models import DocumentChunk, SourceDocument

# Stable namespace so the same content key always maps to the same point ID across runs.
_POINT_NAMESPACE = uuid.UUID("6f1f8f6e-1f2a-5a7b-9b1e-3f6d2c4a8e57")


def content_key(document_id: str, index: int, excerpt: str) -> str:
    """Identity of a chunk: document, ordinal, and a prefix of its text."""
    return f"{document_id}:{index}:{excerpt[:80]}"


def chunk_point_id(stable_key: str) -> str:
    """Deterministic UUID for a chunk key.

    Qdrant accepts unsigned 64-bit integers or UUIDs as point IDs and rejects raw
    SHA-256 hex digests, so the content hash is namespaced into a UUID. Repeated
    ingestion of the same document therefore overwrites the same points.
    """
    return str(uuid.uuid5(_POINT_NAMESPACE, stable_key))


def chunk_document(document: SourceDocument, chunk_size: int = 1200, overlap: int = 180) -> list[DocumentChunk]:
    """Split text into stable, overlapping character chunks while preserving source metadata."""
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0")

    text = " ".join(document.text.split())
    if not text:
        return []

    step = chunk_size - overlap
    chunks: list[DocumentChunk] = []
    for index, start in enumerate(range(0, len(text), step)):
        excerpt = text[start : start + chunk_size]
        if not excerpt:
            break
        stable_key = content_key(document.document_id, index, excerpt)
        content_hash = hashlib.sha256(stable_key.encode("utf-8")).hexdigest()
        chunks.append(
            DocumentChunk(
                chunk_id=chunk_point_id(stable_key),
                document_id=document.document_id,
                text=excerpt,
                chunk_index=index,
                metadata={**document.to_payload(), "content_hash": content_hash},
            )
        )
    return chunks
