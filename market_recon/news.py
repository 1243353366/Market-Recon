from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_WATCHLIST = [
    {"symbol": "AAPL", "company": "Apple Inc.", "sector": "Technology"},
    {"symbol": "MSFT", "company": "Microsoft Corporation", "sector": "Technology"},
    {"symbol": "NVDA", "company": "NVIDIA Corporation", "sector": "Technology"},
    {"symbol": "AMZN", "company": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
    {"symbol": "BRK-B", "company": "Berkshire Hathaway", "sector": "Financial Services"},
]


def load_watchlist(path: str | Path | None = None) -> list[dict[str, Any]]:
    if path is None:
        return DEFAULT_WATCHLIST

    target = Path(path)
    if not target.exists():
        return DEFAULT_WATCHLIST

    with target.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else DEFAULT_WATCHLIST


def save_watchlist(items: list[dict[str, Any]], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as fh:
        json.dump(items, fh, indent=2)


def add_symbol_to_watchlist(symbol: str, company: str, sector: str, path: str | Path | None = None) -> list[dict[str, Any]]:
    items = load_watchlist(path)
    if any(item.get("symbol", "").upper() == symbol.upper() for item in items):
        return items
    items.append({"symbol": symbol.upper(), "company": company, "sector": sector})
    if path is not None:
        save_watchlist(items, path)
    return items
