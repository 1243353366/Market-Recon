### SEC filing text extraction

Added `market_recon/sources/sec_parser.py` for line-preserving SEC HTML cleanup and rule-based 10-K/10-Q Item extraction. It selects the longest duplicated section candidate (often distinguishing table-of-contents headings from body text) and retains full text for verification. This is a practical starter parser—not legal-grade extraction; validate each section against the original filing.

### Registry and ingestion

Copy `config/sources.example.json`, enable desired sources, set credentials through environment variables, and run:

```bash
python -m market_recon.sources.ingest --config config/sources.example.json --source yahoo_finance --params '{"symbol":"AAPL","period":"1mo"}' --format sqlite --output data/market.db
python -m market_recon.sources.ingest --config config/sources.example.json --source stooq --params '{"symbol":"AAPL","start_date":"2025-01-01","end_date":"2025-03-31"}' --format json --output data/prices.jsonl
```

The ingestion runner writes JSONL, CSV, or idempotent SQLite records with provenance. See `docs/source-adapters.md` and `market_recon/sources/README.md` for current adapter status and config details.

### Market data adapters

Added Yahoo Finance (`yfinance`, an unofficial wrapper) and Stooq daily CSV adapters. Check provider terms, coverage, delays, adjustment behavior, and licensing before relying on or redistributing data. No adapter silently substitutes sample prices.

### GrayHatWarfare

Not integrated. GrayHatWarfare searches exposed cloud storage/assets and may surface third-party data or sensitive material. Market Recon will not enumerate, ingest, or index exposed assets. Use authorized public datasets and documented APIs instead; source availability does not imply authorization to access or redistribute content.
