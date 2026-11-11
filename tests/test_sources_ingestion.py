from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest

from market_recon.sources.loader import load_adapters
from market_recon.sources.schema import NormalizedRecord
from market_recon.sources.storage import write_records


def record(record_id: str = "test:1") -> NormalizedRecord:
    return NormalizedRecord(record_id, "test", "collection", "kind", "Test", "https://example.org/1", "2026-01-01T00:00:00Z", {"x": 1}, observed_at="2026-01-01")


def test_storage_jsonl_csv_and_sqlite_are_idempotent(tmp_path: Path) -> None:
    item = record()
    json_path = tmp_path / "records.jsonl"
    csv_path = tmp_path / "records.csv"
    sqlite_path = tmp_path / "records.db"
    assert write_records([item], json_path, "json") == 1
    assert json.loads(json_path.read_text())["record_id"] == "test:1"
    assert write_records([item], csv_path, "csv") == 1
    assert "record_id" in csv_path.read_text()
    write_records([item], sqlite_path, "sqlite")
    write_records([item], sqlite_path, "sqlite")
    with sqlite3.connect(sqlite_path) as connection:
        assert connection.execute("select count(*) from normalized_records").fetchone()[0] == 1


def test_loader_only_initializes_enabled_sources(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRED_API_KEY", "test-key")
    config = tmp_path / "sources.json"
    config.write_text(json.dumps({"sources": {"fred": {"enabled": True, "api_key_env": "FRED_API_KEY"}, "stooq": {"enabled": False}}}))
    adapters = load_adapters(str(config))
    assert list(adapters) == ["fred"]


def test_record_requires_https_provenance() -> None:
    with pytest.raises(ValueError):
        NormalizedRecord("a", "s", "c", "r", "name", "http://example.org", "now", {})
