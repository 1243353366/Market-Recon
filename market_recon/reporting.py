from __future__ import annotations

import pandas as pd


def calculate_sma(series: pd.Series, window: int = 20) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()


def calculate_ema(series: pd.Series, span: int = 20) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram


def calculate_atr(frame: pd.DataFrame, period: int = 14) -> pd.Series:
    high = frame["High"]
    low = frame["Low"]
    close = frame["Close"]
    prev_close = close.shift(1)
    true_range = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return true_range.rolling(window=period, min_periods=1).mean()


def summarize_technical_metrics(frame: pd.DataFrame) -> dict[str, float]:
    close = pd.to_numeric(frame["Close"], errors="coerce")
    sma_20 = calculate_sma(close, 20).iloc[-1]
    ema_20 = calculate_ema(close, 20).iloc[-1]
    rsi = calculate_rsi(close, 14).iloc[-1]
    macd, signal, histogram = calculate_macd(close)
    atr = calculate_atr(frame, 14).iloc[-1]

    return {
        "sma_20": float(sma_20),
        "ema_20": float(ema_20),
        "rsi_14": float(rsi),
        "macd": float(macd.iloc[-1]),
        "signal": float(signal.iloc[-1]),
        "histogram": float(histogram.iloc[-1]),
        "atr_14": float(atr),
    }
