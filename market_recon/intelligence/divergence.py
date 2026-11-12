from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable

from .models import PublicSignal, SignalDirection


@dataclass(frozen=True)
class SignalDivergence:
    entity_id: str
    entity_name: str
    window_start: date
    window_end: date
    positive_signal_count: int
    negative_signal_count: int
    signals: tuple[PublicSignal, ...]
    interpretation: str
    distinct_kind_count: int = 2
    distinct_source_count: int = 1
    divergence_caveat: str | None = None


def find_cross_signal_divergences(
    signals: Iterable[PublicSignal],
    *,
    as_of: date,
    window_days: int = 120,
    minimum_distinct_kinds: int = 2,
) -> list[SignalDivergence]:
    """Find mixed evidence clusters for research review; never score securities or infer causality.

    Signals are deduplicated by (entity_id, signal_id) to prevent duplicate evidence from
    fabricating false divergence clusters. Unknown/mixed directions are retained as context
    but do not count toward either side. Canonical entity name is selected from the most recent
    observation in the evaluation window.
    """
    if window_days < 1:
        raise ValueError("window_days must be positive")
    if minimum_distinct_kinds < 2:
        raise ValueError("minimum_distinct_kinds must be at least 2")

    start = as_of - timedelta(days=window_days)
    groups: dict[str, list[PublicSignal]] = defaultdict(list)
    seen_signals: set[tuple[str, str]] = set()

    for signal in signals:
        if not isinstance(signal, PublicSignal):
            raise TypeError("Each observation must be an instance of PublicSignal")
        sig_key = (signal.entity_id, signal.signal_id)
        if sig_key in seen_signals:
            continue
        seen_signals.add(sig_key)
        if start <= signal.observed_on <= as_of:
            groups[signal.entity_id].append(signal)

    results: list[SignalDivergence] = []
    for entity_id, observations in groups.items():
        directions: set[SignalDirection] = {item.direction for item in observations}
        kinds = {item.kind for item in observations}
        if not ({"positive", "negative"} <= directions and len(kinds) >= minimum_distinct_kinds):
            continue

        ordered = tuple(sorted(observations, key=lambda item: (item.observed_on, item.signal_id)))
        canonical_entity_name = ordered[-1].entity_name

        sources = {item.source_name for item in ordered}
        baselines = {item.baseline for item in ordered if item.baseline}

        caveats: list[str] = []
        if len(sources) < 2:
            caveats.append("All diverging signals originate from a single source; independent cross-source corroboration is absent.")
        if len(baselines) > 1:
            caveats.append(f"Signals reference heterogeneous baselines ({', '.join(sorted(baselines))}); metrics may not be directly comparable.")

        caveat_text = " ".join(caveats) if caveats else None
        base_interpretation = (
            "Mixed public observations warrant verification. Signals may use different definitions, "
            "periods, populations, and coverage; this is not evidence of deception, causation, "
            "future performance, or an investment recommendation."
        )
        full_interpretation = f"{base_interpretation} {caveat_text}".strip() if caveat_text else base_interpretation

        results.append(SignalDivergence(
            entity_id=entity_id,
            entity_name=canonical_entity_name,
            window_start=start,
            window_end=as_of,
            positive_signal_count=sum(item.direction == "positive" for item in ordered),
            negative_signal_count=sum(item.direction == "negative" for item in ordered),
            signals=ordered,
            interpretation=full_interpretation,
            distinct_kind_count=len(kinds),
            distinct_source_count=len(sources),
            divergence_caveat=caveat_text,
        ))

    return sorted(results, key=lambda result: result.entity_id)
