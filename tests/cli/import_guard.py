"""Helpers for asserting CLI import boundaries without a subprocess."""

from __future__ import annotations

import builtins
from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import patch


@contextmanager
def reject_imports(*blocked_prefixes: str) -> Iterator[None]:
    """Fail when code in this scope imports one of ``blocked_prefixes``."""

    original_import = builtins.__import__

    def guarded_import(name: str, *args: object, **kwargs: object) -> object:
        if any(name == prefix or name.startswith(f"{prefix}.") for prefix in blocked_prefixes):
            raise AssertionError(f"unexpected import: {name}")
        return original_import(name, *args, **kwargs)

    with patch.object(builtins, "__import__", guarded_import):
        yield
