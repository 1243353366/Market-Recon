from __future__ import annotations

from typing import Any


def build_company_report(symbol: str, snapshot: dict[str, Any], metrics: dict[str, float]) -> str:
    """Render a market-data summary without presenting technical metrics as a buy/sell signal."""
    company = snapshot.get("company", symbol.upper())
    return f"""# {company} ({symbol.upper()})

> Educational research summary only. This is not investment advice or a trading signal.

## Business overview
- Company: {company}
- Sector: {snapshot.get('sector', 'Unknown')}
- Industry: {snapshot.get('industry', 'Unknown')}
- Data status: {snapshot.get('data_status', 'source and retrieval metadata not supplied')}

## Technical metrics
- SMA(20): {metrics['sma_20']:.2f}
- EMA(20): {metrics['ema_20']:.2f}
- RSI(14): {metrics['rsi_14']:.2f}
- MACD: {metrics['macd']:.4f}
- MACD signal: {metrics['signal']:.4f}
- MACD histogram: {metrics['histogram']:.4f}
- ATR(14): {metrics['atr_14']:.4f}

## Limitations and risk notes
- Indicators summarize historical prices and do not predict future returns.
- Validate all data, dates, adjustments, and source provenance independently.
- Review company filings, financial statements, and risks before drawing conclusions.
"""
