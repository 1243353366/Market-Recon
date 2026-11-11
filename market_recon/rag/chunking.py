from __future__ import annotations

import hashlib

from .models import DocumentChunk, SourceDocument


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
        stable_key = f"{document.document_id}:{index}:{excerpt[:80]}"
        chunk_id = hashlib.sha256(stable_key.encode("utf-8")).hexdigest()
        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                document_id=document.document_id,
                text=excerpt,
                chunk_index=index,
                metadata=document.to_payload(),
            )
        )
    return chunks
