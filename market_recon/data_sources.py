from __future__ import annotations

from typing import Any

import pandas as pd

try:
    import yfinance as yf
except ImportError:  # pragma: no cover - optional runtime fallback
    yf = None


def fetch_price_history(symbol: str, period: str = "180d", interval: str = "1d") -> pd.DataFrame:
    """Fetch prices; raise on unavailable/empty live data instead of silently substituting fake prices."""
    if yf is None:
        raise RuntimeError("yfinance is not installed; install the project dependencies or use an explicit sample dataset")
    frame = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
    if frame.empty:
        raise LookupError(f"No price history returned for {symbol!r}")
    frame = frame.reset_index()
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = [column[0] if isinstance(column, tuple) else column for column in frame.columns]
    date_column = next((name for name in ("Date", "Datetime", "index") if name in frame.columns), None)
    if date_column and date_column != "date":
        frame = frame.rename(columns={date_column: "date"})
    return frame


def fetch_company_snapshot(symbol: str) -> dict[str, Any]:
    """Return clearly labeled example metadata; this is not a live company-data provider."""
    examples = {
        "AAPL": {"company": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
        "MSFT": {"company": "Microsoft Corporation", "sector": "Technology", "industry": "Software Infrastructure"},
        "NVDA": {"company": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
    }
    details = examples.get(symbol.upper(), {"company": f"{symbol.upper()} (unverified)", "sector": "Unknown", "industry": "Unknown"})
    return {"symbol": symbol.upper(), **details, "data_status": "static example; verify with primary sources"}


def list_example_watchlist() -> list[dict[str, Any]]:
    return [
        {"symbol": "AAPL", "company": "Apple Inc.", "sector": "Technology"},
        {"symbol": "MSFT", "company": "Microsoft Corporation", "sector": "Technology"},
        {"symbol": "NVDA", "company": "NVIDIA Corporation", "sector": "Technology"},
        {"symbol": "AMZN", "company": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
    ]
