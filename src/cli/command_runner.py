"""
Command parsing, planning, and result rendering for the CLI.
"""

from __future__ import annotations

import asyncio
import json
import typing
from collections.abc import Coroutine

from src.cli.formatting import (
    _structured_tool_payload,
    _tool_result_to_json_text,
    format_json,
    render_output,
    select_tabular_payload,
)
from src.cli.help_output import render_action_help, render_entity_actions, render_global_help
from src.cli.models import OUTPUT_FORMATS, CLIContext, CLIError, PreparedCommand

PRETTY_JSON_HINT = "--pretty is valid only for action commands using JSON output: omit --format or use --format json."


def parse_args_json(args_json: str) -> dict[str, typing.Any]:
    """Parse the raw --args payload and enforce object-shaped input."""
    try:
        parsed = json.loads(args_json)
    except json.JSONDecodeError as error:
        raise CLIError(
            f"Invalid JSON in --args: {error}",
            hint="Example: --args '{\"test_case_id\": 1234}'",
            exit_code=1,
        ) from None

    if not isinstance(parsed, dict):
        raise CLIError(
            "Invalid --args payload: expected a JSON object",
            hint="Example: --args '{\"project_id\": 1}'",
            exit_code=1,
        )
    return typing.cast(dict[str, typing.Any], parsed)


def build_tool_args(args_dict: dict[str, typing.Any], output_format: str) -> dict[str, typing.Any]:
    """Append the tool contract output format to validated command arguments."""
    tool_output_format = "plain" if output_format == "plain" else "json"
    return {**args_dict, "output_format": tool_output_format}


def prepare_command(
    argv: list[str],
    *,
    context: CLIContext,
    load_tool_schemas: typing.Callable[[], dict[str, typing.Any]],
    build_command_registry: typing.Callable[[dict[str, typing.Any]], dict[str, dict[str, typing.Any]]],
    resolve_entity_name: typing.Callable[[str, dict[str, dict[str, typing.Any]]], str],
    resolve_action_name: typing.Callable[[str, str, dict[str, typing.Any]], str],
    parse_action_options: typing.Callable[[list[str]], typing.Any],
    validate_args_against_schema: typing.Callable[[dict[str, typing.Any], str, dict[str, typing.Any]], None],
) -> PreparedCommand | None:
    """Resolve argv into a prepared action command or execute help/version flows."""
    if "--pretty" in argv:
        if (
            len(argv) == 1
            or argv[0] in {"--help", "-h", "help", "--version", "-V", "version"}
            or (len(argv) >= 2 and argv[1] in {"--pretty", "--help", "-h", "help"})
        ):
            raise CLIError(
                "Unsupported --pretty option",
                hint=PRETTY_JSON_HINT,
                exit_code=1,
            )

    if not argv or argv[0] in {"--help", "-h", "help"}:
        registry = build_command_registry(load_tool_schemas())
        render_global_help(registry, context.console_out)
        return None

    if argv[0] in {"--version", "-V", "version"}:
        context.console_out.print(f"lucius {context.version}")
        return None

    if argv[0] == "call":
        raise CLIError(
            "Legacy command style detected",
            hint=(
                "Use entity/action format instead. Examples:\n  lucius test_case\n  lucius test_case list --args '{}'"
            ),
            exit_code=1,
        )

    registry = build_command_registry(load_tool_schemas())
    entity = resolve_entity_name(argv[0], registry)
    actions = registry[entity]

    if len(argv) == 1 or argv[1] in {"--help", "-h", "help"}:
        render_entity_actions(entity, actions, context.console_out)
        return None

    action = resolve_action_name(entity, argv[1], actions)
    spec = actions[action]
    options = parse_action_options(argv[2:])

    if options.output_format not in OUTPUT_FORMATS:
        raise CLIError(
            f"Invalid format '{options.output_format}'",
            hint="Use --format json|table|plain|csv",
            exit_code=1,
        )

    if options.pretty_json and options.output_format != "json":
        raise CLIError(
            f"--pretty cannot be used with --format {options.output_format}",
            hint=PRETTY_JSON_HINT,
            exit_code=1,
        )

    if options.show_help:
        render_action_help(spec, context.console_out)
        return None

    args_dict = parse_args_json(options.args_json)
    validate_args_against_schema(args_dict, f"{entity} {action}", spec.schema)
    return PreparedCommand(
        entity=entity,
        action=action,
        spec=spec,
        options=options,
        args_dict=args_dict,
        tool_args=build_tool_args(args_dict, options.output_format),
    )


