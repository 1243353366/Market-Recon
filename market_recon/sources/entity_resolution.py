from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

MatchMethod = Literal[
    "exact_cik",
    "exact_ticker",
    "exact_recipient_id",
    "normalized_legal_name",
    "unresolved",
]

MatchStatus = Literal["confirmed", "probable", "unresolved"]

_COMMON_AMBIGUOUS_NAMES = {
    "capital", "holdings", "management", "investments", "acquisition corp",
    "technologies", "services", "partners", "enterprises", "solutions",
}

_STRIP_SUFFIXES = re.compile(
    r"\b(inc|incorporated|corp|corporation|llc|ltd|limited|co|company|group|holdings|plc|lp)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EntityResolutionResult:
    entity_id: str | None
    canonical_name: str
    match_method: MatchMethod
    confidence: float  # 0.0 to 1.0
    status: MatchStatus
    stable_identifiers: dict[str, str]
    notes: str = ""

    @property
    def is_resolved(self) -> bool:
        return self.status in ("confirmed", "probable") and self.entity_id is not None


def normalize_entity_name(name: str) -> str:
    cleaned = _STRIP_SUFFIXES.sub("", name)
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip().casefold()


class EntityResolver:
    """Deterministic entity resolver relying on stable identifiers first, then legal name matching.

    Rejects forced linking on generic/ambiguous names to prevent false corroboration.
    """

    def __init__(self, known_registry: dict[str, dict[str, str]] | None = None) -> None:
        # Map normalized name or ticker -> {"entity_id": ..., "canonical_name": ..., "cik": ...}
        self.registry = known_registry or {}

    def register(self, entity_id: str, canonical_name: str, ticker: str | None = None, cik: str | None = None) -> None:
        entry = {"entity_id": entity_id, "canonical_name": canonical_name}
        if ticker:
            entry["ticker"] = ticker.upper()
            self.registry[f"ticker:{ticker.upper()}"] = entry
        if cik:
            clean_cik = cik.lstrip("0")
            entry["cik"] = cik.zfill(10)
            self.registry[f"cik:{clean_cik}"] = entry
        norm = normalize_entity_name(canonical_name)
        if norm and norm not in _COMMON_AMBIGUOUS_NAMES:
            self.registry[f"name:{norm}"] = entry

    def resolve(
        self,
        name: str | None = None,
        ticker: str | None = None,
        cik: str | None = None,
        recipient_id: str | None = None,
    ) -> EntityResolutionResult:
        stable_ids: dict[str, str] = {}

        # 1. Authoritative SEC CIK
        if cik and cik.strip():
            clean_cik = cik.strip().lstrip("0")
            stable_ids["cik"] = cik.strip().zfill(10)
            entry = self.registry.get(f"cik:{clean_cik}")
            canonical = entry["canonical_name"] if entry else (name.strip() if name else f"CIK {cik}")
            entity_id = entry["entity_id"] if entry else f"entity:sec:cik:{cik.strip().zfill(10)}"
            return EntityResolutionResult(
                entity_id=entity_id,
                canonical_name=canonical,
                match_method="exact_cik",
                confidence=1.0,
                status="confirmed",
                stable_identifiers=stable_ids,
                notes="Matched via authoritative SEC Central Index Key (CIK)",
            )

        # 2. Authoritative Exchange Ticker
        if ticker and ticker.strip():
            norm_ticker = ticker.strip().upper()
            stable_ids["ticker"] = norm_ticker
            entry = self.registry.get(f"ticker:{norm_ticker}")
            if entry:
                return EntityResolutionResult(
                    entity_id=entry["entity_id"],
                    canonical_name=entry["canonical_name"],
                    match_method="exact_ticker",
                    confidence=1.0,
                    status="confirmed",
                    stable_identifiers=stable_ids,
                    notes=f"Matched via registered ticker {norm_ticker}",
                )

        # 3. Government / External Recipient ID
        if recipient_id and recipient_id.strip():
            clean_id = recipient_id.strip()
            stable_ids["recipient_id"] = clean_id
            return EntityResolutionResult(
                entity_id=f"entity:gov:{clean_id}",
                canonical_name=name.strip() if name else f"Recipient {clean_id}",
                match_method="exact_recipient_id",
                confidence=1.0,
                status="confirmed",
                stable_identifiers=stable_ids,
                notes="Matched via unique government award recipient identifier (UEI/DUNS)",
            )

        # 4. Normalized Legal Name Check
        if name and name.strip():
            norm_name = normalize_entity_name(name)
            if not norm_name or norm_name in _COMMON_AMBIGUOUS_NAMES:
                # Ambiguous or generic name without stable identifier: do NOT force a link!
                return EntityResolutionResult(
                    entity_id=None,
                    canonical_name=name.strip(),
                    match_method="unresolved",
                    confidence=0.0,
                    status="unresolved",
                    stable_identifiers=stable_ids,
                    notes="Generic or ambiguous legal name; unlinked to prevent false cross-entity links",
                )

            entry = self.registry.get(f"name:{norm_name}")
            if entry:
                return EntityResolutionResult(
                    entity_id=entry["entity_id"],
                    canonical_name=entry["canonical_name"],
                    match_method="normalized_legal_name",
                    confidence=0.95,
                    status="confirmed",
                    stable_identifiers=stable_ids,
                    notes="Matched via normalized corporate legal name",
                )

        # Fallback: unresolved
        return EntityResolutionResult(
            entity_id=None,
            canonical_name=name.strip() if name else "Unresolved Entity",
            match_method="unresolved",
            confidence=0.0,
            status="unresolved",
            stable_identifiers=stable_ids,
            notes="No stable identifier and no registered name match; requires manual analyst review",
        )
