from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

import api.app as evidence_api
from market_recon.sources.schema import NormalizedRecord
from market_recon.sources.storage import write_records


def test_records_api_filters_paginates_and_cites(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "market.db"
    rows = [
        NormalizedRecord(f"test:{i}", "test", "filings", "filing", "Example Source", f"https://example.org/{i}", f"2026-01-0{i}T00:00:00Z", {"text": "public evidence"}, observed_at=f"2026-01-0{i}", entity_name="Example Co", ticker="TEST")
        for i in range(1, 4)
    ]
    write_records(rows, database, "sqlite")
    monkeypatch.setattr(evidence_api, "DEFAULT_DB", database)
    client = TestClient(evidence_api.app)
    response = client.get("/api/records", params={"ticker": "test", "page": 2, "page_size": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 1
    assert body["items"][0]["source_url"].startswith("https://")
    detail = client.get(f"/api/records/{body['items'][0]['record_id']}")
    assert detail.status_code == 200
    assert detail.json()["data"]["text"] == "public evidence"


def test_records_api_handles_missing_database(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(evidence_api, "DEFAULT_DB", tmp_path / "absent.db")
    assert TestClient(evidence_api.app).get("/api/records").status_code == 503
