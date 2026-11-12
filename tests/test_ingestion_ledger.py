from __future__ import annotations

from pathlib import Path

from market_recon.sources.ledger import IngestionLedger, IngestionRun, generate_run_id


def test_ingestion_ledger_records_and_retrieves_runs(tmp_path: Path):
    db_path = tmp_path / "ledger.db"
    ledger = IngestionLedger(db_path)

    run_id = generate_run_id("sec", "ticker:AAPL limit:10", "2026-02-12T00:00:00Z")
    run = IngestionRun(
        run_id=run_id,
        source_id="sec",
        requested_range="ticker:AAPL limit:10",
        retrieved_at="2026-02-12T00:00:00Z",
        records_fetched=10,
        records_skipped=1,
        errors_count=0,
        parser_version="sec_parser:v1.0.0",
        license_status="public_domain",
        config_hash="cfg_abc123",
        notes="Primary 10-K documents ingested; exhibits omitted.",
    )

    ledger.record_run(run)

    retrieved = ledger.get_run(run_id)
    assert retrieved is not None
    assert retrieved.run_id == run_id
    assert retrieved.source_id == "sec"
    assert retrieved.records_fetched == 10
    assert retrieved.records_skipped == 1
    assert retrieved.errors_count == 0
    assert retrieved.parser_version == "sec_parser:v1.0.0"

    runs = ledger.list_runs("sec")
    assert len(runs) == 1
    assert runs[0].run_id == run_id

    empty_runs = ledger.list_runs("fred")
    assert len(empty_runs) == 0
