from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable

from .filing_diff import FilingVersion


@dataclass(frozen=True)
class FilingFinding:
    category: str
    change: str
    section: str
    text: str
    before_url: str
    after_url: str
    before_filing_date: str
    after_filing_date: str
    method: str = "heuristic text-diff classification; human verification required"


# Rules are intentionally transparent. They surface candidate changed lines only;
# they do not establish materiality, legal status, causation, or business impact.
_RULES: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    ("risks", ("risk factor", "material adverse", "could adversely", "uncertaint", "exposure to", "may adversely", "could negatively"), ("item 1a", "risk factor")),
    ("executive_changes", ("chief executive", "chief financial", "chief operating", "ceo", "cfo", "coo", "appointed", "resigned", "retired", "departure", "successor", "executive officer", "director nominee"), ("executive", "management", "item 10", "item 5")),
    ("compensation_changes", ("compensation", "remuneration", "salary", "incentive plan", "performance award", "equity award", "stock option", "bonus", "pay ratio", "clawback"), ("compensation", "item 11", "executive compensation")),
    ("supply_chain_changes", ("supply chain", "supplier", "vendor", "sourcing", "manufactur", "component", "inventory", "logistics", "shipping", "procurement", "raw material", "capacity constraint"), ("supply", "item 1", "item 1a", "item 7")),
    ("litigation_changes", ("litigation", "legal proceeding", "lawsuit", "litigat", "claim", "settlement", "subpoena", "investigation", "regulatory proceeding", "court", "arbitration"), ("legal", "item 3", "item 1a", "item 8", "litigation")),
)


def _normalize(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def _changed_lines(before: str, after: str) -> tuple[list[str], list[str]]:
    old_lines = [_normalize(line) for line in before.splitlines() if _normalize(line)]
    new_lines = [_normalize(line) for line in after.splitlines() if _normalize(line)]
    added: list[str] = []
    removed: list[str] = []
    for tag, i1, i2, j1, j2 in SequenceMatcher(a=old_lines, b=new_lines, autojunk=False).get_opcodes():
        if tag in ("replace", "delete"):
            removed.extend(old_lines[i1:i2])
        if tag in ("replace", "insert"):
            added.extend(new_lines[j1:j2])
    return added, removed


def _matches(category: str, section: str, line: str) -> bool:
    rule = next(rule for rule in _RULES if rule[0] == category)
    normalized = f"{section} {line}".casefold()
    keywords, section_hints = rule[1], rule[2]
    return any(keyword in normalized for keyword in keywords) or any(hint in section.casefold() for hint in section_hints)


def classify_filing_changes(before: FilingVersion, after: FilingVersion) -> list[FilingFinding]:
    """Surface candidate new/removed risk, executive, compensation, supply-chain and litigation text.

    This rule-based layer analyzes section text already extracted from filings. It can
    miss semantic changes and produce false positives (for example boilerplate or
    sentence reflow). Findings preserve both original filing URLs and dates.
    """
    if before.cik.lstrip("0") != after.cik.lstrip("0"):
        raise ValueError("Cannot compare filings for different CIKs")
    if before.form.upper().removesuffix("/A") != after.form.upper().removesuffix("/A"):
        raise ValueError("Cannot compare different base filing forms")
    findings: list[FilingFinding] = []
    for section in sorted(set(before.sections) | set(after.sections)):
        added, removed = _changed_lines(before.sections.get(section, ""), after.sections.get(section, ""))
        for category, _, _ in _RULES:
            for change, lines in (("new", added), ("removed", removed)):
                for line in lines:
                    if _matches(category, section, line):
                        findings.append(FilingFinding(
                            category=category,
                            change=change,
                            section=section,
                            text=line,
                            before_url=before.source_url,
                            after_url=after.source_url,
                            before_filing_date=before.filing_date,
                            after_filing_date=after.filing_date,
                        ))
    # Stable deduplication: repeated identical lines are still one review item per section/category/change.
    unique: dict[tuple[str, str, str, str], FilingFinding] = {}
    for finding in findings:
        unique[(finding.category, finding.change, finding.section, finding.text)] = finding
    return sorted(unique.values(), key=lambda item: (item.category, item.section, item.change, item.text))


def summarize_filing_changes(before: FilingVersion, after: FilingVersion) -> dict[str, list[FilingFinding]]:
    """Return all requested review categories, including empty lists for no detected changes."""
    categories = ("risks", "executive_changes", "compensation_changes", "supply_chain_changes", "litigation_changes")
    grouped: dict[str, list[FilingFinding]] = {category: [] for category in categories}
    for finding in classify_filing_changes(before, after):
        grouped[finding.category].append(finding)
    return grouped
