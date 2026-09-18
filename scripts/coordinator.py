"""Select eligible issues and advance a bounded agent workflow."""

from __future__ import annotations

import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any

try:
    from scripts.project_config import config_value, load_config
except ModuleNotFoundError:
    from project_config import config_value, load_config

MAX_REPAIR_ITERATIONS = 2
DEFAULT_ELIGIBLE_LABEL = "backlog"
EXCLUDED_LABELS = {"epic", "automation-in-progress"}
STATE_MARKER = "<!-- coordinator-state -->"
ISSUE_REFERENCE_PATTERN = re.compile(
    r"(?i)(?:closes|closed|close|fixes|fixed|fix|resolves|resolved|resolve)\s+#(\d+)"
)


def parse_issue_number(value: str) -> int:
    normalized = value.strip()
    if normalized.startswith("#"):
        normalized = normalized[1:]
    return int(normalized)


def select_issue(
    issues: list[dict[str, Any]],
    requested_number: int | None = None,
    eligible_label: str = DEFAULT_ELIGIBLE_LABEL,
) -> dict[str, Any] | None:
    eligible = []
    for issue in issues:
        labels = {label["name"] for label in issue.get("labels", [])}
        body = issue.get("body") or ""
        if (
            issue.get("state") == "OPEN"
            and eligible_label in labels
            and not labels & EXCLUDED_LABELS
            and "## Acceptance criteria" in body
            and "-" in body.split("## Acceptance criteria", 1)[1]
        ):
            eligible.append(issue)
    if requested_number is not None:
        return next(
            (issue for issue in eligible if issue["number"] == requested_number), None
        )
    return min(eligible, key=lambda issue: issue["number"]) if eligible else None


def start_run(
    issue_number: int, max_repairs: int = MAX_REPAIR_ITERATIONS, run_id: str | None = None
) -> dict[str, Any]:
    return {
        "run_id": run_id or f"issue-{issue_number}-{uuid.uuid4().hex[:8]}",
        "issue_number": issue_number,
        "architect_status": "pending",
        "developer_pr": None,
        "ci_status": "pending",
        "review_status": "pending",
        "repair_iterations": 0,
        "max_repair_iterations": max_repairs,
        "next_action": "architect",
    }


def advance_run(
    state: dict[str, Any], event: str, details: dict[str, Any] | None = None
) -> dict[str, Any]:
    details = details or {}
    expected_actions = {
        "architect_validated": "architect",
        "developer_pr_created": "developer",
        "ci_passed": "ci",
        "review_approved": "reviewer",
        "review_changes_requested": "reviewer",
    }
    if event not in expected_actions:
        raise ValueError(f"unknown coordinator event: {event}")
    if state["next_action"] != expected_actions[event]:
        raise ValueError(
            f"event {event} is invalid while next action is {state['next_action']}"
        )

    updated = dict(state)
    if event == "architect_validated":
        updated["architect_status"] = "validated"
        updated["next_action"] = "developer"
    elif event == "developer_pr_created":
        if "pr_number" not in details:
            raise ValueError("developer_pr_created requires pr_number")
        updated["developer_pr"] = details["pr_number"]
        updated["next_action"] = "ci"
    elif event == "ci_passed":
        updated["ci_status"] = "passed"
        updated["next_action"] = "reviewer"
    elif event == "review_approved":
        updated["review_status"] = "approved"
        updated["next_action"] = "merge"
    elif event == "review_changes_requested":
        iterations = state["repair_iterations"] + 1
        updated["repair_iterations"] = iterations
        updated["review_status"] = "changes_requested"
        updated["next_action"] = (
            "developer" if iterations <= state["max_repair_iterations"] else "human"
        )
    return updated


def render_state_comment(state: dict[str, Any]) -> str:
    return f"{STATE_MARKER}\n```json\n{json.dumps(state, indent=2)}\n```"


def comment_body(comment: dict[str, Any] | str) -> str:
    body = comment if isinstance(comment, str) else comment.get("body", "")
    return body.replace("\\n", "\n")


