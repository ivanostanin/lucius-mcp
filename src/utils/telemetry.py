"""Telemetry helpers for runtime tool instrumentation."""

from __future__ import annotations

import inspect
import time
import typing
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from src.services.telemetry_service import TelemetryService

type ToolFn = Callable[..., Awaitable[object]]

_telemetry_service: TelemetryService | None = None


def set_telemetry_service(service: TelemetryService) -> None:
    """Configure the telemetry service used by tool wrappers."""
    global _telemetry_service
    _telemetry_service = service


def wrap_tool_with_telemetry(tool: ToolFn, *, output_model: type[BaseModel] | None = None) -> ToolFn:
    """Wrap a tool with telemetry and the MCP-only structured-output contract."""

    @wraps(tool)
    async def wrapped(*args: object, **kwargs: object) -> object:
        started_at = time.perf_counter()
        try:
            result = await tool(*args, **kwargs)
        except Exception as exc:
            duration_ms = (time.perf_counter() - started_at) * 1000.0
            if _telemetry_service is not None:
                _telemetry_service.emit_tool_usage_event(
                    tool_name=tool.__name__,
                    outcome="error",
                    duration_ms=duration_ms,
                    error=exc,
                )
            raise

        if output_model is not None:
            result = _apply_mcp_output_contract(result, output_model)

        duration_ms = (time.perf_counter() - started_at) * 1000.0
        if _telemetry_service is not None:
            _telemetry_service.emit_tool_usage_event(
                tool_name=tool.__name__,
                outcome="success",
                duration_ms=duration_ms,
            )
        return result

    wrapped.__signature__ = inspect.signature(tool)  # type: ignore[attr-defined]
    return typing.cast(ToolFn, wrapped)


def _apply_mcp_output_contract(result: object, output_model: type[BaseModel]) -> object:
    """Validate structured payloads and keep plain output text-only for MCP."""
    from fastmcp.tools.base import ToolResult
    from mcp.types import TextContent

    if isinstance(result, str):
        return ToolResult(content=[TextContent(type="text", text=result)])
    if not isinstance(result, ToolResult) or result.structured_content is None:
        return result

    payload = output_model.model_validate(result.structured_content).model_dump(
        mode="json", by_alias=True, exclude_unset=True
    )
    return ToolResult(
        content=result.content,
        structured_content=payload,
        meta=result.meta,
        is_error=result.is_error,
    )
