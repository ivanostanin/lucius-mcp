"""
Shared CLI models and constants.
"""

from __future__ import annotations

import typing
from dataclasses import dataclass
from pathlib import Path

OUTPUT_FORMATS = {"json", "table", "plain", "csv"}


class CLIError(Exception):
    """Custom exception for CLI errors with user-friendly messages."""

    def __init__(self, message: str, hint: str | None = None, exit_code: int = 1) -> None:
        self.message = message
        self.hint = hint
        self.exit_code = exit_code
        super().__init__(message)


@dataclass(frozen=True)
class ActionSpec:
    """Resolved command target for one entity/action pair."""

    tool_name: str
    entity: str
    action: str
    schema: dict[str, typing.Any]


@dataclass
class ActionOptions:
    """Parsed options for an action command."""

    args_json: str = "{}"
    output_format: str = "json"
    pretty_json: bool = False
    show_help: bool = False


@dataclass(frozen=True)
class CLIContext:
    """Shared runtime dependencies for CLI execution."""

    console_out: typing.Any
    console_err: typing.Any
    tool_schemas_path: Path
    version: str


@dataclass(frozen=True)
class PreparedCommand:
    """Fully parsed action command ready for invocation."""

    entity: str
    action: str
    spec: ActionSpec
    options: ActionOptions
    args_dict: dict[str, typing.Any]
    tool_args: dict[str, typing.Any]
