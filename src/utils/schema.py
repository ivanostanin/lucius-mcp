"""Schema generation utilities for MCP tool input/output schemas."""

from __future__ import annotations

import typing
from typing import Any

from fastmcp.tools.function_parsing import ParsedFunction
from pydantic import BaseModel, TypeAdapter

from src.tools.output_schemas import get_output_schema_model


class SchemaGenerator:
    """Utility for generating JSON Schema from Pydantic models and function signatures."""

    def __init__(self) -> None:
        self._schema_cache: dict[type, dict[str, Any]] = {}

    def generate_input_schema(self, func: typing.Callable[..., Any]) -> dict[str, Any]:
        """Generate input schema from a function's signature using FastMCP's parsing."""
        parsed = ParsedFunction.from_function(func)
        schema = parsed.input_schema
        # Ensure 'required' is always present (JSON Schema spec requires it)
        if "required" not in schema:
            schema["required"] = []
        return schema

    def generate_output_schema(self, func: typing.Callable[..., Any]) -> dict[str, Any] | None:
        """Generate output schema from a function's return annotation."""
        parsed = ParsedFunction.from_function(func)
        return parsed.output_schema

    def generate_from_pydantic_model(self, model: type[BaseModel]) -> dict[str, Any]:
        """Generate JSON schema from a Pydantic model."""
        if model in self._schema_cache:
            return self._schema_cache[model]

        adapter = TypeAdapter(model)
        schema = adapter.json_schema(mode="serialization")

        # Compress schema (remove titles, etc.)
        schema = self._compress_schema(schema)

        self._schema_cache[model] = schema
        return schema

    def _compress_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Compress schema by removing titles and unnecessary metadata."""
        if not isinstance(schema, dict):
            return schema

        # Remove title keys
        schema.pop("title", None)

        # Ensure 'required' is always present at object level
        if schema.get("type") == "object" and "required" not in schema:
            schema["required"] = []

        # Recursively process properties
        if "properties" in schema and isinstance(schema["properties"], dict):
            for prop_name, prop_schema in schema["properties"].items():
                if isinstance(prop_schema, dict):
                    schema["properties"][prop_name] = self._compress_schema(prop_schema)

        # Recursively process items in arrays
        if "items" in schema and isinstance(schema["items"], dict):
            schema["items"] = self._compress_schema(schema["items"])

        # Recursively process $defs
        if "$defs" in schema and isinstance(schema["$defs"], dict):
            for def_name, def_schema in schema["$defs"].items():
                if isinstance(def_schema, dict):
                    schema["$defs"][def_name] = self._compress_schema(def_schema)

        return schema

    def get_output_schema_for_tool(self, func: typing.Callable[..., Any]) -> dict[str, Any] | None:
        """Get the output schema for a tool function based on its registered output model."""
        tool_name = func.__name__

        # Look up the explicit output schema model
        output_model = get_output_schema_model(tool_name)
        if output_model is not None:
            return self.generate_from_pydantic_model(output_model)

        # Fall back to auto-generation from return annotation
        auto_schema = self.generate_output_schema(func)
        if auto_schema is not None:
            # Ensure 'required' is always present
            if "required" not in auto_schema:
                auto_schema["required"] = []
            return auto_schema

        # No explicit output model and no return annotation -> valid empty object schema
        return {"type": "object", "properties": {}, "required": []}


# Global schema generator instance
_schema_generator = SchemaGenerator()


def get_schema_generator() -> SchemaGenerator:
    """Get the global schema generator instance."""
    return _schema_generator


def get_tool_input_schema(func: typing.Callable[..., Any]) -> dict[str, Any]:
    """Get the input schema for a tool function."""
    return _schema_generator.generate_input_schema(func)


def get_tool_output_schema(func: typing.Callable[..., Any]) -> dict[str, Any] | None:
    """Get the output schema for a tool function."""
    return _schema_generator.get_output_schema_for_tool(func)
