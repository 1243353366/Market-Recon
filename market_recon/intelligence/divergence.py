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


def find_cross_signal_divergences(
    signals: Iterable[PublicSignal],
    *,
    as_of: date,
    window_days: int = 120,
    minimum_distinct_kinds: int = 2,
) -> list[SignalDivergence]:
    """Find mixed evidence clusters for research review; never score securities or infer causality.

    Signals are grouped by resolved entity ID and a fixed lookback window. Unknown/mixed
    directions are retained as context but do not count toward either side. Each output
    preserves all source-linked observations so users can inspect the evidence.
    """
    if window_days < 1:
        raise ValueError("window_days must be positive")
    if minimum_distinct_kinds < 2:
        raise ValueError("minimum_distinct_kinds must be at least 2")
    start = as_of - timedelta(days=window_days)
    groups: dict[str, list[PublicSignal]] = defaultdict(list)
    for signal in signals:
        if start <= signal.observed_on <= as_of:
            groups[signal.entity_id].append(signal)

    results: list[SignalDivergence] = []
    for entity_id, observations in groups.items():
        directions: set[SignalDirection] = {item.direction for item in observations}
        kinds = {item.kind for item in observations}
        if not ({"positive", "negative"} <= directions and len(kinds) >= minimum_distinct_kinds):
            continue
        ordered = tuple(sorted(observations, key=lambda item: (item.observed_on, item.signal_id)))
        results.append(SignalDivergence(
            entity_id=entity_id,
            entity_name=ordered[0].entity_name,
            window_start=start,
            window_end=as_of,
            positive_signal_count=sum(item.direction == "positive" for item in ordered),
            negative_signal_count=sum(item.direction == "negative" for item in ordered),
            signals=ordered,
            interpretation=(
                "Mixed public observations warrant verification. Signals may use different definitions, "
                "periods, populations, and coverage; this is not evidence of deception, causation, "
                "future performance, or an investment recommendation."
            ),
        ))
    return sorted(results, key=lambda result: result.entity_id)
