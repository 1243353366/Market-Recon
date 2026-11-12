# Changelog

All notable changes to Market Recon are documented in this file.

## [Unreleased]

### Fixed
- **Pytest Discovery & Packaging**: Added `[tool.pytest.ini_options]` with `pythonpath = ["."]` to `pyproject.toml`, resolving module import errors when running `pytest` in clean environments.
- **Go Ingest Gateway**: Enforced JSON object structure on `data` and `metadata` fields, rejecting primitive values and arrays with HTTP 400 before persistence.
- **Rust Signal Engine**: Added finite checks for `metric_value` and bounds checks `[0.0, 1.0]` for `confidence`, eliminating downstream JSON serialization panics caused by NaN or Infinity. Added window day upper bound guard.
- **Normalized Records (Python)**: Enforced strict dictionary type validation on `data` and `metadata` in `NormalizedRecord.__post_init__`.
- **SEC Filing Version Store (SQL)**: Added missing `idx_filing_versions_ticker` index on `filing_versions(ticker, form, filing_date DESC)`.
- **Evidence API (FastAPI)**: Hardened `_record` row parser to always guarantee dictionary returns for `data` and `metadata` even if corrupted values exist in the database.
- **Evidence UI (TypeScript/React)**: Added optional chaining on `selected.data?.license_status` and default `{}` fallbacks to prevent runtime `TypeError` crashes if record payloads contain nullish values.
- **Go Ingest Gateway Directory Creation**: Fixed 500 error on nested directory targets by ensuring `os.MkdirAll` is invoked before opening the JSONL store in `ingest()`.
- **SEC Filing Version Store Tiebreaking**: Added deterministic retrieval-timestamp ordering to prevent URL hash order inversion when filings share a filing date, and added support for amendment pairing (`10-K/A`, `10-Q/A`).
- **Price Adapters**: Added validation preventing inverted date ranges (`start_date > end_date`) in `YahooFinanceAdapter` and `StooqAdapter`.
- **FRED Data Quality**: Mapped FRED missing observation sentinel `"."` to `None`.
- **Stock Screener**: Fixed `TypeError` in `run_screening` when metric fields are `None`, and prevented missing metrics from passing filter rules.
- **Technical Analysis**: Updated `calculate_atr` to Wilder exponential smoothing and prevented metric fabrication when High/Low prices are absent.
- **Investing Coach**: Prioritized risk category matching over incidental account mentions.
- **Repository Structure**: Removed 16 empty placeholder directories containing only stub README files.

### Added
- **Multi-language Test Coverage**:
  - **Go**: Added tests for JSON object validation on data/metadata, trailing record rejection, empty required fields, HTTP 405 Method Not Allowed enforcement, and concurrent append safety (8 tests passing).
  - **Rust**: Added tests for finite metric values, confidence bounds, window bounds, HTTPS citation requirements, identifier emptiness guards, signal direction validation, multi-entity isolation, and deterministic ordering (11 tests passing).
  - **TypeScript**: Added unit test suite in `web/src/schema.test.ts` verifying license status fallback resolution, null safety on data/metadata, API search parameter encoding, and pagination calculation (5 tests passing).
  - **SQL**: Added `tests/test_sql_store.py` covering SQLite upsert idempotency, index creation, read-only mode enforcement, same-day filing tiebreaking, amendment pairing, and ticker index presence (67 Python tests passing).
