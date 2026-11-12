from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .schema import utc_now_iso


@dataclass(frozen=True)
class IngestionRun:
    """Audit ledger entry tracking an individual ingestion run."""

    run_id: str
    source_id: str
    requested_range: str
    retrieved_at: str
    records_fetched: int
    records_skipped: int
    errors_count: int
    parser_version: str
    license_status: str
    config_hash: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def generate_run_id(source_id: str, requested_range: str, retrieved_at: str) -> str:
    digest = hashlib.sha256(f"{source_id}:{requested_range}:{retrieved_at}".encode("utf-8")).hexdigest()[:12]
    return f"run:{source_id}:{digest}"


class IngestionLedger:
    """SQLite-backed ingestion ledger recording run provenance, scope, counts, and errors."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ingestion_runs (
                    run_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    requested_range TEXT NOT NULL,
                    retrieved_at TEXT NOT NULL,
                    records_fetched INTEGER NOT NULL,
                    records_skipped INTEGER NOT NULL,
                    errors_count INTEGER NOT NULL,
                    parser_version TEXT NOT NULL,
                    license_status TEXT NOT NULL,
                    config_hash TEXT NOT NULL,
                    notes TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_runs_source_time ON ingestion_runs(source_id, retrieved_at DESC)")

    def record_run(self, run: IngestionRun) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute("""
                INSERT INTO ingestion_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    records_fetched=excluded.records_fetched,
                    records_skipped=excluded.records_skipped,
                    errors_count=excluded.errors_count,
                    notes=excluded.notes
            """, (
                run.run_id,
                run.source_id,
                run.requested_range,
                run.retrieved_at,
                run.records_fetched,
                run.records_skipped,
                run.errors_count,
                run.parser_version,
                run.license_status,
                run.config_hash,
                run.notes,
            ))

    def get_run(self, run_id: str) -> IngestionRun | None:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM ingestion_runs WHERE run_id = ?", (run_id,)).fetchone()
            if row is None:
                return None
            return IngestionRun(
                run_id=row["run_id"],
                source_id=row["source_id"],
                requested_range=row["requested_range"],
                retrieved_at=row["retrieved_at"],
                records_fetched=row["records_fetched"],
                records_skipped=row["records_skipped"],
                errors_count=row["errors_count"],
                parser_version=row["parser_version"],
                license_status=row["license_status"],
                config_hash=row["config_hash"],
                notes=row["notes"],
            )

    def list_runs(self, source_id: str | None = None, limit: int = 50) -> list[IngestionRun]:
        query = "SELECT * FROM ingestion_runs"
        params: list[Any] = []
        if source_id:
            query += " WHERE source_id = ?"
            params.append(source_id)
        query += " ORDER BY retrieved_at DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            return [
                IngestionRun(
                    run_id=row["run_id"],
                    source_id=row["source_id"],
                    requested_range=row["requested_range"],
                    retrieved_at=row["retrieved_at"],
                    records_fetched=row["records_fetched"],
                    records_skipped=row["records_skipped"],
                    errors_count=row["errors_count"],
                    parser_version=row["parser_version"],
                    license_status=row["license_status"],
                    config_hash=row["config_hash"],
                    notes=row["notes"],
                )
                for row in rows
            ]
