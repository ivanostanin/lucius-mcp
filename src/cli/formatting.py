"""
CLI output formatting helpers.
"""

from __future__ import annotations

import csv
import io
import json
import typing

from src.cli.models import CLIError


def format_json(data: typing.Any) -> str:
    """Format data as JSON string."""
    return json.dumps(data, ensure_ascii=False, default=str, indent=2)


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


def _structured_tool_payload(result: typing.Any) -> typing.Any | None:
    """Extract structured content from ToolResult-like outputs."""
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        return structured
    return getattr(result, "structuredContent", None)


def _tool_result_to_json_text(result: typing.Any) -> str | None:
    """Render structured tool output as compact JSON text for CLI formats."""
    structured = _structured_tool_payload(result)
    if structured is None:
        return None
    return json.dumps(structured, ensure_ascii=False, default=str, separators=(",", ":"))


def _tool_schema_rows(data: dict[str, typing.Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for tool_name in sorted(data):
        tool_info = data[tool_name]
        properties = tool_info.get("input_schema", {}).get("properties", {})
        param_list = list(properties.keys()) if properties else ["(no parameters)"]
        rows.append(
            {
                "tool_name": tool_name,
                "description": tool_info.get("description", "No description"),
                "parameters": ", ".join(param_list[:5]) + ("..." if len(param_list) > 5 else ""),
            }
        )
    return rows


def _ordered_columns(rows: list[dict[str, typing.Any]]) -> list[str]:
    column_names: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in column_names:
                column_names.append(str(key))
    return column_names


def _new_result_table() -> typing.Any:
    from rich.table import Table

    return Table(title="Command Result")


def _format_tool_schema_table(data: dict[str, typing.Any]) -> typing.Any:
    from rich.table import Table

    rows = _tool_schema_rows(data)
    table = Table(title="Available Lucius Tools")
    table.add_column("Tool Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")
    table.add_column("Parameters", style="yellow")
    for row in rows:
        table.add_row(row["tool_name"], row["description"][:60], row["parameters"])
    return table


def _format_dict_table(data: dict[str, typing.Any]) -> typing.Any:
    table = _new_result_table()
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    for key, value in data.items():
        table.add_row(str(key), _format_table_value(value))
    return table


def _format_list_table(data: list[typing.Any]) -> typing.Any:
    if not data:
        table = _new_result_table()
        table.add_column("Result", style="green")
        table.add_row("(empty)")
        return table

    if all(isinstance(item, dict) for item in data):
        rows = typing.cast(list[dict[str, typing.Any]], data)
        column_names = _ordered_columns(rows)
        table = _new_result_table()
        for name in column_names:
            table.add_column(name, style="green")
        for item in rows:
            table.add_row(*[_format_table_value(item.get(name)) for name in column_names])
        return table

    table = _new_result_table()
    table.add_column("Value", style="green")
    for item in data:
        table.add_row(_format_table_value(item))
    return table


def format_as_table(data: typing.Any) -> typing.Any:
    """Format tool schemas or generic results as a Rich table."""
    if _is_tool_schema_map(data):
        return _format_tool_schema_table(typing.cast(dict[str, typing.Any], data))

    if isinstance(data, dict):
        return _format_dict_table(data)

    if isinstance(data, list):
        return _format_list_table(data)

    table = _new_result_table()
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
        rows = _tool_schema_rows(typing.cast(dict[str, typing.Any], data))
        writer.writerow(["tool_name", "description", "parameters"])
        for row in rows:
            writer.writerow([row["tool_name"], row["description"], row["parameters"]])
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
            rows = typing.cast(list[dict[str, typing.Any]], data)
            column_names = _ordered_columns(rows)
            writer.writerow(column_names)
            for item in rows:
                writer.writerow([_format_csv_value(item.get(name)) for name in column_names])
            return output.getvalue()

        writer.writerow(["value"])
        for item in data:
            writer.writerow([_format_csv_value(item)])
        return output.getvalue()

    writer.writerow(["value"])
    writer.writerow([_format_csv_value(data)])
    return output.getvalue()


def render_output(data: typing.Any, output_format: str, console: typing.Any) -> None:
    """Print command output in the selected format."""
    if output_format == "json":
        console.print_json(format_json(data))
    elif output_format == "table":
        console.print(format_as_table(data))
    elif output_format == "csv":
        console.print(format_as_csv(data), end="")
    elif output_format == "plain":
        console.print(format_as_plain(data))
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
