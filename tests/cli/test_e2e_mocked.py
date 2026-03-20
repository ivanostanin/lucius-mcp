"""
E2E-style CLI unit tests with mocked command execution.
"""

from __future__ import annotations

import json
import sys
from unittest.mock import AsyncMock, patch

import pytest
from rich.console import Console

from src.cli import cli_entry
from src.cli.cli_entry import (
    ActionSpec,
    CLIError,
    build_command_registry,
    call_tool_function,
    format_as_csv,
    format_as_plain,
    format_as_table,
    format_json,
    load_tool_schemas,
    print_action_help,
    resolve_action_name,
    resolve_entity_name,
    run_cli,
    validate_args_against_schema,
)


def render_table(table: object) -> str:
    """Render a Rich table-like object to text for assertions."""
    console = Console(record=True, width=140)
    console.print(table)
    return console.export_text()


class TestE2ECommandRegistry:
    """Validate entity/action registry mapping."""

    def test_build_registry_contains_expected_mappings(self) -> None:
        schemas = load_tool_schemas()
        registry = build_command_registry(schemas)

        assert registry["test_case"]["list"].tool_name == "list_test_cases"
        assert registry["test_case"]["get"].tool_name == "get_test_case_details"
        assert registry["test_case"]["create"].tool_name == "create_test_case"
        assert registry["test_case"]["update"].tool_name == "update_test_case"
        assert registry["test_case"]["delete"].tool_name == "delete_test_case"
        assert registry["test_case"]["search"].tool_name == "search_test_cases"
        assert registry["launch"]["create"].tool_name == "create_launch"
        assert registry["launch"]["close"].tool_name == "close_launch"
        assert registry["launch"]["reopen"].tool_name == "reopen_launch"
        assert registry["integration"]["list"].tool_name == "list_integrations"
        assert registry["shared_step"]["delete_archived"].tool_name == "delete_archived_shared_steps"
        assert registry["shared_step"]["link_test_case"].tool_name == "link_shared_step"
        assert registry["shared_step"]["unlink_test_case"].tool_name == "unlink_shared_step"
        assert registry["defect"]["link_test_case"].tool_name == "link_defect_to_test_case"
        assert registry["test_plan"]["delete"].tool_name == "delete_test_plan"

    def test_resolve_entity_plural_alias(self) -> None:
        schemas = load_tool_schemas()
        registry = build_command_registry(schemas)
        assert resolve_entity_name("integrations", registry) == "integration"
        assert resolve_entity_name("test-cases", registry) == "test_case"

    def test_resolve_entity_unknown(self) -> None:
        schemas = load_tool_schemas()
        registry = build_command_registry(schemas)
        with pytest.raises(CLIError) as exc_info:
            resolve_entity_name("unknown_entity", registry)
        assert "Unknown entity" in exc_info.value.message
        assert exc_info.value.hint
        assert "Canonical entities:" in exc_info.value.hint
        assert "test_case" in exc_info.value.hint

    def test_resolve_action_alias(self) -> None:
        schemas = load_tool_schemas()
        registry = build_command_registry(schemas)
        actions = registry["custom_field"]
        assert resolve_action_name("custom_field", "list", actions) == "get"
        assert resolve_action_name("custom_field", "delete-unused", actions) == "delete_unused"

    def test_resolve_action_unknown(self) -> None:
        schemas = load_tool_schemas()
        registry = build_command_registry(schemas)
        actions = registry["test_case"]
        with pytest.raises(CLIError) as exc_info:
            resolve_action_name("test_case", "bad_action", actions)
        assert "Unknown action" in exc_info.value.message


