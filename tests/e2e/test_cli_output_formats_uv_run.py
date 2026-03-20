"""E2E checks for CLI format behavior executed through `uv run`."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def run_cli_with_mocked_result_via_uv(
    args: list[str],
    tool_name: str,
    mocked_result: object,
    expected_tool_output_format: str,
) -> subprocess.CompletedProcess[str]:
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
    return subprocess.run(
        ["uv", "run", "--python", "3.13", "python", "-c", script],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


def test_e2e_uv_run_cli_default_json() -> None:
    """Without --format, CLI explicitly requests json from the tool."""
    result = run_cli_with_mocked_result_via_uv(
        ["test_case", "list", "--args", "{}"],
        "list_test_cases",
        '{"ok":true,"count":2}',
        expected_tool_output_format="json",
    )
    assert result.returncode == 0
    assert result.stdout.strip() == '{"ok":true,"count":2}'


def test_e2e_uv_run_cli_plain() -> None:
    """With --format plain, CLI explicitly requests plain from the tool."""
    result = run_cli_with_mocked_result_via_uv(
        ["test_case", "get", "--args", '{"test_case_id": 1}', "--format", "plain"],
        "get_test_case_details",
        "line1\nline2",
        expected_tool_output_format="plain",
    )
    assert result.returncode == 0
    assert result.stdout == "line1\nline2"


def test_e2e_uv_run_cli_csv() -> None:
    """With --format csv, CLI requests json from the tool and renders csv."""
    result = run_cli_with_mocked_result_via_uv(
        ["test_case", "list", "--args", "{}", "--format", "csv"],
        "list_test_cases",
        json.dumps([{"id": 1, "name": "Alpha"}, {"id": 2, "name": "Beta"}]),
        expected_tool_output_format="json",
    )
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert lines[0] == "id,name"
    assert lines[1] == "1,Alpha"
    assert lines[2] == "2,Beta"


def test_e2e_uv_run_cli_table() -> None:
    """With --format table, CLI requests json from the tool and renders a table."""
    result = run_cli_with_mocked_result_via_uv(
        ["test_case", "list", "--args", "{}", "--format", "table"],
        "list_test_cases",
        json.dumps([{"id": 1, "name": "Alpha"}]),
        expected_tool_output_format="json",
    )
    assert result.returncode == 0
    assert "Command Result" in result.stdout
    assert "Alpha" in result.stdout
