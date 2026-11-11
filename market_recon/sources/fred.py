from __future__ import annotations

from datetime import date
from typing import Any

from market_recon.data_sources_api import FredClient
from .schema import NormalizedRecord


class FREDAdapter:
    source_id = "fred"

    def __init__(self, client: FredClient) -> None:
        self.client = client

    def fetch(
        self,
        *,
        series_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 1000,
        **_: Any,
    ) -> list[NormalizedRecord]:
        rows = self.client.observations(series_id, start_date=start_date, end_date=end_date, limit=limit)
        return [NormalizedRecord(
            record_id=row.record_id,
            source_id=self.source_id,
            collection="macro_observations",
            record_type=row.record_type,
            source_name=row.source_name,
            source_url=row.source_url,
            retrieved_at=row.retrieved_at,
            observed_at=row.observed_on,
            data=row.data,
            license_status="fred_api_terms_review_required",
            metadata={"series_id": series_id},
        ) for row in rows]
