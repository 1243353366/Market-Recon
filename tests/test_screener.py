from __future__ import annotations

from market_recon.screener import ScreenerRule, run_screening


def test_missing_null_and_non_numeric_values_do_not_pass_rules() -> None:
    rows = [
        {"symbol": "MISSING"},
        {"symbol": "NULL", "pe_ratio": None},
        {"symbol": "INVALID", "pe_ratio": "unknown"},
        {"symbol": "NAN", "pe_ratio": float("nan")},
        {"symbol": "VALID", "pe_ratio": 20},
    ]
    result = run_screening(rows, [ScreenerRule("Max P/E", "pe_ratio", max_value=30)])
    assert [row["symbol"] for row in result] == ["VALID"]
