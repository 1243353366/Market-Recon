from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher, unified_diff
from typing import Mapping


@dataclass(frozen=True)
class FilingVersion:
    """Parsed filing version with source-citable section text."""

    cik: str
    form: str
    filing_date: str
    source_url: str
    sections: Mapping[str, str]

    def __post_init__(self) -> None:
        if not self.cik.strip():
            raise ValueError("cik is required")
        if self.form.upper() not in {"10-K", "10-Q", "10-K/A", "10-Q/A"}:
            raise ValueError("Only 10-K/10-Q filings and amendments can be compared")
        if not self.source_url.startswith("https://"):
            raise ValueError("source_url must be HTTPS")
        if not self.filing_date.strip():
            raise ValueError("filing_date is required")


@dataclass(frozen=True)
class SectionChange:
    section: str
    status: str
    similarity: float
    before_excerpt: str
    after_excerpt: str
    unified_diff: str
    before_url: str
    after_url: str


def compare_filing_versions(
    before: FilingVersion,
    after: FilingVersion,
    *,
    excerpt_chars: int = 1200,
    context_lines: int = 2,
) -> list[SectionChange]:
    """Compare same-company 10-K/10-Q sections, returning text differences and citations.

    This is a deterministic change inventory, not a materiality, sentiment, fraud,
    or investment-signal assessment. Filing amendments and presentation changes can
    generate large differences; users must validate every excerpt against sources.
    """
    if before.cik.lstrip("0") != after.cik.lstrip("0"):
        raise ValueError("Cannot compare filings for different CIKs")
    if before.form.upper().removesuffix("/A") != after.form.upper().removesuffix("/A"):
        raise ValueError("Cannot compare different base filing forms")
    if excerpt_chars < 1 or context_lines < 0:
        raise ValueError("excerpt_chars must be positive and context_lines non-negative")
    changes: list[SectionChange] = []
    for section in sorted(set(before.sections) | set(after.sections)):
        old = _normalize(before.sections.get(section, ""))
        new = _normalize(after.sections.get(section, ""))
        if old == new:
            continue
        if not old:
            status = "added"
        elif not new:
            status = "removed"
        else:
            status = "changed"
        diff = "\n".join(unified_diff(
            old.splitlines(), new.splitlines(),
            fromfile=f"{before.form} {before.filing_date} {section}",
            tofile=f"{after.form} {after.filing_date} {section}",
            n=context_lines,
            lineterm="",
        ))
        changes.append(SectionChange(
            section=section,
            status=status,
            similarity=SequenceMatcher(a=old, b=new, autojunk=False).ratio() if old and new else 0.0,
            before_excerpt=old[:excerpt_chars],
            after_excerpt=new[:excerpt_chars],
            unified_diff=diff[: excerpt_chars * 4],
            before_url=before.source_url,
            after_url=after.source_url,
        ))
    return changes


def _normalize(text: str) -> str:
    return "\n".join(" ".join(line.split()) for line in text.splitlines() if line.strip())
