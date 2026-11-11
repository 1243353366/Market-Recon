from __future__ import annotations

import pandas as pd


def _validate_period(period: int, name: str) -> None:
    if period < 1:
        raise ValueError(f"{name} must be a positive integer")


def calculate_sma(series: pd.Series, window: int = 20) -> pd.Series:
    _validate_period(window, "window")
    return series.rolling(window=window, min_periods=1).mean()


def calculate_ema(series: pd.Series, span: int = 20) -> pd.Series:
    _validate_period(span, "span")
    return series.ewm(span=span, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Wilder-smoothed RSI; flat series resolves to 50, zero-loss gains to 100."""
    _validate_period(period, "period")
    values = pd.to_numeric(series, errors="coerce")
    delta = values.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    average_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    average_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    ratio = average_gain / average_loss.replace(0, float("nan"))
    rsi = 100 - 100 / (1 + ratio)
    rsi = rsi.mask((average_loss == 0) & (average_gain > 0), 100)
    rsi = rsi.mask((average_loss == 0) & (average_gain == 0), 50)
    return rsi.fillna(50)


def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    for value, name in ((fast, "fast"), (slow, "slow"), (signal, "signal")):
        _validate_period(value, name)
    if fast >= slow:
        raise ValueError("fast period must be smaller than slow period")
    macd = calculate_ema(series, fast) - calculate_ema(series, slow)
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line, macd - signal_line


def calculate_atr(frame: pd.DataFrame, period: int = 14) -> pd.Series:
    _validate_period(period, "period")
    required = {"High", "Low", "Close"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing OHLC columns: {', '.join(sorted(missing))}")
    high, low, close = (pd.to_numeric(frame[key], errors="coerce") for key in ("High", "Low", "Close"))
    previous_close = close.shift(1)
    true_range = pd.concat([(high - low).abs(), (high - previous_close).abs(), (low - previous_close).abs()], axis=1).max(axis=1)
    # Wilder smoothing is the standard ATR recurrence, matching calculate_rsi.
    atr = pd.Series(float("nan"), index=true_range.index, dtype=float)
    if len(true_range) < period:
        return atr
    first = period - 1
    atr.iloc[first] = true_range.iloc[:period].mean()
    for index in range(first + 1, len(true_range)):
        atr.iloc[index] = (atr.iloc[index - 1] * (period - 1) + true_range.iloc[index]) / period
    return atr


def summarize_technical_metrics(frame: pd.DataFrame) -> dict[str, float]:
    if frame.empty or "Close" not in frame:
        raise ValueError("Price frame must contain at least one Close value")
    close = pd.to_numeric(frame["Close"], errors="coerce").dropna()
    if close.empty:
        raise ValueError("Close column has no numeric values")
    clean = frame.loc[close.index].copy()
    clean["Close"] = close
    has_ohlc = {"High", "Low"}.issubset(clean.columns)
    macd, signal, histogram = calculate_macd(close)
    values = {
        "sma_20": calculate_sma(close, 20).iloc[-1],
        "ema_20": calculate_ema(close, 20).iloc[-1],
        "rsi_14": calculate_rsi(close, 14).iloc[-1],
        "macd": macd.iloc[-1],
        "signal": signal.iloc[-1],
        "histogram": histogram.iloc[-1],
    }
    if has_ohlc:
        values["atr_14"] = calculate_atr(clean, 14).iloc[-1]
    return {key: float(value) for key, value in values.items()}
