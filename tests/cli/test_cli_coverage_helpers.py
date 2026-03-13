"""
Additional CLI tests to satisfy coverage and error-path requirements.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

import src.cli
from src.cli import cli_entry
from src.cli.cli_entry import (
    ActionSpec,
    CLIError,
    _build_example_args,
    _error_hint_from_exception,
    _first_line,
    _load_tool_function,
    all_entities_with_aliases,
    build_command_registry,
    format_as_plain,
    format_as_table,
    format_output_data,
    load_tool_schemas,
    parse_action_options,
    print_action_help,
    resolve_entity_name,
    run_cli,
)
from src.cli.route_matrix import all_route_tool_names, iter_actions


class TestCLICoverageHelpers:
    """Exercise less common branches in CLI code."""

    def test_src_cli_main_wrapper(self) -> None:
        with patch("src.cli.cli_entry.main") as mocked_main:
            src.cli.main()
        mocked_main.assert_called_once()

    def test_load_tool_schemas_missing_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(cli_entry.Path, "exists", lambda _self: False)
        with pytest.raises(CLIError) as exc_info:
            load_tool_schemas()
        assert "Tool schemas not found" in exc_info.value.message

    def test_load_tool_schemas_invalid_json(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        invalid_file = tmp_path / "tool_schemas.json"
        invalid_file.write_text("{invalid json")
        monkeypatch.setattr(cli_entry, "TOOL_SCHEMAS_PATH", invalid_file)
        with pytest.raises(CLIError) as exc_info:
            load_tool_schemas()
        assert "Invalid tool schemas JSON" in exc_info.value.message

    def test_format_as_table_list_variants(self) -> None:
        assert format_as_table([]) is not None
        assert format_as_table([{"a": 1}, {"a": 2, "b": 3}]) is not None
        assert format_as_table(["x", "y"]) is not None
        assert format_as_table("value") is not None

    def test_format_as_plain_variants(self) -> None:
        assert "x" in format_as_plain(["x", "y"])
        assert format_as_plain("plain") == "plain"

    def test_format_output_data_branches(self) -> None:
        with (
            patch.object(cli_entry.console_out, "print_json") as print_json_mock,
            patch.object(cli_entry.console_out, "print") as print_mock,
        ):
            format_output_data({"ok": True}, "json")
            format_output_data({"ok": True}, "table")
            format_output_data({"ok": True}, "plain")
        assert print_json_mock.called
        assert print_mock.called

        with pytest.raises(CLIError):
            format_output_data({}, "yaml")

    def test_build_registry_missing_and_extra_schema(self) -> None:
        with pytest.raises(CLIError) as missing:
            build_command_registry({})
        assert "missing" in missing.value.message.lower()

        schemas = load_tool_schemas()
        schemas["unexpected_tool"] = {
            "name": "unexpected_tool",
            "description": "unexpected",
            "input_schema": {"type": "object", "properties": {}},
        }
        with pytest.raises(CLIError) as extra:
            build_command_registry(schemas)
        assert "not represented" in extra.value.message

    def test_resolve_entity_with_partial_registry(self) -> None:
        alias_map = all_entities_with_aliases()
        partial = {"test_case": {}}
        assert "test_cases" in alias_map["test_case"]
        assert resolve_entity_name("test-cases", partial) == "test_case"

    def test_error_hint_variants(self) -> None:
        assert "credentials" in _error_hint_from_exception(Exception("API_TOKEN not set in environment")).lower()
        assert "permissions" in _error_hint_from_exception(Exception("401 unauthorized")).lower()
        assert "parameters" in _error_hint_from_exception(Exception("ValidationError: field required")).lower()
        assert "json" in _error_hint_from_exception(Exception("invalid json payload")).lower()
        assert "review command parameters" in _error_hint_from_exception(Exception("other")).lower()

    def test_first_line_and_example_args(self) -> None:
        assert _first_line("one\ntwo") == "one"
        assert _first_line("   ") == "No description"

        schema = {
            "input_schema": {
                "required": ["x", "flag", "items", "obj", "opt"],
                "properties": {
                    "x": {"type": "integer"},
                    "flag": {"type": "boolean"},
                    "items": {"type": "array"},
                    "obj": {"type": "object"},
                    "opt": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                },
            }
        }
        args = _build_example_args(schema)
        assert args["x"] == 123
        assert args["flag"] is True
        assert args["items"] == []
        assert args["obj"] == {}
        assert args["opt"] == "value"

    def test_print_action_help_no_params(self, capsys: pytest.CaptureFixture[str]) -> None:
        spec = ActionSpec(
            tool_name="list_defects",
            entity="defect",
            action="list",
            schema={"description": "List defects", "input_schema": {"type": "object", "properties": {}}},
        )
        print_action_help(spec)
        out = capsys.readouterr().out
        assert "(no parameters)" in out

    def test_parse_action_options_error_paths(self) -> None:
        options = parse_action_options(["--help"])
        assert options.show_help is True

        with pytest.raises(CLIError):
            parse_action_options(["--args"])
        with pytest.raises(CLIError):
            parse_action_options(["--format"])
        with pytest.raises(CLIError):
            parse_action_options(["--unknown"])

    def test_load_tool_function_paths(self) -> None:
        assert callable(_load_tool_function("create_test_case"))
        assert callable(_load_tool_function("delete_test_plan"))
        with pytest.raises(CLIError):
            _load_tool_function("tool_that_does_not_exist")

    @pytest.mark.asyncio
    async def test_call_tool_function_extra_branches(self) -> None:
        with patch("src.cli.cli_entry._load_tool_function", return_value=AsyncMock(side_effect=CLIError("x"))):
            with pytest.raises(CLIError):
                await cli_entry.call_tool_function("a", {})

        with patch(
            "src.cli.cli_entry._load_tool_function",
            return_value=AsyncMock(side_effect=asyncio.CancelledError()),
        ):
            with pytest.raises(CLIError) as cancelled:
                await cli_entry.call_tool_function("a", {})
        assert "cancelled" in cancelled.value.message.lower()

    def test_run_cli_additional_error_paths(self) -> None:
        with pytest.raises(CLIError):
            run_cli(["test_case", "list", "--format", "yaml"])
        with pytest.raises(CLIError):
            run_cli(["test_case", "list", "--args", "[]"])

        with (
            patch("src.cli.cli_entry.call_tool_function", new=AsyncMock(return_value={"ok": True})),
            patch("src.cli.cli_entry.format_output_data"),
        ):
            run_cli(["test_case", "list", "--help"])

    def test_main_error_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "argv", ["lucius"])

        with patch("src.cli.cli_entry.run_cli", side_effect=CLIError("bad")):
            with pytest.raises(SystemExit):
                cli_entry.main()

        with patch("src.cli.cli_entry.run_cli", side_effect=KeyboardInterrupt()):
            with pytest.raises(SystemExit) as keyboard_exit:
                cli_entry.main()
        assert keyboard_exit.value.code == 130

        with patch("src.cli.cli_entry.run_cli", side_effect=Exception("boom")):
            with pytest.raises(SystemExit):
                cli_entry.main()

    def test_route_matrix_helpers(self) -> None:
        names = all_route_tool_names()
        assert "list_test_cases" in names
        assert "create_launch" in names
        actions = list(iter_actions("test_case"))
        assert "get" in actions
        assert "search" in actions

    def test_schema_file_contains_entity_action(self) -> None:
        schemas = load_tool_schemas()
        assert schemas["get_test_case_details"]["entity"] == "test_case"
        assert schemas["get_test_case_details"]["action"] == "get"
        assert "example_command" in schemas["get_test_case_details"]

    def test_schema_json_serializable(self) -> None:
        schemas = load_tool_schemas()
        serialized = json.dumps(schemas)
        assert "create_test_case" in serialized
