"""
CLI module for lucius-mcp command-line interface.

IMPORTANT: No HTTP server imports allowed in CLI module.
CLI uses stdio transport only for MCP communication.
"""

from __future__ import annotations


def main() -> None:
    """Lazy main import to avoid side effects during module execution."""
    from .cli_entry import main as cli_main

    cli_main()


__all__ = ["main"]
