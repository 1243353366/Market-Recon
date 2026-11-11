from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "investors" / "investors.json"


def load_investors(path: str | Path = DATASET_PATH) -> list[dict[str, Any]]:
    """Load curated investor profiles; no third-party scraping or holdings inference."""
    with Path(path).open("r", encoding="utf-8") as source:
        records = json.load(source)
    if not isinstance(records, list):
        raise ValueError("Investor catalog must be a JSON list")
    seen: set[str] = set()
    for record in records:
        if not record.get("id") or record["id"] in seen:
            raise ValueError("Investor records require unique, non-empty ids")
        if not record.get("name") or not record.get("source_url", "").startswith("https://"):
            raise ValueError(f"Investor record {record.get('id')} needs a name and HTTPS source URL")
        seen.add(record["id"])
    return records


def search_investors(query: str, category: str | None = None) -> list[dict[str, Any]]:
    """Case-insensitive catalog search over names, category, strategy, and research notes."""
    terms = [term for term in query.casefold().split() if term]
    results = []
    for record in load_investors():
        if category and record["category"].casefold() != category.casefold():
            continue
        haystack = " ".join(str(record.get(field, "")) for field in ("name", "category", "strategy", "research_note")).casefold()
        if all(term in haystack for term in terms):
            results.append(record)
    return results


def categories() -> list[str]:
    return sorted({record["category"] for record in load_investors()})
