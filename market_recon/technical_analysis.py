from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

try:
    import yfinance as yf
except ImportError:  # pragma: no cover
    yf = None


@dataclass(frozen=True)
class DataSource:
    name: str
    url: str
    kind: str
    notes: str


PUBLIC_SOURCES = [
    DataSource(
        name="Yahoo Finance",
        url="https://finance.yahoo.com",
        kind="price_history",
        notes="Daily market data and historical quotes.",
    ),
    DataSource(
        name="SEC EDGAR",
        url="https://www.sec.gov/edgar",
        kind="filings",
        notes="Public company filings and disclosures.",
    ),
    DataSource(
        name="FRED",
        url="https://fred.stlouisfed.org",
        kind="macro",
        notes="Macroeconomic indicators and policy datasets.",
    ),
]


def fetch_price_history(symbol: str, period: str = "180d", interval: str = "1d") -> pd.DataFrame:
    """Fetch daily price history for a ticker. Falls back to a safe sample when the library is unavailable."""
    if yf is not None:
        data = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
        if not data.empty:
            return data.reset_index().rename(columns={"index": "date"})

    sample_rows = [
        {"date": "2025-01-02", "Open": 100.0, "High": 102.0, "Low": 99.0, "Close": 101.5, "Adj Close": 101.5, "Volume": 1200000},
        {"date": "2025-01-03", "Open": 101.5, "High": 104.0, "Low": 100.5, "Close": 103.2, "Adj Close": 103.2, "Volume": 1400000},
        {"date": "2025-01-06", "Open": 103.2, "High": 105.0, "Low": 102.1, "Close": 104.8, "Adj Close": 104.8, "Volume": 1600000},
        {"date": "2025-01-07", "Open": 104.8, "High": 106.1, "Low": 103.9, "Close": 105.6, "Adj Close": 105.6, "Volume": 1800000},
        {"date": "2025-01-08", "Open": 105.6, "High": 106.8, "Low": 104.9, "Close": 106.3, "Adj Close": 106.3, "Volume": 1700000},
    ]
    return pd.DataFrame(sample_rows)


def fetch_company_snapshot(symbol: str) -> dict[str, Any]:
    """Return a minimal structured company snapshot record."""
    company_map = {
        "AAPL": {
            "symbol": "AAPL",
            "company": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "market_cap": 2950000000000,
        },
        "MSFT": {
            "symbol": "MSFT",
            "company": "Microsoft Corporation",
            "sector": "Technology",
            "industry": "Software Infrastructure",
            "market_cap": 3200000000000,
        },
        "NVDA": {
            "symbol": "NVDA",
            "company": "NVIDIA Corporation",
            "sector": "Technology",
            "industry": "Semiconductors",
            "market_cap": 2800000000000,
        },
    }

    record = company_map.get(symbol.upper(), {
        "symbol": symbol.upper(),
        "company": f"{symbol.upper()} Company",
        "sector": "Unknown",
        "industry": "Unknown",
        "market_cap": 0,
    })
    return record


def list_example_watchlist() -> list[dict[str, Any]]:
    return [
        {"symbol": "AAPL", "company": "Apple Inc.", "sector": "Technology", "market_cap": 2950000000000},
        {"symbol": "MSFT", "company": "Microsoft Corporation", "sector": "Technology", "market_cap": 3200000000000},
        {"symbol": "NVDA", "company": "NVIDIA Corporation", "sector": "Technology", "market_cap": 2800000000000},
        {"symbol": "AMZN", "company": "Amazon.com Inc.", "sector": "Consumer Discretionary", "market_cap": 2100000000000},
    ]
