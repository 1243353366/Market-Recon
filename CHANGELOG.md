# Changelog

All notable changes to Market Recon are documented in this file.

## [Unreleased]

### Fixed
- **Signal Intelligence Robustness & Deduplication**:
  - Fixed `AttributeError` in `PublicSignal.__post_init__` by enforcing strict `isinstance(val, str)` type checks before calling string methods, cleanly raising `ValueError` on malformed inputs.
  - Added `(entity_id, signal_id)` deduplication in `find_cross_signal_divergences` to prevent duplicate evidence from fabricating false mixed-signal clusters.
  - Selected canonical entity name from the most recent signal observation rather than stale oldest records.
  - Qualified divergence results with `distinct_source_count` and `divergence_caveat` when evidence is uncorroborated (single source) or compares disparate baselines.
- **CI TypeScript Test Compatibility (FAIL-001)**: Fixed CI failure where Node 20 LTS crashed after 11s due to unsupported `--experimental-strip-types`. Configured `web/tsconfig.test.json` compiling tests to `.test-dist/` and running native `node --test`, certified across both Node 20 and Node 22 matrix jobs in GitHub Actions.
- **Engineering Failure Changelog**: Added `FAILURE_CHANGELOG.md` as an operational defensive playbook documenting observed failure modes, root causes, and engineering invariants to prevent regressions across cross-language pipelines.
- **Filing Classifier False Positives (Backlog #1)**: Enforced strict requirement that changed lines must contain category-specific terminology. Section hints (e.g. Item 1, Item 1A, Item 7) now act strictly as scoping context and confidence modifiers rather than independent triggers, preventing unrelated business or accounting prose from being misclassified as supply chain, litigation, or executive changes.
- **Finding Provenance & Audit Metadata**: Enhanced `FilingFinding` with `matched_phrase`, `matched_section_hint`, `match_reason`, and explicit `analyst_status` ("unreviewed" by default, supporting "confirmed", "false_positive", and "uncertain").
- **Go Ingest Gateway**: Enforced JSON object structure on `data` and `metadata` fields, rejecting primitive values and arrays with HTTP 400 before persistence. Fixed 500 error on nested directory targets by ensuring `os.MkdirAll` is invoked before opening the JSONL store in `ingest()`.
- **Rust Signal Engine**: Added finite checks for `metric_value` and bounds checks `[0.0, 1.0]` for `confidence`, eliminating downstream JSON serialization panics caused by NaN or Infinity. Added window day upper bound guard.
- **Normalized Records & Storage**: Added `run_id` to `NormalizedRecord` schema, CSV export, and SQLite storage tables without breaking existing record ingest.
- **Pytest Discovery & Packaging**: Added `[tool.pytest.ini_options]` with `pythonpath = ["."]` to `pyproject.toml`, resolving module import errors when running `pytest` in clean environments.
- **SEC Filing Version Store (SQL)**: Added missing `idx_filing_versions_ticker` index on `filing_versions(ticker, form, filing_date DESC)`, retrieval-timestamp tiebreaking for same-day filings, and support for amendment pairing (`10-K/A`, `10-Q/A`).
- **Price Adapters**: Added validation preventing inverted date ranges (`start_date > end_date`) in `YahooFinanceAdapter` and `StooqAdapter`.
- **FRED Data Quality**: Mapped FRED missing observation sentinel `"."` to `None`.
- **Stock Screener**: Fixed `TypeError` in `run_screening` when metric fields are `None`, and prevented missing metrics from passing filter rules.
- **Technical Analysis**: Updated `calculate_atr` to Wilder exponential smoothing and prevented metric fabrication when High/Low prices are absent.
- **Investing Coach**: Prioritized risk category matching over incidental account mentions.

### Added
- **Filing Change Quality Benchmark (Backlog #6)**: Created `benchmark/filing_change_corpus.json` (v1.0.0) with synthetic human-reviewed positive cases and hard negatives, paired with `benchmark/filing_eval.py` and `tests/test_filing_eval.py` to evaluate and track precision, recall, and F1 by category.
- **Entity Resolution Engine (Backlog #8)**: Added `market_recon/sources/entity_resolution.py` with deterministic priority for authoritative identifiers (SEC CIK, exchange ticker, federal recipient UEI/DUNS) and legal suffix normalization. Enforces ambiguity defense by leaving generic/common entity names unresolved rather than forcing false cross-source links.
- **Ingestion Run Audit Ledger (Backlog #10)**: Added `market_recon/sources/ledger.py` with SQLite-backed `IngestionLedger` recording run ID, source, requested range, retrieval timestamp, records fetched/skipped, errors count, parser version, and license status.
- **Cross-Language Contracts & Verification (Backlog #19)**:
  - Published canonical schemas `contracts/record_contract.json` and `contracts/signal_contract.json`.
  - Added unit test verification against shared contracts in Python (`tests/test_contracts.py`), Go (`go/ingest-gateway/main_test.go`), Rust (`rust/signal-engine/src/main.rs`), and TypeScript (`web/src/schema.test.ts`).
  - Replaced single-language workflow with multi-job `.github/workflows/ci.yml` running independent test jobs for Python, Go (1.22), Rust (stable), and TypeScript/Node (20).
