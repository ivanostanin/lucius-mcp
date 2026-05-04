"""Tests for CLI completion generation and installation."""

from __future__ import annotations

import builtins
import io
import os
from pathlib import Path

import pytest
from rich.console import Console

from src.cli import cli_entry
from src.cli.models import CLIContext, CLIError
from tests.cli.subprocess_helpers import run_cli, run_python_snippet, run_uv_cli


def test_install_completions_help_is_cli_local(capsys: pytest.CaptureFixture[str]) -> None:
    """`install-completions` is handled before entity/action routing."""
    cli_entry.run_cli(["install-completions", "--help"])

    output = capsys.readouterr().out
    assert "lucius install-completions" in output
    assert "--shell <shell>" in output
    assert "--path <file>" in output
    assert "--force" in output
    assert "--print" in output


def test_install_completions_print_outputs_embedded_script_only(capsys: pytest.CaptureFixture[str]) -> None:
    """Print mode writes completion text to stdout and does not install files."""
    cli_entry.run_cli(["install-completions", "--shell", "bash", "--print"])

    output = capsys.readouterr().out
    assert "_lucius_completion" in output
    assert "install-completions" in output
    assert "Installed" not in output


def test_install_completions_print_does_not_wrap_script_lines() -> None:
    from src.cli.completion_installer import handle_install_completions_command

    stream = io.StringIO()
    console = Console(file=stream, width=40, force_terminal=False)
    context = CLIContext(
        console_out=console,
        console_err=console,
        tool_schemas_path=Path("unused"),
        version="test",
    )

    handle_install_completions_command(["--shell", "bash", "--print"], context=context)

    output = stream.getvalue()
    assert '"cf cfv custom-field custom-field-value custom-field-values' in output


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("bash", "bash"),
        ("/bin/zsh", "zsh"),
        ("fish", "fish"),
        ("pwsh", "powershell"),
        ("powershell.exe", "powershell"),
        (r"C:\Program Files\PowerShell\7\pwsh.exe", "powershell"),
    ],
)
def test_normalize_shell_aliases(raw: str, expected: str) -> None:
    from src.cli.completion_installer import normalize_shell

    assert normalize_shell(raw) == expected


def test_normalize_shell_rejects_unsupported_shell() -> None:
    from src.cli.completion_installer import normalize_shell

    with pytest.raises(CLIError) as exc_info:
        normalize_shell("tcsh")
    assert "Unsupported shell" in exc_info.value.message
    assert "bash|zsh|fish|powershell" in (exc_info.value.hint or "")


def test_detect_shell_prefers_explicit_over_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.cli.completion_installer import detect_shell

    monkeypatch.setenv("SHELL", "/bin/zsh")
    assert detect_shell("bash") == "bash"


def test_detect_shell_rejects_empty_explicit_value(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.cli.completion_installer import detect_shell

    monkeypatch.setenv("SHELL", "/bin/zsh")
    with pytest.raises(CLIError) as exc_info:
        detect_shell("")
    assert "Unsupported shell" in exc_info.value.message


def test_detect_shell_prefers_powershell_signals_over_inherited_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.cli.completion_installer import detect_shell

    monkeypatch.setenv("SHELL", "/bin/zsh")
    monkeypatch.setenv("PSModulePath", "/opt/microsoft/powershell/7/Modules")
    assert detect_shell(None) == "powershell"


def test_detect_shell_uses_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.cli.completion_installer import detect_shell

    monkeypatch.delenv("PSModulePath", raising=False)
    monkeypatch.setenv("SHELL", "/usr/local/bin/fish")
    assert detect_shell(None) == "fish"


def test_default_completion_paths_use_user_level_roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.cli.completion_installer import default_completion_path

    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "localappdata"))

    assert default_completion_path("bash") == tmp_path / "data" / "bash-completion" / "completions" / "lucius"
    assert default_completion_path("zsh") == tmp_path / "data" / "zsh" / "site-functions" / "_lucius"
    assert default_completion_path("fish") == tmp_path / "config" / "fish" / "completions" / "lucius.fish"
    assert default_completion_path("powershell") == tmp_path / "localappdata" / "lucius" / "completions" / "lucius.ps1"


def test_custom_path_install_uses_safe_overwrite(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "lucius.bash"
    cli_entry.run_cli(["install-completions", "--shell", "bash", "--path", str(target)])
    first = capsys.readouterr().out

    assert target.exists()
    assert "_lucius_completion" in target.read_text()
    assert str(target) in first

    with pytest.raises(CLIError) as exc_info:
        cli_entry.run_cli(["install-completions", "--shell", "bash", "--path", str(target)])
    assert "already exists" in exc_info.value.message
    assert "--force" in (exc_info.value.hint or "")

    cli_entry.run_cli(["install-completions", "--shell", "bash", "--path", str(target), "--force"])
    assert "_lucius_completion" in target.read_text()


def test_custom_relative_path_does_not_chmod_existing_parent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.cli.completion_installer import install_completion

    monkeypatch.chdir(tmp_path)
    before = tmp_path.stat().st_mode & 0o777

    result = install_completion(shell_name="bash", path=Path("lucius.bash"), force=False)

    assert result.path == Path("lucius.bash")
    assert (tmp_path / "lucius.bash").exists()
    assert tmp_path.stat().st_mode & 0o777 == before


def test_directory_target_is_rejected_even_with_force(tmp_path: Path) -> None:
    from src.cli.completion_installer import install_completion

    with pytest.raises(CLIError) as exc_info:
        install_completion(shell_name="fish", path=tmp_path, force=True)

    assert "target is a directory" in exc_info.value.message
    assert "file path" in (exc_info.value.hint or "")


def test_print_mode_does_not_write_custom_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "lucius.fish"

    cli_entry.run_cli(["install-completions", "--shell", "fish", "--path", str(target), "--print"])

    output = capsys.readouterr().out
    assert "complete -c lucius" in output
    assert not target.exists()


def test_powershell_profile_hook_is_idempotent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.cli.completion_installer import install_completion

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "localappdata"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "profile-home"))
    result_one = install_completion(shell_name="powershell", path=None, force=False)
    result_two = install_completion(shell_name="powershell", path=None, force=True)

    assert result_one.profile_path is not None
    assert result_two.profile_path == result_one.profile_path
    profile_text = result_one.profile_path.read_text()
    assert profile_text.count("Lucius completion start") == 1
    assert profile_text.count(str(result_one.path)) == 1


