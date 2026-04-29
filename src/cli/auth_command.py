"""CLI-local auth command handling."""

from __future__ import annotations

import asyncio
import getpass
from dataclasses import dataclass
from typing import Any, Literal, cast

from pydantic import SecretStr

from src.cli.auth_config import auth_config_path, clear_auth_config, load_auth_config, save_auth_config
from src.cli.local_commands import (
    AUTH_HELP_TOKENS,
    AUTH_OPTIONS,
    AUTH_SUBCOMMAND_BY_TOKEN,
    AUTH_VALUE_OPTIONS,
    auth_usage_lines,
)
from src.cli.models import CLIContext, CLIError
from src.client.client import AllureClient
from src.client.exceptions import AllureAPIError, AllureAuthError, AllureNotFoundError, AllureValidationError


@dataclass(frozen=True)
class AuthCommandOptions:
    """Parsed auth command options."""

    mode: Literal["configure", "status", "clear"] = "configure"
    url: str | None = None
    token: str | None = None
    project: str | None = None
    show_help: bool = False


def render_auth_help(console: Any) -> None:
    """Print help for the CLI-local auth command."""
    for line in auth_usage_lines():
        console.print(line)


def _replace_auth_option(
    options: AuthCommandOptions,
    *,
    url: str | None = None,
    token: str | None = None,
    project: str | None = None,
    show_help: bool | None = None,
) -> AuthCommandOptions:
    return AuthCommandOptions(
        mode=options.mode,
        url=options.url if url is None else url,
        token=options.token if token is None else token,
        project=options.project if project is None else project,
        show_help=options.show_help if show_help is None else show_help,
    )


def _supported_auth_options_hint() -> str:
    return f"Supported auth options: {', '.join(AUTH_OPTIONS)}"


def _parse_auth_subcommand(argv: list[str], *, mode: Literal["status", "clear"]) -> AuthCommandOptions:
    if len(argv) == 1:
        return AuthCommandOptions(mode=mode)
    if len(argv) == 2 and argv[1] in AUTH_HELP_TOKENS:
        return AuthCommandOptions(mode=mode, show_help=True)
    raise CLIError(
        f"Unknown option '{argv[1]}'",
        hint="Supported auth subcommand options: --help/-h",
        exit_code=1,
    )


def parse_auth_command_options(argv: list[str]) -> AuthCommandOptions:
    """Parse `lucius auth` arguments."""
    if argv and argv[0] in AUTH_SUBCOMMAND_BY_TOKEN:
        return _parse_auth_subcommand(argv, mode=cast(Literal["status", "clear"], argv[0]))

    options = AuthCommandOptions()
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg in AUTH_HELP_TOKENS:
            options = _replace_auth_option(options, show_help=True)
            index += 1
            continue
        if arg in AUTH_VALUE_OPTIONS:
            if index + 1 >= len(argv):
                raise CLIError(
                    f"Missing value for {arg}",
                    hint=_supported_auth_options_hint(),
                )
            value = argv[index + 1]
            target_field = AUTH_VALUE_OPTIONS[arg].target_field
            if target_field is None:
                raise RuntimeError(f"Auth option '{arg}' is missing a target field")
            if target_field == "url":
                options = _replace_auth_option(options, url=value)
            elif target_field == "token":
                options = _replace_auth_option(options, token=value)
            elif target_field == "project":
                options = _replace_auth_option(options, project=value)
            else:
                raise RuntimeError(f"Unsupported auth option target field: {target_field}")
            index += 2
            continue
        raise CLIError(
            f"Unknown option '{arg}'",
            hint=f"{_supported_auth_options_hint()}, --help/-h",
            exit_code=1,
        )
    return options


def _prompt_non_empty(prompt: str) -> str:
    try:
        value = input(prompt).strip()
    except EOFError:
        raise CLIError(
            "Interactive input was cancelled.",
            hint="Re-run 'lucius auth' and provide the requested value.",
        ) from None
    if not value:
        raise CLIError(
            f"{prompt.rstrip(': ')} is required.",
            hint="Provide the missing value non-interactively or re-run the command and answer the prompt.",
            exit_code=1,
        )
    return value


def _prompt_token() -> str:
    try:
        value = getpass.getpass("Allure API token: ").strip()
    except EOFError:
        raise CLIError(
            "Interactive input was cancelled.",
            hint="Re-run 'lucius auth' and provide the requested value.",
        ) from None
    if not value:
        raise CLIError(
            "Allure API token is required.",
            hint="Provide --token non-interactively or re-run the command and answer the prompt.",
            exit_code=1,
        )
    return value


