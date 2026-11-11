from __future__ import annotations

import argparse
import json
from pathlib import Path

from .scoring import load_cases, score_review_cases


def main() -> None:
    parser = argparse.ArgumentParser(description="Score AI code-review benchmark predictions")
    parser.add_argument("--cases", type=Path, default=Path("benchmark/cases.json"))
    parser.add_argument("--predictions", type=Path, required=True, help="JSON object keyed by benchmark case id")
    args = parser.parse_args()
    predictions = json.loads(args.predictions.read_text(encoding="utf-8"))
    if not isinstance(predictions, dict):
        parser.error("predictions file must be a JSON object")
    print(json.dumps(score_review_cases(load_cases(args.cases), predictions), indent=2))


if __name__ == "__main__":
    main()
