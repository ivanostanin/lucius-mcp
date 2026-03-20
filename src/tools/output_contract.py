"""Shared output-contract helpers for tool functions."""

from __future__ import annotations

import inspect
import json
import typing
import unittest.mock
from dataclasses import asdict, is_dataclass

OutputFormat = typing.Literal["plain", "json"]
SUPPORTED_OUTPUT_FORMATS: set[str] = {"plain", "json"}
DEFAULT_OUTPUT_FORMAT: OutputFormat = "plain"


def _to_plain_output(result: typing.Any) -> str:
    """Normalize tool output to plain text."""
    if isinstance(result, str):
        return result.replace("\\n", "\n")
    return str(result).replace("\\n", "\n")


def _to_json_payload(result: typing.Any) -> typing.Any:
    """Normalize tool output to JSON-serializable payload."""
    if result is None or isinstance(result, (str, int, float, bool)):
        return result

    if isinstance(result, unittest.mock.Mock):
        return str(result)

    if isinstance(result, dict):
        return {str(key): _to_json_payload(value) for key, value in result.items()}
    if isinstance(result, (list, tuple, set)):
        return [_to_json_payload(value) for value in result]

    model_dump_static = inspect.getattr_static(result, "model_dump", None)
    if callable(model_dump_static):
        model_dump = getattr(result, "model_dump", None)
        if callable(model_dump):
            return _to_json_payload(model_dump())

    if is_dataclass(result) and not isinstance(result, type):
        return _to_json_payload(asdict(result))

    # Avoid traversing arbitrary __dict__ objects (for example mocks), which can
    # retain large cyclic graphs and cause runaway memory usage during serialization.
    return str(result)


def _validate_output_format(output_format: str) -> OutputFormat:
    if output_format not in SUPPORTED_OUTPUT_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_OUTPUT_FORMATS))
        raise ValueError(f"Unsupported output_format '{output_format}'. Supported values: {supported}")
    return typing.cast(OutputFormat, output_format)


def apply_output_contract(result: typing.Any, output_format: str) -> str:
    """Render tool output according to the tool-level output contract."""
    normalized = _validate_output_format(output_format)

    if normalized == "plain":
        return _to_plain_output(result)

    payload = _to_json_payload(result)
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def render_output(
    *,
    plain: str,
    json_payload: typing.Any,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
) -> str:
    """Render explicit plain/json payloads under the output contract."""
    normalized = _validate_output_format(output_format)
    if normalized == "plain":
        return _to_plain_output(plain)
    return json.dumps(_to_json_payload(json_payload), ensure_ascii=False, separators=(",", ":"))


def render_message_output(
    message: str,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
) -> str:
    """Render message-only tool outputs (plain string + JSON message object)."""
    return render_output(
        plain=message,
        json_payload={"message": _to_plain_output(message)},
        output_format=output_format,
    )


def render_confirmation_required(
    *,
    action: str,
    plain: str,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    **payload_fields: typing.Any,
) -> str:
    """Render a standard confirmation-required response envelope."""
    return render_output(
        plain=plain,
        json_payload={
            "requires_confirmation": True,
            "action": action,
            **payload_fields,
        },
        output_format=output_format,
    )


def render_collection_output(
    *,
    items: list[typing.Any],
    plain_empty: str,
    plain_lines: list[str] | None = None,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    total: int | None = None,
    **payload_fields: typing.Any,
) -> str:
    """Render a standard collection response envelope."""
    payload = {
        **payload_fields,
        "items": items,
        "total": len(items) if total is None else total,
    }
    if not items:
        return render_output(plain=plain_empty, json_payload=payload, output_format=output_format)
    return render_output(
        plain="\n".join(plain_lines or []),
        json_payload=payload,
        output_format=output_format,
    )
