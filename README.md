# Market Recon

> Public-source market research toolkit emphasizing deterministic pipelines, transparent heuristics, and explicit provenance citations.

Market Recon is an educational research toolkit designed to ingest, normalize, and explore public market data and SEC filings.

---

## Architecture Overview

```
                                      ┌────────────────────────┐
                                      │  Public Data Sources   │
                                      │ (SEC, FRED, USAspend)  │
                                      └───────────┬────────────┘
                                                  │
                                                  ▼
┌───────────────────────┐             ┌────────────────────────┐
│  Go Ingest Gateway    │────────────▶│    Normalized Records  │
│  (Token Auth, JSONL)  │             │ (Schema with citations)│
└───────────────────────┘             └───────────┬────────────┘
                                                  │
                     ┌────────────────────────────┼────────────────────────────┐
                     ▼                            ▼                            ▼
        ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
        │  SQLite Evidence DB     │  │  Qdrant RAG Store       │  │  Rust Signal Engine     │
        │  (Read-only API access) │  │  (Hybrid Vector/Lexical)│  │  (Divergence Detector)  │
        └────────────┬────────────┘  └─────────────────────────┘  └─────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │  React Evidence UI      │
        │  (Vite + TypeScript)    │
        └─────────────────────────┘
```

---

## Verification & Test Suites

The repository contains automated test suites across four languages:

### 1. Python (Core Logic, Adapters & SQL)
```bash
pip install -e '.[rag]'
pytest tests/ -v
```
Covers SEC parsing, schema normalization, technical indicators, stock screener rules, SQLite storage, and the Evidence API.

### 2. Go (Ingest Gateway)
```bash
cd go/ingest-gateway
go test -v ./...
```
Validates bearer token authorization, payload schemas, trailing object rejection, and thread-safe persistence.

### 3. Rust (Signal Divergence Engine)
```bash
cd rust/signal-engine
cargo test
```
Tests signal validation, HTTPS citation enforcement, multi-entity isolation, window boundary rules, and deterministic sorting.

### 4. TypeScript (Evidence UI)
```bash
cd web
npm install
npm test
npm run build
```
Typechecks with TypeScript `strict` mode, runs unit tests for record normalization and pagination math, and builds the Vite frontend.

---

## Quickstart

### Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-api.txt -r requirements-dev.txt
```

### Run Market Research CLI
```bash
python -m market_recon.cli --symbol AAPL --period 1mo --report
```

### Run SEC Filing Comparison
```bash
python -m market_recon.sources.filing_cli ingest --ticker AAPL --form 10-K
python -m market_recon.sources.filing_cli compare --ticker AAPL --form 10-K
```

---


---

## Engineering Quality & Defensive Playbook

Market-Recon maintains an autonomous engineering post-mortem catalog and defensive playbook in [FAILURE_CHANGELOG.md](FAILURE_CHANGELOG.md). It documents observed failure modes, root-cause analyses, and invariants across Python, Go, Rust, and TypeScript to systematically prevent pipeline and CI regressions.

## License & Limitations

Distributed under the MIT License.

*Research and educational use only. This software does not provide investment advice, trading recommendations, or financial advisory services. Always verify all citations and metrics against primary public records.*
