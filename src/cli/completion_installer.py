"""Install embedded Lucius shell completion scripts."""

from __future__ import annotations

import os
import platform
import tempfile
import typing
from dataclasses import dataclass
from pathlib import Path

from src.cli.completions import generate_completion
from src.cli.local_commands import INSTALL_COMPLETIONS_HELP_TOKENS, install_completions_usage_lines
from src.cli.models import CLIContext, CLIError

ShellName = str
SUPPORTED_SHELLS = ("bash", "zsh", "fish", "powershell")
SHELL_HINT = "Use --shell bash|zsh|fish|powershell"
PROFILE_MARKER_START = "# >>> Lucius completion start >>>"
PROFILE_MARKER_END = "# <<< Lucius completion end <<<"


@dataclass(frozen=True)
class InstallCompletionOptions:
    """Parsed `install-completions` options."""

    shell: str | None = None
    path: Path | None = None
    force: bool = False
    print_only: bool = False
    show_help: bool = False


@dataclass(frozen=True)
class InstallCompletionResult:
    """Result of installing a completion script."""

    shell: ShellName
    path: Path
    profile_path: Path | None
    guidance: str


def normalize_shell(value: str) -> ShellName:
    """Normalize shell names, aliases, executable names, and path-like values."""
    normalized = Path(value.strip().replace("\\", "/")).name.lower()
    if normalized.endswith(".exe"):
        normalized = normalized[:-4]

    aliases = {
        "bash": "bash",
        "zsh": "zsh",
        "fish": "fish",
        "pwsh": "powershell",
        "powershell": "powershell",
    }
    shell = aliases.get(normalized)
    if shell is None:
        raise CLIError(
            f"Unsupported shell '{value}'",
            hint=f"{SHELL_HINT}. Supported shells: {', '.join(SUPPORTED_SHELLS)}",
            exit_code=1,
        )
    return shell


def detect_shell(explicit_shell: str | None) -> ShellName:
    """Detect the target shell from explicit option, environment, or platform."""
    if explicit_shell is not None:
        return normalize_shell(explicit_shell)

    if os.environ.get("PSModulePath"):
        return "powershell"

    for env_name in ("SHELL", "ComSpec"):
        value = os.environ.get(env_name)
        if not value:
            continue
        try:
            return normalize_shell(value)
        except CLIError:
            continue

    if platform.system().lower() == "windows":
        return "powershell"

    raise CLIError(
        "Could not detect current shell",
        hint=f"{SHELL_HINT}; auto-detection checks SHELL, ComSpec, PowerShell hints, and platform defaults.",
        exit_code=1,
    )


def _home_dir() -> Path:
    return Path.home()


def _xdg_data_home() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME") or (_home_dir() / ".local" / "share"))


def _xdg_config_home() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME") or (_home_dir() / ".config"))


def default_completion_path(shell: ShellName) -> Path:
    """Return default user-level completion target path for a shell."""
    if shell == "bash":
        return _xdg_data_home() / "bash-completion" / "completions" / "lucius"
    if shell == "zsh":
        return _xdg_data_home() / "zsh" / "site-functions" / "_lucius"
    if shell == "fish":
        return _xdg_config_home() / "fish" / "completions" / "lucius.fish"
    if shell == "powershell":
        base = Path(os.environ.get("LOCALAPPDATA") or (_xdg_data_home()))
        return base / "lucius" / "completions" / "lucius.ps1"
    raise CLIError(f"Unsupported shell '{shell}'", hint=SHELL_HINT, exit_code=1)


def default_powershell_profile_path() -> Path:
    """Return a per-user PowerShell profile path."""
    if platform.system().lower() == "windows":
        base = Path(os.environ.get("USERPROFILE") or _home_dir()) / "Documents"
        ps_module_path = os.environ.get("PSModulePath", "").lower().replace("\\", "/")
        if "powershell/7" in ps_module_path or "/powershell/" in ps_module_path:
            return base / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
        return base / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
    return _xdg_config_home() / "powershell" / "Microsoft.PowerShell_profile.ps1"


def _ensure_parent(path: Path, *, private: bool) -> None:
    missing_parents = [parent for parent in reversed(path.parent.parents) if not parent.exists()]
    if not path.parent.exists():
        missing_parents.append(path.parent)
    path.parent.mkdir(parents=True, exist_ok=True)
    if private and os.name == "posix":
        for parent in missing_parents:
            parent.chmod(0o700)


