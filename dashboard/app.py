from __future__ import annotations

import argparse
from pathlib import Path

from .data_sources import fetch_company_snapshot, fetch_price_history
from .reporting import build_company_report
from .technical_analysis import summarize_technical_metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Market Recon CLI")
    parser.add_argument("--symbol", default="AAPL", help="Ticker symbol to analyze")
    parser.add_argument("--period", default="180d", help="Lookback period for price data")
    parser.add_argument("--report", action="store_true", help="Emit a Markdown research report")
    parser.add_argument("--output", type=Path, default=None, help="Optional output path for the report")
    args = parser.parse_args()

    snapshot = fetch_company_snapshot(args.symbol)
    frame = fetch_price_history(args.symbol, period=args.period)
    metrics = summarize_technical_metrics(frame)
    report = build_company_report(args.symbol, snapshot, metrics)

    if args.report:
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report, encoding="utf-8")
            print(f"Report written to {args.output}")
        else:
            print(report)
    else:
        print(f"Symbol: {args.symbol}")
        print(f"Snapshot: {snapshot}")
        print(f"Technical metrics: {metrics}")


if __name__ == "__main__":
    main()
