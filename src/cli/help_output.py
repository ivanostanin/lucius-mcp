"""
CLI help rendering helpers.
"""

from __future__ import annotations

import json
import typing

from src.cli.models import ActionSpec
from src.cli.route_matrix import all_entities_with_aliases


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


def render_global_help(registry: dict[str, dict[str, ActionSpec]], console: typing.Any) -> None:
    """Print root CLI help."""
    from rich.table import Table

    console.print("Lucius CLI - Entity/action interface\n")
    console.print("Usage:")
    console.print("  lucius --help")
    console.print("  lucius --version")
    console.print("  lucius auth [--url <url>] [--token <token>] [--project <id>]")
    console.print("  lucius auth status")
    console.print("  lucius list")
    console.print("  lucius list --help")
    console.print("  lucius <entity>")
    console.print("  lucius <entity> <action> --args '<json>' [--format json|table|plain|csv]")
    console.print("  lucius <entity> <action> --help\n")

    command_table = Table(title="CLI-Local Commands")
    command_table.add_column("Command", style="cyan", no_wrap=True)
    command_table.add_column("Description", style="green")
    command_table.add_row("auth", "Validate and save Allure CLI credentials for later runs.")
    command_table.add_row("list", "Print local static discovery metadata without credentials or network access.")
    console.print(command_table)

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
    console.print(table)


def render_entity_actions(entity: str, actions: dict[str, ActionSpec], console: typing.Any) -> None:
    """Print available actions for one entity."""
    from rich.table import Table

    console.print(f"\nEntity: [bold cyan]{entity}[/bold cyan]\n")
    console.print("Usage:")
    console.print(f"  lucius {entity} <action> --args '<json>' [--format json|table|plain|csv]")
    console.print(f"  lucius {entity} <action> --help\n")

    table = Table(title=f"Actions for {entity}")
    table.add_column("Action", style="cyan", no_wrap=True)
    table.add_column("Mapped Tool", style="magenta")
    table.add_column("Description", style="green")
    for action_name in sorted(actions.keys()):
        spec = actions[action_name]
        summary = _first_line(spec.schema.get("description", "No description"))
        table.add_row(action_name, spec.tool_name, summary[:120])
    console.print(table)


def render_action_help(spec: ActionSpec, console: typing.Any) -> None:
    """Print help for one entity/action command."""
    from rich.panel import Panel

    schema = spec.schema
    input_schema = schema.get("input_schema", {})
    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])

    console.print(f"\n[bold cyan]Command:[/bold cyan] lucius {spec.entity} {spec.action}")
    console.print(f"[dim]Mapped tool:[/dim] {spec.tool_name}\n")
    console.print(f"[yellow]Description:[/yellow] {schema.get('description', 'No description')}\n")

    if properties:
        console.print("[yellow]Parameters:[/yellow]\n")
        for param_name, param_info in properties.items():
            param_type = param_info.get("type")
            if param_type is None and isinstance(param_info.get("anyOf"), list):
                types = [item.get("type") for item in param_info["anyOf"] if item.get("type") != "null"]
                param_type = "|".join(types) if types else "unknown"
            param_desc = param_info.get("description", "")
            req_marker = "[red]* (required)[/red]" if param_name in required else "[green](optional)[/green]"
            console.print(f"  [cyan]{param_name}[/cyan] : [dim]{param_type or 'unknown'}[/dim] {req_marker}")
            if param_desc:
                console.print(f"    {param_desc}\n")
    else:
        console.print("[yellow]Parameters:[/yellow] (no parameters)\n")

    example_args = _build_example_args(schema)
    if example_args:
        example_cmd = f"lucius {spec.entity} {spec.action} --args '{json.dumps(example_args)}'"
    else:
        example_cmd = f"lucius {spec.entity} {spec.action} --args '{{}}'"
    console.print("[yellow]Example:[/yellow]\n")
    console.print(Panel(example_cmd, title="Command"))