def parse_project_id(raw_value: str) -> int:
    """Parse and validate a positive integer project ID."""
    try:
        project_id = int(raw_value)
    except ValueError:
        raise CLIError(
            "Project ID must be a positive integer.",
            hint="Use --project <id> with a value like 123.",
        ) from None
    if project_id <= 0:
        raise CLIError("Project ID must be a positive integer.", hint="Use --project <id> with a value like 123.")
    return project_id


def _normalize_url(url: str) -> str:
    normalized = url.strip().rstrip("/")
    if not normalized:
        raise CLIError("Allure URL is required.", hint="Use --url https://example.testops.cloud or answer the prompt.")
    return normalized


def _map_auth_validation_error(error: Exception, *, project_id: int) -> CLIError:
    if isinstance(error, ValueError):
        return CLIError(
            "Invalid Allure URL.",
            hint="Use a full base URL that starts with http:// or https://.",
            exit_code=1,
        )
    if isinstance(error, AllureAuthError):
        return CLIError(
            "Authentication failed for the provided Allure token.",
            hint="Verify the API token and confirm it has access to the requested project.",
            exit_code=1,
        )
    if isinstance(error, AllureNotFoundError):
        return CLIError(
            f"Project {project_id} was not found or is not accessible.",
            hint="Verify the project ID and confirm the token can access that project.",
            exit_code=1,
        )
    if isinstance(error, AllureValidationError):
        return CLIError(
            f"Unable to validate project {project_id}.",
            hint="Verify the Allure URL and project ID, then try again.",
            exit_code=1,
        )
    if isinstance(error, AllureAPIError):
        message = str(error).lower()
        if "request error" in message or "connect" in message or "timeout" in message:
            return CLIError(
                "Unable to reach the Allure TestOps server.",
                hint="Check the URL, network connectivity, and TLS/proxy settings.",
                exit_code=1,
            )
        return CLIError(
            "Allure credential validation failed.",
            hint="Verify the URL, token, and project access, then try again.",
            exit_code=1,
        )
    return CLIError(
        "Unexpected auth validation error.",
        hint="Verify the URL, token, and project access, then try again.",
        exit_code=1,
    )


async def validate_auth_credentials(*, url: str, token: str, project_id: int) -> None:
    """Validate auth credentials with a live Allure token exchange and project probe."""
    try:
        async with AllureClient(base_url=url, token=SecretStr(token), project=project_id) as client:
            await client.validate_project_access(project_id)
    except Exception as error:
        raise _map_auth_validation_error(error, project_id=project_id) from None


def _render_auth_status(context: CLIContext) -> None:
    config = load_auth_config()
    path = auth_config_path()
    if config is None:
        context.console_out.print("CLI auth status: not configured")
        context.console_out.print(f"Location: {path}")
        context.console_out.print("Run 'lucius auth' to save credentials for future CLI launches.")
        return

    context.console_out.print("CLI auth status: configured")
    context.console_out.print(f"Location: {path}")
    context.console_out.print(f"URL: {config.allure_endpoint}")
    context.console_out.print(f"Project ID: {config.allure_project_id}")
    context.console_out.print("API token: configured")


def _clear_auth(context: CLIContext) -> None:
    path = auth_config_path()
    removed = clear_auth_config(path)
    if removed:
        context.console_out.print("Cleared saved CLI auth configuration.")
        context.console_out.print(f"Location: {path}")
        return

    context.console_out.print("CLI auth was already clear.")
    context.console_out.print(f"Location: {path}")


def handle_auth_command(argv: list[str], *, context: CLIContext) -> None:
    """Execute the CLI-local `lucius auth` command."""
    options = parse_auth_command_options(argv)
    if options.show_help:
        render_auth_help(context.console_out)
        return

    if options.mode == "status":
        _render_auth_status(context)
        return
    if options.mode == "clear":
        _clear_auth(context)
        return

    raw_url = options.url.strip() if options.url is not None else ""
    url = _normalize_url(raw_url) if raw_url else _normalize_url(_prompt_non_empty("Allure URL: "))

    token = options.token.strip() if options.token is not None else ""
    if not token:
        token = _prompt_token()

    raw_project = options.project.strip() if options.project is not None else ""
    if not raw_project:
        raw_project = _prompt_non_empty("Default project ID: ")
    project_id = parse_project_id(raw_project.strip())

    asyncio.run(validate_auth_credentials(url=url, token=token, project_id=project_id))
    saved_path = save_auth_config(url=url, token=token, project_id=project_id)

    context.console_out.print("Saved CLI auth configuration.")
    context.console_out.print(f"Location: {saved_path}")
    context.console_out.print(f"URL: {url}")
    context.console_out.print(f"Project ID: {project_id}")
