from __future__ import annotations

from .models import PublicSignal

# Source registry describes potential evidence providers and implementation/access status.
# Listing a source does not imply a collector, permission to scrape, or permission to reuse.
SOURCE_CATALOG = {
    "sec_edgar": {"name": "SEC EDGAR", "url": "https://www.sec.gov/edgar/search/", "signals": ["insider_purchase", "institutional_holding_change", "management_demand_commentary", "board_change"], "status": "limited_adapter"},
    "usaspending": {"name": "USAspending.gov", "url": "https://www.usaspending.gov/", "signals": ["government_award"], "status": "adapter_available"},
    "sam_gov": {"name": "SAM.gov", "url": "https://sam.gov/", "signals": ["government_award"], "status": "planned_adapter"},
    "github": {"name": "GitHub public API", "url": "https://docs.github.com/en/rest", "signals": ["open_source_activity"], "status": "planned_adapter; project attribution required"},
    "pypi": {"name": "PyPI", "url": "https://pypi.org/help/", "signals": ["package_activity"], "status": "planned_adapter; download counts are not unique users"},
    "npm": {"name": "npm registry", "url": "https://registry.npmjs.org/", "signals": ["package_activity"], "status": "planned_adapter; download counts are not unique users"},
    "osv": {"name": "OSV vulnerability database", "url": "https://osv.dev/", "signals": ["cve_disclosure"], "status": "planned_adapter"},
    "conference_materials": {"name": "Public technical conference materials", "url": "https://www.usenix.org/", "signals": ["technical_presentation"], "status": "source-specific terms and attribution review"},
    "ieee": {"name": "IEEE standards and publications", "url": "https://standards.ieee.org/", "signals": ["standards_publication"], "status": "public metadata only; content licensing review required"},
    "w3c": {"name": "W3C", "url": "https://www.w3.org/standards/", "signals": ["standards_publication"], "status": "planned_adapter"},
    "ietf": {"name": "IETF Datatracker", "url": "https://datatracker.ietf.org/", "signals": ["standards_publication"], "status": "planned_adapter"},
    "arxiv": {"name": "arXiv", "url": "https://info.arxiv.org/help/api/", "signals": ["academic_research"], "status": "planned_adapter; affiliation matching is uncertain"},
    "ssrn": {"name": "SSRN", "url": "https://www.ssrn.com/", "signals": ["academic_research"], "status": "metadata/access terms review required"},
    "university_licensing": {"name": "University technology transfer announcements", "url": "https://autm.net/", "signals": ["university_licensing"], "status": "planned adapter"},
    "local_permits": {"name": "Local building/environmental permit portals", "url": "https://www.usa.gov/local-governments", "signals": ["permit_activity", "local_agenda"], "status": "jurisdiction-specific adapter; source availability varies"},
    "regulations_gov": {"name": "Regulations.gov", "url": "https://www.regulations.gov/", "signals": ["regulatory_comment", "agency_docket"], "status": "planned adapter; distinguish proposed from final rules"},
    "courtlistener": {"name": "CourtListener / RECAP", "url": "https://www.courtlistener.com/", "signals": ["litigation_event"], "status": "public records coverage varies; verify source record"},
}


def validate_signal_source(signal: PublicSignal) -> None:
    """Fail closed if provenance is missing; collectors must still validate source rights and accuracy."""
    if not signal.source_name.strip() or not signal.source_url.strip():
        raise ValueError("Public signals require source name and URL")
