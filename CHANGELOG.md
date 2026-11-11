# Changelog

All notable changes to Market Recon are documented in this file.

## [Unreleased]

### Fixed
- **Go Ingest Gateway**: Fixed 500 error on nested directory targets by ensuring `os.MkdirAll` is invoked before opening the JSONL store in `ingest()`.
- **TypeScript Evidence UI**: Added missing `vite-env.d.ts` reference and fixed `ReactNode` type collision on `unknown` license status values in `App.tsx`.
- **SEC Filing Version Store (SQL)**: Added deterministic retrieval-timestamp ordering to prevent URL hash order inversion when filings share a filing date, and added support for amendment pairing (`10-K/A`, `10-Q/A`).
- **Evidence API (SQL)**: Allowed dynamic database path resolution from `MARKET_RECON_DB` at request time.
- **Price Adapters**: Added validation preventing inverted date ranges (`start_date > end_date`) in `YahooFinanceAdapter` and `StooqAdapter`.
- **Normalized Records**: Unified `NormalizedRecord` schema across `data_sources_api.py` and canonical `sources.schema`, removing lossy conversion layers.
- **FRED Data Quality**: Mapped FRED missing observation sentinel `"."` to `None`.
- **Stock Screener**: Fixed `TypeError` in `run_screening` when metric fields are `None`, and prevented missing metrics from passing filter rules.
- **Technical Analysis**: Updated `calculate_atr` to Wilder exponential smoothing and prevented metric fabrication when High/Low prices are absent.
- **Investing Coach**: Prioritized risk category matching over incidental account mentions.
- **Repository Structure**: Removed 16 empty placeholder directories containing only stub README files.

### Added
- **Multi-language Test Coverage**:
  - **Go**: Added tests for trailing record rejection, empty required fields, HTTP 405 Method Not Allowed enforcement, and concurrent append safety.
  - **Rust**: Added tests for HTTPS citation requirements, identifier emptiness guards, signal direction validation, window bounds inclusivity, multi-entity isolation, and deterministic ordering.
  - **TypeScript**: Added unit test suite in `web/src/schema.test.ts` verifying license status fallback resolution, API search parameter encoding, and pagination calculation.
  - **SQL**: Added `tests/test_sql_store.py` covering SQLite upsert idempotency, index creation, read-only mode enforcement, same-day filing tiebreaking, and amendment pairing.
