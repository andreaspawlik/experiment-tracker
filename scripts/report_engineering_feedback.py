"""Report acceptance outcomes and recurring rejection reasons."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def summarize_feedback(
    metrics_path: Path, experiments_path: Path
) -> dict[str, Any]:
    metrics = load_json(metrics_path)
    records = metrics["records"]

    grouped: dict[str, list[bool]] = defaultdict(list)
    rejected_reasons: Counter[str] = Counter()
    remediated_reasons: Counter[str] = Counter()
    for record in records:
        grouped[record["category"]].append(record["merged"])
        if not record["merged"]:
            rejected_reasons.update(record.get("rejection_reasons", []))
        remediated_reasons.update(record.get("remediation_reasons", []))

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
        "rejected_by_reason": dict(sorted(rejected_reasons.items())),
        "remediated_by_reason": dict(sorted(remediated_reasons.items())),
        "experiments": load_json(experiments_path)["experiments"],
    }


if __name__ == "__main__":
    print(
        json.dumps(
            summarize_feedback(Path(sys.argv[1]), Path(sys.argv[2])), indent=2
        )
    )
