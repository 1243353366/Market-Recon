from __future__ import annotations

import csv
import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .schema import NormalizedRecord


def write_records(records: Iterable[NormalizedRecord], output: str | Path, format: str) -> int:
    """Persist records to JSONL, CSV, or SQLite. SQLite upserts by stable record ID."""
    rows = list(records)
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    kind = format.lower()
    if kind == "json":
        with target.open("w", encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(asdict(row), ensure_ascii=False, default=str) + "\n")
    elif kind == "csv":
        fieldnames = ["record_id", "source_id", "collection", "record_type", "source_name", "source_url", "retrieved_at", "observed_at", "published_at", "entity_id", "entity_name", "ticker", "cik", "license_status", "data", "metadata"]
        with target.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                item = asdict(row)
                item["data"] = json.dumps(item["data"], ensure_ascii=False, default=str)
                item["metadata"] = json.dumps(item["metadata"], ensure_ascii=False, default=str)
                writer.writerow(item)
    elif kind == "sqlite":
        with sqlite3.connect(target) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS normalized_records (
                    record_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    collection TEXT NOT NULL,
                    record_type TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    retrieved_at TEXT NOT NULL,
                    observed_at TEXT,
                    published_at TEXT,
                    entity_id TEXT,
                    entity_name TEXT,
                    ticker TEXT,
                    cik TEXT,
                    license_status TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                )
            """)
            connection.execute("CREATE INDEX IF NOT EXISTS idx_records_source_collection ON normalized_records(source_id, collection)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_records_ticker_observed ON normalized_records(ticker, observed_at)")
            connection.executemany("""
                INSERT INTO normalized_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(record_id) DO UPDATE SET
                    source_id=excluded.source_id, collection=excluded.collection, record_type=excluded.record_type,
                    source_name=excluded.source_name, source_url=excluded.source_url, retrieved_at=excluded.retrieved_at,
                    observed_at=excluded.observed_at, published_at=excluded.published_at, entity_id=excluded.entity_id,
                    entity_name=excluded.entity_name, ticker=excluded.ticker, cik=excluded.cik,
                    license_status=excluded.license_status, data_json=excluded.data_json, metadata_json=excluded.metadata_json
            """, [(
                row.record_id, row.source_id, row.collection, row.record_type, row.source_name, row.source_url,
                row.retrieved_at, row.observed_at, row.published_at, row.entity_id, row.entity_name,
                row.ticker, row.cik, row.license_status,
                json.dumps(row.data, ensure_ascii=False, default=str),
                json.dumps(row.metadata, ensure_ascii=False, default=str),
            ) for row in rows])
    else:
        raise ValueError("format must be one of: json, csv, sqlite")
    return len(rows)
