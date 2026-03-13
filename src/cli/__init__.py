"""
CLI module for lucius-mcp command-line interface.

IMPORTANT: No HTTP server imports allowed in CLI module.
CLI does not depend on FastMCP runtime; it calls service-backed tool functions directly.
"""

from __future__ import annotations


def main() -> None:
    """Lazy main import to avoid side effects during module execution."""
    from .cli_entry import main as cli_main

    cli_main()


__all__ = ["main"]
