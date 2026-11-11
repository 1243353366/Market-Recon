# Changelog

## Unreleased

### Fixed

- **FRED missing observations.** Normalize the provider's `"."` no-data sentinel to `None`, so it cannot masquerade as a numeric value.
- **Normalized source records.** FRED and USAspending clients now emit the shared `sources.schema.NormalizedRecord` directly, preserving canonical source, collection, observed-date, license, and metadata fields without adapter translations.
- **Screener handling of incomplete data.** Missing, null, nonnumeric, and NaN rule values no longer crash or accidentally qualify as zero; incomplete rows are excluded from numeric rules.
- **Coach topic priority.** Risk language now takes precedence over incidental mentions of an account, so account-risk questions receive risk education rather than tax-account guidance.
- **ATR input and smoothing.** Calculate ATR with Wilder smoothing and only when real High/Low/Close columns exist; close-only price data no longer produces a fabricated ATR.
- **Project setup documentation.** Replaced the minimal README with quickstarts, supported workflows, prerequisites, boundaries, and testing guidance.

### Added

- Regression tests for FRED sentinel normalization, canonical records, incomplete screener values, risk routing, and ATR validation/smoothing.

### Validation

- Tested unchanged commit `5d7143f00b24d69460d04d073b5958a2cf35aa40` before editing: Python suite passed (55 tests) after installing the dependencies needed by the documented test workflow.
- Confirmed on the unchanged commit: screener crashed on a `None` metric; FRED passed `"."` through as a value; risk-in-account wording routed to account/tax guidance; and close-only price data returned a numeric ATR.
- After changes: `PYTHONPATH=. python -m pytest tests -q` passes (59 tests). Static concerns not reproduced as runtime failures remain open for later work.


### Fixed

- **Qdrant point IDs (blocking).** `chunking.chunk_document` derived a 64-character
  SHA-256 hex digest as `chunk_id` and `QdrantKnowledgeBase.upsert` passed it straight to
  `PointStruct.id`. Qdrant accepts unsigned integers or UUIDs, so every real upsert was
  rejected with `Point id ... is not a valid UUID`. Chunk IDs are now deterministic UUIDv5
  values derived from the chunk content key; the SHA-256 digest is retained as
  `payload["content_hash"]`. `QdrantKnowledgeBase.upsert` now validates each ID (unsigned 64-bit integer or
  UUID) and raises a clear `ValueError` before calling Qdrant.
- **Test suite could not run.** `benchmark/__init__.py` and `scripts/seed_demo_data.py`
  contained Markdown prose, so `python -m pytest tests` aborted at collection with a
  `SyntaxError` and the seed script was not executable. Both are now valid Python;
  `scripts/seed_demo_data.py` seeds synthetic demo rows for the read-only evidence UI.
- **Two red tests.** `test_filing_workflow_fetches_parses_chunks_indexes_and_compares`
  asserted one section for a two-Item fixture (it is two). `test_filing_intelligence` fed
  `DEF 14A` into `FilingVersion`, which rejected it, so the executive-change and
  compensation categories the intelligence layer advertises were unreachable. `FilingVersion`
  now accepts `DEF 14A`.
- **Collection identifier drift.** The registry declared `sec_filings`, `sec_insider`,
  `fred_macro`, `usaspending_awards` while adapters emitted `filings`, `insider`,
  `macro_observations`, `federal_awards`, so registry-driven filters matched nothing.
  Adapters now emit registry identifiers; `market_prices` and `alternative_data` are
  registered; `tests/test_collections_registry.py` fails if an adapter emits an
  unregistered collection.
- **SEC extraction.** The RAG SEC client stripped `script`, `style` and `ix:header` but not
  `ix:hidden`, unlike `sources/sec_parser.html_to_text`. The client now calls the shared
  helper, so hidden Inline XBRL facts no longer reach filing text or embeddings.
- **License status in the review UI.** `App.tsx` read `license_status` from `data`/`metadata`
  instead of the top-level normalized field, so a real value was masked by the fallback.

### Added

- `tests/test_qdrant_store.py` exercises a real local Qdrant collection (upsert, retrieve,
  idempotent re-ingestion, ID validation, search), which the fake-index workflow test could
  not cover.
- `tests/test_sec_html_extraction.py` drives the SEC client through a fake session against
  Inline XBRL markup containing hidden facts.
- `tests/test_collections_registry.py` AST-scans adapters for `collection=` literals.
