"""Load and validate the project-specific agentic engineering contract."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REQUIRED_STATUS_NAMES = ("todo", "in_progress", "done")


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as config_file:
        config = json.load(config_file)

    project = config.get("project", {})
    backlog = config.get("backlog", {})
    github = config.get("github", {})
    status_options = github.get("status_options", {})
    required_values = {
        "project.name": project.get("name"),
        "project.language": project.get("language"),
        "project.test_command": project.get("test_command"),
        "project.coverage_command": project.get("coverage_command"),
        "backlog.label": backlog.get("label"),
        "backlog.project_name": backlog.get("project_name"),
        "github.project_owner": github.get("project_owner"),
        "github.project_number": github.get("project_number"),
        "github.project_id": github.get("project_id"),
        "github.status_field_id": github.get("status_field_id"),
    }
    required_values.update({
        f"github.status_options.{name}": status_options.get(name)
        for name in REQUIRED_STATUS_NAMES
    })
    missing = [name for name, value in required_values.items() if value in (None, "")]
    if missing:
        raise ValueError(f"missing project configuration: {", ".join(missing)}")
    threshold = project.get("coverage_threshold")
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 100:
        raise ValueError("project.coverage_threshold must be between 0 and 100")
    return config


def configured_command(config: dict[str, Any], key: str) -> str:
    value: Any = config
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            raise ValueError(f"missing project configuration: {key}")
        value = value[part]
    if not isinstance(value, str) or not value:
        raise ValueError(f"project configuration is not a command: {key}")
    return value


def config_value(config: dict[str, Any], key: str) -> str:
    value: Any = config
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            raise ValueError(f"missing project configuration: {key}")
        value = value[part]
    if not isinstance(value, (str, int, float)) or value == "":
        raise ValueError(f"project configuration value is invalid: {key}")
    return str(value)


def run_configured_command(path: Path, key: str) -> int:
    return subprocess.run(configured_command(load_config(path), key), shell=True, check=False).returncode


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "run":
        raise SystemExit(run_configured_command(Path("agentic-project.json"), sys.argv[2]))
    if len(sys.argv) >= 3 and sys.argv[1] == "get":
        print(config_value(load_config(Path("agentic-project.json")), sys.argv[2]))
        raise SystemExit(0)
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("agentic-project.json")
    print(json.dumps(load_config(config_path), indent=2))
