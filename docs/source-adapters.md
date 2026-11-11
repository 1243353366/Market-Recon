# Source Catalog and API Adapter Plan

Market Recon uses a common record model for every source and explicitly separates original government disclosures from third-party aggregations.

## Canonical record schema

`market_recon.sources.schema.NormalizedRecord` fields:

- `record_id`: stable provider-qualified identifier
- `source_id`, `collection`, `record_type`: source and data-domain classification
- `source_name`, `source_url`: provenance/citation
- `retrieved_at`: UTC ingestion time
- `observed_at`, `published_at`: event/period date and publication date (when known)
- `entity_id`, `entity_name`, `ticker`, `cik`: resolved identity fields (optional)
- `data`: raw provider fields; no implicit lossy conversions
- `license_status`: explicit rights/access review marker
- `metadata`: transformation and source-specific notes

## Collection map

| Source | Collection(s) | Typical records | Status |
|---|---|---|---|
| SEC EDGAR | `sec_filings`, `sec_insider`, `sec_institutional_holdings`, `sec_resale_notices` | 10-K/Q, 8-K, S-1, DEF 14A, 13D/G, Forms 3/4/5, 13F-HR, Form 144 | limited adapter; filing text is not yet a full structured parser |
| FRED | `fred_macro` | time series observations | API adapter; key required |
| USAspending | `usaspending_awards` | contract/grant awards | API adapter; public API |
| Quiver | `quiver_congressional_trades`, `quiver_lobbying`, `quiver_contracts`, `quiver_patents`, `quiver_holdings` | provider-specific alternative datasets | configurable adapter; endpoint/auth/terms must be verified |

Definitions are listed in `market_recon/sources/collections.py`. Collections represent logical domains, not necessarily separate vector DB collections. Numeric/time-series data should stay in structured storage; only text documents/chunks belong in vector search.

## Folder structure

See `market_recon/sources/README.md` for exact paths, example construction, and adapter contract.

## Important interpretation controls

- 13F-HR data are delayed quarter-end holdings disclosures, not real-time positions, insider trades, or proof of conviction.
- Form 144 is notice of a proposed sale and not proof a sale took place.
- A government award value is not equivalent to recognized company revenue.
- FRED observations can be revised; preserve series identity, units, frequency, and vintages when applicable.
- Quiver is a third-party aggregation. Preserve its lineage and verify material claims against primary sources.
- Free tier, API access, rate limits, license, redistribution, and caching permissions can change. Check each provider's current documentation and terms.

## Configuration

Use environment variables for `SEC_USER_AGENT`, `FRED_API_KEY`, and `QUIVER_API_KEY`. Never commit credentials. USAspending public endpoints do not require a key. See `docs/data-sources.md` for client details.
