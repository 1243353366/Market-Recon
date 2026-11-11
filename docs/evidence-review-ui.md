# Evidence API and TypeScript UI

This adds a read-only evidence review interface: Python/FastAPI serves normalized records from the existing SQLite `normalized_records` table, while a small React + TypeScript + Vite frontend filters, paginates, and inspects source-cited records.

## Python backend

From the repository root:

```bash
pip install -r requirements-api.txt
uvicorn api.app:app --reload
```

The API reads `MARKET_RECON_DB` (defaults to `data/market.db`), opens SQLite in read-only mode, and exposes:

- `GET /health`
- `GET /api/records?page=1&page_size=25`
- optional filters: `ticker`, `source_id`, `collection`, `q`
- `GET /api/records/{record_id}`

Populate the database using the Python source adapters and existing `write_records(..., format="sqlite")` function. Example:

```bash
python -m market_recon.sources.ingest \
  --config config/sources.example.json \
  --source usaspending \
  --params '{"start_date":"2025-01-01","end_date":"2025-03-31","limit":25}' \
  --format sqlite --output data/market.db
```

The endpoint is read-only and parameterizes query values. CORS is restricted to local Vite origins by default; configure `MARKET_RECON_CORS_ORIGINS` with exact origins if needed. Do not expose this development API publicly without authentication, TLS termination, rate limits, and deployment review.

## TypeScript frontend

```bash
cd web
npm install
npm run dev
```

Vite serves on `http://127.0.0.1:5173`. Set `VITE_API_BASE_URL` to the API origin if it differs from `http://127.0.0.1:8000`. Build with `npm run build`.

The UI is an evidence browser, not an anomaly or investment recommendation engine. It displays the original citation link, source, observation/retrieval dates, and normalized record payload. Treat raw data as untrusted text; the UI renders it as text rather than HTML.

Python remains the default implementation language for collectors, storage, and orchestration. Add another language only after profiling demonstrates a concrete performance or deployment need.
