from __future__ import annotations

from datetime import date
from io import StringIO
from urllib.parse import urlencode

import pandas as pd
import requests

from .schema import NormalizedRecord, utc_now_iso

STOOQ_CSV_URL = "https://stooq.com/q/d/l/"


class StooqAdapter:
    """Daily historical OHLCV from Stooq's CSV endpoint; verify usage terms and coverage."""

    source_id = "stooq"

    def __init__(self, *, session: requests.Session | None = None, timeout: float = 30) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.session = session or requests.Session()
        self.timeout = timeout

    def fetch(self, *, symbol: str, start_date: date | None = None, end_date: date | None = None, **_: object) -> list[NormalizedRecord]:
        if not symbol.strip():
            raise ValueError("symbol is required")
        provider_symbol = symbol.lower() if "." in symbol else f"{symbol.lower()}.us"
        params = {"s": provider_symbol, "i": "d"}
        if start_date:
            params["d1"] = start_date.strftime("%Y%m%d")
        if end_date:
            params["d2"] = end_date.strftime("%Y%m%d")
        response = self.session.get(STOOQ_CSV_URL, params=params, timeout=self.timeout)
        response.raise_for_status()
        frame = pd.read_csv(StringIO(response.text))
        if frame.empty or "Date" not in frame.columns:
            return []
        retrieved = utc_now_iso()
        encoded_query = urlencode(params)
        url = f"{STOOQ_CSV_URL}?{encoded_query}"
        return [NormalizedRecord(
            record_id=f"stooq:{symbol.upper()}:{row['Date']}:1d", source_id=self.source_id,
            collection="market_prices", record_type="ohlcv", source_name="Stooq",
            source_url=url, retrieved_at=retrieved, observed_at=str(row["Date"]), ticker=symbol.upper(),
            data={key: _clean(value) for key, value in row.to_dict().items()},
            license_status="provider_terms_review_required", metadata={"interval": "1d", "provider_symbol": provider_symbol},
        ) for _, row in frame.iterrows()]


def _clean(value: object) -> object:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value
