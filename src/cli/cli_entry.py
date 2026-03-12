#!/usr/bin/env python3
"""
Lucius CLI - Type-safe CLI for lucius-mcp Allure TestOps MCP Server.

This CLI provides direct access to MCP tools from the command line,
without requiring an MCP client runtime.

KEY DESIGN PRINCIPLES:
- Lazy initialization: Fast startup (< 1s), MCP client loaded only on tool call
- Clean error output: No MCP/Python logs/tracebacks, only user-facing errors
- Individual tool help: Every tool has isolated --help generated from schema
- Multiple output formats: JSON (default), table, plain
- Use MCP tools directly: No reimplementation of business logic
- No HTTP server: CLI uses stdio transport only, no HTTP imports

Usage:
    lucius --help                         # Show help
    lucius --version                      # Show version
    lucius list                           # List all available tools (JSON format)
    lucius list --format table            # List tools in table format
    lucius list --format plain            # List tools in plain format
    lucius call <tool_name>               # Call a tool with help
    lucius call <tool_name> --help        # Show tool-specific help
    lucius call <tool_name> --args '{..}' # Call tool with JSON arguments
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import typing
from pathlib import Path

import rich.console
from cyclopts import App, Parameter

# NO EAGER IMPORTS OF SRC.MAIN.MCP - Causes slow startup!
# MCP client imported lazily only when lucius call executed
from src.version import __version__

# Setup
console_err = rich.console.Console(stderr=True)
console_out = rich.console.Console()

# NOTE: Logging is disabled in main() to avoid affecting tests
# Importing this module should not disable logging globally

# Path to static tool schemas generated at build time
TOOL_SCHEMAS_PATH = Path(__file__).parent / "data" / "tool_schemas.json"


class CLIError(Exception):
    """Custom exception for CLI errors with user-friendly messages."""

    def __init__(self, message: str, hint: str | None = None, exit_code: int = 1) -> None:
        self.message = message
        self.hint = hint
        self.exit_code = exit_code
        super().__init__(message)


def load_tool_schemas() -> dict[str, typing.Any]:
    """
    Load tool schemas from static JSON file (build-time generated).

    Returns:
        Directory of tool schemas

    Raises:
        CLIError: If schemas file not found or invalid
    """
    # Try multiple possible locations for bundled data files
    possible_paths = [
        TOOL_SCHEMAS_PATH,  # Standard: module/data/file
        Path(__file__).parent.parent / "data" / "tool_schemas.json",  # On Windows/macOS bundle
        Path(__file__).parent / "tool_schemas.json",  # Same directory as module
    ]

    # Find first existing path
    actual_path: Path | None = None
    for path in possible_paths:
        if path.exists():
            actual_path = path
            break

    if actual_path is None:
        raise CLIError(
            "Tool schemas not found",
            hint="Rebuild the CLI binary from the latest source code",
            exit_code=2,
        )

    try:
        with actual_path.open("r") as f:
            return typing.cast(dict[str, typing.Any], json.load(f))
    except json.JSONDecodeError as e:
        raise CLIError(
            f"Invalid tool schemas JSON: {e}",
            hint="Regenerate tool schemas by running scripts/build_tool_schema.py",
            exit_code=2,
        ) from None


def format_json(data: typing.Any) -> str:
    """Format data as JSON string."""
    return json.dumps(data, default=str, indent=2)


def _is_tool_schema_map(data: typing.Any) -> bool:
    """Return True when data looks like the static tool schema dictionary."""
    if not isinstance(data, dict) or not data:
        return False
    return all(isinstance(value, dict) and "input_schema" in value for value in data.values())


def _format_table_value(value: typing.Any) -> str:
    """Format arbitrary values for table cells."""
    if isinstance(value, (dict, list)):
        rendered = json.dumps(value, default=str)
        return rendered if len(rendered) <= 200 else rendered[:197] + "..."
    return str(value)


def format_as_table(data: typing.Any) -> typing.Any:
    """Format tool schemas or generic results as a table."""
    from rich.table import Table

    if _is_tool_schema_map(data):
        table = Table(title="Available Lucius Tools")
        table.add_column("Tool Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Parameters", style="yellow")

        for tool_name, tool_info in data.items():
            properties = tool_info.get("input_schema", {}).get("properties", {})
            param_list = list(properties.keys()) if properties else ["(no parameters)"]
            param_str = ", ".join(param_list[:5]) + ("..." if len(param_list) > 5 else "")
            table.add_row(
                tool_name,
                tool_info.get("description", "No description")[:60],
                param_str,
            )
        return table

    if isinstance(data, dict):
        table = Table(title="Command Result")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        for key, value in data.items():
            table.add_row(str(key), _format_table_value(value))
        return table

    if isinstance(data, list):
        if not data:
            table = Table(title="Command Result")
            table.add_column("Result", style="green")
            table.add_row("(empty)")
            return table

        if all(isinstance(item, dict) for item in data):
            column_names: list[str] = []
            for item in data:
                for key in item.keys():
                    if key not in column_names:
                        column_names.append(str(key))

            table = Table(title="Command Result")
            for name in column_names:
                table.add_column(name, style="green")
            for item in data:
                table.add_row(*[_format_table_value(item.get(name)) for name in column_names])
            return table

        table = Table(title="Command Result")
        table.add_column("Value", style="green")
        for item in data:
            table.add_row(_format_table_value(item))
        return table

    table = Table(title="Command Result")
    table.add_column("Value", style="green")
    table.add_row(_format_table_value(data))
    return table


def format_as_plain(data: typing.Any) -> str:
    """Format data as plain text (human-readable)."""
    if isinstance(data, dict):
        return "\n".join(f"{k}: {v}" for k, v in data.items())
    elif isinstance(data, list):
        return "\n".join(str(item) for item in data)
    else:
        return str(data)


def format_output_data(data: typing.Any, output_format: str = "json") -> None:
    """
    Format and output data based on specified format.

    Args:
        data: Data to output
        output_format: One of 'json', 'table', 'plain'
    """
    if output_format == "json":
        console_out.print_json(format_json(data))
    elif output_format == "table":
        console_out.print(format_as_table(data))
    elif output_format == "plain":
        console_out.print(format_as_plain(data))
    else:
        raise CLIError(
            f"Invalid output format: {output_format}",
            hint="Use --format json|table|plain",
            exit_code=1,
        )


def _error_hint_from_exception(error: Exception) -> str:
    """Generate a user-facing hint based on common tool failure patterns."""
    message = str(error).lower()
    if "not set in environment" in message or "api_token" in message:
        return "Set required credentials (ALLURE_API_TOKEN and ALLURE_API_URL) before calling tools."
    if "401" in message or "403" in message or "unauthorized" in message:
        return "Verify API credentials and permissions for the target project."
    if "validationerror" in message or "field required" in message:
        return "Check required parameters with: lucius call <tool_name> --help."
    if "json" in message:
        return "Ensure --args is valid JSON, for example: --args '{\"id\": 1234}'."
    return "Review arguments with: lucius call <tool_name> --help."


def _exit_with_cli_error(error: CLIError) -> typing.NoReturn:
    """Print a CLIError consistently and terminate."""
    console_err.print(f"[red]Error:[/red] {error.message}")
    if error.hint:
        console_err.print(f"\n[yellow]Hint:[/yellow] {error.hint}")
    raise SystemExit(error.exit_code)


def _rewrite_tool_help_args(argv: list[str]) -> list[str]:
    """
    Rewrite `lucius call <tool> --help` to `--show-help`.

    Cyclopts reserves `--help` for command help, so this preserves standard help
    for `lucius call --help` while enabling per-tool help when a tool name is provided.
    """
    if len(argv) < 3 or argv[0] != "call":
        return argv
    if argv[1].startswith("-"):
        return argv
    if "--help" not in argv and "-h" not in argv:
        return argv
    return [part if part not in ("--help", "-h") else "--show-help" for part in argv]


def print_tool_help(tool_name: str, tool_schema: dict[str, typing.Any]) -> None:
    """
    Print isolated tool help information.

    Args:
        tool_name: Name of the tool
        tool_schema: Tool schema dictionary
    """
    from rich.panel import Panel

    # Tool metadata
    console_out.print(f"\n[bold cyan]Tool: {tool_name}[/bold cyan]\n")

    # Description
    description = tool_schema.get("description", "No description")
    console_out.print(f"[yellow]Description:[/yellow] {description}\n")

    # Parameters
    input_schema = tool_schema.get("input_schema", {})
    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])

    if properties:
        console_out.print("[yellow]Parameters:[/yellow]\n")

        for param_name, param_info in properties.items():
            param_type = param_info.get("type", "unknown")
            param_desc = param_info.get("description", "")
            is_required = param_name in required

            req_marker = "[red]* (required)[/red]" if is_required else "[green](optional)[/green]"
            console_out.print(f"  [cyan]{param_name}[/cyan] : [dim]{param_type}[/dim] {req_marker}")
            if param_desc:
                console_out.print(f"    {param_desc}\n")
    else:
        console_out.print("[yellow]Parameters:[/yellow] (no parameters)\n")

    # Usage example
    example_args: dict[str, typing.Any] = {}
    for param_name in required:
        properties_info = properties.get(param_name, {})
        param_type = properties_info.get("type", "string")
        if param_type == "number":
            example_args[param_name] = 123
        elif param_type == "boolean":
            example_args[param_name] = True
        else:
            example_args[param_name] = "value"

    if example_args:
        console_out.print("[yellow]Example usage:[/yellow]\n")
        example_cmd = f"lucius call {tool_name} --args '{json.dumps(example_args)}'"
        console_out.print(Panel(example_cmd, title="Command"))
    else:
        console_out.print("[yellow]Example usage:[/yellow]\n")
        example_cmd = f"lucius call {tool_name} --args '{{}}'"
        console_out.print(Panel(example_cmd, title="Command"))


def validate_args_against_schema(
    args: dict[str, typing.Any],
    tool_name: str,
    tool_schema: dict[str, typing.Any],
) -> None:
    """
    Validate arguments against tool schema.

    Args:
        args: Parsed arguments
        tool_name: Tool name for error messages
        tool_schema: Tool schema dictionary

    Raises:
        CLIError: If validation fails
    """
    input_schema = tool_schema.get("input_schema", {})
    required = input_schema.get("required", [])
    properties = input_schema.get("properties", {})

    # Check required parameters
    for param_name in required:
        if param_name not in args:
            raise CLIError(
                f"Tool '{tool_name}' requires parameter '{param_name}'",
                hint=f"Provide: --args '{{\"{param_name}\": <value>}}'",
                exit_code=1,
            )

    # Check unknown parameters
    for param_name in args:
        if param_name not in properties:
            raise CLIError(
                f"Unknown parameter '{param_name}' for tool '{tool_name}'",
                hint=f"Valid parameters: {', '.join(properties.keys())}",
                exit_code=1,
            )


async def call_tool_mcp(tool_name: str, args: dict[str, typing.Any]) -> typing.Any:
    """
    Call MCP tool asynchronously (lazy import of MCP client).

    This is the ONLY place where we import src.main.mcp to ensure lazy loading.

    Args:
        tool_name: Name of the tool to call
        args: Arguments to pass to the tool

    Returns:
        Tool result

    Raises:
        CLIError: If tool call fails
    """
    # Lazy import of MCP client - only loaded when tool is called
    from src.main import mcp

    try:
        # Get tool first to validate it exists
        tool = await mcp.get_tool(tool_name)
        if tool is None:
            available_tools = [t.name for t in await mcp.list_tools()]
            raise CLIError(
                f"Tool '{tool_name}' not found",
                hint="Available tools:\n" + "\n".join(f"  - {name}" for name in sorted(available_tools)),
                exit_code=1,
            )

        # Call the tool
        result = await mcp.call_tool(tool_name, arguments=args)

        # Format result - extract content from ToolResult
        if hasattr(result, "content"):
            # Handle ToolResult object from FastMCP
            if len(result.content) == 1 and hasattr(result.content[0], "text"):
                # Single text result
                try:
                    return json.loads(result.content[0].text)
                except json.JSONDecodeError:
                    # Return as text if not valid JSON
                    return result.content[0].text
            else:
                # Multi-part result
                formatted_result: list[dict[str, typing.Any]] = []
                for item in result.content:
                    if hasattr(item, "text"):
                        try:
                            formatted_result.append(json.loads(item.text))
                        except json.JSONDecodeError:
                            formatted_result.append({"type": "text", "content": item.text})
                    elif hasattr(item, "data"):
                        formatted_result.append(
                            {
                                "type": "resource",
                                "mimeType": getattr(item, "mime_type", "application/octet-stream"),
                                "data": str(item.data)[:100] + "...",  # Truncate for display
                            }
                        )
                return formatted_result
        else:
            # Return as-is
            return result

    except CLIError:
        # Re-raise CLIError as-is
        raise
    except asyncio.CancelledError:
        raise CLIError(
            "Tool execution cancelled",
            hint="The operation was interrupted",
            exit_code=130,
        ) from None
    except Exception as e:
        raise CLIError(
            f"Error calling tool '{tool_name}': {e}",
            hint=_error_hint_from_exception(e),
            exit_code=1,
        ) from None


# Create CLI app
app = App(
    name="lucius",
    help="Lucius CLI - Allure TestOps MCP Server Command-Line Interface",
    version=f"lucius {__version__}",
)


@app.command
def version() -> None:
    """Show version information."""
    console_out.print(f"lucius {__version__}")


@app.command(name="list")
def list_tools(
    fmt: typing.Annotated[
        typing.Literal["json", "table", "plain"],
        Parameter(
            name=["--format", "-f"],
            negative="",
        ),
    ] = "json",
) -> None:
    """
    List all available MCP tools.

    Uses static tool schemas for fast startup (no MCP client needed).

    Examples:
        lucius list                      # JSON format (default)
        lucius list --format table       # Table format
        lucius list -f plain             # Plain text format
    """
    # Validate format
    if fmt not in ("json", "table", "plain"):
        console_err.print(f"[red]Error:[/red] Invalid format '{fmt}'")
        console_err.print("[yellow]Hint:[/yellow] Use --format json|table|plain")
        sys.exit(1)

    try:
        schemas = load_tool_schemas()
        format_output_data(schemas, output_format=fmt)
    except CLIError as e:
        _exit_with_cli_error(e)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        _exit_with_cli_error(CLIError(f"Unexpected error in list command: {e}", hint=_error_hint_from_exception(e)))


@app.command
def call(
    tool_name: str,
    args: typing.Annotated[
        str,
        Parameter(
            name=["--args", "-a"],
            allow_leading_hyphen=True,
            negative="",
        ),
    ] = "{}",
    fmt: typing.Annotated[
        typing.Literal["json", "table", "plain"],
        Parameter(
            name=["--format", "-f"],
            negative="",
        ),
    ] = "json",
    show_help: typing.Annotated[
        bool,
        Parameter(
            name=["--show-help"],
            negative="",
        ),
    ] = False,
) -> None:
    """
    Call an MCP tool by name.

    Examples:
        lucius call get_test_case --show-help               # Show tool help
        lucius call get_test_case --args '{"id": 1234}'    # Call with args
        lucius call get_test_case -a '{"id": 1234}' -f table  # Table output
    """
    # Validate format
    if fmt not in ("json", "table", "plain"):
        console_err.print(f"[red]Error:[/red] Invalid format '{fmt}'")
        console_err.print("[yellow]Hint:[/yellow] Use --format json|table|plain")
        sys.exit(1)

    try:
        # Load tool schemas
        schemas = load_tool_schemas()

        # Handle --show-help flag for individual tool help
        if show_help:
            if tool_name not in schemas:
                # List available tools
                available_tools = sorted(schemas.keys())
                raise CLIError(
                    f"Tool '{tool_name}' not found",
                    hint="Available tools:\n" + "\n".join(f"  - {name}" for name in available_tools),
                    exit_code=1,
                )
            print_tool_help(tool_name, schemas[tool_name])
            return

        # Validate tool exists
        if tool_name not in schemas:
            available_tools = sorted(schemas.keys())
            raise CLIError(
                f"Tool '{tool_name}' not found",
                hint="Available tools:\n" + "\n".join(f"  - {name}" for name in available_tools),
                exit_code=1,
            )

        # Parse arguments
        try:
            args_dict = json.loads(args)
        except json.JSONDecodeError as e:
            raise CLIError(
                f"Invalid JSON in --args: {e}",
                hint="Example: --args '{\"id\": 1234}'",
                exit_code=1,
            ) from None

        # Validate arguments against schema
        validate_args_against_schema(args_dict, tool_name, schemas[tool_name])

        # Call tool (lazy import of MCP client happens here)
        result = asyncio.run(call_tool_mcp(tool_name, args_dict))

        # Output result
        format_output_data(result, output_format=fmt)

    except CLIError as e:
        _exit_with_cli_error(e)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        _exit_with_cli_error(CLIError(f"Unexpected error in call command: {e}", hint=_error_hint_from_exception(e)))


def main() -> None:
    """Main entry point."""
    # Disable logging to suppress all MCP and Python logs in CLI output
    # Only user-facing messages printed to stdout/stderr
    logging.disable(logging.CRITICAL)

    try:
        sys.argv = [sys.argv[0], *_rewrite_tool_help_args(sys.argv[1:])]
        app()
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
