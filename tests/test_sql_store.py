from __future__ import annotations

import sqlite3
import time
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.app import app
from market_recon.sources.schema import NormalizedRecord
from market_recon.sources.sec_filing_workflow import FilingVersionStore
from market_recon.sources.storage import write_records
from market_recon.sources.stooq import StooqAdapter
from market_recon.sources.yahoo_finance import YahooFinanceAdapter


def sample_record(record_id: str, ticker: str = "AAPL", observed_at: str = "2026-01-01") -> NormalizedRecord:
    return NormalizedRecord(
        record_id=record_id,
        source_id="sec",
        collection="filings",
        record_type="10-K",
        source_name="SEC EDGAR",
        source_url="https://www.sec.gov/filing",
        retrieved_at="2026-01-01T00:00:00Z",
        observed_at=observed_at,
        ticker=ticker,
        data={"revenue": 100},
        license_status="public_domain",
    )


def test_sqlite_storage_upsert_and_indexing(tmp_path: Path) -> None:
    db_path = tmp_path / "market.db"
    r1 = sample_record("rec:1", "AAPL")
    r2 = sample_record("rec:2", "MSFT")

    # Initial insert
    assert write_records([r1, r2], db_path, format="sqlite") == 2

    with sqlite3.connect(db_path) as conn:
        indices = [row[1] for row in conn.execute("PRAGMA index_list('normalized_records')").fetchall()]
        assert "idx_records_source_collection" in indices
        assert "idx_records_ticker_observed" in indices

    # Upsert with updated payload
    r1_updated = sample_record("rec:1", "AAPL")
    r1_updated.data["revenue"] = 250
    assert write_records([r1_updated], db_path, format="sqlite") == 1

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT data_json FROM normalized_records WHERE record_id = 'rec:1'").fetchall()
        assert len(rows) == 1
        assert '"revenue": 250' in rows[0][0]


def test_sqlite_readonly_uri_blocks_writes(tmp_path: Path) -> None:
    db_path = tmp_path / "market.db"
    write_records([sample_record("rec:1")], db_path, format="sqlite")

    with sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True) as ro_conn:
        row = ro_conn.execute("SELECT COUNT(*) FROM normalized_records").fetchone()
        assert row[0] == 1
        with pytest.raises(sqlite3.OperationalError, match="readonly database"):
            ro_conn.execute("DELETE FROM normalized_records")


def test_filing_version_store_tiebreaks_same_day_by_retrieved_at(tmp_path: Path) -> None:
    db_path = tmp_path / "filings.db"
    store = FilingVersionStore(db_path)

    # Two filings on the exact same filing date
    store.save("doc_hash_b", "TEST", "10-K", "2026-02-01", "0001", "https://sec.gov/first", {"Item 1": "First version"})
    time.sleep(0.01)
    store.save("doc_hash_a", "TEST", "10-K", "2026-02-01", "0001", "https://sec.gov/second", {"Item 1": "Amended text"})

    pair = store.latest_pair("TEST", "10-K")
    assert pair is not None
    older, newer = pair
    assert older.source_url == "https://sec.gov/first"
    assert newer.source_url == "https://sec.gov/second"


def test_filing_version_store_amendment_pairing(tmp_path: Path) -> None:
    db_path = tmp_path / "filings.db"
    store = FilingVersionStore(db_path)

    store.save("doc_1", "NVDA", "10-K", "2026-01-01", "0002", "https://sec.gov/10k", {"Item 1": "Original 10-K"})
    store.save("doc_2", "NVDA", "10-K/A", "2026-02-01", "0002", "https://sec.gov/10ka", {"Item 1": "Amended 10-K/A"})

    # Should match 10-K with its 10-K/A amendment
    pair = store.latest_pair("NVDA", "10-K", include_amendments=True)
    assert pair is not None
    older, newer = pair
    assert older.form == "10-K"
    assert newer.form == "10-K/A"


def test_api_dynamic_env_db_path(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "dynamic_market.db"
    write_records([sample_record("dyn:1", "TSLA")], db_path, format="sqlite")

    monkeypatch.setenv("MARKET_RECON_DB", str(db_path))
    client = TestClient(app)
    response = client.get("/api/records?ticker=TSLA")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["ticker"] == "TSLA"


def test_date_range_validation_rejects_inverted_dates() -> None:
    yf = YahooFinanceAdapter()
    with pytest.raises(ValueError, match="start_date must not be after end_date"):
        yf.fetch(symbol="AAPL", start_date=date(2026, 5, 1), end_date=date(2026, 1, 1))

    stooq = StooqAdapter()
    with pytest.raises(ValueError, match="start_date must not be after end_date"):
        stooq.fetch(symbol="AAPL", start_date=date(2026, 5, 1), end_date=date(2026, 1, 1))


def test_filing_version_store_creates_ticker_index(tmp_path: Path) -> None:
    db_path = tmp_path / "filings_idx.db"
    FilingVersionStore(db_path)
    with sqlite3.connect(db_path) as conn:
        indices = [row[1] for row in conn.execute("PRAGMA index_list('filing_versions')").fetchall()]
        assert "idx_filing_versions_lookup" in indices
        assert "idx_filing_versions_ticker" in indices


def test_normalized_record_enforces_dictionary_data_and_metadata() -> None:
    with pytest.raises(TypeError, match="data must be a dictionary"):
        NormalizedRecord(
            record_id="rec:bad_data",
            source_id="sec",
            collection="filings",
            record_type="10-K",
            source_name="SEC EDGAR",
            source_url="https://sec.gov",
            retrieved_at="2026-01-01T00:00:00Z",
            data="not a dict",  # type: ignore[arg-type]
        )

    with pytest.raises(TypeError, match="metadata must be a dictionary"):
        NormalizedRecord(
            record_id="rec:bad_meta",
            source_id="sec",
            collection="filings",
            record_type="10-K",
            source_name="SEC EDGAR",
            source_url="https://sec.gov",
            retrieved_at="2026-01-01T00:00:00Z",
            data={},
            metadata=[1, 2, 3],  # type: ignore[arg-type]
        )
