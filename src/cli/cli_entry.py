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

import asyncio
import csv
import io
import json
import logging
import sys
import typing
from dataclasses import dataclass
from pathlib import Path

import rich.console

from src.cli.route_matrix import ACTION_ALIASES, CANONICAL_ROUTE_MATRIX, all_entities_with_aliases, normalize_token
from src.cli.schema_validation import SchemaValidationError
from src.cli.schema_validation import validate_args_against_schema as validate_schema_args
from src.cli.tool_resolver import resolve_tool_function
from src.version import __version__

console_err = rich.console.Console(stderr=True)
console_out = rich.console.Console()

TOOL_SCHEMAS_PATH = Path(__file__).parent / "data" / "tool_schemas.json"
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
    show_help: bool = False


def load_tool_schemas() -> dict[str, typing.Any]:
    """Load static tool schemas generated at build time."""
    possible_paths = [
        TOOL_SCHEMAS_PATH,
        Path(__file__).parent.parent / "data" / "tool_schemas.json",
        Path(__file__).parent / "tool_schemas.json",
    ]

    actual_path: Path | None = None
    for path in possible_paths:
        if path.exists():
            actual_path = path
            break

    if actual_path is None:
        raise CLIError(
            "Tool schemas not found",
            hint="Rebuild the CLI binary from the latest source code",
            exit_code=2,
        )

    try:
        with actual_path.open("r") as f:
            return typing.cast(dict[str, typing.Any], json.load(f))
    except json.JSONDecodeError as e:
        raise CLIError(
            f"Invalid tool schemas JSON: {e}",
            hint="Regenerate tool schemas by running scripts/build_tool_schema.py",
            exit_code=2,
        ) from None


def format_json(data: typing.Any) -> str:
    """Format data as JSON string."""
    return json.dumps(data, default=str, indent=2)


def _is_tool_schema_map(data: typing.Any) -> bool:
    if not isinstance(data, dict) or not data:
        return False
    return all(isinstance(value, dict) and "input_schema" in value for value in data.values())


def _format_table_value(value: typing.Any) -> str:
    if isinstance(value, (dict, list)):
        rendered = json.dumps(value, default=str)
        return rendered if len(rendered) <= 200 else rendered[:197] + "..."
    return str(value)


def _format_csv_value(value: typing.Any) -> str:
    """Render CSV cell values without truncation."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str)
    return str(value)


def _plain_text(value: typing.Any) -> str:
    """Render plain output text and normalize escaped newlines."""
    return str(value).replace("\\n", "\n")


def format_as_table(data: typing.Any) -> typing.Any:
    """Format tool schemas or generic results as a Rich table."""
    from rich.table import Table

    if _is_tool_schema_map(data):
        table = Table(title="Available Lucius Tools")
        table.add_column("Tool Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Parameters", style="yellow")

        for tool_name, tool_info in data.items():
            properties = tool_info.get("input_schema", {}).get("properties", {})
            param_list = list(properties.keys()) if properties else ["(no parameters)"]
            param_str = ", ".join(param_list[:5]) + ("..." if len(param_list) > 5 else "")
            table.add_row(
                tool_name,
                tool_info.get("description", "No description")[:60],
                param_str,
            )
        return table

    if isinstance(data, dict):
        table = Table(title="Command Result")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        for key, value in data.items():
            table.add_row(str(key), _format_table_value(value))
        return table

    if isinstance(data, list):
        if not data:
            table = Table(title="Command Result")
            table.add_column("Result", style="green")
            table.add_row("(empty)")
            return table

        if all(isinstance(item, dict) for item in data):
            column_names: list[str] = []
            for item in data:
                for key in item.keys():
                    if key not in column_names:
                        column_names.append(str(key))

            table = Table(title="Command Result")
            for name in column_names:
                table.add_column(name, style="green")
            for item in data:
                table.add_row(*[_format_table_value(item.get(name)) for name in column_names])
            return table

        table = Table(title="Command Result")
        table.add_column("Value", style="green")
        for item in data:
            table.add_row(_format_table_value(item))
        return table

    table = Table(title="Command Result")
    table.add_column("Value", style="green")
    table.add_row(_format_table_value(data))
    return table


def format_as_plain(data: typing.Any) -> str:
    """Format data as plain text."""
    if isinstance(data, dict):
        return "\n".join(f"{k}: {_plain_text(v)}" for k, v in data.items())
    if isinstance(data, list):
        return "\n".join(_plain_text(item) for item in data)
    return _plain_text(data)


def format_as_csv(data: typing.Any) -> str:
    """Format tool schemas or generic results as RFC-4180-compatible CSV."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    if _is_tool_schema_map(data):
        writer.writerow(["tool_name", "description", "parameters"])
        for tool_name in sorted(data):
            tool_info = data[tool_name]
            properties = tool_info.get("input_schema", {}).get("properties", {})
            param_list = list(properties.keys()) if properties else ["(no parameters)"]
            param_str = ", ".join(param_list[:5]) + ("..." if len(param_list) > 5 else "")
            writer.writerow(
                [
                    tool_name,
                    tool_info.get("description", "No description"),
                    param_str,
                ]
            )
        return output.getvalue()

    if isinstance(data, dict):
        field_names = [str(key) for key in data.keys()]
        writer.writerow(field_names)
        writer.writerow([_format_csv_value(data.get(name)) for name in field_names])
        return output.getvalue()

    if isinstance(data, list):
        if not data:
            writer.writerow(["value"])
            return output.getvalue()

        if all(isinstance(item, dict) for item in data):
            column_names: list[str] = []
            for item in data:
                for key in item.keys():
                    if key not in column_names:
                        column_names.append(str(key))
            writer.writerow(column_names)
            for item in data:
                writer.writerow([_format_csv_value(item.get(name)) for name in column_names])
            return output.getvalue()

        writer.writerow(["value"])
        for item in data:
            writer.writerow([_format_csv_value(item)])
        return output.getvalue()

    writer.writerow(["value"])
    writer.writerow([_format_csv_value(data)])
    return output.getvalue()


