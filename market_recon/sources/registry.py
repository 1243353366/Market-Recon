from __future__ import annotations

from market_recon.sources.schema import NormalizedRecord, SourceAdapter
from market_recon.sources.collections import COLLECTIONS

SOURCE_CATALOG = {
    "sec_edgar": {"status": "limited_adapter", "docs": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces", "auth": "SEC_USER_AGENT identification", "collections": ["sec_filings", "sec_insider", "sec_institutional_holdings", "sec_resale_notices"]},
    "fred": {"status": "adapter", "docs": "https://fred.stlouisfed.org/docs/api/fred/", "auth": "FRED_API_KEY", "collections": ["fred_macro"]},
    "usaspending": {"status": "adapter", "docs": "https://api.usaspending.gov/", "auth": "none", "collections": ["usaspending_awards"]},
    "quiver_quant": {"status": "configurable_adapter; verify endpoint and plan", "docs": "https://api.quiverquant.com/docs", "auth": "provider key and configured header", "collections": ["quiver_congressional_trades", "quiver_lobbying", "quiver_contracts", "quiver_patents", "quiver_holdings"]},
}

__all__ = ["NormalizedRecord", "SourceAdapter", "COLLECTIONS", "SOURCE_CATALOG"]
