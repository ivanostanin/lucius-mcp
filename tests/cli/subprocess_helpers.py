"""Shared subprocess helpers for CLI process and uv-run tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run the CLI entrypoint in a subprocess."""
    return subprocess.run(
        [sys.executable, "-m", "src.cli.cli_entry", *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


def run_python_snippet(script: str) -> subprocess.CompletedProcess[str]:
    """Run a Python snippet from the project root."""
    return subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


def run_uv_python_snippet(script: str) -> subprocess.CompletedProcess[str]:
    """Run a Python snippet through `uv run` from the project root."""
    return subprocess.run(
        ["uv", "run", "--python", "3.13", "python", "-c", script],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


def run_cli_with_mocked_result(
    args: list[str],
    mocked_result: object,
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
    return run_python_snippet(script)


def run_cli_with_mocked_result_via_uv(
    args: list[str],
    tool_name: str,
    mocked_result: object,
    expected_tool_output_format: str,
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
    return run_uv_python_snippet(script)
