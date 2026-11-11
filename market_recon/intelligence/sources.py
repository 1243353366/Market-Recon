from __future__ import annotations

from .models import PublicSignal

# Source registry is descriptive only: entries identify candidate public endpoints,
# not implemented collectors or permission to scrape/reuse third-party content.
SOURCE_CATALOG = {
    "sec_edgar": {"name": "SEC EDGAR", "url": "https://www.sec.gov/edgar/search/", "signals": ["insider_purchase", "institutional_holding_change", "management_demand_commentary", "regulatory_action"], "status": "collector_exists_for_basic_filings"},
    "usaspending": {"name": "USAspending.gov", "url": "https://www.usaspending.gov/", "signals": ["government_award"], "status": "planned_adapter"},
    "sam_gov": {"name": "SAM.gov", "url": "https://sam.gov/", "signals": ["government_award"], "status": "planned_adapter"},
    "google_patents": {"name": "Google Patents", "url": "https://patents.google.com/", "signals": ["patent_activity"], "status": "planned_adapter"},
    "uspto": {"name": "USPTO", "url": "https://www.uspto.gov/patents", "signals": ["patent_activity"], "status": "planned_adapter"},
    "fred": {"name": "FRED", "url": "https://fred.stlouisfed.org/", "signals": ["management_demand_commentary"], "status": "planned_adapter"},
    "github": {"name": "GitHub", "url": "https://github.com/", "signals": ["open_source_activity"], "status": "planned_adapter"},
    "company_careers": {"name": "Company career pages", "url": "https://www.sec.gov/", "signals": ["hiring_activity"], "status": "planned_adapter"},
    "port_authorities": {"name": "Port authority open data", "url": "https://www.portoflosangeles.org/business/statistics", "signals": ["import_activity", "export_activity", "shipping_delay"], "status": "source_specific_review_required"},
    "marine_traffic": {"name": "MarineTraffic", "url": "https://www.marinetraffic.com/", "signals": ["shipping_delay"], "status": "terms_or_license_review_required"},
    "import_yeti": {"name": "ImportYeti", "url": "https://www.importyeti.com/", "signals": ["import_activity"], "status": "terms_or_license_review_required"},
    "freightwaves": {"name": "FreightWaves", "url": "https://www.freightwaves.com/", "signals": ["shipping_delay"], "status": "terms_or_license_review_required"},
}


def validate_signal_source(signal: PublicSignal) -> None:
    """Fail closed if provenance is missing; collectors must still validate source rights and accuracy."""
    if not signal.source_name.strip() or not signal.source_url.strip():
        raise ValueError("Public signals require source name and URL")
