"""E2E coverage for CLI-local commands executed through `uv run lucius`."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from src.cli.route_matrix import CANONICAL_ROUTE_MATRIX
from tests.cli.subprocess_helpers import (
    assert_clean_cli_result,
    assert_uses_uv_lucius_command,
    run_uv_cli,
)

CLI_LOCAL_UV_RUN_COVERAGE = {
    "root_discovery": [],
    "root_help": ["--help"],
    "version": ["--version"],
    "list": ["list"],
    "list_help": ["list", "--help"],
    "auth_help": ["auth", "--help"],
    "auth_setup": ["auth", "--url", "https://example.testops.cloud", "--token", "<redacted>", "--project", "555"],
    "auth_status": ["auth", "status"],
    "install_completions_help": ["install-completions", "--help"],
    "install_completions_print": ["install-completions", "--shell", "bash", "--print"],
}


def _isolated_cli_env(tmp_path: Path, *, sitecustomize: Path | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env["HOME"] = str(tmp_path / "home")
    env["XDG_CONFIG_HOME"] = str(tmp_path / "config")
    env["XDG_DATA_HOME"] = str(tmp_path / "data")
    env["LOCALAPPDATA"] = str(tmp_path / "local-app-data")
    env["APPDATA"] = str(tmp_path / "app-data")
    env["USERPROFILE"] = str(tmp_path / "user-profile")
    env["UV_CACHE_DIR"] = str(tmp_path / "uv-cache")
    if sitecustomize is not None:
        existing_pythonpath = env.get("PYTHONPATH")
        env["PYTHONPATH"] = (
            str(sitecustomize)
            if not existing_pythonpath
            else os.pathsep.join([str(sitecustomize), existing_pythonpath])
        )
    return env


def _auth_validation_sitecustomize(tmp_path: Path) -> Path:
    directory = tmp_path / "sitecustomize"
    directory.mkdir()
    (directory / "sitecustomize.py").write_text(
        "\n".join(
            [
                "import src.cli.auth_command as auth_command",
                "async def _fake_validate(*, url, token, project_id):",
                "    assert url == 'https://example.testops.cloud'",
                "    assert token == 'uv-secret-token'",
                "    assert project_id == 555",
                "auth_command.validate_auth_credentials = _fake_validate",
            ]
        ),
        encoding="utf-8",
    )
    return directory


def test_uv_run_local_command_coverage_inventory_is_explicit() -> None:
    """Keep the shared source-invoked suite visible when adding CLI-local commands."""
    assert_uses_uv_lucius_command()
    assert set(CLI_LOCAL_UV_RUN_COVERAGE) == {
        "root_discovery",
        "root_help",
        "version",
        "list",
        "list_help",
        "auth_help",
        "auth_setup",
        "auth_status",
        "install_completions_help",
        "install_completions_print",
    }


@pytest.mark.parametrize("entity", sorted(CANONICAL_ROUTE_MATRIX))
def test_uv_run_all_entities_have_discovery_help(entity: str) -> None:
    result = run_uv_cli([entity])

    assert_clean_cli_result(result)
    assert f"Actions for {entity}" in result.stdout


@pytest.mark.parametrize(
    ("entity", "action", "tool_name"),
    [
        (entity, action, tool_name)
        for entity, actions in sorted(CANONICAL_ROUTE_MATRIX.items())
        for action, tool_name in sorted(actions.items())
    ],
)
def test_uv_run_all_actions_have_help(entity: str, action: str, tool_name: str) -> None:
    result = run_uv_cli([entity, action, "--help"])

    assert_clean_cli_result(result)
    assert "Command:" in result.stdout
    assert f"lucius {entity} {action}" in result.stdout
    assert "Mapped tool:" in result.stdout
    assert tool_name in result.stdout


@pytest.mark.parametrize(
    ("args", "markers"),
    [
        ([], ("CLI-Local Commands", "Available Entities", "test_case")),
        (["--help"], ("Usage:", "lucius auth", "lucius list", "lucius install-completions")),
        (["--version"], ("lucius",)),
        (["list"], ("CLI-Local Commands", "Available Entities", "test_case")),
        (["list", "--help"], ("CLI-local discovery command", "Does not require --args")),
        (["auth", "--help"], ("lucius auth", "lucius auth status", "--token")),
        (["install-completions", "--help"], ("lucius install-completions", "--shell", "--print")),
    ],
)
def test_uv_run_local_commands_exit_cleanly(args: list[str], markers: tuple[str, ...], tmp_path: Path) -> None:
    result = run_uv_cli(args, env=_isolated_cli_env(tmp_path))

    assert_clean_cli_result(result)
    for marker in markers:
        assert marker in result.stdout


def test_uv_run_auth_status_uses_isolated_saved_config_location(tmp_path: Path) -> None:
    result = run_uv_cli(["auth", "status"], env=_isolated_cli_env(tmp_path))

    assert_clean_cli_result(result)
    assert "CLI auth status: not configured" in result.stdout
    assert "config/lucius/auth.json" in result.stdout


def test_uv_run_auth_setup_saves_config_without_exposing_token(tmp_path: Path) -> None:
    sitecustomize = _auth_validation_sitecustomize(tmp_path)
    env = _isolated_cli_env(tmp_path, sitecustomize=sitecustomize)
    setup = run_uv_cli(
        [
            "auth",
            "--url",
            "https://example.testops.cloud",
            "--token",
            "uv-secret-token",
            "--project",
            "555",
        ],
        env=env,
    )

    assert_clean_cli_result(setup)
    assert "Saved CLI auth configuration." in setup.stdout
    assert "Project ID: 555" in setup.stdout
    assert "uv-secret-token" not in setup.stdout
    assert "uv-secret-token" not in setup.stderr

    status = run_uv_cli(["auth", "status"], env=env)
    assert_clean_cli_result(status)
    assert "CLI auth status: configured" in status.stdout
    assert "uv-secret-token" not in status.stdout
    assert "uv-secret-token" not in status.stderr


def test_uv_run_install_completions_print_is_source_invoked_and_clean(tmp_path: Path) -> None:
    result = run_uv_cli(["install-completions", "--shell", "bash", "--print"], env=_isolated_cli_env(tmp_path))

    assert_clean_cli_result(result)
    assert "_lucius_completion" in result.stdout
    assert "install-completions" in result.stdout


def test_uv_run_local_command_errors_do_not_expose_internals(tmp_path: Path) -> None:
    result = run_uv_cli(["install-completions", "--shell", "tcsh"], env=_isolated_cli_env(tmp_path))

    assert_clean_cli_result(result, expected_returncode=1)
    output = result.stdout.lower() + result.stderr.lower()
    assert "unsupported shell" in output
    assert "bash|zsh|fish|powershell" in output
