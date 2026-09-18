"""Record a closed pull request in the acceptance metrics log."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 3
IGNORED_LABELS = {"backlog", "epic", "needs-review"}
REJECTION_REASON_LABELS = {
    "acceptance-gap",
    "missing-tests",
    "regression",
    "ci-failure",
    "scope-creep",
    "documentation-gap",
    "merge-conflict",
    "edge-case-gap",
}


def load_event(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as event_file:
        return json.load(event_file)


def build_record(event: dict[str, Any]) -> dict[str, Any]:
    pull_request = event["pull_request"]
    label_names = {label["name"] for label in pull_request.get("labels", [])}
    labels = sorted(
        label_name
        for label_name in label_names
        if label_name not in IGNORED_LABELS
        and label_name not in REJECTION_REASON_LABELS
    )
    reasons = sorted(label_names & REJECTION_REASON_LABELS)
    return {
        "pr_number": pull_request["number"],
        "title": pull_request["title"],
        "category": labels[0] if labels else "uncategorized",
        "rejection_reasons": reasons if not pull_request.get("merged", False) else [],
        "remediation_reasons": reasons if pull_request.get("merged", False) else [],
        "merged": bool(pull_request.get("merged", False)),
        "closed_at": pull_request["closed_at"],
        "head_sha": pull_request["head"]["sha"],
    }


def record_outcome(event_path: Path, metrics_path: Path) -> None:
    event = load_event(event_path)
    record = build_record(event)

    if metrics_path.exists():
        with metrics_path.open(encoding="utf-8") as metrics_file:
            metrics = json.load(metrics_file)
    else:
        metrics = {"schema_version": SCHEMA_VERSION, "records": []}

    for existing in metrics["records"]:
        reasons = existing.pop("rejection_reasons", [])
        existing["rejection_reasons"] = reasons if not existing["merged"] else []
        existing.setdefault("remediation_reasons", reasons if existing["merged"] else [])

    records = [
        existing
        for existing in metrics["records"]
        if existing["pr_number"] != record["pr_number"]
    ]
    records.append(record)
    records.sort(key=lambda item: item["pr_number"])
    metrics["schema_version"] = SCHEMA_VERSION
    metrics["records"] = records

    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("w", encoding="utf-8") as metrics_file:
        json.dump(metrics, metrics_file, indent=2)
        metrics_file.write("\n")


if __name__ == "__main__":
    record_outcome(Path(sys.argv[1]), Path(sys.argv[2]))