def format_output_data(data: typing.Any, output_format: str = "json") -> None:
    """Print command output in the selected format."""
    if output_format == "json":
        console_out.print_json(format_json(data))
    elif output_format == "table":
        console_out.print(format_as_table(data))
    elif output_format == "csv":
        console_out.print(format_as_csv(data), end="")
    elif output_format == "plain":
        console_out.print(format_as_plain(data))
    else:
        raise CLIError(
            f"Invalid output format: {output_format}",
            hint="Use --format json|table|plain|csv",
            exit_code=1,
        )


def select_tabular_payload(data: typing.Any) -> typing.Any:
    """Prefer row collections from JSON envelopes for table/csv rendering."""
    if not isinstance(data, dict):
        return data

    items = data.get("items")
    if isinstance(items, list):
        return items
    return data


def build_command_registry(schemas: dict[str, typing.Any]) -> dict[str, dict[str, ActionSpec]]:
    """Build {entity: {action: ActionSpec}} from canonical route matrix."""
    registry: dict[str, dict[str, ActionSpec]] = {}

    for entity, action_map in CANONICAL_ROUTE_MATRIX.items():
        by_action = registry.setdefault(entity, {})
        for action, tool_name in action_map.items():
            schema = schemas.get(tool_name)
            if not isinstance(schema, dict):
                missing = ", ".join(sorted(action_map.values()))
                raise CLIError(
                    f"Tool schema for '{tool_name}' is missing",
                    hint=f"Regenerate schemas. Expected tools for '{entity}': {missing}",
                    exit_code=2,
                )
            if action in by_action:
                existing = by_action[action].tool_name
                raise CLIError(
                    f"Ambiguous command mapping for '{entity} {action}'",
                    hint=f"Tools '{existing}' and '{tool_name}' map to the same command",
                    exit_code=2,
                )
            by_action[action] = ActionSpec(
                tool_name=tool_name,
                entity=entity,
                action=action,
                schema=typing.cast(dict[str, typing.Any], schema),
            )

    represented = {spec.tool_name for actions in registry.values() for spec in actions.values()}
    for tool_name in schemas:
        if tool_name not in represented:
            raise CLIError(
                f"Tool schema '{tool_name}' is not represented in canonical route matrix",
                hint="Update src/cli/route_matrix.py canonical routes to include this tool.",
                exit_code=2,
            )
    return registry


