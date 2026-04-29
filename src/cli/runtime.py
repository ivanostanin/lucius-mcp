"""
Runtime helpers for CLI error handling and tool invocation.
"""

from __future__ import annotations

import asyncio
import typing
from collections.abc import Coroutine

from src.cli.models import CLIError
from src.cli.tool_resolver import resolve_tool_function


def error_hint_from_exception(error: Exception) -> str:
    """Map low-level runtime errors to user-oriented CLI hints."""
    message = str(error).lower()
    if "not set in environment" in message or "api_token" in message:
        return (
            "Set credentials with 'lucius auth' or with ALLURE_ENDPOINT and ALLURE_API_TOKEN before calling commands."
        )
    if "401" in message or "403" in message or "unauthorized" in message:
        return "Verify API credentials and permissions for the target project."
    if "validationerror" in message or "field required" in message:
        return "Check command parameters with: lucius <entity> <action> --help."
    if "json" in message:
        return "Ensure --args is valid JSON, for example: --args '{\"id\": 1234}'."
    return "Review command parameters with: lucius <entity> <action> --help."


def load_tool_function(tool_name: str) -> typing.Callable[..., Coroutine[typing.Any, typing.Any, typing.Any]]:
    """Lazy-load a tool function by name from src.tools package."""
    try:
        resolved = resolve_tool_function(tool_name)
    except RuntimeError:
        raise CLIError(
            f"Implementation for tool '{tool_name}' not found",
            hint="Ensure the existing tool function exists in src/tools/*.py.",
            exit_code=2,
        ) from None
    return typing.cast(typing.Callable[..., Coroutine[typing.Any, typing.Any, typing.Any]], resolved)


async def call_tool_function(
    tool_name: str,
    args: dict[str, typing.Any],
    *,
    tool_loader: (
        typing.Callable[[str], typing.Callable[..., Coroutine[typing.Any, typing.Any, typing.Any]]] | None
    ) = None,
    error_hint_provider: typing.Callable[[Exception], str] | None = None,
) -> typing.Any:
    """Execute one service-backed tool function asynchronously."""
    if tool_loader is None:
        tool_loader = load_tool_function
    if error_hint_provider is None:
        error_hint_provider = error_hint_from_exception
    tool_function = tool_loader(tool_name)
    try:
        return await tool_function(**args)
    except CLIError:
        raise
    except asyncio.CancelledError:
        raise CLIError(
            "Command execution cancelled",
            hint="The operation was interrupted",
            exit_code=130,
        ) from None
    except TypeError as error:
        raise CLIError(
            f"Invalid parameters for tool '{tool_name}': {error}",
            hint="Check parameter names and types with --help.",
            exit_code=1,
        ) from None
    except Exception as error:
        raise CLIError(
            f"Error executing '{tool_name}': {error}",
            hint=error_hint_provider(error),
            exit_code=1,
        ) from None


def exit_with_cli_error(error: CLIError, console_err: typing.Any) -> typing.NoReturn:
    """Render a CLI error and exit with its configured status code."""
    console_err.print(f"[red]Error:[/red] {error.message}")
    if error.hint:
        console_err.print(f"\n[yellow]Hint:[/yellow] {error.hint}")
    raise SystemExit(error.exit_code)
