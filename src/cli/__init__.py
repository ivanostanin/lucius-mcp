"""
CLI module for lucius-mcp command-line interface.

IMPORTANT: No HTTP server imports allowed in CLI module.
CLI does not depend on FastMCP runtime; it calls service-backed tool functions directly.
"""

from __future__ import annotations

import importlib

_EXPORTS: dict[str, str] = {
    "ActionSpec": "src.cli.models",
    "CLIContext": "src.cli.models",
    "CLIError": "src.cli.models",
    "OUTPUT_FORMATS": "src.cli.models",
    "TOOL_SCHEMAS_PATH": "src.cli.cli_entry",
    "_build_example_args": "src.cli.help_output",
    "_first_line": "src.cli.help_output",
    "_format_action_list": "src.cli.help_output",
    "all_entities_with_aliases": "src.cli.route_matrix",
    "build_command_registry": "src.cli.routing",
    "call_tool_function": "src.cli.runtime",
    "candidate_tool_schema_paths": "src.cli.schema_loader",
    "console_err": "src.cli.cli_entry",
    "console_out": "src.cli.cli_entry",
    "error_hint_from_exception": "src.cli.runtime",
    "exit_with_cli_error": "src.cli.runtime",
    "format_as_csv": "src.cli.formatting",
    "format_as_plain": "src.cli.formatting",
    "format_as_table": "src.cli.formatting",
    "format_json": "src.cli.formatting",
    "load_tool_function": "src.cli.runtime",
    "load_tool_schemas": "src.cli.schema_loader",
    "main": "src.cli.cli_entry",
    "parse_action_options": "src.cli.option_parsing",
    "read_tool_schemas": "src.cli.schema_loader",
    "render_action_help": "src.cli.help_output",
    "render_entity_actions": "src.cli.help_output",
    "render_global_help": "src.cli.help_output",
    "render_output": "src.cli.formatting",
    "resolve_action_name": "src.cli.routing",
    "resolve_entity_name": "src.cli.routing",
    "resolve_tool_schema_path": "src.cli.schema_loader",
    "run_cli": "src.cli.cli_entry",
    "run_cli_command": "src.cli.command_runner",
    "validate_args_against_schema": "src.cli.option_parsing",
}

__all__ = sorted(_EXPORTS)


def __getattr__(name: str) -> object:
    """Lazily resolve package exports without importing the full CLI stack."""
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = importlib.import_module(_EXPORTS[name])
    return getattr(module, name)


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + __all__)


def main() -> None:
    """Lazy main import to avoid side effects during module execution."""
    from .cli_entry import main as cli_main

    cli_main()
