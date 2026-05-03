"""
CLI output formatting helpers.
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import typing
from dataclasses import dataclass
from datetime import UTC, datetime, tzinfo
from pathlib import Path
from zoneinfo import TZPATH, ZoneInfo, ZoneInfoNotFoundError

from src.cli.models import CLIError


@dataclass(frozen=True)
class DisplayTimezone:
    """Timezone and display label used for table datetime rendering."""

    tzinfo: tzinfo
    label: str


_TIME_FIELD_PREFIXES = {
    "created",
    "end",
    "ended",
    "finish",
    "finished",
    "last",
    "modified",
    "start",
    "started",
    "stop",
    "stopped",
    "update",
    "updated",
}


def format_json(data: typing.Any) -> str:
    """Format data as JSON string."""
    return json.dumps(data, ensure_ascii=False, default=str, indent=2)


def _is_tool_schema_map(data: typing.Any) -> bool:
    if not isinstance(data, dict) or not data:
        return False
    return all(isinstance(value, dict) and "input_schema" in value for value in data.values())


def _timezone_from_key(key: str) -> DisplayTimezone | None:
    try:
        return DisplayTimezone(ZoneInfo(key), key)
    except (ValueError, ZoneInfoNotFoundError):
        return None


def _timezone_from_localtime_path(path: Path) -> DisplayTimezone | None:
    try:
        resolved_path = path.resolve(strict=True)
    except OSError:
        return None

    for tz_root in TZPATH:
        try:
            resolved_root = Path(tz_root).resolve(strict=True)
            zone_key = resolved_path.relative_to(resolved_root).as_posix()
        except (OSError, ValueError):
            continue
        return _timezone_from_key(zone_key)

    return None


def _resolve_display_timezone() -> DisplayTimezone:
    """Resolve local display timezone, falling back deterministically to UTC."""
    env_tz = os.environ.get("TZ")
    if env_tz:
        candidate = env_tz[1:] if env_tz.startswith(":") else env_tz
        display_timezone = (
            _timezone_from_localtime_path(Path(candidate))
            if Path(candidate).is_absolute()
            else _timezone_from_key(candidate)
        )
        return display_timezone or DisplayTimezone(UTC, "UTC")

    return _timezone_from_localtime_path(Path("/etc/localtime")) or DisplayTimezone(UTC, "UTC")


def _is_datetime_field_name(field_name: str | None) -> bool:
    if not field_name:
        return False

    snake_case_name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", field_name)
    normalized = snake_case_name.replace("-", "_").replace(" ", "_").replace(".", "_").lower()
    tokens = [token for token in normalized.split("_") if token]
    if any(token in {"date", "datetime", "timestamp"} for token in tokens):
        return True
    if normalized.endswith("_at"):
        return True
    if normalized == "time":
        return True
    if tokens and tokens[-1] == "time":
        return any(token in _TIME_FIELD_PREFIXES for token in tokens[:-1])
    return normalized.endswith(("date", "datetime", "timestamp")) or any(
        normalized == f"{prefix}time" for prefix in _TIME_FIELD_PREFIXES
    )


def _parse_datetime_value(value: typing.Any, field_name: str | None = None) -> datetime | None:
    """Parse a table value as datetime only for date/time-like fields."""
    if not _is_datetime_field_name(field_name):
        return None

    try:
        if isinstance(value, bool):
            return None
        if isinstance(value, int | float):
            epoch_value = float(value)
            if abs(epoch_value) >= 100_000_000_000:
                epoch_value = epoch_value / 1000
            return datetime.fromtimestamp(epoch_value, tz=UTC)
        if isinstance(value, str):
            candidate = value.strip()
            if not candidate:
                return None
            if candidate.endswith("Z"):
                candidate = candidate[:-1] + "+00:00"
            parsed = datetime.fromisoformat(candidate)
            return parsed if parsed.tzinfo is not None else None
    except (OSError, OverflowError, ValueError):
        return None

    return None


def _render_table_cell(
    value: typing.Any,
    field_name: str | None,
    display_timezone: DisplayTimezone,
) -> tuple[str, bool, bool]:
    parsed_datetime = _parse_datetime_value(value, field_name)
    if parsed_datetime is not None:
        try:
            return parsed_datetime.astimezone(display_timezone.tzinfo).strftime("%Y-%m-%d %H:%M:%S"), True, False
        except (OSError, OverflowError, ValueError):
            return parsed_datetime.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S"), True, True

    if isinstance(value, (dict, list)):
        rendered = json.dumps(value, default=str)
        return (rendered if len(rendered) <= 200 else rendered[:197] + "..."), False, False
    return str(value), False, False


def _format_table_value(value: typing.Any) -> str:
    rendered, _, _ = _render_table_cell(value, None, _resolve_display_timezone())
    return rendered


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


def _apply_timezone_caption(
    table: typing.Any,
    display_timezone: DisplayTimezone,
    has_datetime: bool,
    used_utc_fallback: bool = False,
) -> typing.Any:
    if has_datetime:
        timezone_label = "UTC" if used_utc_fallback else display_timezone.label
        table.caption = f"Timezone: {timezone_label}"
    return table


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
    display_timezone = _resolve_display_timezone()
    has_datetime = False
    used_utc_fallback = False
    table = _new_result_table()
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    for key, value in data.items():
        rendered, used_datetime, cell_used_utc_fallback = _render_table_cell(value, str(key), display_timezone)
        has_datetime = has_datetime or used_datetime
        used_utc_fallback = used_utc_fallback or cell_used_utc_fallback
        table.add_row(str(key), rendered)
    return _apply_timezone_caption(table, display_timezone, has_datetime, used_utc_fallback)


def _format_list_table(data: list[typing.Any]) -> typing.Any:
    display_timezone = _resolve_display_timezone()
    has_datetime = False
    used_utc_fallback = False
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
            rendered_row: list[str] = []
            for name in column_names:
                rendered, used_datetime, cell_used_utc_fallback = _render_table_cell(
                    item.get(name), name, display_timezone
                )
                has_datetime = has_datetime or used_datetime
                used_utc_fallback = used_utc_fallback or cell_used_utc_fallback
                rendered_row.append(rendered)
            table.add_row(*rendered_row)
        return _apply_timezone_caption(table, display_timezone, has_datetime, used_utc_fallback)

    table = _new_result_table()
    table.add_column("Value", style="green")
    for item in data:
        rendered, used_datetime, cell_used_utc_fallback = _render_table_cell(item, None, display_timezone)
        has_datetime = has_datetime or used_datetime
        used_utc_fallback = used_utc_fallback or cell_used_utc_fallback
        table.add_row(rendered)
    return _apply_timezone_caption(table, display_timezone, has_datetime, used_utc_fallback)


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
    display_timezone = _resolve_display_timezone()
    rendered, used_datetime, used_utc_fallback = _render_table_cell(data, None, display_timezone)
    table.add_row(rendered)
    return _apply_timezone_caption(table, display_timezone, used_datetime, used_utc_fallback)


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
