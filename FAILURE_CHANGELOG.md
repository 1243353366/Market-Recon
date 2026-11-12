# Engineering Failure Changelog & Defensive Playbook

This document is an append-only retrospective catalog of observed engineering failures, blind spots, and regression root causes across the Market-Recon codebase.

It is repurposed as an **autonomous operational playbook**: before designing or merging cross-language features, inspect these failure modes and enforce their corresponding defensive invariants.

---

## Operational Defensive Invariants

1. **Stable Runtime Invariant**: Test commands in `package.json` and CI workflows must never invoke experimental runtime flags (e.g. `--experimental-strip-types`). Always compile to standard ECMAScript or bundle before executing native test runners.
2. **Multi-LTS Verification Invariant**: CI matrix must test both Active LTS and Current LTS runtimes for interpreted/bundled languages (e.g. Node 20 and Node 22).
3. **Hermetic Packaging Invariant**: Test suites must execute successfully in a bare clone without requiring an ambient editable install (`pip install -e .`), enforced by explicit test-runner path resolution (`pythonpath = ["."]`).
4. **Filesystem Idempotency Invariant**: Any service writing to local storage (JSONL, SQLite, logs) must ensure parent directories exist (`os.MkdirAll` / `pathlib.Path.mkdir(parents=True)`) before opening file handles.
5. **Context Scoping vs. Signal Match Invariant**: Heuristic classification rules must never classify a document solely on structural metadata or section headers without corroborating signal phrases in the diff payload.
6. **External Sentinel Sanitization Invariant**: Ingestion adapters must normalize vendor-specific missing data sentinels (e.g. FRED's `"."`, SEC placeholders) to native `null` / `None` at the adapter boundary.
7. **Strict Finite Serialization Invariant**: All floating-point metrics destined for JSON serialization must assert finiteness (`is_finite()`) and bounded ranges before formatting.
8. **Platform Permission Transparency**: When GitHub API returns HTTP 404 for tree or commit creation affecting `.github/workflows/*`, check OAuth token scopes for `workflow` before debugging Git object hashes.

---

## Failure Catalog

### FAIL-001: CI TypeScript Tests Failing After 11s on Node 20 LTS
- **Date**: 2026-11-12
- **Trigger**: GitHub Actions workflow run `43287428537`, commit `703f11b` (`typescript-tests`)
- **Observed Symptom**: Job terminated after 11 seconds with exit code 9:
  ```
  node: bad option: --experimental-strip-types
  npm error Lifecycle script `test` failed with error:
  npm error Command failed. Exit code: 9
  ```
- **Root Cause**: `web/package.json` test script executed `node --experimental-strip-types --test src/**/*.test.ts`. The `--experimental-strip-types` flag was introduced in Node.js v22.6.0. The CI workflow was configured with Node.js 20 (Active LTS), which rejects unrecognized command-line arguments immediately.
- **Resolution**:
  1. Created `web/tsconfig.test.json` targeting standard NodeNext output into `.test-dist/`.
  2. Updated `web/package.json` test script to compile tests first (`tsc -p tsconfig.test.json`) and execute the stable native test runner: `node --test .test-dist/**/*.test.js`.
  3. Added `.test-dist/` to `.gitignore`.
  4. Expanded `.github/workflows/ci.yml` `typescript-tests` to run on a matrix of both Node 20 and Node 22 to prevent LTS regression.
- **Repurposed Playbook Rule**: *Rule #1 & #2 (Stable Runtime & Multi-LTS Verification).*

---

### FAIL-002: GitHub API Rejection (HTTP 404) on Workflow Tree Creation
- **Date**: 2026-11-12
- **Trigger**: GitHub REST API `POST /repos/.../git/trees` during commit push
- **Observed Symptom**: Tree creation for `.github/workflows/ci.yml` failed with HTTP 404 Not Found, despite repository and parent commit shas being verified as valid.
- **Root Cause**: GitHub's authorization model returns HTTP 404 instead of HTTP 403 when attempting to create or modify workflow definitions under `.github/workflows/` without the explicit `workflow` OAuth scope.
- **Resolution**: Reconnected GitHub connection requesting `required_scopes: ["workflow"]`. Verified tree creation succeeded once scope was granted.
- **Repurposed Playbook Rule**: *Rule #8 (Platform Permission Transparency).*

---

### FAIL-003: Fresh Clone Test Collection Failure in Bare Virtualenv
- **Date**: 2026-11-11
- **Trigger**: Local pytest run immediately following fresh clone
- **Observed Symptom**:
  ```
  ModuleNotFoundError: No module named 'market_recon'
  ```
- **Root Cause**: Test files imported `from market_recon.sources...` assuming `market_recon` was installed into the environment's `site-packages` via `pip install -e .`.
- **Resolution**: Added `pythonpath = ["."]` in `pyproject.toml` under `[tool.pytest.ini_options]` so pytest automatically resolves the repository root without environment mutation.
- **Repurposed Playbook Rule**: *Rule #3 (Hermetic Packaging Invariant).*

---

### FAIL-004: Go Ingest Gateway Panic on Uncreated Storage Directory
- **Date**: 2026-11-11
- **Trigger**: Calling `/ingest` endpoint on fresh Go gateway startup
- **Observed Symptom**: HTTP 500 Internal Server Error; gateway logged `no such file or directory` when attempting `os.OpenFile("data/audit.jsonl", os.O_CREATE|os.O_APPEND, 0644)`.
- **Root Cause**: The gateway assumed the `./data` directory was created by external deployment scripts or previous runs.
- **Resolution**: Added `os.MkdirAll(filepath.Dir(path), 0755)` prior to file creation in `go/ingest-gateway/main.go`. Added regression test `TestIngestRequiresBearerAndPersistsJSONL`.
- **Repurposed Playbook Rule**: *Rule #4 (Filesystem Idempotency Invariant).*

---

### FAIL-005: Filing Classifier False Positives on Broad Section Hints
- **Date**: 2026-11-12
- **Trigger**: Adversarial filing diff evaluation with unrelated corporate governance text in Item 1 and Item 7
- **Observed Symptom**: Unrelated text modifications in large 10-K sections were classified as `supply_chain_changes` solely because Item 1 / Item 7 were listed in section hints.
- **Root Cause**: In `market_recon/filing_intelligence.py`, `_matches()` evaluated `matches_section or matches_phrase`, allowing a section match to label any changed line without textual confirmation.
- **Resolution**: Refactored `_matches()` to strictly require `matches_phrase` for all categories. Section hints are retained purely to scope or provide contextual confidence. Added `benchmark/filing_eval.py` with 5 hard negatives to enforce this invariant.
- **Repurposed Playbook Rule**: *Rule #5 (Context Scoping vs. Signal Match Invariant).*

---

### FAIL-006: FRED Missing-Data Sentinel Leaking Into Numeric Calculations
- **Date**: 2026-11-11
- **Trigger**: Ingesting FRED series containing observation dates with missing data
- **Observed Symptom**: String sentinel `"."` preserved as string in `data["value"]`, causing downstream `float()` casting and screening calculation crashes.
- **Root Cause**: The Federal Reserve economic database encodes missing or unreleased observations as a single period character (`"."`) instead of omitting or returning null.
- **Resolution**: Added normalization check in `FredClient._parse_observations` to convert `"."` into `None`, and validated numeric coercion in screening rules.
- **Repurposed Playbook Rule**: *Rule #6 (External Sentinel Sanitization Invariant).*

---

### FAIL-007: Non-Finite Float JSON Serialization Panic in Rust Signal Engine
- **Date**: 2026-11-12
- **Trigger**: Ingesting degenerate market price frames (e.g. flat pricing with zero volatility)
- **Observed Symptom**: `serde_json::to_string(&signals)` returned `Error("JSON cannot represent NaN or Infinity")`.
- **Root Cause**: Standard IEEE 754 floating point arithmetic produces `NaN` on division by zero (e.g. zero standard deviation). `serde_json` strictly enforces RFC 8259, which forbids `NaN` and `Infinity`.
- **Resolution**: Enforced `metric_value.is_finite()` validation in `SignalRecord::new()` and clamped confidence between `0.0` and `1.0`. Added Rust unit tests `rejects_non_finite_metric_value` and `rejects_invalid_confidence`.
- **Repurposed Playbook Rule**: *Rule #7 (Strict Finite Serialization Invariant).*

### FAIL-008: Unvalidated Runtime Types in PublicSignal Causing AttributeError
- **Date**: 2026-11-12
- **Trigger**: Ingestion of malformed signal records (e.g. `source_name=None`, `source_url=123`, `signal_id=None`)
- **Observed Symptom**: Crashed with `AttributeError: 'NoneType' object has no attribute 'strip'` and `'int' object has no attribute 'startswith'` instead of clean contract validation error.
- **Root Cause**: `__post_init__` assumed string types without verifying `isinstance(..., str)` before calling string methods (`strip()`, `startswith()`).
- **Resolution**: Added strict type validation across all required (`signal_id`, `entity_id`, `entity_name`, `summary`, `source_name`, `source_url`) and optional (`metric_name`, `unit`, `baseline`) string fields in `PublicSignal.__post_init__`, raising `ValueError` on type or empty string violations. Added unit tests in `tests/test_intelligence.py`.
- **Repurposed Playbook Rule**: *Runtime dataclass contracts must verify argument types (`isinstance`) before invoking type-specific methods.*

---

### FAIL-009: Unchecked Signal IDs Fabricating False Divergence Clusters
- **Date**: 2026-11-12
- **Trigger**: Repeated ingestion of identical evidence or duplicate signal events
- **Observed Symptom**: Grouping and counting logic in `find_cross_signal_divergences` repeatedly counted duplicate signal IDs, allowing duplicate evidence to meet the divergence threshold or distort positive/negative counts.
- **Root Cause**: `find_cross_signal_divergences` did not deduplicate signals by `(entity_id, signal_id)` before grouping by lookback window.
- **Resolution**: Enforced set-based deduplication by `(entity_id, signal_id)` before grouping. Added regression test `test_divergence_deduplicates_duplicate_signal_ids`.
- **Repurposed Playbook Rule**: *Evidence aggregation algorithms must deduplicate on canonical identifiers before computing summary metrics or anomaly thresholds.*

---

### FAIL-010: Stale Entity Name Selection in Divergence Reporting
- **Date**: 2026-11-12
- **Trigger**: Entity undergoing corporate name change or legal rebranding across multi-month evaluation window
- **Observed Symptom**: `SignalDivergence.entity_name` reported the oldest historical name in the window (`ordered[0].entity_name`) rather than the canonical current name.
- **Root Cause**: Observations were sorted chronologically ascending, and `entity_name` was hardcoded to index 0.
- **Resolution**: Selected canonical entity name from the latest observation in the window (`ordered[-1].entity_name`). Added regression test `test_divergence_uses_latest_entity_name_across_time`.
- **Repurposed Playbook Rule**: *When aggregating time-series records under an entity identifier, select entity display metadata from the latest authoritative observation.*

---

### FAIL-011: Unqualified Divergence Clusters from Single-Source or Disparate Baselines
- **Date**: 2026-11-12
- **Trigger**: Running divergence detection on signals originating from a single press release or across heterogeneous baselines (e.g. YoY vs QoQ)
- **Observed Symptom**: Emitted mixed-signal clusters without surfacing that evidence lacked independent cross-source corroboration or compared conflicting metric baselines.
- **Root Cause**: Divergence evaluation only checked for directional opposition and distinct kind count, without auditing source diversity or baseline comparability.
- **Resolution**: Added `distinct_source_count` and `divergence_caveat` to `SignalDivergence`. Emits explicit caveats when diverging signals originate from a single source or reference heterogeneous baselines.
- **Repurposed Playbook Rule**: *Multi-signal syntheses must qualify whether directional divergence is corroborated across independent sources and comparable measurement baselines.*

---

### FAIL-012: Node 20 CLI Glob Pattern Misinterpretation
- **Date**: 2026-11-12
- **Trigger**: Running `npm test` under Node 20.x in CI with glob argument `.test-dist/**/*.test.js`
- **Observed Symptom**: Crashed with `Could not find '/home/runner/work/Market-Recon/Market-Recon/web/.test-dist/**/*.test.js'` (exit code 1).
- **Root Cause**: Node 22 added internal recursive globbing for CLI arguments, whereas Node 20 passes unexpanded glob strings directly to file lookup when POSIX `sh` does not expand `**`. Because `rootDir` was `./src`, compiled test output resided at `.test-dist/*.test.js`.
- **Resolution**: Updated `npm test` to `.test-dist/*.test.js`, which is portably expanded by standard POSIX shells across Node 18, 20, 22, and 24.
- **Repurposed Playbook Rule**: *In multi-version Node CI matrixes, avoid relying on Node-version-specific CLI globbing; use standard POSIX single-level wildcards or explicit entrypoints.*
