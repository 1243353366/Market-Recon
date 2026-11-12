from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class NormalizedRecord:
    """Canonical source record shared by adapters and downstream stores.

    `observed_at` is when the event/observation applies; `retrieved_at` records
    ingestion time. `source_url` must be a verifiable citation URL. Raw provider
    fields remain under `data`; do not silently coerce numeric strings or dates.
    """

    record_id: str
    source_id: str
    collection: str
    record_type: str
    source_name: str
    source_url: str
    retrieved_at: str
    data: dict[str, Any]
    observed_at: str | None = None
    published_at: str | None = None
    entity_id: str | None = None
    entity_name: str | None = None
    ticker: str | None = None
    cik: str | None = None
    license_status: str = "review_required"
    metadata: dict[str, Any] = field(default_factory=dict)
    run_id: str | None = None

    def __post_init__(self) -> None:
        for name in ("record_id", "source_id", "collection", "record_type", "source_name"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be empty")
        if not self.source_url.startswith("https://"):
            raise ValueError("source_url must be an HTTPS URL")
        if not self.retrieved_at:
            raise ValueError("retrieved_at is required")
        if not isinstance(self.data, dict):
            raise TypeError("data must be a dictionary")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@runtime_checkable
class SourceAdapter(Protocol):
    """Minimal adapter contract: stable ID, provenance, bounded fetch, normalized output."""

    source_id: str

    def fetch(self, **kwargs: Any) -> list[NormalizedRecord]: ...


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
