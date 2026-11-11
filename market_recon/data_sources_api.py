from __future__ import annotations

from datetime import date
from typing import Any

import requests

from market_recon.sources.schema import NormalizedRecord

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"
USA_SPENDING_AWARDS_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"


def _retrieved_at() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


class FredClient:
    """Minimal FRED series observations client. Requires a FRED API key."""

    def __init__(self, api_key: str, *, session: requests.Session | None = None, timeout: float = 20) -> None:
        if not api_key.strip():
            raise ValueError("FRED_API_KEY is required")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.api_key = api_key
        self.session = session or requests.Session()
        self.timeout = timeout

    def observations(
        self,
        series_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 1000,
    ) -> list[NormalizedRecord]:
        if not series_id.strip():
            raise ValueError("series_id must not be empty")
        if limit < 1 or limit > 100000:
            raise ValueError("limit must be between 1 and 100000")
        if start_date and end_date and start_date > end_date:
            raise ValueError("start_date must be on or before end_date")
        params: dict[str, Any] = {
            "api_key": self.api_key,
            "file_type": "json",
            "series_id": series_id,
            "limit": limit,
            "sort_order": "asc",
        }
        if start_date:
            params["observation_start"] = start_date.isoformat()
        if end_date:
            params["observation_end"] = end_date.isoformat()
        response = self.session.get(FRED_OBSERVATIONS_URL, params=params, timeout=self.timeout)
        response.raise_for_status()
        body = response.json()
        retrieved = _retrieved_at()
        return [
            NormalizedRecord(
                record_id=f"fred:{series_id}:{item.get('date', '')}",
                source_id="fred",
                collection="fred_macro",
                record_type="economic_observation",
                source_name="Federal Reserve Bank of St. Louis FRED",
                source_url=f"https://fred.stlouisfed.org/series/{series_id}",
                retrieved_at=retrieved,
                observed_at=item.get("date"),
                data={"series_id": series_id, "value": None if item.get("value") == "." else item.get("value"), "realtime_start": item.get("realtime_start"), "realtime_end": item.get("realtime_end")},
                license_status="fred_api_terms_review_required",
                metadata={"series_id": series_id},
            )
            for item in body.get("observations", [])
        ]


class USASpendingClient:
    """Small client for public USAspending award search; no API key is required."""

    def __init__(self, *, session: requests.Session | None = None, timeout: float = 30) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.session = session or requests.Session()
        self.timeout = timeout

    def search_awards(
        self,
        *,
        start_date: date,
        end_date: date,
        page: int = 1,
        limit: int = 100,
    ) -> list[NormalizedRecord]:
        if start_date > end_date:
            raise ValueError("start_date must be on or before end_date")
        if page < 1 or not 1 <= limit <= 100:
            raise ValueError("page must be positive and limit must be between 1 and 100")
        fields = ["Award ID", "Recipient Name", "Award Amount", "Start Date", "End Date", "Awarding Agency"]
        body = {
            "filters": {
                "time_period": [{"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}],
                "award_type_codes": ["A", "B", "C", "D"],
            },
            "fields": fields,
            "page": page,
            "limit": limit,
            "sort": "Award Amount",
            "order": "desc",
        }
        response = self.session.post(USA_SPENDING_AWARDS_URL, json=body, timeout=self.timeout)
        response.raise_for_status()
        results = response.json().get("results", [])
        retrieved = _retrieved_at()
        records: list[NormalizedRecord] = []
        for item in results:
            award_id = str(item.get("Award ID") or item.get("generated_internal_id") or "")
            if not award_id:
                continue
            records.append(NormalizedRecord(
                record_id=f"usaspending:{award_id}",
                source_id="usaspending",
                collection="usaspending_awards",
                record_type="federal_award",
                source_name="USAspending.gov",
                source_url=f"https://www.usaspending.gov/award/{award_id}",
                retrieved_at=retrieved,
                observed_at=item.get("Start Date"),
                data=item,
                entity_name=str(item.get("Recipient Name") or "") or None,
                license_status="public_api_terms_review_required",
                metadata={"award_id": award_id},
            ))
        return records
