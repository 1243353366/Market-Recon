from __future__ import annotations

import pandas as pd
import pytest

from market_recon.reporting import build_company_report
from market_recon.technical_analysis import calculate_rsi, summarize_technical_metrics


def test_empty_price_frame_fails_explicitly() -> None:
    with pytest.raises(ValueError, match="at least one"):
        summarize_technical_metrics(pd.DataFrame(columns=["Close", "High", "Low"]))


def test_rsi_flat_and_rising_series_have_defined_edges() -> None:
    assert calculate_rsi(pd.Series([5.0] * 20)).iloc[-1] == 50
    assert calculate_rsi(pd.Series(range(1, 21), dtype=float)).iloc[-1] == 100


def test_report_does_not_make_directional_recommendation() -> None:
    metrics = {"sma_20": 1, "ema_20": 1, "rsi_14": 50, "macd": 0, "signal": 0, "histogram": 0, "atr_14": 1}
    report = build_company_report("TEST", {"company": "Test Co"}, metrics)
    assert "not investment advice or a trading signal" in report
    assert "Bullish" not in report
