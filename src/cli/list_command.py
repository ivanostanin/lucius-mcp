"""CLI-local list command handling."""

from __future__ import annotations

import typing

from src.cli.help_output import render_global_help
from src.cli.local_commands import LIST_HELP_TOKENS, list_usage_lines
from src.cli.models import CLIContext, CLIError


def render_list_help(console: typing.Any) -> None:
    """Print help for the CLI-local list command."""
    for line in list_usage_lines():
        console.print(line)


def handle_list_command(
    argv: list[str],
    *,
    context: CLIContext,
    load_tool_schemas: typing.Callable[[], dict[str, typing.Any]],
    build_command_registry: typing.Callable[[dict[str, typing.Any]], dict[str, dict[str, typing.Any]]],
) -> None:
    """Handle `lucius list` without entering entity/action routing."""
    if not argv:
        registry = build_command_registry(load_tool_schemas())
        render_global_help(registry, context.console_out)
        return

    if len(argv) == 1 and argv[0] in LIST_HELP_TOKENS:
        render_list_help(context.console_out)
        return

    raise CLIError(
        f"Unknown option '{argv[0]}'",
        hint="Supported list options: --help/-h",
        exit_code=1,
    )
