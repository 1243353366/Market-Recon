from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class ParsedSecFiling:
    form: str
    sections: dict[str, str]
    full_text: str


_ITEM_HEADING = re.compile(
    r"^\s*(?:PART\s+([IVX]+)\s+)?ITEM\s+(\d+[A-Z]?)\b\s*[.\-: ]*\s*(.*?)\s*$",
    re.IGNORECASE,
)
_PART_HEADING = re.compile(r"^\s*PART\s+([IVX]+)\b\s*$", re.IGNORECASE)


def html_to_text(content: str | bytes) -> str:
    """Convert SEC filing HTML into line-preserving text, dropping executable/style markup."""
    soup = BeautifulSoup(content, "html.parser")
    for node in soup(["script", "style", "ix:header", "ix:hidden"]):
        node.decompose()
    return "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())


def parse_10k_10q(text: str, form: str) -> ParsedSecFiling:
    """Extract common 10-K/10-Q Item sections from filing text.

    This rule-based parser preserves the full text and chooses the longest occurrence
    when a section heading appears in both a table of contents and the filing body.
    Filing layouts vary, so consumers should review the returned excerpts against the
    linked original filing. It is not a substitute for XBRL or legal-grade parsing.
    """
    normalized_form = form.upper().strip()
    if normalized_form not in {"10-K", "10-Q"}:
        raise ValueError("Only 10-K and 10-Q forms are supported")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections: dict[str, str] = {}
    headings: list[tuple[int, str, str]] = []
    current_part = ""
    for index, line in enumerate(lines):
        part_match = _PART_HEADING.match(line)
        if part_match:
            current_part = f"Part {part_match.group(1).upper()} "
            continue
        match = _ITEM_HEADING.match(line)
        if not match:
            continue
        explicit_part, item_number, title = match.groups()
        part = f"Part {explicit_part.upper()} " if explicit_part else current_part
        key = f"{part}Item {item_number.upper()}".strip()
        headings.append((index, key, title.strip()))

    # Keep candidate ranges and choose the richest occurrence for duplicated TOC/body headings.
    candidates: dict[str, list[str]] = {}
    for position, (start, key, title) in enumerate(headings):
        end = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
        body = "\n".join(lines[start + 1 : end]).strip()
        if title:
            body = f"{title}\n{body}".strip()
        if body:
            candidates.setdefault(key, []).append(body)
    for key, excerpts in candidates.items():
        sections[key] = max(excerpts, key=len)
    return ParsedSecFiling(form=normalized_form, sections=sections, full_text="\n".join(lines))
