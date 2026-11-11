from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

from .loader import load_adapters
from .storage import write_records


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch public source records and store normalized outputs")
    parser.add_argument("--config", default="config/sources.example.json")
    parser.add_argument("--source", required=True, choices=("sec_edgar", "fred", "usaspending", "quiver_quant", "yahoo_finance", "stooq"))
    parser.add_argument("--params", required=True, help="JSON object of adapter fetch parameters; use ISO dates")
    parser.add_argument("--format", choices=("json", "csv", "sqlite"), default="sqlite")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        params: dict[str, Any] = json.loads(args.params)
    except json.JSONDecodeError as exc:
        parser.error(f"--params must be valid JSON: {exc}")
    if not isinstance(params, dict):
        parser.error("--params must decode to a JSON object")
    for key in ("start_date", "end_date"):
        if key in params:
            params[key] = _parse_date(params[key])

    adapters = load_adapters(args.config)
    if args.source not in adapters:
        parser.error(f"source {args.source!r} is not enabled in {args.config}")
    records = adapters[args.source].fetch(**params)
    written = write_records(records, args.output, args.format)
    print(json.dumps({"source": args.source, "records": len(records), "written": written, "format": args.format, "output": str(Path(args.output))}, indent=2))


if __name__ == "__main__":
    main()
