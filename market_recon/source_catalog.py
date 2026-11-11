from __future__ import annotations

SOURCE_CATALOG = {
    "sec_edgar": {
        "name": "SEC EDGAR", "docs": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
        "auth": "none for public data; identify requests with SEC_USER_AGENT", "status": "basic filing collector implemented",
        "notes": "Public submissions and filing archives; comply with SEC fair-access guidance.",
    },
    "fred": {
        "name": "FRED", "docs": "https://fred.stlouisfed.org/docs/api/fred/",
        "auth": "FRED_API_KEY", "status": "series observations client implemented",
        "notes": "API registration required; review each series' units, frequency, revisions, and release timing.",
    },
    "usaspending": {
        "name": "USAspending.gov", "docs": "https://api.usaspending.gov/",
        "auth": "none", "status": "award search client implemented",
        "notes": "Awards are not equivalent to revenue; amounts, dates, recipients, and modifications require interpretation.",
    },
    "alpha_vantage": {
        "name": "Alpha Vantage", "docs": "https://www.alphavantage.co/documentation/",
        "auth": "ALPHA_VANTAGE_API_KEY", "status": "planned adapter",
        "notes": "Free-tier coverage and request limits may change; verify current API access and licensing.",
    },
    "financial_modeling_prep": {
        "name": "Financial Modeling Prep", "docs": "https://site.financialmodelingprep.com/developer/docs",
        "auth": "FMP_API_KEY", "status": "planned adapter",
        "notes": "Plans, data coverage, permitted use, and limits vary; verify current terms before use.",
    },
    "import_yeti": {
        "name": "ImportYeti", "docs": "https://docs.importyeti.com/",
        "auth": "verify provider access", "status": "not integrated; access and license review required",
        "notes": "Do not assume a public API or unrestricted reuse; use authorized access only.",
    },
    "quiver_quant": {
        "name": "Quiver Quantitative", "docs": "https://api.quiverquant.com/docs",
        "auth": "provider credentials", "status": "not integrated; plan and terms review required",
        "notes": "Third-party datasets are not official government records; retain source attribution and limitations.",
    },
}