def extract_state(
    comments: list[dict[str, Any] | str], run_id: str
) -> dict[str, Any] | None:
    for comment in reversed(comments):
        body = comment_body(comment)
        if STATE_MARKER not in body or f'"run_id": "{run_id}"' not in body:
            continue
        match = re.search(r"```json\s*(\{.*?\})\s*```", body, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    return None


def find_state(
    comments: list[dict[str, Any] | str], issue_number: int, next_action: str
) -> dict[str, Any] | None:
    for comment in reversed(comments):
        body = comment_body(comment)
        if STATE_MARKER not in body:
            continue
        match = re.search(r"```json\s*(\{.*?\})\s*```", body, re.DOTALL)
        if not match:
            continue
        state = json.loads(match.group(1))
        if state.get("issue_number") == issue_number and state.get("next_action") == next_action:
            return state
    return None


def latest_state_for_issue(
    comments: list[dict[str, Any] | str], issue_number: int
) -> dict[str, Any] | None:
    for comment in reversed(comments):
        body = comment_body(comment)
        if STATE_MARKER not in body:
            continue
        match = re.search(r"```json\s*(\{.*?\})\s*```", body, re.DOTALL)
        if not match:
            continue
        state = json.loads(match.group(1))
        if state.get("issue_number") == issue_number:
            return state
    return None


def linked_issue_number(body: str) -> int | None:
    match = ISSUE_REFERENCE_PATTERN.search(body)
    return int(match.group(1)) if match else None


def find_pr_by_sha(pull_requests: list[dict[str, Any]], head_sha: str) -> dict[str, Any] | None:
    return next(
        (pull_request for pull_request in pull_requests if pull_request.get("headRefOid") == head_sha),
        None,
    )


def parse_comment(body: str) -> tuple[str, str, dict[str, Any] | None]:
    command = body.strip()
    if not command.startswith("/coordinator "):
        raise ValueError("comment must start with /coordinator")
    parts = command.split(maxsplit=3)
    if len(parts) < 3:
        raise ValueError("coordinator comment requires run_id and event")
    run_id, event = parts[1], parts[2]
    details = json.loads(parts[3]) if len(parts) == 4 else None
    return run_id, event, details


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def load_state(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def advance_state(path: Path, event: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    state = advance_run(load_state(path), event, details)
    save_state(path, state)
    return state


def main() -> None:
    command = sys.argv[1]
    if command == "select":
        issues = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        requested_number = (
            parse_issue_number(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else None
        )
        config = load_config(Path("agentic-project.json"))
        eligible_label = config_value(config, "backlog.label")
        print(json.dumps(select_issue(issues, requested_number, eligible_label)))
    elif command == "start":
        max_repairs = int(sys.argv[3]) if len(sys.argv) > 3 else MAX_REPAIR_ITERATIONS
        run_id = sys.argv[4] if len(sys.argv) > 4 else None
        print(json.dumps(start_run(int(sys.argv[2]), max_repairs, run_id)))
    elif command == "advance":
        details = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
        print(json.dumps(advance_state(Path(sys.argv[2]), sys.argv[3], details)))
    elif command == "parse-comment":
        run_id, event, details = parse_comment(Path(sys.argv[2]).read_text(encoding="utf-8"))
        print(json.dumps({"run_id": run_id, "event": event, "details": details}))
    elif command == "advance-comment":
        payload = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        comments = payload.get("comments", payload) if isinstance(payload, dict) else payload
        run_id, event, details = sys.argv[3], sys.argv[4], json.loads(sys.argv[5]) if len(sys.argv) > 5 else None
        state = extract_state(comments, run_id)
        if state is None:
            raise SystemExit(f"no coordinator state found for run_id: {run_id}")
        print(json.dumps(advance_run(state, event, details)))
    elif command == "find-state":
        payload = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        comments = payload.get("comments", payload) if isinstance(payload, dict) else payload
        state = find_state(comments, int(sys.argv[3]), sys.argv[4])
        print(json.dumps(state))
    elif command == "latest-state":
        payload = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        comments = payload.get("comments", payload) if isinstance(payload, dict) else payload
        print(json.dumps(latest_state_for_issue(comments, int(sys.argv[3]))))
    elif command == "linked-issue":
        print(json.dumps(linked_issue_number(Path(sys.argv[2]).read_text(encoding="utf-8"))))
    else:
        raise SystemExit(f"unknown coordinator command: {command}")


if __name__ == "__main__":
    main()