class TestE2EDirectToolExecution:
    """Validate direct execution of service-backed tool functions."""

    @pytest.mark.asyncio
    async def test_call_tool_function_success(self) -> None:
        mock_tool = AsyncMock(return_value={"id": 123, "name": "ok"})
        with patch("src.cli.cli_entry._load_tool_function", return_value=mock_tool):
            result = await call_tool_function("list_test_cases", {"page": 0})
        assert result["id"] == 123
        mock_tool.assert_awaited_once_with(page=0)

    @pytest.mark.asyncio
    async def test_call_tool_function_type_error(self) -> None:
        mock_tool = AsyncMock(side_effect=TypeError("unexpected keyword argument"))
        with patch("src.cli.cli_entry._load_tool_function", return_value=mock_tool):
            with pytest.raises(CLIError) as exc_info:
                await call_tool_function("list_test_cases", {"bad": 1})
        assert "Invalid parameters" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_call_tool_function_runtime_error(self) -> None:
        mock_tool = AsyncMock(side_effect=Exception("401 Unauthorized"))
        with patch("src.cli.cli_entry._load_tool_function", return_value=mock_tool):
            with pytest.raises(CLIError) as exc_info:
                await call_tool_function("list_test_cases", {"page": 0})
        assert "Error executing" in exc_info.value.message
        assert exc_info.value.hint


class TestE2ERouting:
    """Validate top-level command routing behavior."""

    def test_run_cli_entity_prints_actions(self, capsys: pytest.CaptureFixture[str]) -> None:
        run_cli(["test_case"])
        output = capsys.readouterr().out
        assert "Actions for test_case" in output
        assert "list" in output

    def test_run_cli_action_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        run_cli(["test_case", "list", "--help"])
        output = capsys.readouterr().out
        assert "Command:" in output
        assert "lucius test_case list" in output

    def test_run_cli_legacy_call_rejected(self) -> None:
        with pytest.raises(CLIError) as exc_info:
            run_cli(["call", "list_test_cases", "--args", "{}"])
        assert "Legacy command style" in exc_info.value.message

    def test_run_cli_executes_mapped_action(self) -> None:
        with (
            patch("src.cli.cli_entry.call_tool_function", new=AsyncMock(return_value='{"ok":true}')) as mock_call,
            patch.object(cli_entry.console_out, "print") as mock_print,
            patch("src.cli.cli_entry.format_output_data") as mock_format,
        ):
            run_cli(["test_case", "list", "--args", "{}", "--format", "json"])

        mock_call.assert_awaited_once_with("list_test_cases", {"output_format": "json"})
        mock_print.assert_called_once_with('{"ok":true}', end="")
        mock_format.assert_not_called()

    def test_run_cli_uses_json_default_when_format_is_omitted(self) -> None:
        with (
            patch("src.cli.cli_entry.call_tool_function", new=AsyncMock(return_value='{"ok":true}')) as mock_call,
            patch.object(cli_entry.console_out, "print") as mock_print,
            patch("src.cli.cli_entry.format_output_data") as mock_format,
        ):
            run_cli(["test_case", "list", "--args", "{}"])

        mock_call.assert_awaited_once_with("list_test_cases", {"output_format": "json"})
        mock_print.assert_called_once_with('{"ok":true}', end="")
        mock_format.assert_not_called()

    def test_run_cli_plain_mode_passthrough(self) -> None:
        with (
            patch("src.cli.cli_entry.call_tool_function", new=AsyncMock(return_value="line1\nline2")) as mock_call,
            patch.object(cli_entry.console_out, "print") as mock_print,
            patch("src.cli.cli_entry.format_output_data") as mock_format,
        ):
            run_cli(["test_case", "list", "--args", "{}", "--format", "plain"])

        mock_call.assert_awaited_once_with("list_test_cases", {"output_format": "plain"})
        mock_print.assert_called_once_with("line1\nline2", end="")
        mock_format.assert_not_called()

    def test_run_cli_executes_csv_format(self) -> None:
        with (
            patch("src.cli.cli_entry.call_tool_function", new=AsyncMock(return_value='[{"id":1}]')) as mock_call,
            patch("src.cli.cli_entry.format_output_data") as mock_format,
        ):
            run_cli(["test_case", "list", "--args", "{}", "--format", "csv"])

        mock_call.assert_awaited_once_with("list_test_cases", {"output_format": "json"})
        mock_format.assert_called_once_with([{"id": 1}], "csv")

    def test_run_cli_executes_csv_format_from_items_envelope(self) -> None:
        with (
            patch(
                "src.cli.cli_entry.call_tool_function",
                new=AsyncMock(return_value='{"items":[{"id":1,"name":"Alpha"}],"total":1}'),
            ) as mock_call,
            patch("src.cli.cli_entry.format_output_data") as mock_format,
        ):
            run_cli(["test_case", "list", "--args", "{}", "--format", "csv"])

        mock_call.assert_awaited_once_with("list_test_cases", {"output_format": "json"})
        mock_format.assert_called_once_with([{"id": 1, "name": "Alpha"}], "csv")

    def test_run_cli_csv_rejects_invalid_json_tool_output(self) -> None:
        with patch("src.cli.cli_entry.call_tool_function", new=AsyncMock(return_value="not-json")):
            with pytest.raises(CLIError) as exc_info:
                run_cli(["test_case", "list", "--args", "{}", "--format", "csv"])
        assert "invalid json" in exc_info.value.message.lower()

    def test_run_cli_invalid_json(self) -> None:
        with pytest.raises(CLIError) as exc_info:
            run_cli(["test_case", "list", "--args", "{invalid}"])
        assert "Invalid JSON" in exc_info.value.message


