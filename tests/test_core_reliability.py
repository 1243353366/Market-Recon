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


def test_atr_requires_real_ohlc_and_uses_wilder_smoothing() -> None:
    from market_recon.technical_analysis import calculate_atr

    close_only = pd.DataFrame({"Close": [100.0] * 20})
    metrics = summarize_technical_metrics(close_only)
    assert "atr_14" not in metrics
    with pytest.raises(ValueError, match="Missing OHLC columns"):
        calculate_atr(close_only)

    frame = pd.DataFrame({
        "High": [11.0, 13.0, 14.0, 15.0],
        "Low": [9.0, 10.0, 12.0, 13.0],
        "Close": [10.0, 12.0, 13.0, 14.0],
    })
    atr = calculate_atr(frame, period=3)
    # True ranges are [2, 3, 2, 2]; seed with their 3-period mean, then Wilder-update.
    assert atr.iloc[2] == pytest.approx(7 / 3)
    assert atr.iloc[3] == pytest.approx((2 * (7 / 3) + 2) / 3)
