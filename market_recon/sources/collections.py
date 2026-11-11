from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CollectionDefinition:
    collection_id: str
    source_id: str
    description: str
    record_types: tuple[str, ...]
    notes: str


COLLECTIONS = (
    CollectionDefinition("sec_filings", "sec_edgar", "Company reports and material filings.", ("10-K", "10-Q", "8-K", "S-1", "DEF 14A", "SC 13D", "SC 13G"), "Document text plus accession-level provenance."),
    CollectionDefinition("sec_insider", "sec_edgar", "Forms 3, 4, and 5 ownership disclosures.", ("3", "4", "5"), "Use structured filing parsing for transaction analysis; raw filing text is not normalized transaction data."),
    CollectionDefinition("sec_institutional_holdings", "sec_edgar", "13F-HR institutional holdings filings.", ("13F-HR",), "Delayed quarter-end disclosure; not real-time holdings or insider trades."),
    CollectionDefinition("sec_resale_notices", "sec_edgar", "Form 144 notices of proposed sale.", ("144",), "A notice is not proof that a sale occurred."),
    CollectionDefinition("other_sec_filings", "sec_edgar", "SEC filings outside the purpose-built collections.", (), "Catch-all for unclassified forms; do not treat as a curated collection."),
    CollectionDefinition("fred_macro", "fred", "FRED time-series observations.", ("economic_observation",), "Preserve series ID, observation date, units/frequency metadata, and revisions/vintages when available."),
    CollectionDefinition("usaspending_awards", "usaspending", "Federal awards, contracts, grants, and recipient records.", ("federal_award",), "Award amounts do not equal recognized revenue."),
    CollectionDefinition("market_prices", "market_data", "Delayed daily price and volume bars.", ("ohlcv",), "Vendor-delayed bars; not executable quotes or a consolidated tape."),
    CollectionDefinition("quiver_congressional_trades", "quiver_quant", "Third-party congressional-trading records.", ("congressional_trade",), "Endpoint/fields depend on provider plan; verify against primary disclosures."),
    CollectionDefinition("quiver_lobbying", "quiver_quant", "Third-party lobbying records.", ("lobbying_record",), "Third-party aggregation; verify original filings and licensing."),
    CollectionDefinition("quiver_contracts", "quiver_quant", "Third-party government contract records.", ("contract_record",), "Do not merge with official awards without retaining source lineage."),
    CollectionDefinition("quiver_patents", "quiver_quant", "Third-party patent-related records.", ("patent_record",), "Patent applications are not proof of commercial products."),
    CollectionDefinition("quiver_holdings", "quiver_quant", "Third-party institutional holdings records.", ("holding_record",), "Verify reporting dates and underlying SEC filings."),
    CollectionDefinition("alternative_data", "generic", "Adapter output with no purpose-built collection yet.", (), "Uncurated; add a purpose-built collection before relying on it downstream."),
)

COLLECTION_IDS = frozenset(definition.collection_id for definition in COLLECTIONS)