class TestCLIImportBoundary:
    """Ensure CLI execution path doesn't import FastMCP runtime modules."""

    def test_help_path_does_not_import_fastmcp_or_src_main(self, capsys: pytest.CaptureFixture[str]) -> None:
        sys.modules.pop("fastmcp", None)
        sys.modules.pop("src.main", None)
        run_cli(["--help"])
        _ = capsys.readouterr()
        assert "fastmcp" not in sys.modules
        assert "src.main" not in sys.modules

    def test_action_path_does_not_import_fastmcp_or_src_main(self) -> None:
        sys.modules.pop("fastmcp", None)
        sys.modules.pop("src.main", None)
        with (
            patch("src.cli.cli_entry.call_tool_function", new=AsyncMock(return_value='{"ok":true}')),
            patch("src.cli.cli_entry.format_output_data"),
        ):
            run_cli(["test_case", "list", "--args", "{}"])
        assert "fastmcp" not in sys.modules
        assert "src.main" not in sys.modules


class TestE2EFormatting:
    """Test output formatting helpers."""

    def test_format_json_dict(self) -> None:
        data = {"id": 1, "name": "Test", "nested": {"key": "value"}}
        result = format_json(data)
        parsed = json.loads(result)
        assert parsed["id"] == 1
        assert parsed["nested"]["key"] == "value"

    def test_format_table_tools(self) -> None:
        tools = {
            "create_test_case": {
                "name": "create_test_case",
                "description": "Create a new test case",
                "input_schema": {"properties": {"name": {"type": "string"}}},
            },
            "get_test_case_details": {
                "name": "get_test_case_details",
                "description": "Get details",
                "input_schema": {"properties": {"test_case_id": {"type": "integer"}}},
            },
        }
        rendered = render_table(format_as_table(tools))
        assert "create_test_case" in rendered
        assert "Tool Name" in rendered

    def test_format_table_generic_result_dict(self) -> None:
        rendered = render_table(format_as_table({"id": 123, "name": "Sample"}))
        assert "id" in rendered
        assert "123" in rendered
        assert "Sample" in rendered

    def test_format_plain(self) -> None:
        result = format_as_plain({"id": 1, "name": "Test"})
        assert "id: 1" in result
        assert "name: Test" in result

    def test_format_plain_renders_escaped_newlines(self) -> None:
        result = format_as_plain({"message": "line1\\nline2"})
        assert "line1\nline2" in result
        assert "line1\\nline2" not in result

    def test_format_csv_for_multi_record_result(self) -> None:
        csv_output = format_as_csv(
            [
                {"id": 1, "name": "Alpha"},
                {"id": 2, "name": "Beta", "tags": ["smoke", "regression"]},
            ]
        )
        lines = csv_output.strip().splitlines()
        assert lines[0] == "id,name,tags"
        assert lines[1].startswith("1,Alpha,")
        assert lines[2].startswith("2,Beta,")

    def test_format_csv_quotes_values(self) -> None:
        csv_output = format_as_csv([{"id": 1, "name": 'He said "Hi"', "note": "a,b"}])
        assert '"He said ""Hi"""' in csv_output
        assert '"a,b"' in csv_output

    def test_format_csv_does_not_truncate_nested_values(self) -> None:
        long_value = "x" * 260
        csv_output = format_as_csv([{"id": 1, "meta": {"note": long_value}}])
        assert long_value in csv_output
        assert "..." not in csv_output


