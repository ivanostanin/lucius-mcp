"""Definitions for CLI-local commands that are not backed by MCP tools."""

from __future__ import annotations

CLI_LOCAL_COMMANDS = ["auth"]
AUTH_SUBCOMMANDS = ["status"]
AUTH_OPTIONS = ["--url", "--token", "--project", "--help", "-h"]