def _format_pretty_json_text(json_text: str, tool_name: str) -> str:
    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError as error:
        raise CLIError(
            f"Tool '{tool_name}' returned invalid JSON for pretty JSON output: {error}",
            hint="Use --pretty only when the selected action returns valid JSON text.",
            exit_code=2,
        ) from None
    return format_json(parsed)


def _render_json_result(result: typing.Any, *, pretty_json: bool, tool_name: str, console_out: typing.Any) -> None:
    if isinstance(result, str):
        console_out.print(_format_pretty_json_text(result, tool_name) if pretty_json else result, end="")
        return

    json_text = _tool_result_to_json_text(result)
    if json_text is not None:
        console_out.print(_format_pretty_json_text(json_text, tool_name) if pretty_json else json_text, end="")
        return

    raise CLIError(
        f"Tool '{tool_name}' returned non-JSON output for 'json' mode",
        hint="Tool output contract requires json mode to return structured content or JSON text.",
        exit_code=2,
    )


def render_tool_result(
    prepared: PreparedCommand,
    result: typing.Any,
    *,
    console_out: typing.Any,
) -> None:
    """Render the invoked tool result according to the requested CLI output mode."""
    output_format = prepared.options.output_format
    pretty_json = prepared.options.pretty_json
    tool_name = prepared.spec.tool_name

    if output_format == "plain":
        if isinstance(result, str):
            console_out.print(result, end="")
            return
        raise CLIError(
            f"Tool '{tool_name}' returned non-string output for 'plain' mode",
            hint="Tool output contract requires plain mode to return text output.",
            exit_code=2,
        )

    if output_format == "json":
        _render_json_result(result, pretty_json=pretty_json, tool_name=tool_name, console_out=console_out)
        return

    if not isinstance(result, str):
        parsed = _structured_tool_payload(result)
        if parsed is None:
            raise CLIError(
                f"Tool '{tool_name}' returned non-JSON output for '{output_format}' mode",
                hint="Tool output contract requires structured content or JSON text for table/csv rendering.",
                exit_code=2,
            )
    else:
        try:
            parsed = json.loads(result)
        except json.JSONDecodeError as error:
            raise CLIError(
                f"Tool '{tool_name}' returned invalid JSON for '{output_format}' mode: {error}",
                hint="Tool output contract requires valid JSON text output for table/csv rendering.",
                exit_code=2,
            ) from None

    render_output(select_tabular_payload(parsed), output_format, console_out)


def run_cli_command(
    argv: list[str],
    *,
    context: CLIContext,
    load_tool_schemas: typing.Callable[[], dict[str, typing.Any]],
    build_command_registry: typing.Callable[[dict[str, typing.Any]], dict[str, dict[str, typing.Any]]],
    resolve_entity_name: typing.Callable[[str, dict[str, dict[str, typing.Any]]], str],
    resolve_action_name: typing.Callable[[str, str, dict[str, typing.Any]], str],
    parse_action_options: typing.Callable[[list[str]], typing.Any],
    validate_args_against_schema: typing.Callable[[dict[str, typing.Any], str, dict[str, typing.Any]], None],
    call_tool_function: typing.Callable[[str, dict[str, typing.Any]], Coroutine[typing.Any, typing.Any, typing.Any]],
) -> None:
    """Route a CLI request from argv through parse, invoke, and render phases."""
    prepared = prepare_command(
        argv,
        context=context,
        load_tool_schemas=load_tool_schemas,
        build_command_registry=build_command_registry,
        resolve_entity_name=resolve_entity_name,
        resolve_action_name=resolve_action_name,
        parse_action_options=parse_action_options,
        validate_args_against_schema=validate_args_against_schema,
    )
    if prepared is None:
        return

    result: typing.Any = asyncio.run(call_tool_function(prepared.spec.tool_name, prepared.tool_args))
    render_tool_result(
        prepared,
        result,
        console_out=context.console_out,
    )