class TestE2EValidationAndHelp:
    """Test schema validation and help rendering."""

    def test_validate_args_required_param_missing(self) -> None:
        schema = {
            "name": "get_test_case_details",
            "input_schema": {
                "type": "object",
                "properties": {"test_case_id": {"type": "integer"}},
                "required": ["test_case_id"],
            },
        }
        with pytest.raises(CLIError) as exc_info:
            validate_args_against_schema({}, "test_case get", schema)
        assert "requires parameter 'test_case_id'" in exc_info.value.message

    def test_validate_args_unknown_param(self) -> None:
        schema = {
            "name": "list_test_cases",
            "input_schema": {
                "type": "object",
                "properties": {"page": {"type": "integer"}},
                "required": [],
            },
        }
        with pytest.raises(CLIError) as exc_info:
            validate_args_against_schema({"bad": 1}, "test_case list", schema)
        assert "Unknown parameter 'bad'" in exc_info.value.message

    def test_validate_args_success(self) -> None:
        schema = {
            "name": "list_test_cases",
            "input_schema": {
                "type": "object",
                "properties": {"page": {"type": "integer"}},
                "required": [],
            },
        }
        validate_args_against_schema({"page": 0}, "test_case list", schema)

    def test_validate_args_type_mismatch(self) -> None:
        schema = {
            "name": "list_test_cases",
            "input_schema": {
                "type": "object",
                "properties": {"page": {"type": "integer"}},
                "required": [],
            },
        }
        with pytest.raises(CLIError) as exc_info:
            validate_args_against_schema({"page": "zero"}, "test_case list", schema)
        assert "Invalid value for parameter 'page'" in exc_info.value.message

    def test_validate_args_enum_and_numeric_constraints(self) -> None:
        schema = {
            "name": "search_test_cases",
            "input_schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["active", "draft"]},
                    "size": {"type": "integer", "minimum": 1, "maximum": 100},
                },
                "required": [],
            },
        }
        with pytest.raises(CLIError) as enum_error:
            validate_args_against_schema({"status": "archived"}, "test_case search", schema)
        assert "must be one of" in enum_error.value.message

        with pytest.raises(CLIError) as range_error:
            validate_args_against_schema({"size": 0}, "test_case search", schema)
        assert "must be >=" in range_error.value.message

    def test_validate_args_anyof_accepts_nullable(self) -> None:
        schema = {
            "name": "list_launches",
            "input_schema": {
                "type": "object",
                "properties": {
                    "project_id": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                },
                "required": [],
            },
        }
        validate_args_against_schema({"project_id": None}, "launch list", schema)
        validate_args_against_schema({"project_id": "123"}, "launch list", schema)

    def test_print_action_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        spec = ActionSpec(
            tool_name="list_test_cases",
            entity="test_case",
            action="list",
            schema={
                "description": "List all test cases.",
                "input_schema": {
                    "type": "object",
                    "properties": {"page": {"type": "integer", "description": "Page index."}},
                    "required": [],
                },
            },
        )
        print_action_help(spec)
        output = capsys.readouterr().out
        assert "lucius test_case list" in output
        assert "List all test cases." in output
        assert "page" in output
