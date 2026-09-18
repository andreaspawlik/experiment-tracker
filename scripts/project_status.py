"""Build GitHub Project status update commands for coordinator lifecycle events."""

from __future__ import annotations

PROJECT_ID = "PVT_kwHOAGflZs4BjpbP"
STATUS_FIELD_ID = "PVTSSF_lAHOAGflZs4BjpbPzhic-GE"
STATUS_OPTIONS = {"in_progress": "47fc9ee4", "done": "98236657"}


def build_update_command(item_id: str, status: str) -> list[str]:
    try:
        option_id = STATUS_OPTIONS[status]
    except KeyError as error:
        raise ValueError(f"unknown project status: {status}") from error
    return [
        "gh",
        "project",
        "item-edit",
        "--project-id",
        PROJECT_ID,
        "--id",
        item_id,
        "--field-id",
        STATUS_FIELD_ID,
        "--single-select-option-id",
        option_id,
    ]


def find_item_command(issue_number: int) -> list[str]:
    return [
        "gh",
        "project",
        "item-list",
        "1",
        "--owner",
        "andreaspawlik",
        "--format",
        "json",
        "--jq",
        f'.items[] | select(.content.number == {issue_number}) | .id',
    ]
