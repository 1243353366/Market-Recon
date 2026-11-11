from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = ROOT_DIR / "docs"
DEFAULT_TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK-B", "TSLA"]

SOURCE_CATALOG = {
    "yahoo_finance": {
        "name": "Yahoo Finance",
        "kind": "price_history",
        "url": "https://finance.yahoo.com",
        "notes": "Public market data and daily price history.",
    },
    "sec_edgar": {
        "name": "SEC EDGAR",
        "kind": "filings",
        "url": "https://www.sec.gov/edgar",
        "notes": "Public company filings and disclosures.",
    },
    "fred": {
        "name": "FRED",
        "kind": "macro",
        "url": "https://fred.stlouisfed.org",
        "notes": "Macroeconomic and policy data.",
    },
}
