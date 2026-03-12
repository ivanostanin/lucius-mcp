#!/usr/bin/env python3
"""
Build-time tool schema generator for Lucius CLI.

This script extracts tool schemas from the MCP server and generates
a static JSON file that the CLI can use for:

1. Fast `lucius list` command (no MCP client needed)
2. Individual tool help: `lucius call <tool> --help`
3. Type-safe validation for CLI arguments

This script is run during the build process to generate src/cli/data/tool_schemas.json
"""

import asyncio
import json
import sys
import typing
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.main import mcp  # noqa: E402


async def extract_tool_schemas() -> dict[str, dict[str, typing.Any]]:
    """
    Extract tool schemas from MCP server.

    Returns:
        Dictionary mapping tool names to their schemas with all metadata.
    """
    tools = await mcp.list_tools()

    schemas: dict[str, dict[str, typing.Any]] = {}
    for tool in tools:
        # Get parameters as dict (already converted by FastMCP)
        params_dict = tool.parameters if tool.parameters else {}

        tool_schema: dict[str, typing.Any] = {
            "name": tool.name,
            "description": tool.description or "",
            "input_schema": params_dict,
            "tags": getattr(tool, "tags", []),
            "annotations": getattr(tool, "annotations", {}),
        }
        schemas[tool.name] = tool_schema

    return schemas


async def main() -> None:
    """
    Main function to generate tool schemas JSON file.
    """
    print("Extracting tool schemas from MCP server...")

    schemas = await extract_tool_schemas()

    print(f"Extracted {len(schemas)} tools")

    # Create data directory if it doesn't exist
    data_dir = project_root / "src" / "cli" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Write schemas to JSON file
    schemas_file = data_dir / "tool_schemas.json"
    with schemas_file.open("w") as f:
        json.dump(schemas, f, indent=2, default=str)

    print(f"Tool schemas written to {schemas_file}")
    print(f"Tool list size: {schemas_file.stat().st_size} bytes")


if __name__ == "__main__":
    asyncio.run(main())
