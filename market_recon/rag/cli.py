from __future__ import annotations

import argparse
import json
import os
from typing import Any

from .pipeline import create_store, ingest_documents, load_jsonl_documents
from .sec_edgar import SecEdgarClient, filing_forms


def main() -> None:
    parser = argparse.ArgumentParser(description="Market Recon public-document RAG tools")
    sub = parser.add_subparsers(dest="command", required=True)

    sec = sub.add_parser("ingest-sec", help="Download and index recent SEC filings for a ticker")
    sec.add_argument("--ticker", required=True)
    sec.add_argument("--forms", nargs="*", default=sorted(filing_forms()))
    sec.add_argument("--limit", type=int, default=20)

    local = sub.add_parser("ingest-jsonl", help="Index normalized documents from JSON Lines")
    local.add_argument("path")

    search = sub.add_parser("search", help="Search indexed documents with citations")
    search.add_argument("query")
    search.add_argument("--ticker")
    search.add_argument("--form")
    search.add_argument("--limit", type=int, default=8)

    parser.add_argument("--model", default=os.getenv("MARKET_RECON_EMBEDDING_MODEL", "BAAI/bge-m3"))
    parser.add_argument("--qdrant-path", default=os.getenv("QDRANT_PATH", "data/qdrant"))
    parser.add_argument("--qdrant-url", default=os.getenv("QDRANT_URL"))
    parser.add_argument("--qdrant-api-key", default=os.getenv("QDRANT_API_KEY"))
    args = parser.parse_args()

    store = create_store(args.model, args.qdrant_path, args.qdrant_url, args.qdrant_api_key)
    if args.command == "ingest-sec":
        client = SecEdgarClient(os.getenv("SEC_USER_AGENT", ""))
        docs = client.recent_filings(args.ticker, set(args.forms), args.limit)
        count = ingest_documents(docs, store)
        print(json.dumps({"documents": len(docs), "chunks_indexed": count}, indent=2))
    elif args.command == "ingest-jsonl":
        count = ingest_documents(load_jsonl_documents(args.path), store)
        print(json.dumps({"chunks_indexed": count}, indent=2))
    else:
        filters: dict[str, Any] = {}
        if args.ticker:
            filters["ticker"] = args.ticker.upper()
        if args.form:
            filters["document_type"] = args.form
        hits = store.search(args.query, limit=args.limit, filters=filters)
        for number, hit in enumerate(hits, start=1):
            metadata = hit.metadata
            print(f"[{number}] {metadata.get('title', hit.document_id)} — {metadata.get('source_name')} ({metadata.get('published_at') or 'date unknown'})")
            print(f"    {metadata.get('source_url', '')}")
            print(f"    {hit.text[:700]}{'…' if len(hit.text) > 700 else ''}\n")


if __name__ == "__main__":
    main()
