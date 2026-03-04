"""Telemetry helpers for runtime tool instrumentation."""

from __future__ import annotations

import inspect
import time
import typing
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.telemetry_service import TelemetryService

type ToolFn = Callable[..., Awaitable[object]]

_telemetry_service: TelemetryService | None = None


def set_telemetry_service(service: TelemetryService) -> None:
    """Configure the telemetry service used by tool wrappers."""
    global _telemetry_service
    _telemetry_service = service


def wrap_tool_with_telemetry(tool: ToolFn) -> ToolFn:
    """Wrap a tool to emit telemetry without changing tool behavior."""

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
