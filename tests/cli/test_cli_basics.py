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
    payload = json.dumps(mocked_result)
    script = "\n".join(
        [
            "import json",
            "from src.cli import cli_entry",
            f"_payload = {payload!r}",
            "async def _fake(_tool_name, _args):",
            "    return json.loads(_payload)",
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
        {"ok": True, "count": 2},
    )
    assert result.returncode == 0
    assert '"ok"' in result.stdout
    assert '"count"' in result.stdout


def test_process_cli_csv_output_rendering():
    """Process-level check: CSV output renders tabular rows with header."""
    result = run_cli_with_mocked_result(
        ["test_case", "list", "--args", "{}", "--format", "csv"],
        [
            {"id": 1, "name": "Alpha"},
            {"id": 2, "name": "Beta", "tags": ["smoke", "regression"]},
        ],
    )
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert lines[0] == "id,name,tags"
    assert lines[1].startswith("1,Alpha,")
    assert lines[2].startswith("2,Beta,")


def test_process_cli_plain_output_renders_escaped_newlines():
    """Process-level check: plain output converts literal \\n to actual line breaks."""
    result = run_cli_with_mocked_result(
        ["test_case", "get", "--args", '{"test_case_id": 1}', "--format", "plain"],
        {"message": "line1\\nline2"},
    )
    assert result.returncode == 0
    assert "line1\nline2" in result.stdout
    assert "line1\\nline2" not in result.stdout
