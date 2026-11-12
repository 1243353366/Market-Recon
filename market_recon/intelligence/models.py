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
        for field_name in ("signal_id", "entity_id", "entity_name", "summary", "source_url"):
            val = getattr(self, field_name)
            if not isinstance(val, str) or not val.strip():
                raise ValueError(f"{field_name} must be a non-empty string")

        if not isinstance(self.source_name, str) or not self.source_name.strip():
            raise ValueError("Each signal requires a valid source name (source_name)")

        for opt_field in ("metric_name", "unit", "baseline"):
            opt_val = getattr(self, opt_field)
            if opt_val is not None and (not isinstance(opt_val, str) or not opt_val.strip()):
                raise ValueError(f"{opt_field} must be a non-empty string when provided")

        if self.kind not in get_args(SignalKind):
            raise ValueError(f"Unsupported signal kind: {self.kind}")
        if self.direction not in get_args(SignalDirection):
            raise ValueError(f"Unsupported signal direction: {self.direction}")
        if not isinstance(self.observed_on, date):
            raise ValueError("observed_on must be a date")
        if not self.source_url.startswith("https://"):
            raise ValueError("Each signal requires an HTTPS source URL")
        if not isfinite(self.confidence) or not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be finite and between 0 and 1")
        if self.metric_value is not None and not isfinite(self.metric_value):
            raise ValueError("metric_value must be finite when provided")
