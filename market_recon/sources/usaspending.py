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
        return self.client.search_awards(start_date=start_date, end_date=end_date, page=page, limit=limit)
