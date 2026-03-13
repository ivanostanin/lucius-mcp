"""
JSON-schema-like argument validation helpers for CLI command input.
"""

from __future__ import annotations

import typing
from dataclasses import dataclass


@dataclass
class SchemaValidationError(Exception):
    """Validation failure details that can be translated to CLI-facing errors."""

    message: str
    hint: str | None = None
    exit_code: int = 1

    def __post_init__(self) -> None:
        super().__init__(self.message)


def _matches_type(value: typing.Any, expected_type: str) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "null":
        return value is None
    return True


def _describe_expected_type(schema: dict[str, typing.Any]) -> str:
    expected = schema.get("type")
    if isinstance(expected, str):
        return expected
    any_of = schema.get("anyOf")
    if isinstance(any_of, list):
        types = [
            typing.cast(str, entry.get("type"))
            for entry in any_of
            if isinstance(entry, dict) and isinstance(entry.get("type"), str)
        ]
        if types:
            return "|".join(types)
    return "valid schema type"


def _validate_any_of(
    value: typing.Any,
    schema: dict[str, typing.Any],
    path: str,
) -> tuple[bool, str | None]:
    any_of = schema.get("anyOf")
    if not isinstance(any_of, list) or not any_of:
        return False, None

    for candidate in any_of:
        if isinstance(candidate, dict) and _validate_value_against_schema(value, candidate, path) is None:
            return True, None

    return True, f"expected type {_describe_expected_type(schema)}, got {type(value).__name__}"


def _validate_enum(value: typing.Any, schema: dict[str, typing.Any]) -> str | None:
    enum_values = schema.get("enum")
    if isinstance(enum_values, list) and value not in enum_values:
        return f"must be one of {enum_values!r}"
    return None


def _validate_type(value: typing.Any, schema: dict[str, typing.Any]) -> str | None:
    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not _matches_type(value, expected_type):
        return f"expected type {expected_type}, got {type(value).__name__}"
    return None


def _validate_string_constraints(value: typing.Any, schema: dict[str, typing.Any]) -> str | None:
    if not isinstance(value, str):
        return None

    min_length = schema.get("minLength")
    max_length = schema.get("maxLength")
    if isinstance(min_length, int) and len(value) < min_length:
        return f"length must be >= {min_length}"
    if isinstance(max_length, int) and len(value) > max_length:
        return f"length must be <= {max_length}"
    return None


def _validate_numeric_constraints(value: typing.Any, schema: dict[str, typing.Any]) -> str | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None

    minimum = schema.get("minimum")
    exclusive_minimum = schema.get("exclusiveMinimum")
    maximum = schema.get("maximum")
    exclusive_maximum = schema.get("exclusiveMaximum")

    if isinstance(minimum, (int, float)) and value < minimum:
        return f"must be >= {minimum}"
    if isinstance(exclusive_minimum, (int, float)) and value <= exclusive_minimum:
        return f"must be > {exclusive_minimum}"
    if isinstance(maximum, (int, float)) and value > maximum:
        return f"must be <= {maximum}"
    if isinstance(exclusive_maximum, (int, float)) and value >= exclusive_maximum:
        return f"must be < {exclusive_maximum}"
    return None


def _validate_array_items(value: typing.Any, schema: dict[str, typing.Any], path: str) -> str | None:
    if not isinstance(value, list):
        return None

    item_schema = schema.get("items")
    if not isinstance(item_schema, dict):
        return None

    for index, item in enumerate(value):
        nested_path = f"{path}[{index}]"
        nested_error = _validate_value_against_schema(item, item_schema, nested_path)
        if nested_error:
            return nested_error
    return None


def _validate_object_properties(value: typing.Any, schema: dict[str, typing.Any], path: str) -> str | None:
    if not isinstance(value, dict):
        return None

    additional = schema.get("additionalProperties", True)
    if not isinstance(additional, dict):
        return None

    for key, nested_value in value.items():
        nested_path = f"{path}.{key}"
        nested_error = _validate_value_against_schema(nested_value, additional, nested_path)
        if nested_error:
            return nested_error
    return None


def _validate_value_against_schema(value: typing.Any, schema: dict[str, typing.Any], path: str) -> str | None:
    handled_any_of, any_of_error = _validate_any_of(value, schema, path)
    if handled_any_of:
        return any_of_error

    validators: tuple[typing.Callable[[], str | None], ...] = (
        lambda: _validate_enum(value, schema),
        lambda: _validate_type(value, schema),
        lambda: _validate_string_constraints(value, schema),
        lambda: _validate_numeric_constraints(value, schema),
        lambda: _validate_array_items(value, schema, path),
        lambda: _validate_object_properties(value, schema, path),
    )
    for validate in validators:
        error = validate()
        if error:
            return error
    return None


def validate_args_against_schema(
    args: dict[str, typing.Any],
    command_name: str,
    tool_schema: dict[str, typing.Any],
) -> None:
    """Validate JSON arguments against a tool input schema."""
    input_schema = tool_schema.get("input_schema", {})
    required = input_schema.get("required", [])
    properties = input_schema.get("properties", {})

    for param_name in required:
        if param_name not in args:
            raise SchemaValidationError(
                f"Command '{command_name}' requires parameter '{param_name}'",
                hint=f"Provide: --args '{{\"{param_name}\": <value>}}'",
            )

    for param_name in args:
        if param_name not in properties:
            valid = ", ".join(properties.keys()) if properties else "(none)"
            raise SchemaValidationError(
                f"Unknown parameter '{param_name}' for command '{command_name}'",
                hint=f"Valid parameters: {valid}",
            )
        schema = properties.get(param_name)
        if isinstance(schema, dict):
            error = _validate_value_against_schema(args[param_name], schema, param_name)
            if error:
                raise SchemaValidationError(
                    f"Invalid value for parameter '{param_name}' in command '{command_name}': {error}",
                    hint="Check parameter types and constraints with: lucius <entity> <action> --help.",
                )
