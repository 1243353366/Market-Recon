from __future__ import annotations

from datetime import date
from typing import Any

from market_recon.data_sources_api import USASpendingClient
from .schema import NormalizedRecord


class USAspendingAdapter:
    source_id = "usaspending"

    def __init__(self, client: USASpendingClient) -> None:
        self.client = client

    def fetch(self, *, start_date: date, end_date: date, page: int = 1, limit: int = 100, **_: Any) -> list[NormalizedRecord]:
        rows = self.client.search_awards(start_date=start_date, end_date=end_date, page=page, limit=limit)
        return [NormalizedRecord(
            record_id=row.record_id,
            source_id=self.source_id,
            collection="federal_awards",
            record_type=row.record_type,
            source_name=row.source_name,
            source_url=row.source_url,
            retrieved_at=row.retrieved_at,
            observed_at=row.observed_on,
            data=row.data,
            entity_name=str(row.data.get("Recipient Name") or "") or None,
            license_status="public_api_terms_review_required",
            metadata={"award_id": row.record_id.removeprefix("usaspending:")},
        ) for row in rows]
