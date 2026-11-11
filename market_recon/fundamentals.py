from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .config import DEFAULT_TICKERS


def get_sample_fundamentals() -> dict[str, dict[str, Any]]:
    return {
        "AAPL": {
            "symbol": "AAPL",
            "company": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "market_cap": 2950000000000,
            "pe_ratio": 30.4,
            "ev_ebitda": 25.7,
            "revenue_growth": 0.08,
            "net_margin": 0.25,
            "roa": 0.16,
            "roe": 0.18,
            "debt_to_equity": 1.7,
            "free_cash_flow": 110000000000,
        },
        "MSFT": {
            "symbol": "MSFT",
            "company": "Microsoft Corporation",
            "sector": "Technology",
            "industry": "Software Infrastructure",
            "market_cap": 3200000000000,
            "pe_ratio": 34.1,
            "ev_ebitda": 28.6,
            "revenue_growth": 0.12,
            "net_margin": 0.35,
            "roa": 0.21,
            "roe": 0.32,
            "debt_to_equity": 0.4,
            "free_cash_flow": 95000000000,
        },
        "NVDA": {
            "symbol": "NVDA",
            "company": "NVIDIA Corporation",
            "sector": "Technology",
            "industry": "Semiconductors",
            "market_cap": 2800000000000,
            "pe_ratio": 53.6,
            "ev_ebitda": 42.8,
            "revenue_growth": 0.56,
            "net_margin": 0.28,
            "roa": 0.19,
            "roe": 0.37,
            "debt_to_equity": 0.2,
            "free_cash_flow": 65000000000,
        },
        "AMZN": {
            "symbol": "AMZN",
            "company": "Amazon.com Inc.",
            "sector": "Consumer Discretionary",
            "industry": "Internet Retail",
            "market_cap": 2100000000000,
            "pe_ratio": 37.4,
            "ev_ebitda": 21.2,
            "revenue_growth": 0.11,
            "net_margin": 0.08,
            "roa": 0.07,
            "roe": 0.16,
            "debt_to_equity": 0.5,
            "free_cash_flow": 54000000000,
        },
    }


def load_fundamentals(symbol: str | None = None) -> dict[str, Any] | pd.DataFrame:
    data = get_sample_fundamentals()
    if symbol is not None:
        return data.get(symbol.upper(), {})
    return pd.DataFrame.from_records(list(data.values()))


def sample_market_snapshot() -> dict[str, Any]:
    return {
        "index": "SPY",
        "market_status": "Open",
        "vix": 13.2,
        "treasury_yield_10y": 4.15,
        "risk_environment": "Moderate",
    }