def resolve_entity_name(entity_input: str, registry: dict[str, dict[str, ActionSpec]]) -> str:
    """Resolve entity aliases defined in route matrix metadata."""
    normalized = normalize_token(entity_input)
    alias_map: dict[str, str] = {}
    for entity, aliases in all_entities_with_aliases().items():
        if entity not in registry:
            continue
        for alias in aliases:
            alias_map.setdefault(alias, entity)

    if normalized not in alias_map:
        canonical = ", ".join(sorted(registry.keys()))
        alias_names = ", ".join(
            sorted(alias for alias in alias_map if alias not in registry and "_" not in alias and "-" not in alias)
        )
        hint = f"Canonical entities: {canonical}"
        if alias_names:
            hint += f". Aliases: {alias_names}"
        raise CLIError(
            f"Unknown entity '{entity_input}'",
            hint=hint,
            exit_code=1,
        )
    return alias_map[normalized]


def resolve_action_name(entity: str, action_input: str, actions: dict[str, ActionSpec]) -> str:
    """Resolve action aliases (hyphen/underscore normalization)."""
    normalized = normalize_token(action_input)
    if normalized in actions:
        return normalized

    alias_map: dict[str, str] = {}
    for action_name in actions:
        aliases = {action_name, action_name.replace("_", "-")}
        canonical_aliases = ACTION_ALIASES.get(entity, {})
        for alias, canonical in canonical_aliases.items():
            if canonical == action_name:
                aliases.add(alias)
        for alias in aliases:
            alias_map.setdefault(alias, action_name)

    if normalized not in alias_map:
        available = ", ".join(sorted(actions.keys()))
        raise CLIError(
            f"Unknown action '{action_input}' for entity '{entity}'",
            hint=f"Available actions: {available}",
            exit_code=1,
        )

    return alias_map[normalized]


def _error_hint_from_exception(error: Exception) -> str:
    message = str(error).lower()
    if "not set in environment" in message or "api_token" in message:
        return "Set required credentials (ALLURE_API_TOKEN and ALLURE_API_URL) before calling commands."
    if "401" in message or "403" in message or "unauthorized" in message:
        return "Verify API credentials and permissions for the target project."
    if "validationerror" in message or "field required" in message:
        return "Check command parameters with: lucius <entity> <action> --help."
    if "json" in message:
        return "Ensure --args is valid JSON, for example: --args '{\"id\": 1234}'."
    return "Review command parameters with: lucius <entity> <action> --help."


def _exit_with_cli_error(error: CLIError) -> typing.NoReturn:
    console_err.print(f"[red]Error:[/red] {error.message}")
    if error.hint:
        console_err.print(f"\n[yellow]Hint:[/yellow] {error.hint}")
    raise SystemExit(error.exit_code)


def _first_line(text: str) -> str:
    stripped = text.strip()
    return stripped.splitlines()[0] if stripped else "No description"


def _format_action_list(actions: typing.Iterable[str]) -> str:
    """Render action names for entity overview table."""
    sorted_actions = sorted(actions)
    if not sorted_actions:
        return "-"
    return ", ".join(sorted_actions)


def _build_example_args(schema: dict[str, typing.Any]) -> dict[str, typing.Any]:
    input_schema = schema.get("input_schema", {})
    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])
    example_args: dict[str, typing.Any] = {}

    for param_name in required:
        param_info = properties.get(param_name, {})
        param_type = param_info.get("type")
        if param_type is None and isinstance(param_info.get("anyOf"), list):
            any_of = [item for item in param_info["anyOf"] if item.get("type") != "null"]
            param_type = any_of[0].get("type") if any_of else "string"
        if param_type in {"integer", "number"}:
            example_args[param_name] = 123
        elif param_type == "boolean":
            example_args[param_name] = True
        elif param_type == "array":
            example_args[param_name] = []
        elif param_type == "object":
            example_args[param_name] = {}
        else:
            example_args[param_name] = "value"
    return example_args


