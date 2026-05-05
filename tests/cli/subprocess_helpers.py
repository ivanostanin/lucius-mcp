"""Shared subprocess helpers for CLI process and uv-run tests."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
UV_PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
UV_PYTHON_COMMAND = ("uv", "run", "--python", UV_PYTHON_VERSION, "python")
UV_LUCIUS_COMMAND = ("uv", "run", "--python", UV_PYTHON_VERSION, "lucius")


def assert_uses_uv_lucius_command() -> None:
    """Assert the shared direct CLI helper is source-invoked through `uv run lucius`."""
    assert UV_LUCIUS_COMMAND[:3] == ("uv", "run", "--python")
    assert UV_LUCIUS_COMMAND[-1] == "lucius"


def assert_clean_cli_result(
    result: subprocess.CompletedProcess[str],
    *,
    expected_returncode: int = 0,
) -> None:
    """Assert a CLI subprocess exited as expected without leaking Python internals."""
    combined = result.stdout + result.stderr
    assert result.returncode == expected_returncode, combined
    assert "Traceback" not in combined
    assert "Unexpected CLI error" not in combined
    assert "DEBUG:" not in combined
    assert "INFO:" not in combined
    assert "WARNING:" not in combined


def _subprocess_env(env: Mapping[str, str] | None = None) -> dict[str, str]:
    resolved = dict(os.environ if env is None else env)
    resolved.setdefault("UV_CACHE_DIR", tempfile.mkdtemp(prefix="lucius-uv-cache-"))
    return resolved


def run_cli(args: list[str], *, env: Mapping[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run the CLI entrypoint in a subprocess."""
    return subprocess.run(
        [sys.executable, "-m", "src.cli.cli_entry", *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=_subprocess_env(env),
    )


def run_python_snippet(script: str, *, env: Mapping[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run a Python snippet from the project root."""
    return subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=_subprocess_env(env),
    )


def run_uv_python_snippet(script: str, *, env: Mapping[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run a Python snippet through `uv run` from the project root."""
    return subprocess.run(
        [*UV_PYTHON_COMMAND, "-c", script],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=_subprocess_env(env),
    )


def run_uv_cli(args: list[str], *, env: Mapping[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run the installed local `lucius` console script through `uv run`."""
    return subprocess.run(
        [*UV_LUCIUS_COMMAND, *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=_subprocess_env(env),
    )


def run_cli_with_mocked_result(
    args: list[str],
    mocked_result: object,
    *,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run CLI routing in a subprocess with a mocked async tool result."""
    payload = repr(mocked_result)
    script = "\n".join(
        [
            "from src.cli import cli_entry",
            f"_payload = {payload}",
            "async def _fake(_tool_name, _args):",
            "    return _payload",
            "cli_entry.call_tool_function = _fake",
            f"cli_entry.run_cli({args!r})",
        ]
    )
    return run_python_snippet(script, env=env)


def run_cli_with_mocked_result_via_uv(
    args: list[str],
    tool_name: str,
    mocked_result: object,
    expected_tool_output_format: str,
    *,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run CLI via `uv run` subprocess with a stubbed tool function."""
    payload = repr(mocked_result)
    script = "\n".join(
        [
            "from src.cli import cli_entry",
            "import src.tools as tools",
            f"_payload = {payload}",
            f"_tool_name = {tool_name!r}",
            f"_expected = {expected_tool_output_format!r}",
            "async def _fake(**kwargs):",
            "    assert kwargs.get('output_format') == _expected, (_expected, kwargs)",
            "    return _payload",
            "setattr(tools, _tool_name, _fake)",
            f"cli_entry.run_cli({args!r})",
        ]
    )
    return run_uv_python_snippet(script, env=env)


def run_uv_cli_with_mocked_result(
    args: list[str],
    tool_name: str,
    mocked_result: object,
    expected_tool_output_format: str,
    *,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run the `uv run lucius` console script with a startup stubbed tool function."""
    with tempfile.TemporaryDirectory(prefix="lucius-sitecustomize-") as patch_dir:
        patch_path = Path(patch_dir)
        sitecustomize = patch_path / "sitecustomize.py"
        payload = repr(mocked_result)
        sitecustomize.write_text(
            "\n".join(
                [
                    "from src.cli import cli_entry",
                    "import src.tools as tools",
                    f"_payload = {payload}",
                    f"_tool_name = {tool_name!r}",
                    f"_expected = {expected_tool_output_format!r}",
                    "async def _fake(**kwargs):",
                    "    assert kwargs.get('output_format') == _expected, (_expected, kwargs)",
                    "    return _payload",
                    "setattr(tools, _tool_name, _fake)",
                    "async def _call_tool(called_tool_name, args):",
                    "    assert called_tool_name == _tool_name, (_tool_name, called_tool_name)",
                    "    return await _fake(**args)",
                    "cli_entry.call_tool_function = _call_tool",
                ]
            ),
            encoding="utf-8",
        )
        resolved_env = _subprocess_env(env)
        pythonpath_parts = [str(patch_path), str(PROJECT_ROOT)]
        existing_pythonpath = resolved_env.get("PYTHONPATH")
        if existing_pythonpath:
            pythonpath_parts.append(existing_pythonpath)
        resolved_env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
        return subprocess.run(
            [*UV_LUCIUS_COMMAND, *args],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            env=resolved_env,
        )


def run_uv_cli_with_mocked_message_output(
    args: list[str],
    tool_name: str,
    message: str,
    expected_tool_output_format: str,
    *,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run `uv run lucius` with a tool fake that uses the real message output contract."""
    with tempfile.TemporaryDirectory(prefix="lucius-sitecustomize-") as patch_dir:
        patch_path = Path(patch_dir)
        sitecustomize = patch_path / "sitecustomize.py"
        sitecustomize.write_text(
            "\n".join(
                [
                    "from src.cli import cli_entry",
                    "import src.tools as tools",
                    "from src.tools.output_contract import render_message_output",
                    f"_message = {message!r}",
                    f"_tool_name = {tool_name!r}",
                    f"_expected = {expected_tool_output_format!r}",
                    "async def _fake(**kwargs):",
                    "    assert kwargs.get('output_format') == _expected, (_expected, kwargs)",
                    "    return render_message_output(_message, output_format=kwargs['output_format'])",
                    "setattr(tools, _tool_name, _fake)",
                    "async def _call_tool(called_tool_name, args):",
                    "    assert called_tool_name == _tool_name, (_tool_name, called_tool_name)",
                    "    return await _fake(**args)",
                    "cli_entry.call_tool_function = _call_tool",
                ]
            ),
            encoding="utf-8",
        )
        resolved_env = _subprocess_env(env)
        pythonpath_parts = [str(patch_path), str(PROJECT_ROOT)]
        existing_pythonpath = resolved_env.get("PYTHONPATH")
        if existing_pythonpath:
            pythonpath_parts.append(existing_pythonpath)
        resolved_env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
        return subprocess.run(
            [*UV_LUCIUS_COMMAND, *args],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            env=resolved_env,
        )
