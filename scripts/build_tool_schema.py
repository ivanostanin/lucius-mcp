#!/usr/bin/env python3
"""
Build-time tool schema generator for Lucius CLI.

This script introspects existing tool functions directly (no FastMCP runtime)
and emits metadata used by:
1. `lucius <entity>` action discovery
2. `lucius <entity> <action> --help`
3. CLI argument validation
"""

from __future__ import annotations

import inspect
import json
import sys
import types
import typing
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.cli.route_matrix import CANONICAL_ROUTE_MATRIX, all_canonical_routes, all_route_tool_names  # noqa: E402
from src.cli.tool_resolver import resolve_tool_function  # noqa: E402


def _normalize_json_type(value: object) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def _annotated_metadata(
    annotation: object,
) -> tuple[object, str | None, dict[str, int | float]]:
    """Return (base_annotation, description, constraints)."""
    description: str | None = None
    constraints: dict[str, int | float] = {}
    base = annotation

    origin = typing.get_origin(annotation)
    if origin is typing.Annotated:
        args = typing.get_args(annotation)
        if args:
            base = args[0]
            for metadata in args[1:]:
                if isinstance(metadata, str) and description is None:
                    description = metadata
                meta_desc = getattr(metadata, "description", None)
                if isinstance(meta_desc, str) and meta_desc and description is None:
                    description = meta_desc

                for attr_name, schema_key in (
                    ("ge", "minimum"),
                    ("gt", "exclusiveMinimum"),
                    ("le", "maximum"),
                    ("lt", "exclusiveMaximum"),
                    ("max_length", "maxLength"),
                    ("min_length", "minLength"),
                ):
                    value = getattr(metadata, attr_name, None)
                    if isinstance(value, (int, float)):
                        constraints[schema_key] = value

    return base, description, constraints


def _type_to_schema(annotation: object) -> dict[str, typing.Any]:
    """Convert Python type annotation to minimal JSON schema fragment."""
    if annotation in {inspect._empty, typing.Any, object}:
        return {}

    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)

    if origin is typing.Literal:
        enum_values = list(args)
        schema: dict[str, typing.Any] = {"enum": enum_values}
        if enum_values:
            schema["type"] = _normalize_json_type(enum_values[0])
        return schema

    if origin is list:
        item_ann = args[0] if args else typing.Any
        return {"type": "array", "items": _type_to_schema(item_ann)}

    if origin is dict:
        value_ann = args[1] if len(args) == 2 else typing.Any
        return {"type": "object", "additionalProperties": _type_to_schema(value_ann) or True}

    if origin in {typing.Union, types.UnionType}:
        non_none = [item for item in args if item is not type(None)]
        has_none = len(non_none) != len(args)
        any_of = [_type_to_schema(item) for item in non_none]
        if has_none:
            any_of.append({"type": "null"})
        return {"anyOf": any_of} if any_of else {"type": "null"}

    primitive_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        type(None): "null",
    }
    if annotation in primitive_map:
        return {"type": primitive_map[typing.cast(type[object], annotation)]}

    return {"type": "object"}


def _build_input_schema(function: typing.Callable[..., typing.Any]) -> dict[str, typing.Any]:
    """Build JSON schema for function signature."""
    signature = inspect.signature(function)
    properties: dict[str, typing.Any] = {}
    required: list[str] = []

    for param_name, parameter in signature.parameters.items():
        if parameter.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
            continue
        if param_name == "output_format":
            continue

        annotation, description, constraints = _annotated_metadata(parameter.annotation)
        schema = _type_to_schema(annotation)
        if description:
            schema["description"] = description
        schema.update(constraints)

        if parameter.default is not inspect._empty:
            schema["default"] = parameter.default
        else:
            required.append(param_name)

        properties[param_name] = schema

    input_schema: dict[str, typing.Any] = {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
    }
    if required:
        input_schema["required"] = required
    return input_schema


def extract_tool_schemas() -> dict[str, dict[str, typing.Any]]:
    """Extract schemas for all canonical routes."""
    tool_schemas: dict[str, dict[str, typing.Any]] = {}

    for entity, action, tool_name in all_canonical_routes():
        function = resolve_tool_function(tool_name)
        doc = inspect.getdoc(function) or ""
        input_schema = _build_input_schema(function)
        example_args: dict[str, typing.Any] = {}
        for required_name in input_schema.get("required", []):
            required_schema = input_schema["properties"].get(required_name, {})
            param_type = required_schema.get("type")
            if param_type == "integer":
                example_args[required_name] = 123
            elif param_type == "number":
                example_args[required_name] = 1.23
            elif param_type == "boolean":
                example_args[required_name] = True
            elif param_type == "array":
                example_args[required_name] = []
            elif param_type == "object":
                example_args[required_name] = {}
            else:
                example_args[required_name] = "value"

        tool_schemas[tool_name] = {
            "name": tool_name,
            "entity": entity,
            "action": action,
            "description": doc,
            "input_schema": input_schema,
            "example_command": f"lucius {entity} {action} --args '{json.dumps(example_args)}'",
        }

    expected = all_route_tool_names()
    actual = set(tool_schemas.keys())
    if expected != actual:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise RuntimeError(f"Route/schema mismatch. Missing={missing} Extra={extra}")

    return dict(sorted(tool_schemas.items()))


def main() -> None:
    """Generate src/cli/data/tool_schemas.json from tool function metadata."""
    print("Extracting tool schemas from existing tool functions...")
    schemas = extract_tool_schemas()
    print(f"Extracted {len(schemas)} tools from canonical route matrix ({len(CANONICAL_ROUTE_MATRIX)} entities)")

    data_dir = project_root / "src" / "cli" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    schemas_file = data_dir / "tool_schemas.json"

    with schemas_file.open("w") as stream:
        json.dump(schemas, stream, indent=2, default=str)

    print(f"Tool schemas written to {schemas_file}")
    print(f"Schema file size: {schemas_file.stat().st_size} bytes")


if __name__ == "__main__":
    main()
