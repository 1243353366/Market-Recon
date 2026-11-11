from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

from market_recon.rag.chunking import chunk_document
from market_recon.rag.models import DocumentChunk, SourceDocument
from market_recon.rag.sec_edgar import SecEdgarClient
from market_recon.sources.filing_diff import FilingVersion
from market_recon.sources.filing_intelligence import summarize_filing_changes
from market_recon.sources.sec_parser import parse_10k_10q
from market_recon.sources.schema import utc_now_iso


class ChunkIndex(Protocol):
    def upsert(self, chunks: list[DocumentChunk], batch_size: int = 64) -> int: ...


@dataclass(frozen=True)
class IngestResult:
    documents: int
    sections: int
    chunks_indexed: int
    filing_dates: tuple[str, ...]


class FilingVersionStore:
    """Small SQLite archive of parsed filing versions used for reproducible comparisons."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS filing_versions (
                    document_id TEXT PRIMARY KEY,
                    cik TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    form TEXT NOT NULL,
                    filing_date TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    sections_json TEXT NOT NULL,
                    retrieved_at TEXT NOT NULL
                )
            """)
            connection.execute("CREATE INDEX IF NOT EXISTS idx_filing_versions_lookup ON filing_versions(cik, form, filing_date DESC)")

    def save(self, document_id: str, ticker: str, form: str, filing_date: str, cik: str, source_url: str, sections: dict[str, str]) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute("""
                INSERT INTO filing_versions VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    cik=excluded.cik, ticker=excluded.ticker, form=excluded.form,
                    filing_date=excluded.filing_date, source_url=excluded.source_url,
                    sections_json=excluded.sections_json, retrieved_at=excluded.retrieved_at
            """, (document_id, cik, ticker, form, filing_date, source_url,
                  json.dumps(sections, ensure_ascii=False), utc_now_iso()))

    def latest_pair(self, ticker: str, form: str, include_amendments: bool = True) -> tuple[FilingVersion, FilingVersion] | None:
        base_form = form.upper().removesuffix("/A")
        forms = (base_form, f"{base_form}/A") if include_amendments else (form.upper(),)
        placeholders = ", ".join("?" for _ in forms)
        with sqlite3.connect(self.path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                f"SELECT cik, form, filing_date, source_url, sections_json FROM filing_versions "
                f"WHERE ticker = ? AND form IN ({placeholders}) ORDER BY filing_date DESC, retrieved_at DESC, document_id DESC LIMIT 2",
                [ticker.upper(), *forms],
            ).fetchall()
        if len(rows) < 2:
            return None
        newer, older = rows[0], rows[1]
        return (
            FilingVersion(older["cik"], older["form"], older["filing_date"], older["source_url"], json.loads(older["sections_json"])),
            FilingVersion(newer["cik"], newer["form"], newer["filing_date"], newer["source_url"], json.loads(newer["sections_json"])),
        )


class SecFilingWorkflow:
    """10-K/10-Q workflow: fetch → parse → chunk → index → archive → compare → explain/cite."""

    def __init__(self, client: SecEdgarClient, index: ChunkIndex, versions: FilingVersionStore) -> None:
        self.client = client
        self.index = index
        self.versions = versions

    def ingest(self, ticker: str, form: str = "10-K", limit: int = 10) -> IngestResult:
        normalized_form = form.upper()
        if normalized_form not in {"10-K", "10-Q"}:
            raise ValueError("form must be 10-K or 10-Q")
        if limit < 1:
            raise ValueError("limit must be positive")
        documents = self.client.recent_filings(ticker, {normalized_form}, limit)
        all_chunks: list[DocumentChunk] = []
        section_count = 0
        dates: list[str] = []
        for document in documents:
            if not document.cik or not document.published_at:
                continue
            parsed = parse_10k_10q(document.text, normalized_form)
            if not parsed.sections:
                continue
            self.versions.save(
                document_id=document.document_id,
                ticker=ticker.upper(),
                form=normalized_form,
                filing_date=document.published_at,
                cik=document.cik,
                source_url=document.source_url,
                sections=parsed.sections,
            )
            dates.append(document.published_at)
            for section, text in parsed.sections.items():
                section_count += 1
                section_document = SourceDocument(
                    document_id=f"{document.document_id}:{section}",
                    title=f"{ticker.upper()} {normalized_form} {document.published_at} — {section}",
                    text=text,
                    source_name=document.source_name,
                    source_url=document.source_url,
                    document_type=normalized_form,
                    published_at=document.published_at,
                    retrieved_at=document.retrieved_at,
                    ticker=ticker.upper(),
                    cik=document.cik,
                    metadata={**document.metadata, "section": section, "workflow": "sec_filing_comparison"},
                )
                all_chunks.extend(chunk_document(section_document))
        chunks_indexed = self.index.upsert(all_chunks) if all_chunks else 0
        return IngestResult(len(documents), section_count, chunks_indexed, tuple(sorted(set(dates))))

    def compare_latest(self, ticker: str, form: str = "10-K") -> dict[str, object]:
        return compare_latest_filings(self.versions, ticker, form)


def compare_latest_filings(versions: FilingVersionStore, ticker: str, form: str = "10-K") -> dict[str, object]:
    """Compare archived filings without initializing an embedding or vector-store client."""
    pair = versions.latest_pair(ticker, form)
    if pair is None:
        raise LookupError(f"Need at least two indexed {form.upper()} filings for {ticker.upper()} to compare")
    before, after = pair
    grouped = summarize_filing_changes(before, after)
    result: dict[str, object] = {
        "ticker": ticker.upper(),
        "form": form.upper(),
        "before": {"filing_date": before.filing_date, "source_url": before.source_url},
        "after": {"filing_date": after.filing_date, "source_url": after.source_url},
        "method": "deterministic section text diff and transparent keyword/section heuristics",
        "limitations": "Candidate changes only; verify both filings. Absence from parsed text does not prove a risk or event ended.",
        "changes": {},
    }
    serialized: dict[str, list[dict[str, object]]] = {}
    for category, findings in grouped.items():
        serialized[category] = []
        for finding in findings:
            item = asdict(finding)
            item["explanation"] = (
                f"This {finding.change} text was surfaced because a changed line matched the "
                f"documented {category.replace('_', ' ')} keyword/section heuristic. It is not a verified conclusion."
            )
            serialized[category].append(item)
    result["changes"] = serialized
    return result
