"""Seed a small set of labelled demo records for the read-only evidence UI.

These records are synthetic examples, not collected source data: they exist so the
review UI and API can be exercised without provider credentials. Run with::

    python scripts/seed_demo_data.py data/market.db
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from market_recon.sources.schema import NormalizedRecord, utc_now_iso
from market_recon.sources.storage import write_records

DEMO_RECORDS = (
    NormalizedRecord(
        record_id="demo:fred_macro:GDPC1:2025-01-01",
        source_id="fred",
        collection="fred_macro",
        record_type="economic_observation",
        source_name="FRED (demo fixture)",
        source_url="https://fred.stlouisfed.org/series/GDPC1",
        retrieved_at=utc_now_iso(),
        observed_at="2025-01-01",
        ticker=None,
        license_status="demo_fixture",
        data={"series_id": "GDPC1", "date": "2025-01-01", "value": 23000.0, "units": "billions_chained_2017_usd"},
        metadata={"synthetic": True, "note": "Example row for UI review only"},
    ),
    NormalizedRecord(
        record_id="demo:sec_filings:0000000000:demo-10k",
        source_id="sec_edgar",
        collection="sec_filings",
        record_type="sec_filing",
        source_name="SEC EDGAR (demo fixture)",
        source_url="https://www.sec.gov/Archives/edgar/data/0000000000/000000000000000000/demo-10k.htm",
        retrieved_at=utc_now_iso(),
        published_at="2026-02-01",
        entity_id="CIK0000000000",
        ticker="DEMO",
        cik="0000000000",
        license_status="public_source_terms_review_required",
        data={"title": "DEMO 10-K (example)", "text": "Item 1A. Risk Factors. Example supplier concentration risk."},
        metadata={"synthetic": True, "accession_number": "0000-00-000000"},
    ),
)


def main() -> int:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "data/market.db")
    count = write_records(DEMO_RECORDS, target, "sqlite")
    print(f"Seeded {count} demo records into {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
