#!/usr/bin/env python3
"""
Lucius CLI - Entity/action interface for lucius-mcp tools.

Design:
- Thin CLI, service-backed execution via existing tool functions
- No FastMCP dependency at CLI runtime
- Entity/action routing: lucius <entity> <action>
- JSON-schema validation and per-action help from static tool schemas
"""

from __future__ import annotations

import logging
import sys
from functools import partial
from pathlib import Path

import rich.console

from src.cli.command_runner import run_cli_command
from src.cli.models import CLIContext, CLIError
from src.cli.option_parsing import parse_action_options, validate_args_against_schema
from src.cli.routing import build_command_registry, resolve_action_name, resolve_entity_name
from src.cli.runtime import call_tool_function, error_hint_from_exception, exit_with_cli_error
from src.cli.schema_loader import load_tool_schemas
from src.version import __version__

console_err = rich.console.Console(stderr=True)
console_out = rich.console.Console()

TOOL_SCHEMAS_PATH = Path(__file__).parent / "data" / "tool_schemas.json"


def run_cli(argv: list[str]) -> None:
    """Route CLI command and execute."""
    context = CLIContext(
        console_out=console_out,
        console_err=console_err,
        tool_schemas_path=TOOL_SCHEMAS_PATH,
        version=__version__,
    )
    run_cli_command(
        argv,
        context=context,
        load_tool_schemas=partial(load_tool_schemas, TOOL_SCHEMAS_PATH, Path(__file__)),
        build_command_registry=build_command_registry,
        resolve_entity_name=resolve_entity_name,
        resolve_action_name=resolve_action_name,
        parse_action_options=parse_action_options,
        validate_args_against_schema=validate_args_against_schema,
        call_tool_function=call_tool_function,
    )


def main() -> None:
    """CLI entry point."""
    logging.disable(logging.CRITICAL)
    try:
        run_cli(sys.argv[1:])
    except CLIError as error:
        exit_with_cli_error(error, console_err)
    except KeyboardInterrupt:
        raise SystemExit(130) from None
    except Exception as error:
        exit_with_cli_error(
            CLIError(
                f"Unexpected CLI error: {error}",
                hint=error_hint_from_exception(error),
                exit_code=1,
            ),
            console_err,
        )


if __name__ == "__main__":
    main()
