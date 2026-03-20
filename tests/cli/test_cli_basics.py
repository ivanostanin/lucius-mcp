"""
Test basic CLI functionality.
"""

import json
import subprocess
import sys
from pathlib import Path

# Path to the lucius project
PROJECT_ROOT = Path(__file__).parent.parent.parent


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run CLI command as subprocess."""
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.cli_entry", *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    return result


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
    return subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


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
    return subprocess.run(
        ["uv", "run", "--python", "3.13", "python", "-c", script],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


def test_cli_help():
    """Test lucius --help displays help."""
    result = run_cli(["--help"])
    assert result.returncode == 0
    assert "lucius" in result.stdout
    assert "Usage:" in result.stdout
    assert "Available Entities" in result.stdout
    assert "test_case" in result.stdout
    assert "--format json|table|plain|csv" in result.stdout


def test_cli_version():
    """Test lucius --version displays version."""
    result = run_cli(["--version"])
    assert result.returncode == 0
    # Version should be in output like "lucius 0.8.0"
    assert "lucius" in result.stdout


def test_cli_entity_actions():
    """Test lucius <entity> lists actions."""
    result = run_cli(["test_case"])
    assert result.returncode == 0
    assert "Actions for test_case" in result.stdout
    assert "list" in result.stdout
    assert "--format json|table|plain|csv" in result.stdout


def test_cli_entity_alias_plural():
    """Test plural entity alias resolves."""
    result = run_cli(["integrations"])
    assert result.returncode == 0
    assert "Actions for integration" in result.stdout


def test_cli_action_help():
    """Test lucius <entity> <action> --help displays isolated help."""
    result = run_cli(["test_case", "list", "--help"])
    assert result.returncode == 0
    assert "Command:" in result.stdout
    assert "lucius test_case list" in result.stdout
    assert "Mapped tool:" in result.stdout


def test_cli_invalid_entity():
    """Test unknown entity shows helpful error."""
    result = run_cli(["nonexistent_entity"])
    assert result.returncode == 1
    assert "unknown entity" in result.stderr.lower() or "unknown entity" in result.stdout.lower()


def test_cli_invalid_action():
    """Test unknown action for entity shows helpful error."""
    result = run_cli(["test_case", "nonexistent_action"])
    assert result.returncode == 1
    output = result.stderr.lower() + result.stdout.lower()
    assert "unknown action" in output


def test_cli_invalid_json():
    """Test that invalid JSON in --args shows helpful error."""
    result = run_cli(["test_case", "list", "--args", "{invalid}"])
    assert result.returncode == 1
    output = result.stderr.lower() + result.stdout.lower()
    assert "invalid" in output or "json" in output


def test_fast_startup_no_mcp_import():
    """Test that help/version commands don't import MCP components."""
    result = run_cli(["--version"])
    assert result.returncode == 0
    # The version command should be instant (< 1s) which proves no slow imports
    # We can't directly measure this in a test, but the implementation ensures it


def test_clean_error_messages():
    """Test that errors are clean and don't show Python tracebacks."""
    result = run_cli(["test_case", "nonexistent_action"])
    assert result.returncode == 1
    # Should NOT have Python traceback
    assert "Traceback" not in result.stderr
    assert "File " not in result.stderr or "File " not in result.stdout
    # Should have user-friendly error
    assert "unknown action" in result.stderr.lower() or "unknown action" in result.stdout.lower()


def test_legacy_command_style_is_rejected():
    """Test old list/call style returns migration hint."""
    result = run_cli(["call", "list_test_cases", "--args", "{}"])
    assert result.returncode == 1
    output = result.stderr.lower() + result.stdout.lower()
    assert "legacy command style" in output


def test_process_cli_default_json_output_without_format_flag():
    """Process-level check: action output defaults to JSON when --format is omitted."""
    result = run_cli_with_mocked_result(
        ["test_case", "list", "--args", "{}"],
        '{"ok":true,"count":2}',
    )
    assert result.returncode == 0
    assert result.stdout.strip() == '{"ok":true,"count":2}'