def print_global_help(registry: dict[str, dict[str, ActionSpec]]) -> None:
    """Print root CLI help."""
    from rich.table import Table

    console_out.print("Lucius CLI - Entity/action interface\n")
    console_out.print("Usage:")
    console_out.print("  lucius --help")
    console_out.print("  lucius --version")
    console_out.print("  lucius <entity>")
    console_out.print("  lucius <entity> <action> --args '<json>' [--format json|table|plain|csv]")
    console_out.print("  lucius <entity> <action> --help\n")

    table = Table(title="Available Entities")
    table.add_column("Entity", style="cyan", no_wrap=True)
    table.add_column("Actions", style="green")
    table.add_column("Examples", style="yellow")
    entity_aliases = all_entities_with_aliases()
    for entity in sorted(registry.keys()):
        aliases = sorted(
            alias
            for alias in entity_aliases.get(entity, {entity})
            if alias != entity and "_" not in alias and "-" not in alias
        )
        alias_text = f" ({', '.join(aliases)})" if aliases else ""
        table.add_row(entity + alias_text, _format_action_list(registry[entity].keys()), f"lucius {entity}")
    console_out.print(table)


def print_entity_actions(entity: str, actions: dict[str, ActionSpec]) -> None:
    """Print available actions for one entity."""
    from rich.table import Table

    console_out.print(f"\nEntity: [bold cyan]{entity}[/bold cyan]\n")
    console_out.print("Usage:")
    console_out.print(f"  lucius {entity} <action> --args '<json>' [--format json|table|plain|csv]")
    console_out.print(f"  lucius {entity} <action> --help\n")

    table = Table(title=f"Actions for {entity}")
    table.add_column("Action", style="cyan", no_wrap=True)
    table.add_column("Mapped Tool", style="magenta")
    table.add_column("Description", style="green")
    for action_name in sorted(actions.keys()):
        spec = actions[action_name]
        summary = _first_line(spec.schema.get("description", "No description"))
        table.add_row(action_name, spec.tool_name, summary[:120])
    console_out.print(table)


