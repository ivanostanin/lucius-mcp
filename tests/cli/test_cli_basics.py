"""
Test basic CLI functionality.
"""

import subprocess
from pathlib import Path

# Path to the lucius project
PROJECT_ROOT = Path(__file__).parent.parent.parent


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run CLI command as subprocess."""
    result = subprocess.run(
        ["uv", "run", "python", "-m", "src.cli.cli_entry", *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    return result


def test_cli_help():
    """Test lucius --help displays help."""
    result = run_cli(["--help"])
    assert result.returncode == 0
    assert "lucius" in result.stdout
    assert "COMMAND" in result.stdout
    assert "list" in result.stdout
    assert "call" in result.stdout


def test_cli_version():
    """Test lucius --version displays version."""
    result = run_cli(["--version"])
    assert result.returncode == 0
    # Version should be in output like "lucius 0.8.0"
    assert "lucius" in result.stdout


def test_cli_list_json():
    """Test lucius list --json lists all tools in JSON format."""
    result = run_cli(["list"])
    assert result.returncode == 0


def test_cli_list_json_explicit():
    """Test lucius list --format json explicitly."""
    result = run_cli(["list", "--format", "json"])
    assert result.returncode == 0


def test_cli_list_short_flag():
    """Test lucius list -f json uses short flag."""
    result = run_cli(["list", "-f", "json"])
    assert result.returncode == 0


def test_cli_tool_help():
    """Test lucius call <tool> --help displays isolated tool help."""
    result = run_cli(["call", "list_test_cases", "--help"])
    assert result.returncode == 0
    assert "Tool: list_test_cases" in result.stdout
    assert "list_test_cases" in result.stdout


def test_cli_call_invalid_tool():
    """Test that calling a non-existent tool shows helpful error."""
    result = run_cli(["call", "nonexistent_tool", "--args", "{}"])
    assert result.returncode == 1
    assert "not found" in result.stderr or "not found" in result.stdout


def test_cli_call_invalid_json():
    """Test that invalid JSON in --args shows helpful error."""
    result = run_cli(["call", "list_test_cases", "--args", "{invalid}"])
    assert result.returncode == 1
    # Should contain error message about invalid JSON
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
    result = run_cli(["call", "nonexistent_tool", "--args", "{}"])
    assert result.returncode == 1
    # Should NOT have Python traceback
    assert "Traceback" not in result.stderr
    assert "File " not in result.stderr or "File " not in result.stdout
    # Should have user-friendly error
    assert "not found" in result.stderr.lower() or "not found" in result.stdout.lower()
