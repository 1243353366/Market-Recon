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
        return self.client.observations(series_id, start_date=start_date, end_date=end_date, limit=limit)
