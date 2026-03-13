"""
Shared helpers for resolving existing tool callables from src.tools.
"""

from __future__ import annotations

import importlib
import pkgutil
import typing


def resolve_tool_function(tool_name: str) -> typing.Callable[..., typing.Any]:
    """Resolve a tool function by name from src.tools package modules."""
    tools_module = importlib.import_module("src.tools")
    top_level = getattr(tools_module, tool_name, None)
    if callable(top_level):
        return typing.cast(typing.Callable[..., typing.Any], top_level)

    package_path = getattr(tools_module, "__path__", [])
    for module_info in pkgutil.iter_modules(package_path):
        module = importlib.import_module(f"src.tools.{module_info.name}")
        candidate = getattr(module, tool_name, None)
        if callable(candidate):
            return typing.cast(typing.Callable[..., typing.Any], candidate)

    raise RuntimeError(f"Unable to locate tool function '{tool_name}' in src.tools package")
