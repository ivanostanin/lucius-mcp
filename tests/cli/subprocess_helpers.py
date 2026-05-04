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
        ["uv", "run", "--python", UV_PYTHON_VERSION, "python", "-c", script],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=_subprocess_env(env),
    )


def run_uv_cli(args: list[str], *, env: Mapping[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run the installed local `lucius` console script through `uv run`."""
    return subprocess.run(
        ["uv", "run", "--python", UV_PYTHON_VERSION, "lucius", *args],
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
                    "cli_entry.call_tool_function = lambda tool_name, args: _fake(**args)",
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
            ["uv", "run", "--python", UV_PYTHON_VERSION, "lucius", *args],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            env=resolved_env,
        )
