"""Print acceptance rates from the pull request outcome log."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def summarize(metrics_path: Path) -> dict[str, Any]:
    with metrics_path.open(encoding="utf-8") as metrics_file:
        records = json.load(metrics_file)["records"]

    grouped: dict[str, list[bool]] = defaultdict(list)
    for record in records:
        grouped[record["category"]].append(record["merged"])

    def result(values: list[bool]) -> dict[str, Any]:
        accepted = sum(values)
        return {
            "closed": len(values),
            "accepted": accepted,
            "acceptance_rate": round(accepted / len(values), 4) if values else 0.0,
        }

    return {
        "overall": result([record["merged"] for record in records]),
        "categories": {
            category: result(values) for category, values in sorted(grouped.items())
        },
    }


if __name__ == "__main__":
    print(json.dumps(summarize(Path(sys.argv[1])), indent=2))
