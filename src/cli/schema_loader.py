"""
Helpers for locating and loading CLI tool schemas.
"""

from __future__ import annotations

import json
import typing
from pathlib import Path

from src.cli.models import CLIError


def candidate_tool_schema_paths(primary_path: Path, current_file: Path) -> list[Path]:
    """Return the supported fallback locations for the generated schema file."""
    return [
        primary_path,
        current_file.parent.parent / "data" / "tool_schemas.json",
        current_file.parent / "tool_schemas.json",
    ]


def resolve_tool_schema_path(candidate_paths: list[Path]) -> Path:
    """Return the first existing schema path from the candidate list."""
    for path in candidate_paths:
        if path.exists():
            return path
    raise CLIError(
        "Tool schemas not found",
        hint="Rebuild the CLI binary from the latest source code",
        exit_code=2,
    )


def read_tool_schemas(path: Path) -> dict[str, typing.Any]:
    """Load the tool schema JSON document from disk."""
    try:
        with path.open("r") as file_handle:
            return typing.cast(dict[str, typing.Any], json.load(file_handle))
    except json.JSONDecodeError as error:
        raise CLIError(
            f"Invalid tool schemas JSON: {error}",
            hint="Regenerate tool schemas by running scripts/build_tool_schema.py",
            exit_code=2,
        ) from None


def load_tool_schemas(primary_path: Path, current_file: Path) -> dict[str, typing.Any]:
    """Load static tool schemas using the supported CLI fallback paths."""
    candidate_paths = candidate_tool_schema_paths(primary_path, current_file)
    return read_tool_schemas(resolve_tool_schema_path(candidate_paths))