def test_powershell_profile_hook_uses_absolute_custom_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.cli.completion_installer import install_completion

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "localappdata"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))

    result = install_completion(shell_name="powershell", path=Path("lucius.ps1"), force=False)

    assert result.profile_path is not None
    profile_text = result.profile_path.read_text()
    assert str((tmp_path / "lucius.ps1").resolve()) in profile_text
    assert "$luciusCompletion = 'lucius.ps1'" not in profile_text


def test_powershell_profile_path_uses_core_profile_when_core_signal_present(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.cli.completion_installer import default_powershell_profile_path

    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "user"))
    monkeypatch.setenv("PSModulePath", r"C:\Program Files\PowerShell\7\Modules")

    assert default_powershell_profile_path() == (
        tmp_path / "user" / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
    )


def test_corrupt_powershell_profile_marker_is_repaired(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.cli.completion_installer import install_completion

    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "localappdata"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    profile_path = tmp_path / "config" / "powershell" / "Microsoft.PowerShell_profile.ps1"
    profile_path.parent.mkdir(parents=True)
    profile_path.write_text("before\n# >>> Lucius completion start >>>\nstale\n")

    result = install_completion(shell_name="powershell", path=None, force=False)

    assert result.profile_path == profile_path
    profile_text = profile_path.read_text()
    assert "stale" not in profile_text
    assert profile_text.count("Lucius completion start") == 1
    assert profile_text.count("Lucius completion end") == 1


def test_completion_scripts_include_install_command_and_options() -> None:
    from src.cli.completions import generate_all_completions

    rendered = generate_all_completions()
    for script in rendered.values():
        assert "install-completions" in script
    for shell in ("bash", "zsh", "fish", "powershell"):
        script = rendered[shell]
        for token in ("--shell", "--path", "--force", "--print", "--help", "-h"):
            assert token in script


def test_runtime_installation_does_not_read_repository_completion_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.cli.completion_installer import install_completion

    repo_completion_dir = Path(__file__).resolve().parents[2] / "deployment" / "shell-completions"
    original_open = builtins.open

    def guarded_open(file: object, *args: object, **kwargs: object) -> object:
        path = Path(os.fspath(file)).resolve()
        if repo_completion_dir in path.parents:
            raise AssertionError(f"unexpected repository completion read: {path}")
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", guarded_open)
    target = tmp_path / "lucius.zsh"
    result = install_completion(shell_name="zsh", path=target, force=False)

    assert result.path == target
    assert "_lucius" in target.read_text()


def test_install_completions_import_boundary() -> None:
    script = "\n".join(
        [
            "import builtins",
            "import sys",
            "_blocked = ('src.tools', 'src.main', 'fastmcp', 'starlette', 'uvicorn')",
            "_original_import = builtins.__import__",
            "def _guard(name, globals=None, locals=None, fromlist=(), level=0):",
            "    if any(name == prefix or name.startswith(prefix + '.') for prefix in _blocked):",
            "        raise AssertionError(f'blocked import: {name}')",
            "    return _original_import(name, globals, locals, fromlist, level)",
            "builtins.__import__ = _guard",
            "from src.cli.cli_entry import run_cli",
            "run_cli(['install-completions', '--help'])",
            "run_cli(['install-completions', '--shell', 'bash', '--print'])",
            "assert all(prefix not in sys.modules for prefix in _blocked)",
        ]
    )
    result = run_python_snippet(script)
    assert result.returncode == 0, result.stderr


def test_process_install_completions_rejects_unsupported_shell_without_traceback() -> None:
    result = run_cli(["install-completions", "--shell", "tcsh"])
    output = result.stdout.lower() + result.stderr.lower()

    assert result.returncode == 1
    assert "unsupported shell" in output
    assert "bash|zsh|fish|powershell" in output
    assert "traceback" not in output
    assert "file " not in output


def test_install_completions_help_alias_is_rejected() -> None:
    result = run_cli(["install-completions", "help"])
    output = result.stdout.lower() + result.stderr.lower()

    assert result.returncode == 1
    assert "unknown option 'help'" in output


def test_uv_run_install_completions_help_and_print() -> None:
    help_result = run_uv_cli(["install-completions", "--help"])
    print_result = run_uv_cli(["install-completions", "--shell", "bash", "--print"])

    assert help_result.returncode == 0
    assert "lucius install-completions" in help_result.stdout
    assert print_result.returncode == 0
    assert "_lucius_completion" in print_result.stdout
    assert "install-completions" in print_result.stdout


def test_uv_run_install_completions_rejects_unsupported_shell_without_traceback() -> None:
    result = run_uv_cli(["install-completions", "--shell", "tcsh"])
    output = result.stdout.lower() + result.stderr.lower()

    assert result.returncode == 1
    assert "unsupported shell" in output
    assert "bash|zsh|fish|powershell" in output
    assert "traceback" not in output
