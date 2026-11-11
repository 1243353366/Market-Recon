from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

SignalKind = Literal[
    "management_demand_commentary",
    "import_activity",
    "export_activity",
    "shipping_delay",
    "hiring_activity",
    "insider_purchase",
    "institutional_holding_change",
    "patent_activity",
    "government_award",
    "regulatory_action",
    "customer_sentiment",
    "open_source_activity",
]
SignalDirection = Literal["positive", "negative", "mixed", "unknown"]


@dataclass(frozen=True)
class PublicSignal:
    """Normalized public observation; direction describes a measured change, not investment merit."""

    signal_id: str
    entity_id: str
    entity_name: str
    kind: SignalKind
    direction: SignalDirection
    observed_on: date
    summary: str
    source_name: str
    source_url: str
    metric_name: str | None = None
    metric_value: float | None = None
    unit: str | None = None
    baseline: str | None = None
    confidence: float = 0.5

    def __post_init__(self) -> None:
        if not self.signal_id.strip() or not self.entity_id.strip():
            raise ValueError("signal_id and entity_id must be non-empty")
        if not self.source_url.startswith("https://"):
            raise ValueError("Each signal requires an HTTPS source URL")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if not self.summary.strip():
            raise ValueError("summary must be non-empty")
