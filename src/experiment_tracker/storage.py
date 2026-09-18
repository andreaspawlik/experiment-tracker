import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    category TEXT NOT NULL,
    hypothesis TEXT NOT NULL,
    baseline TEXT NOT NULL,
    success_criteria TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


def _normalize_required_value(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def init_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute(SCHEMA)


def list_experiments(path: Path) -> list[dict[str, Any]]:
    init_db(path)
    with sqlite3.connect(path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM experiments ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def create_experiment(
    path: Path,
    title: str,
    category: str,
    hypothesis: str,
    baseline: str,
    success_criteria: str,
) -> int:
    values = {
        "title": _normalize_required_value(title, "title"),
        "category": _normalize_required_value(category, "category"),
        "hypothesis": _normalize_required_value(hypothesis, "hypothesis"),
        "baseline": _normalize_required_value(baseline, "baseline"),
        "success_criteria": _normalize_required_value(success_criteria, "success_criteria"),
    }
    init_db(path)
    with sqlite3.connect(path) as connection:
        cursor = connection.execute(
            """INSERT INTO experiments
            (title, category, hypothesis, baseline, success_criteria)
            VALUES (:title, :category, :hypothesis, :baseline, :success_criteria)""",
            values,
        )
        return int(cursor.lastrowid)
