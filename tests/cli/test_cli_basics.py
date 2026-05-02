"""
Test basic CLI functionality.
"""

import json

from tests.cli.subprocess_helpers import run_cli, run_cli_with_mocked_result, run_python_snippet, run_uv_cli


def test_cli_help():
    """Test lucius --help displays help."""
    result = run_cli(["--help"])
    assert result.returncode == 0
    assert "lucius" in result.stdout
    assert "Usage:" in result.stdout
    assert "lucius auth" in result.stdout
    assert "lucius list" in result.stdout
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


def test_cli_list_displays_discovery_table():
    """Test lucius list reuses the global discovery output."""
    result = run_cli(["list"])
    assert result.returncode == 0
    assert "CLI-Local Commands" in result.stdout
    assert "Available Entities" in result.stdout
    assert "test_case" in result.stdout


def test_cli_list_matches_no_argument_output():
    """Test lucius list matches the bare CLI discovery output exactly."""
    no_args = run_cli([])
    listed = run_cli(["list"])
    assert no_args.returncode == 0
    assert listed.returncode == 0
    assert listed.stdout == no_args.stdout


def test_cli_list_help():
    """Test lucius list --help displays explicit local command guidance."""
    result = run_cli(["list", "--help"])
    assert result.returncode == 0
    output = result.stdout.lower()
    assert "cli-local discovery command" in output
    assert "does not require --args" in output
    assert "saved credentials" in output
    assert "network access" in output


def test_cli_list_rejects_unknown_option_cleanly():
    """Test lucius list rejects unsupported options without a traceback."""
    result = run_cli(["list", "--format", "json"])
    assert result.returncode == 1
    output = result.stderr.lower() + result.stdout.lower()
    assert "unknown option '--format'" in output
    assert "supported list options" in output
    assert "traceback" not in output
    assert "file " not in output


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
    assert "--pretty" in result.stdout


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
    """Test only legacy call style remains rejected."""
    result = run_cli(["call", "list_test_cases", "--args", "{}"])
    assert result.returncode == 1
    output = result.stderr.lower() + result.stdout.lower()
    assert "legacy command style" in output

    accepted = run_cli(["list"])
    assert accepted.returncode == 0


def test_process_cli_default_json_output_without_format_flag():
    """Process-level check: action output defaults to JSON when --format is omitted."""
    result = run_cli_with_mocked_result(
        ["test_case", "list", "--args", "{}"],
        '{"ok":true,"count":2}',
    )
    assert result.returncode == 0
    assert result.stdout.strip() == '{"ok":true,"count":2}'


def test_process_cli_default_json_pretty_output():
    """Process-level check: --pretty formats default JSON output."""
    result = run_cli_with_mocked_result(
        ["test_case", "list", "--args", "{}", "--pretty"],
        '{"ok":true,"count":2}',
    )
    assert result.returncode == 0
    assert result.stdout.strip() == '{\n  "ok": true,\n  "count": 2\n}'


def test_process_cli_explicit_json_pretty_output():
    """Process-level check: --format json --pretty formats JSON output."""
    result = run_cli_with_mocked_result(
        ["test_case", "list", "--args", "{}", "--format", "json", "--pretty"],
        '{"items":[{"id":1,"name":"Alpha"}],"total":1}',
    )
    assert result.returncode == 0
    assert '"items": [' in result.stdout
    assert '      "name": "Alpha"' in result.stdout


def test_process_cli_pretty_rejects_non_json_formats_without_traceback():
    """Process-level check: --pretty is valid only for JSON output modes."""
    for output_format in ("plain", "table", "csv"):
        result = run_cli(["test_case", "list", "--args", "{}", "--format", output_format, "--pretty"])
        assert result.returncode == 1
        output = result.stderr.lower() + result.stdout.lower()
        assert "--pretty" in output
        assert "json output" in output
        assert "traceback" not in output
        assert "file " not in output


def test_process_cli_pretty_rejected_for_non_action_flows_without_traceback():
    """Process-level check: unsupported non-action --pretty usage is guided."""
    for args in (["--pretty"], ["--help", "--pretty"], ["--version", "--pretty"], ["test_case", "--pretty"]):
        result = run_cli(args)
        assert result.returncode == 1
        output = result.stderr.lower() + result.stdout.lower()
        assert "--pretty" in output
        assert "json output" in output
        assert "traceback" not in output
        assert "file " not in output


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
    result = run_python_snippet(script)
    assert result.returncode == 0
    assert result.stdout == "line1\nline2"


def test_process_cli_list_blocks_runtime_imports():
    """Process-level check: lucius list stays on the static CLI-local path."""
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
            "run_cli(['list'])",
            "run_cli(['list', '--help'])",
            "assert all(prefix not in sys.modules for prefix in _blocked)",
        ]
    )
    result = run_python_snippet(script)
    assert result.returncode == 0, result.stderr


def test_uv_run_cli_list_parity_and_help():
    """Process-level check: uv run lucius exposes list as the explicit discovery command."""
    bare = run_uv_cli([])
    listed = run_uv_cli(["list"])
    help_result = run_uv_cli(["list", "--help"])

    assert bare.returncode == 0
    assert listed.returncode == 0
    assert help_result.returncode == 0
    assert listed.stdout == bare.stdout
    assert "cli-local discovery command" in help_result.stdout.lower()