def _write_text_atomically(path: Path, content: str, *, force: bool, private_parent: bool = False) -> None:
    if path.is_dir():
        raise CLIError(
            f"Completion target is a directory: {path}",
            hint="Provide a file path, not a directory path.",
            exit_code=1,
        )
    if path.exists() and not force:
        raise CLIError(
            f"Completion file already exists: {path}",
            hint="Re-run with --force to overwrite it, or choose a different --path.",
            exit_code=1,
        )

    _ensure_parent(path, private=private_parent)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        if os.name == "posix":
            tmp_path.chmod(0o600)
        tmp_path.replace(path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def _powershell_profile_block(completion_path: Path) -> str:
    escaped_path = str(completion_path).replace("'", "''")
    return (
        f"{PROFILE_MARKER_START}\n"
        f"$luciusCompletion = '{escaped_path}'\n"
        "if (Test-Path $luciusCompletion) { . $luciusCompletion }\n"
        f"{PROFILE_MARKER_END}"
    )


def _update_marker_block(path: Path, block: str) -> None:
    _ensure_parent(path, private=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    start_index = existing.find(PROFILE_MARKER_START)
    end_index = existing.find(PROFILE_MARKER_END)
    if start_index >= 0 and end_index >= start_index:
        end_index += len(PROFILE_MARKER_END)
        updated = existing[:start_index].rstrip() + "\n\n" + block + existing[end_index:]
    elif start_index >= 0:
        updated = existing[:start_index].rstrip() + "\n\n" + block + "\n"
    elif end_index >= 0:
        updated = block + existing[end_index + len(PROFILE_MARKER_END) :]
    else:
        separator = "\n\n" if existing.strip() else ""
        updated = existing.rstrip() + separator + block + "\n"
    _write_text_atomically(path, updated, force=True, private_parent=True)


def activation_guidance(shell: ShellName, path: Path, profile_path: Path | None = None) -> str:
    """Return shell-specific activation guidance."""
    if shell == "bash":
        return f"Restart your shell or run: source {path}"
    if shell == "zsh":
        return f"Restart zsh or run: fpath=({path.parent} $fpath); autoload -Uz compinit && compinit"
    if shell == "fish":
        return "Restart fish or run: source ~/.config/fish/config.fish"
    if shell == "powershell":
        if profile_path is None:
            return f"Start a new PowerShell session or dot-source: . '{path}'"
        return f"Profile hook updated at {profile_path}. Start a new PowerShell session."
    raise CLIError(f"Unsupported shell '{shell}'", hint=SHELL_HINT, exit_code=1)


def install_completion(*, shell_name: ShellName, path: Path | None, force: bool) -> InstallCompletionResult:
    """Write embedded completion content and any required shell profile hook."""
    normalized_shell = normalize_shell(shell_name)
    target_path = path.expanduser() if path is not None else default_completion_path(normalized_shell)
    content = generate_completion(normalized_shell)

    _write_text_atomically(target_path, content, force=force, private_parent=path is None)

    profile_path: Path | None = None
    if normalized_shell == "powershell":
        profile_path = default_powershell_profile_path()
        _update_marker_block(profile_path, _powershell_profile_block(target_path.resolve()))

    return InstallCompletionResult(
        shell=normalized_shell,
        path=target_path,
        profile_path=profile_path,
        guidance=activation_guidance(normalized_shell, target_path, profile_path),
    )


def parse_install_completion_options(argv: list[str]) -> InstallCompletionOptions:
    """Parse `install-completions` options without importing action routing."""
    shell: str | None = None
    path: Path | None = None
    force = False
    print_only = False
    index = 0

    if len(argv) == 1 and argv[0] in INSTALL_COMPLETIONS_HELP_TOKENS:
        return InstallCompletionOptions(show_help=True)

    while index < len(argv):
        option = argv[index]
        if option in INSTALL_COMPLETIONS_HELP_TOKENS:
            return InstallCompletionOptions(show_help=True)
        if option == "--shell":
            index += 1
            if index >= len(argv):
                raise CLIError("Missing value for --shell", hint=SHELL_HINT, exit_code=1)
            shell = argv[index]
        elif option == "--path":
            index += 1
            if index >= len(argv):
                raise CLIError("Missing value for --path", hint="Provide a file path after --path.", exit_code=1)
            path = Path(argv[index])
        elif option == "--force":
            force = True
        elif option == "--print":
            print_only = True
        else:
            raise CLIError(
                f"Unknown option '{option}'",
                hint="Supported options: --shell, --path, --force, --print, --help, -h",
                exit_code=1,
            )
        index += 1

    return InstallCompletionOptions(shell=shell, path=path, force=force, print_only=print_only)


def render_install_completions_help(console: typing.Any) -> None:
    """Print help for `lucius install-completions`."""
    for line in install_completions_usage_lines():
        console.print(line)


def handle_install_completions_command(argv: list[str], *, context: CLIContext) -> None:
    """Handle `lucius install-completions` as a CLI-local setup command."""
    options = parse_install_completion_options(argv)
    if options.show_help:
        render_install_completions_help(context.console_out)
        return

    shell = detect_shell(options.shell)
    if options.print_only:
        context.console_out.print(generate_completion(shell), end="", soft_wrap=True)
        return

    result = install_completion(shell_name=shell, path=options.path, force=options.force)
    context.console_out.print(f"Installed {result.shell} completions: {result.path}", soft_wrap=True)
    context.console_out.print(result.guidance, soft_wrap=True)
