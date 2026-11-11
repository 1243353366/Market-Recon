from __future__ import annotations

import argparse
import json
import os

from market_recon.rag.pipeline import create_store
from market_recon.rag.sec_edgar import SecEdgarClient
from market_recon.sources.sec_filing_workflow import FilingVersionStore, SecFilingWorkflow, compare_latest_filings


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse, chunk, index, and compare public SEC 10-K/10-Q filings")
    sub = parser.add_subparsers(dest="command", required=True)
    ingest = sub.add_parser("ingest", help="Fetch filings, parse sections, chunk, index, and archive versions")
    ingest.add_argument("--ticker", required=True)
    ingest.add_argument("--form", choices=("10-K", "10-Q"), default="10-K")
    ingest.add_argument("--limit", type=int, default=10)
    compare = sub.add_parser("compare", help="Compare the two latest archived parsed filings")
    compare.add_argument("--ticker", required=True)
    compare.add_argument("--form", choices=("10-K", "10-Q"), default="10-K")
    for command in (ingest, compare):
        command.add_argument("--database", default=os.getenv("MARKET_RECON_DB", "data/market.db"))
    ingest.add_argument("--model", default=os.getenv("MARKET_RECON_EMBEDDING_MODEL", "BAAI/bge-m3"))
    ingest.add_argument("--qdrant-path", default=os.getenv("QDRANT_PATH", "data/qdrant"))
    ingest.add_argument("--qdrant-url", default=os.getenv("QDRANT_URL"))
    ingest.add_argument("--qdrant-api-key", default=os.getenv("QDRANT_API_KEY"))

    args = parser.parse_args()
    if args.command == "ingest" and args.limit < 1:
        parser.error("--limit must be positive")

    versions = FilingVersionStore(args.database)
    if args.command == "ingest":
        user_agent = os.getenv("SEC_USER_AGENT", "")
        if not user_agent:
            parser.error("Set SEC_USER_AGENT to an identifying application name and contact email")
        index = create_store(args.model, args.qdrant_path, args.qdrant_url, args.qdrant_api_key)
        workflow = SecFilingWorkflow(SecEdgarClient(user_agent), index, versions)
        print(json.dumps(workflow.ingest(args.ticker, args.form, args.limit).__dict__, indent=2))
    else:
        # Comparison only needs SQLite; avoid loading large embedding models or Qdrant.
        print(json.dumps(compare_latest_filings(versions, args.ticker, args.form), indent=2))


if __name__ == "__main__":
    main()
