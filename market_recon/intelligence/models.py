from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Literal, get_args

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
    "package_activity",
    "cve_disclosure",
    "technical_presentation",
    "standards_publication",
    "academic_research",
    "university_licensing",
    "permit_activity",
    "local_agenda",
    "regulatory_comment",
    "agency_docket",
    "litigation_event",
    "board_change",
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
        if self.kind not in get_args(SignalKind):
            raise ValueError(f"Unsupported signal kind: {self.kind}")
        if self.direction not in get_args(SignalDirection):
            raise ValueError(f"Unsupported signal direction: {self.direction}")
        if not isinstance(self.observed_on, date):
            raise ValueError("observed_on must be a date")
        if not self.source_name.strip() or not self.source_url.startswith("https://"):
            raise ValueError("Each signal requires a source name and HTTPS source URL")
        if not isfinite(self.confidence) or not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be finite and between 0 and 1")
        if self.metric_value is not None and not isfinite(self.metric_value):
            raise ValueError("metric_value must be finite when provided")
        if not self.summary.strip():
            raise ValueError("summary must be non-empty")