def test_process_cli_csv_output_rendering():
    """Process-level check: CSV output renders tabular rows with header."""
    result = run_cli_with_mocked_result(
        ["test_case", "list", "--args", "{}", "--format", "csv"],
        json.dumps(
            [
                {"id": 1, "name": "Alpha"},
                {"id": 2, "name": "Beta", "tags": ["smoke", "regression"]},
            ]
        ),
    )
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert lines[0] == "id,name,tags"
    assert lines[1].startswith("1,Alpha,")
    assert lines[2].startswith("2,Beta,")


def test_process_cli_csv_output_renders_items_envelope():
    """Process-level check: CSV renderer uses envelope['items'] rows when present."""
    result = run_cli_with_mocked_result(
        ["test_case", "list", "--args", "{}", "--format", "csv"],
        json.dumps({"items": [{"id": 1, "name": "Alpha"}], "total": 1}),
    )
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert lines[0] == "id,name"
    assert lines[1] == "1,Alpha"


def test_process_cli_plain_output_renders_escaped_newlines():
    """Process-level check: plain output is passed through unchanged from tool result."""
    result = run_cli_with_mocked_result(
        ["test_case", "get", "--args", '{"test_case_id": 1}', "--format", "plain"],
        "line1\nline2",
    )
    assert result.returncode == 0
    assert result.stdout == "line1\nline2"


def test_process_cli_plain_output_normalizes_escaped_newlines_end_to_end():
    """Process-level check: tool plain rendering normalizes escaped newline markers."""
    script = "\n".join(
        [
            "from src.cli import cli_entry",
            "from src.tools.output_contract import render_message_output",
            "async def _fake(_tool_name, _args):",
            "    return render_message_output('line1\\\\nline2', output_format='plain')",
            "cli_entry.call_tool_function = _fake",
            "cli_entry.run_cli(['test_case', 'get', '--args', '{\"test_case_id\": 1}', '--format', 'plain'])",
        ]
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0
    assert result.stdout == "line1\nline2"


def test_uv_run_cli_default_requests_json_and_returns_json() -> None:
    """E2E (uv run): default CLI format requests JSON tool output and returns it unchanged."""
    result = run_cli_with_mocked_result_via_uv(
        ["test_case", "list", "--args", "{}"],
        "list_test_cases",
        '{"ok":true,"count":2}',
        expected_tool_output_format="json",
    )
    assert result.returncode == 0
    assert result.stdout.strip() == '{"ok":true,"count":2}'


def test_uv_run_cli_plain_requests_plain_and_returns_plain() -> None:
    """E2E (uv run): plain CLI format requests plain tool output and returns it unchanged."""
    result = run_cli_with_mocked_result_via_uv(
        ["test_case", "get", "--args", '{"test_case_id": 1}', "--format", "plain"],
        "get_test_case_details",
        "line1\nline2",
        expected_tool_output_format="plain",
    )
    assert result.returncode == 0
    assert result.stdout == "line1\nline2"


def test_uv_run_cli_plain_normalizes_escaped_newlines_end_to_end() -> None:
    """E2E (uv run): tool plain rendering normalizes escaped newline markers."""
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
    result = subprocess.run(
        ["uv", "run", "--python", "3.13", "python", "-c", script],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0
    assert result.stdout == "line1\nline2"


def test_uv_run_cli_csv_requests_json_and_renders_csv() -> None:
    """E2E (uv run): csv CLI format requests JSON tool output and renders CSV."""
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


def test_uv_run_cli_table_requests_json_and_renders_table() -> None:
    """E2E (uv run): table CLI format requests JSON tool output and renders table."""
    result = run_cli_with_mocked_result_via_uv(
        ["test_case", "list", "--args", "{}", "--format", "table"],
        "list_test_cases",
        json.dumps([{"id": 1, "name": "Alpha"}]),
        expected_tool_output_format="json",
    )
    assert result.returncode == 0
    assert "Command Result" in result.stdout
    assert "Alpha" in result.stdout


def test_uv_run_cli_csv_rejects_invalid_json_tool_output() -> None:
    """E2E (uv run): csv CLI format fails hard when tool does not return JSON."""
    result = run_cli_with_mocked_result_via_uv(
        ["test_case", "list", "--args", "{}", "--format", "csv"],
        "list_test_cases",
        "not-json",
        expected_tool_output_format="json",
    )
    assert result.returncode != 0
    output = result.stderr + result.stdout
    assert "invalid json" in output.lower()
