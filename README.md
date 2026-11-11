# Market Recon: Python + Go + Rust

Market Recon is a public-source research toolkit. Python remains the source-adapter, parsing, RAG, and exploratory-analysis layer. This update adds a small Go ingestion gateway and a Rust batch engine for deterministic cross-signal grouping. These components do not produce trading recommendations.

## Component boundaries

```text
Python source adapters / SEC parsers / RAG
                  │ NormalizedRecord JSON
                  ▼
Go ingestion gateway (localhost by default; bearer token; append-only JSONL)
                  │ JSONL records / exported PublicSignal JSONL
                  ▼
Rust signal engine (deterministic, date-bounded mixed-evidence grouping)
```

- **Python**: API collectors, document extraction, RAG, exploratory workflows.
- **Go**: small typed HTTP boundary for authenticated, size-limited, provenance-validated record intake and durable JSONL append.
- **Rust**: CPU-efficient batch processing of `PublicSignal` JSONL, with bounded date windows and source-cited findings.

## Run the Go gateway

```bash
cd go/ingest-gateway
export MARKET_RECON_INGEST_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
go test ./...
go run .
```

Defaults to `127.0.0.1:8081` and `data/normalized-records.jsonl`. Set `MARKET_RECON_LISTEN_ADDR` deliberately before exposing it beyond localhost. The bearer token is required and must be at least 24 characters. `GET /health` is unauthenticated and reports process health only; `POST /v1/records` requires the token. The gateway validates shape/provenance and appends JSONL; it does not deduplicate or claim transactional database semantics.

Send a canonical `NormalizedRecord` as one JSON object:

```bash
curl -X POST http://127.0.0.1:8081/v1/records \
  -H "Authorization: Bearer $MARKET_RECON_INGEST_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"record_id":"demo:1","source_id":"demo","collection":"filings","record_type":"filing","source_name":"Public source","source_url":"https://example.org/filing","retrieved_at":"2026-01-01T00:00:00Z","data":{"text":"example"},"license_status":"review_required"}'
```

## Run Rust signal engine

Requires Rust stable and Cargo:

```bash
cd rust/signal-engine
cargo test
cargo run -- 2026-02-01 120 2 < ../../data/examples/public-signals.jsonl
```

Input is one JSON `PublicSignal` per line with fields matching `market_recon/intelligence/models.py`; output is a JSON array containing mixed positive/negative observations, source URLs, dates, and a non-predictive interpretation. The engine is deterministic and does not infer deception, causation, materiality, or investment merit.

## Scope and safeguards

Use authorized public sources and documented APIs. Do not collect exposed cloud assets, leaked/private material, login-gated data without permission, or confidential information. Preserve source URLs and terms/license status. Signal direction describes measured change relative to a baseline—not whether a stock is good or bad. This is a research utility, not investment advice.

These are starter components; no build/test execution is claimed unless CI or a local test log confirms it.