def print_action_help(spec: ActionSpec) -> None:
    """Print help for one entity/action command."""
    from rich.panel import Panel

    schema = spec.schema
    input_schema = schema.get("input_schema", {})
    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])

    console_out.print(f"\n[bold cyan]Command:[/bold cyan] lucius {spec.entity} {spec.action}")
    console_out.print(f"[dim]Mapped tool:[/dim] {spec.tool_name}\n")
    console_out.print(f"[yellow]Description:[/yellow] {schema.get('description', 'No description')}\n")

    if properties:
        console_out.print("[yellow]Parameters:[/yellow]\n")
        for param_name, param_info in properties.items():
            param_type = param_info.get("type")
            if param_type is None and isinstance(param_info.get("anyOf"), list):
                types = [item.get("type") for item in param_info["anyOf"] if item.get("type") != "null"]
                param_type = "|".join(types) if types else "unknown"
            param_desc = param_info.get("description", "")
            req_marker = "[red]* (required)[/red]" if param_name in required else "[green](optional)[/green]"
            console_out.print(f"  [cyan]{param_name}[/cyan] : [dim]{param_type or 'unknown'}[/dim] {req_marker}")
            if param_desc:
                console_out.print(f"    {param_desc}\n")
    else:
        console_out.print("[yellow]Parameters:[/yellow] (no parameters)\n")

    example_args = _build_example_args(schema)
    if example_args:
        example_cmd = f"lucius {spec.entity} {spec.action} --args '{json.dumps(example_args)}'"
    else:
        example_cmd = f"lucius {spec.entity} {spec.action} --args '{{}}'"
    console_out.print("[yellow]Example:[/yellow]\n")
    console_out.print(Panel(example_cmd, title="Command"))


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
        raise CLIError(
            f"Unknown option '{token}'",
            hint="Supported options: --args/-a, --format/-f, --help/-h",
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


def _load_tool_function(tool_name: str) -> typing.Callable[..., typing.Awaitable[typing.Any]]:
    """Lazy-load a tool function by name from src.tools package."""
    try:
        resolved = resolve_tool_function(tool_name)
    except RuntimeError:
        raise CLIError(
            f"Implementation for tool '{tool_name}' not found",
            hint="Ensure the existing tool function exists in src/tools/*.py.",
            exit_code=2,
        ) from None
    return typing.cast(typing.Callable[..., typing.Awaitable[typing.Any]], resolved)


async def call_tool_function(tool_name: str, args: dict[str, typing.Any]) -> typing.Any:
    """Execute one service-backed tool function asynchronously."""
    tool_function = _load_tool_function(tool_name)
    try:
        return await tool_function(**args)
    except CLIError:
        raise
    except asyncio.CancelledError:
        raise CLIError(
            "Command execution cancelled",
            hint="The operation was interrupted",
            exit_code=130,
        ) from None
    except TypeError as e:
        raise CLIError(
            f"Invalid parameters for tool '{tool_name}': {e}",
            hint="Check parameter names and types with --help.",
            exit_code=1,
        ) from None
    except Exception as e:
        raise CLIError(
            f"Error executing '{tool_name}': {e}",
            hint=_error_hint_from_exception(e),
            exit_code=1,
        ) from None


def run_cli(argv: list[str]) -> None:
    """Route CLI command and execute."""
    if not argv or argv[0] in {"--help", "-h", "help"}:
        schemas = load_tool_schemas()
        registry = build_command_registry(schemas)
        print_global_help(registry)
        return

    if argv[0] in {"--version", "-V", "version"}:
        console_out.print(f"lucius {__version__}")
        return

    if argv[0] in {"list", "call"}:
        raise CLIError(
            "Legacy command style detected",
            hint=(
                "Use entity/action format instead. Examples:\n  lucius test_case\n  lucius test_case list --args '{}'"
            ),
            exit_code=1,
        )

    schemas = load_tool_schemas()
    registry = build_command_registry(schemas)

    entity = resolve_entity_name(argv[0], registry)
    actions = registry[entity]

    if len(argv) == 1 or argv[1] in {"--help", "-h", "help"}:
        print_entity_actions(entity, actions)
        return

    action = resolve_action_name(entity, argv[1], actions)
    spec = actions[action]
    options = parse_action_options(argv[2:])

    if options.output_format not in OUTPUT_FORMATS:
        raise CLIError(
            f"Invalid format '{options.output_format}'",
            hint="Use --format json|table|plain|csv",
            exit_code=1,
        )

    if options.show_help:
        print_action_help(spec)
        return

    try:
        args_dict = json.loads(options.args_json)
    except json.JSONDecodeError as e:
        raise CLIError(
            f"Invalid JSON in --args: {e}",
            hint="Example: --args '{\"test_case_id\": 1234}'",
            exit_code=1,
        ) from None

    if not isinstance(args_dict, dict):
        raise CLIError(
            "Invalid --args payload: expected a JSON object",
            hint="Example: --args '{\"project_id\": 1}'",
            exit_code=1,
        )

    validate_args_against_schema(args_dict, f"{entity} {action}", spec.schema)
    tool_output_format = "plain" if options.output_format == "plain" else "json"
    tool_args = {**args_dict, "output_format": tool_output_format}
    result = asyncio.run(call_tool_function(spec.tool_name, tool_args))

    if options.output_format in {"plain", "json"}:
        if isinstance(result, str):
            console_out.print(result, end="")
            return
        raise CLIError(
            f"Tool '{spec.tool_name}' returned non-string output for '{options.output_format}' mode",
            hint="Tool output contract requires plain/json modes to return serialized text output.",
            exit_code=2,
        )

    if not isinstance(result, str):
        raise CLIError(
            f"Tool '{spec.tool_name}' returned non-string output for '{options.output_format}' mode",
            hint="Tool output contract requires JSON text output for table/csv rendering.",
            exit_code=2,
        )

    try:
        parsed: typing.Any = json.loads(result)
    except json.JSONDecodeError as exc:
        raise CLIError(
            f"Tool '{spec.tool_name}' returned invalid JSON for '{options.output_format}' mode: {exc}",
            hint="Tool output contract requires valid JSON text output for table/csv rendering.",
            exit_code=2,
        ) from None

    format_output_data(select_tabular_payload(parsed), options.output_format)


def main() -> None:
    """CLI entry point."""
    logging.disable(logging.CRITICAL)
    try:
        run_cli(sys.argv[1:])
    except CLIError as error:
        _exit_with_cli_error(error)
    except KeyboardInterrupt:
        raise SystemExit(130) from None
    except Exception as error:
        _exit_with_cli_error(
            CLIError(
                f"Unexpected CLI error: {error}",
                hint=_error_hint_from_exception(error),
                exit_code=1,
            )
        )


if __name__ == "__main__":
    main()
