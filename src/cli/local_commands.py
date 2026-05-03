"""Definitions for CLI-local commands that are not backed by MCP tools."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalCommandOption:
    """One CLI-local option token."""

    token: str
    value_name: str | None = None
    description: str | None = None
    target_field: str | None = None


@dataclass(frozen=True)
class LocalCommandSubcommand:
    """One CLI-local subcommand token."""

    token: str
    description: str


CLI_LOCAL_COMMANDS = ["auth", "list", "install-completions"]
AUTH_HELP_TOKENS = ("--help", "-h", "help")
LIST_HELP_TOKENS = ("--help", "-h", "help")
INSTALL_COMPLETIONS_HELP_TOKENS = ("--help", "-h")
AUTH_CONFIGURE_OPTIONS = (
    LocalCommandOption("--url", value_name="<url>", description="Allure TestOps base URL", target_field="url"),
    LocalCommandOption("--token", value_name="<token>", description="Allure API token", target_field="token"),
    LocalCommandOption(
        "--project",
        value_name="<id>",
        description="Default Allure project ID (positive integer)",
        target_field="project",
    ),
    LocalCommandOption("--help", description="Show auth command help"),
    LocalCommandOption("-h", description="Show auth command help"),
)
AUTH_SUBCOMMAND_SPECS = (
    LocalCommandSubcommand("status", "Show whether saved CLI auth is configured."),
    LocalCommandSubcommand("clear", "Remove saved CLI auth configuration."),
)

AUTH_OPTIONS = [option.token for option in AUTH_CONFIGURE_OPTIONS]
AUTH_VALUE_OPTIONS = {option.token: option for option in AUTH_CONFIGURE_OPTIONS if option.target_field is not None}
AUTH_SUBCOMMANDS = [subcommand.token for subcommand in AUTH_SUBCOMMAND_SPECS]
AUTH_SUBCOMMAND_BY_TOKEN = {subcommand.token: subcommand for subcommand in AUTH_SUBCOMMAND_SPECS}
INSTALL_COMPLETIONS_OPTIONS = ["--shell", "--path", "--force", "--print", "--help", "-h"]


def auth_usage_lines() -> list[str]:
    """Build help output for `lucius auth` from shared command metadata."""
    option_lines = [
        f"  {option.token} {option.value_name:<8} {option.description}"
        if option.value_name is not None
        else f"  {option.token:<19} {option.description}"
        for option in AUTH_CONFIGURE_OPTIONS
    ]
    return [
        "CLI auth stores Allure credentials for future Lucius CLI runs.\n",
        "Usage:",
        "  lucius auth",
        "  lucius auth --url <url> --token <token> --project <id>",
        *[f"  lucius auth {subcommand.token}" for subcommand in AUTH_SUBCOMMAND_SPECS],
        "  lucius auth --help\n",
        "Options:",
        *option_lines,
        "\nPrecedence for later tool execution:",
        "  explicit tool args > environment variables > saved CLI auth config > defaults",
    ]


def list_usage_lines() -> list[str]:
    """Build help output for `lucius list` from shared command metadata."""
    return [
        "CLI-local discovery command that prints the same static discovery output as `lucius` with no arguments.\n",
        "Usage:",
        "  lucius list",
        "  lucius list --help\n",
        "Options:",
        "  --help             Show list command help",
        "  -h                 Show list command help",
        "\nNotes:",
        "  - Prints local static discovery metadata only.",
        "  - Does not require --args, saved credentials, or network access.",
    ]


def install_completions_usage_lines() -> list[str]:
    """Build help output for `lucius install-completions`."""
    return [
        "Install or print embedded Lucius shell completion scripts.\n",
        "Usage:",
        "  lucius install-completions [--shell <shell>] [--path <file>] [--force] [--print]",
        "  lucius install-completions --help\n",
        "Options:",
        "  --shell <shell>     Target shell: bash, zsh, fish, or powershell",
        "  --path <file>       Write completion script to a custom file",
        "  --force             Overwrite an existing completion file",
        "  --print             Print selected completion script to stdout without writing files",
        "  --help              Show install-completions help",
        "  -h                  Show install-completions help",
        "\nExamples:",
        "  lucius install-completions --shell zsh",
        "  lucius install-completions --shell bash --print",
        "  lucius install-completions --shell fish --path ~/.config/fish/completions/lucius.fish --force",
    ]
