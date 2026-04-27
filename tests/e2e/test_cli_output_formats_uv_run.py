"""E2E checks for CLI format behavior executed through `uv run`."""

from __future__ import annotations

import json

from tests.cli.subprocess_helpers import run_cli_with_mocked_result_via_uv, run_uv_python_snippet


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


def test_e2e_uv_run_cli_plain_normalizes_escaped_newlines() -> None:
    """With --format plain, escaped newline markers are normalized before CLI passthrough."""
    script = "\n".join(
        [
            "from src.cli import cli_entry",
            "import src.tools as tools",
            "from src.tools.output_contract import render_message_output",
            "async def _fake(**kwargs):",
            "    assert kwargs.get('output_format') == 'plain', kwargs",
            "    return render_message_output('line1\\\\nline2', output_format=kwargs['output_format'])",
            "setattr(tools, 'get_test_case_details', _fake)",
            "cli_entry.run_cli(['test_case', 'get', '--args', '{\"test_case_id\": 1}', '--format', 'plain'])",
        ]
    )
    result = run_uv_python_snippet(script)
    assert result.returncode == 0
    assert result.stdout == "line1\nline2"


def test_e2e_uv_run_cli_json_serializes_structured_tool_result() -> None:
    """With --format json, structured-only tool results are serialized for CLI stdout."""
    script = "\n".join(
        [
            "from src.cli import cli_entry",
            "import src.tools as tools",
            "from src.tools.output_contract import render_message_output",
            "async def _fake(**kwargs):",
            "    assert kwargs.get('output_format') == 'json', kwargs",
            "    return render_message_output('done', output_format=kwargs['output_format'])",
            "setattr(tools, 'get_test_case_details', _fake)",
            "cli_entry.run_cli(['test_case', 'get', '--args', '{\"test_case_id\": 1}', '--format', 'json'])",
        ]
    )
    result = run_uv_python_snippet(script)
    assert result.returncode == 0
    assert result.stdout == '{"message":"done"}'


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


def test_e2e_uv_run_cli_csv_rejects_invalid_json_tool_output() -> None:
    """With --format csv, CLI fails hard when the tool does not return JSON."""
    result = run_cli_with_mocked_result_via_uv(
        ["test_case", "list", "--args", "{}", "--format", "csv"],
        "list_test_cases",
        "not-json",
        expected_tool_output_format="json",
    )
    assert result.returncode != 0
    output = result.stderr + result.stdout
    assert "invalid json" in output.lower()
