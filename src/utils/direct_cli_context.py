"""Process-scoped state for CLI commands that exit after one invocation."""

from __future__ import annotations

from contextvars import ContextVar, Token

_DIRECT_CLI_REQUEST: ContextVar[bool] = ContextVar("lucius_direct_cli_attachment_request", default=False)


def set_direct_cli_attachment_request(value: bool) -> Token[bool]:
    """Mark a one-shot CLI invocation without importing runtime services."""
    return _DIRECT_CLI_REQUEST.set(value)


def reset_direct_cli_attachment_request(token: Token[bool]) -> None:
    """Restore the caller's attachment delivery context."""
    _DIRECT_CLI_REQUEST.reset(token)


def is_direct_cli_attachment_request() -> bool:
    """Return whether preparation is running in a process that exits after rendering."""
    return _DIRECT_CLI_REQUEST.get()
