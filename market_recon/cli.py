from __future__ import annotations

import argparse
from pathlib import Path

from .data_sources import fetch_company_snapshot, fetch_price_history
from .reporting import build_company_report
from .technical_analysis import summarize_technical_metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Market Recon public-market research CLI")
    parser.add_argument("--symbol", default="AAPL", help="Ticker symbol")
    parser.add_argument("--period", default="180d", help="Price-history lookback accepted by the data provider")
    parser.add_argument("--report", action="store_true", help="Print a Markdown research summary")
    parser.add_argument("--output", type=Path, help="Optional report output path")
    args = parser.parse_args()

    prices = fetch_price_history(args.symbol, period=args.period)
    metrics = summarize_technical_metrics(prices)
    snapshot = fetch_company_snapshot(args.symbol)
    if args.report or args.output:
        report = build_company_report(args.symbol, snapshot, metrics)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report, encoding="utf-8")
            print(f"Report written to {args.output}")
        else:
            print(report)
    else:
        print(f"Symbol: {args.symbol.upper()}\nSnapshot: {snapshot}\nMetrics: {metrics}")


if __name__ == "__main__":
    main()
