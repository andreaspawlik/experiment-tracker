"""Evaluate whether a coordinated pull request may merge."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def evaluate_gate(state: dict[str, Any], pull_request_number: int) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if state.get("developer_pr") != pull_request_number:
        failures.append("coordinator PR does not match pull request")
    if state.get("architect_status") != "validated":
        failures.append("Architect validation is not complete")
    if state.get("ci_status") != "passed":
        failures.append("CI has not passed")
    if state.get("review_status") != "approved":
        failures.append("Reviewer approval is not recorded")
    if state.get("next_action") != "merge":
        failures.append("coordinator state is not ready to merge")
    if state.get("repair_iterations", 0) > state.get("max_repair_iterations", 0):
        failures.append("repair limit has been exceeded")
    return not failures, failures


def main() -> None:
    state = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    allowed, failures = evaluate_gate(state, int(sys.argv[2]))
    print(json.dumps({"allowed": allowed, "failures": failures}))
    raise SystemExit(0 if allowed else 1)


if __name__ == "__main__":
    main()
