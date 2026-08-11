"""Mock helpers for tool modules that share names with package exports."""

from __future__ import annotations

from importlib import import_module
from typing import Any
from unittest.mock import patch as stdlib_patch


def patch(target: str, *args: Any, **kwargs: Any) -> Any:
    """Patch a tool module directly instead of resolving through ``src.tools``.

    On Python 3.10, ``unittest.mock.patch`` resolves ``src.tools.<tool>``
    through the package export first.  That export is a callable rather than
    the submodule, so attributes such as ``AllureClient`` cannot be found.
    Resolving only the requested submodule keeps the package exports intact.
    """
    parts = target.split(".")
    if len(parts) >= 4 and parts[:2] == ["src", "tools"]:
        patch_target = import_module(".".join(parts[:3]))
        for component in parts[3:-1]:
            patch_target = getattr(patch_target, component)
        return stdlib_patch.object(patch_target, parts[-1], *args, **kwargs)
    return stdlib_patch(target, *args, **kwargs)
