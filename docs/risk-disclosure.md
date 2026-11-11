from __future__ import annotations

from typing import Any


def sample_news_items() -> list[dict[str, Any]]:
    return [
        {
            "title": "Chip demand remains elevated across AI infrastructure suppliers",
            "source": "Public market coverage",
            "category": "Technology",
            "sentiment": "Positive",
        },
        {
            "title": "Software providers continue to report durable recurring revenue growth",
            "source": "Public market coverage",
            "category": "Software",
            "sentiment": "Neutral",
        },
        {
            "title": "Treasury yields remain a key macro input for equity valuation",
            "source": "Public market coverage",
            "category": "Macro",
            "sentiment": "Cautious",
        },
    ]
