from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_DB = Path(os.getenv("MARKET_RECON_DB", "data/market.db"))
app = FastAPI(title="Market Recon Evidence API", version="0.1.0", description="Read-only API for public-source research records")

# Keep browser access local by default. Override with a comma-separated explicit allowlist.
_origins = [origin.strip() for origin in os.getenv("MARKET_RECON_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)


def _db_target() -> Path:
    env_path = os.getenv("MARKET_RECON_DB")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB


def _connect() -> sqlite3.Connection:
    target = _db_target()
    if not target.exists():
        raise HTTPException(status_code=503, detail="Evidence database is not initialized")
    connection = sqlite3.connect(f"file:{target.resolve()}?mode=ro", uri=True, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def _record(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    for key in ("data_json", "metadata_json"):
        raw = result.pop(key, None)
        try:
            val = json.loads(raw) if raw else {}
            result["data" if key == "data_json" else "metadata"] = val if isinstance(val, dict) else {}
        except (json.JSONDecodeError, TypeError):
            result["data" if key == "data_json" else "metadata"] = {}
    return result


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/records")
def list_records(
    source_id: str | None = None,
    collection: str | None = None,
    ticker: str | None = None,
    q: str | None = Query(default=None, max_length=200),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    clauses: list[str] = []
    params: list[Any] = []
    for field, value in (("source_id", source_id), ("collection", collection), ("ticker", ticker.upper() if ticker else None)):
        if value:
            clauses.append(f"{field} = ?")
            params.append(value)
    if q and q.strip():
        clauses.append("(entity_name LIKE ? OR record_type LIKE ? OR source_name LIKE ?)")
        pattern = f"%{q.strip()}%"
        params.extend([pattern, pattern, pattern])
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    offset = (page - 1) * page_size
    try:
        with _connect() as connection:
            total = connection.execute(f"SELECT COUNT(*) FROM normalized_records{where}", params).fetchone()[0]
            rows = connection.execute(
                f"SELECT * FROM normalized_records{where} ORDER BY COALESCE(observed_at, retrieved_at) DESC, record_id LIMIT ? OFFSET ?",
                [*params, page_size, offset],
            ).fetchall()
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=503, detail="Evidence database schema is unavailable") from exc
    return {"items": [_record(row) for row in rows], "page": page, "page_size": page_size, "total": total}


@app.get("/api/records/{record_id:path}")
def get_record(record_id: str) -> dict[str, Any]:
    try:
        with _connect() as connection:
            row = connection.execute("SELECT * FROM normalized_records WHERE record_id = ?", (record_id,)).fetchone()
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=503, detail="Evidence database schema is unavailable") from exc
    if row is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return _record(row)
