from pathlib import Path

import pytest

from experiment_tracker.storage import create_experiment, init_db, list_experiments


def test_init_db_creates_experiment_table(tmp_path: Path):
    database = tmp_path / "experiments.db"

    init_db(database)

    assert list_experiments(database) == []


def test_create_and_list_experiment(tmp_path: Path):
    database = tmp_path / "experiments.db"

    experiment_id = create_experiment(
        database,
        "Require category labels",
        "agent-guidance",
        "Category labels reduce uncategorized metrics.",
        "PR 5 was uncategorized.",
        "The next three PRs have aligned labels.",
    )

    experiments = list_experiments(database)
    assert experiment_id == experiments[0]["id"]
    assert experiments[0]["title"] == "Require category labels"
    assert experiments[0]["status"] == "active"


def test_create_experiment_rejects_empty_fields(tmp_path: Path):
    with pytest.raises(ValueError, match="must not be empty"):
        create_experiment(tmp_path / "experiments.db", "", "architecture", "h", "b", "s")


def test_create_experiment_trims_whitespace_and_rejects_blank_values(tmp_path: Path):
    database = tmp_path / "experiments.db"

    experiment_id = create_experiment(
        database,
        "  Require category labels  ",
        "  architecture  ",
        "  Category labels reduce uncategorized metrics.  ",
        "  PR 5 was uncategorized.  ",
        "  The next three PRs have aligned labels.  ",
    )

    experiments = list_experiments(database)
    assert experiment_id == experiments[0]["id"]
    assert experiments[0]["title"] == "Require category labels"
    assert experiments[0]["category"] == "architecture"

    with pytest.raises(ValueError, match="must not be empty"):
        create_experiment(database, "   ", "architecture", "h", "b", "s")
