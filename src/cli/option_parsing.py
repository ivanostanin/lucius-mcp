"""
CLI action option parsing and schema validation helpers.
"""

from __future__ import annotations

import typing

from src.cli.models import ActionOptions, CLIError
from src.cli.schema_validation import SchemaValidationError
from src.cli.schema_validation import validate_args_against_schema as validate_schema_args

PRETTY_OPTION = "--pretty"


def parse_action_options(argv: list[str]) -> ActionOptions:
    """Parse options after <entity> <action>."""
    options = ActionOptions()
    index = 0
    while index < len(argv):
        token = argv[index]
        if token in {"--help", "-h"}:
            options.show_help = True
            index += 1
            continue
        if token in {"--args", "-a"}:
            if index + 1 >= len(argv):
                raise CLIError("Missing value for --args", hint="Provide JSON object: --args '{\"id\": 123}'")
            options.args_json = argv[index + 1]
            index += 2
            continue
        if token in {"--format", "-f"}:
            if index + 1 >= len(argv):
                raise CLIError("Missing value for --format", hint="Use --format json|table|plain|csv")
            options.output_format = argv[index + 1]
            index += 2
            continue
        if token == PRETTY_OPTION:
            options.pretty_json = True
            index += 1
            continue
        raise CLIError(
            f"Unknown option '{token}'",
            hint="Supported options: --args/-a, --format/-f, --pretty, --help/-h",
        )
    return options


def validate_args_against_schema(
    args: dict[str, typing.Any],
    command_name: str,
    tool_schema: dict[str, typing.Any],
) -> None:
    """Validate JSON arguments against a tool input schema."""
    try:
        validate_schema_args(args, command_name, tool_schema)
    except SchemaValidationError as error:
        raise CLIError(error.message, hint=error.hint, exit_code=error.exit_code) from None
