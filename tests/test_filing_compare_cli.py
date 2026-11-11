from __future__ import annotations

import json
from pathlib import Path

from market_recon.sources.filing_cli import main
from market_recon.sources.sec_filing_workflow import FilingVersionStore


def test_compare_cli_uses_archived_versions_without_vector_store(tmp_path: Path, monkeypatch, capsys):
    database = tmp_path / "filings.sqlite"
    store = FilingVersionStore(database)
    store.save("old", "TEST", "10-K", "2025-01-01", "000123", "https://www.sec.gov/old", {"Part I Item 1A": "Supplier risk factor."})
    store.save("new", "TEST", "10-K", "2026-01-01", "000123", "https://www.sec.gov/new", {"Part I Item 1A": "New cybersecurity risk factor."})
    monkeypatch.setattr("sys.argv", ["filing_cli", "compare", "--ticker", "TEST", "--database", str(database)])
    main()
    output = json.loads(capsys.readouterr().out)
    assert output["ticker"] == "TEST"
    assert output["before"]["source_url"].endswith("old")
    assert output["after"]["source_url"].endswith("new")
