from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "examples"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    watchlist = [
        {"symbol": "AAPL", "company": "Apple Inc.", "sector": "Technology"},
        {"symbol": "MSFT", "company": "Microsoft Corporation", "sector": "Technology"},
        {"symbol": "NVDA", "company": "NVIDIA Corporation", "sector": "Technology"},
        {"symbol": "AMZN", "company": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
    ]
    fundamentals = {
        "AAPL": {"symbol": "AAPL", "pe_ratio": 30.4, "market_cap": 2950000000000, "revenue_growth": 0.08},
        "MSFT": {"symbol": "MSFT", "pe_ratio": 34.1, "market_cap": 3200000000000, "revenue_growth": 0.12},
        "NVDA": {"symbol": "NVDA", "pe_ratio": 53.6, "market_cap": 2800000000000, "revenue_growth": 0.56},
        "AMZN": {"symbol": "AMZN", "pe_ratio": 37.4, "market_cap": 2100000000000, "revenue_growth": 0.11},
    }
    news = [
        {"title": "Public market sentiment remains positive for AI-linked hardware sellers", "source": "Public coverage", "category": "Technology", "sentiment": "Positive"},
        {"title": "Treasury yields remain an active macro headwind for equity valuation", "source": "Public coverage", "category": "Macro", "sentiment": "Cautious"},
    ]

    with (DATA_DIR / "sample_watchlist.json").open("w", encoding="utf-8") as file:
        json.dump(watchlist, file, indent=2)

    with (DATA_DIR / "sample_fundamentals.json").open("w", encoding="utf-8") as file:
        json.dump(fundamentals, file, indent=2)

    with (DATA_DIR / "sample_news.json").open("w", encoding="utf-8") as file:
        json.dump(news, file, indent=2)

    print(f"Seeded demo data in {DATA_DIR}")


if __name__ == "__main__":
    main()
