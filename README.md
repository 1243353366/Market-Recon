# Market Recon

Market Recon is an open-source research toolkit for exploring public-market data and source-cited company filings. It combines a small Python research CLI, source adapters, an optional SEC filing search/comparison workflow, a read-only evidence API, and early dashboard/UI experiments.

**This is a scaffold and educational research software, not a finished investment product.** Sample data and example screens are not live market analysis. Some modules are prototypes, and configurable providers require your own valid account and current API documentation. Nothing here is investment advice or a trading signal.

## What is implemented

- **Python price research:** fetches price history and company information through `yfinance`, computes common technical indicators, and can write a Markdown company report.
- **Source adapters:** normalized, provenance-bearing records for SEC filings, FRED observations, USAspending awards, Yahoo Finance, and Stooq, plus a deliberately configurable Quiver adapter.
- **SEC filing workflow (optional):** fetch 10-K/10-Q filings, extract sections, index chunks in Qdrant, archive parsed filing versions in SQLite, and compare the latest archived versions with deterministic heuristics and source citations.
- **Evidence API:** read-only SQLite-backed API for normalized records.
- **Prototypes:** investor education, investor library, and web/dashboard interfaces. These should not be mistaken for a complete or personalized investment service.

See [docs/](docs/README.md) for workflow and methodology notes. The previous placeholder-only folders have been removed; active Python code lives under `market_recon/`.

## Quickstart: Python CLI

Python 3.10 or newer is required. In a fresh virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m market_recon.cli --help
```

Run a sample company report (this fetches public provider data, so network access is required):

```bash
python -m market_recon.cli --symbol AAPL --report
```

The default price and company-data paths depend on Yahoo Finance through `yfinance`; provider availability and returned data are not guaranteed. The CLI may not produce a meaningful ATR unless the fetched price frame includes High and Low columns.

## Optional SEC filing workflow

The filing search uses a sentence-transformer embedding model and Qdrant. Install the optional dependencies and configure an identifying SEC User-Agent with a contact address:

```bash
python -m pip install -e '.[rag]'
export SEC_USER_AGENT='MarketRecon research contact@example.org'
```

On first ingestion, the configured model may be downloaded. Ingest recent NVDA 10-Ks:

```bash
python -m market_recon.sources.filing_cli ingest --ticker NVDA --form 10-K --limit 10
```

Compare the latest two archived 10-Ks:

```bash
python -m market_recon.sources.filing_cli compare --ticker NVDA --form 10-K
```

The default SQLite archive and local Qdrant data are written under `data/market.db` and `data/qdrant`. Use `--database`, `--model`, `--qdrant-path`, `--qdrant-url`, or `--qdrant-api-key` to configure storage and indexing. Treat heuristic changes as review candidates and verify both source filings.

## Tests

Install the API and test dependencies, plus Qdrant and BeautifulSoup used by the RAG tests:

```bash
python -m pip install -e . -r requirements-api.txt -r requirements-dev.txt qdrant-client beautifulsoup4
PYTHONPATH=. python -m pytest tests -q
```

Tests use mocked provider HTTP responses and local Qdrant for deterministic coverage. They do not establish that live third-party APIs, every UI, or the full production workflow works with your credentials or network.

## Other entry points

- Streamlit prototype: `streamlit run dashboard/app.py`
- Web evidence UI: `cd web && npm install && npm run dev`
- Evidence API: `uvicorn api.app:app --reload` (configure `MARKET_RECON_DB` before starting if using a non-default database)
- Go ingestion gateway: see `go/ingest-gateway/`
- Rust signal engine: see `rust/signal-engine/`

The UI, API, Go gateway, and Rust engine have separate setup and configuration; see the relevant source folders and docs before using them.

## Data, licensing, and security

Provider access, rate limits, API terms, and redistribution rights vary. Review source-specific terms before storing or sharing fetched data. SEC use requires a descriptive User-Agent; FRED requires an API key. Do not commit credentials. Use environment variables for local configuration and do not send secrets into public issues or logs.

For scope, known limitations, and change history, see [docs/](docs/README.md) and [CHANGELOG.md](CHANGELOG.md).
