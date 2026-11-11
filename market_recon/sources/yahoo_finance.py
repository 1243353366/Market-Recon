from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from urllib.parse import quote

import pandas as pd
import requests

from .schema import NormalizedRecord, utc_now_iso


class YahooFinanceAdapter:
    """Yahoo Finance history via yfinance (unofficial wrapper; terms/access must be reviewed)."""

    source_id = "yahoo_finance"

    def __init__(self, timeout: float = 30) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.timeout = timeout

    def fetch(
        self,
        *,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        start_date: date | None = None,
        end_date: date | None = None,
        **_: Any,
    ) -> list[NormalizedRecord]:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise RuntimeError("Install yfinance to use the Yahoo Finance adapter") from exc
        if not symbol.strip():
            raise ValueError("symbol is required")
        ticker = yf.Ticker(symbol.strip().upper())
        frame = ticker.history(period=period if start_date is None else None, interval=interval,
                               start=start_date.isoformat() if start_date else None,
                               end=end_date.isoformat() if end_date else None, timeout=self.timeout,
                               auto_adjust=False, actions=True)
        if frame.empty:
            return []
        retrieved = utc_now_iso()
        result: list[NormalizedRecord] = []
        for timestamp, row in frame.iterrows():
            observed = timestamp.date().isoformat() if hasattr(timestamp, "date") else str(timestamp)
            payload = {str(key): _native(value) for key, value in row.items()}
            result.append(NormalizedRecord(
                record_id=f"yahoo:{symbol.upper()}:{observed}:{interval}", source_id=self.source_id,
                collection="market_prices", record_type="ohlcv", source_name="Yahoo Finance via yfinance",
                source_url=f"https://finance.yahoo.com/quote/{quote(symbol.upper())}/history/",
                retrieved_at=retrieved, observed_at=observed, ticker=symbol.upper(), data=payload,
                license_status="provider_terms_review_required", metadata={"interval": interval, "period": period, "adjusted": False},
            ))
        return result


def _native(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value
