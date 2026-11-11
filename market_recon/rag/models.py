from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceDocument:
    """A source document with traceable public provenance."""

    document_id: str
    title: str
    text: str
    source_name: str
    source_url: str
    document_type: str
    published_at: str | None = None
    retrieved_at: str | None = None
    ticker: str | None = None
    cik: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("text")
        payload.pop("metadata")
        payload.update(self.metadata)
        return payload


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    document_id: str
    text: str
    chunk_index: int
    metadata: dict[str, Any]


@dataclass(frozen=True)
class SearchHit:
    chunk_id: str
    document_id: str
    text: str
    score: float
    metadata: dict[str, Any]
