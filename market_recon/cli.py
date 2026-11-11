from __future__ import annotations

from typing import Any


def build_company_report(symbol: str, snapshot: dict[str, Any], metrics: dict[str, float]) -> str:
    trend = "Bullish" if metrics["macd"] > metrics["signal"] and metrics["rsi_14"] > 50 else "Cautious"
    report = f"""# {snapshot.get('company', symbol.upper())} ({symbol.upper()})

## Business overview
{snapshot.get('company', symbol.upper())} operates in the {snapshot.get('industry', 'Unknown')} industry within the {snapshot.get('sector', 'Unknown')} sector.

## Financial and market snapshot
- Market cap: ${snapshot.get('market_cap', 0):,.0f}
- Sector: {snapshot.get('sector', 'Unknown')}
- Industry: {snapshot.get('industry', 'Unknown')}

## Technical view
- SMA(20): ${metrics['sma_20']:.2f}
- EMA(20): ${metrics['ema_20']:.2f}
- RSI(14): {metrics['rsi_14']:.2f}
- MACD: {metrics['macd']:.2f}
- Signal: {metrics['signal']:.2f}
- ATR(14): {metrics['atr_14']:.2f}
- Overall trend: {trend}

## Investment thesis
The company is currently showing a {trend.lower()} technical setup based on public market data and valuation context. This report is educational and should be used with additional fundamental and risk analysis.

## Risk notes
- Validate source provenance for all calculations.
- Cross-check price action against earnings, filings, and news catalysts.
- Distinguish reported financials from estimates and third-party aggregations.

## Sources
- Public market data and source metadata should be recorded for every report.
- SEC filings, company disclosures, and public earnings sources should be reviewed before making conclusions.
"""
    return report
