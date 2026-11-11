from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class ScreenerRule:
    name: str
    field: str
    min_value: float | None = None
    max_value: float | None = None


def run_screening(rows: list[dict[str, Any]], rules: list[ScreenerRule]) -> list[dict[str, Any]]:
    filtered = rows
    for rule in rules:
        filtered = [
            row for row in filtered
            if (
                (rule.min_value is None or float(row.get(rule.field, 0)) >= rule.min_value)
                and (rule.max_value is None or float(row.get(rule.field, 0)) <= rule.max_value)
            )
        ]
    return filtered


def default_quality_screen() -> list[ScreenerRule]:
    return [
        ScreenerRule("Min market cap", "market_cap", min_value=1_000_000_000),
        ScreenerRule("Max P/E", "pe_ratio", max_value=40.0),
        ScreenerRule("Min revenue growth", "revenue_growth", min_value=0.05),
    ]


def build_screener_table() -> pd.DataFrame:
    records = [
        {"symbol": "AAPL", "market_cap": 2950000000000, "pe_ratio": 30.4, "revenue_growth": 0.08, "sector": "Technology"},
        {"symbol": "MSFT", "market_cap": 3200000000000, "pe_ratio": 34.1, "revenue_growth": 0.12, "sector": "Technology"},
        {"symbol": "NVDA", "market_cap": 2800000000000, "pe_ratio": 53.6, "revenue_growth": 0.56, "sector": "Technology"},
        {"symbol": "AMZN", "market_cap": 2100000000000, "pe_ratio": 37.4, "revenue_growth": 0.11, "sector": "Consumer Discretionary"},
    ]
    return pd.DataFrame(records)
