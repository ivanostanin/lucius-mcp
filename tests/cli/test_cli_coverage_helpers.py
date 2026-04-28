"""
Additional CLI tests to satisfy coverage and error-path requirements.
"""

from __future__ import annotations

import ast
import asyncio
import inspect
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

import src.cli
from src.cli import cli_entry
from src.cli.cli_entry import run_cli
from src.cli.formatting import format_as_csv, format_as_plain, format_as_table, render_output
from src.cli.help_output import _build_example_args, _first_line, _format_action_list, render_action_help
from src.cli.models import ActionSpec, CLIError
from src.cli.option_parsing import parse_action_options
from src.cli.route_matrix import all_entities_with_aliases, all_route_tool_names, iter_actions
from src.cli.routing import build_command_registry, resolve_entity_name
from src.cli.runtime import call_tool_function, error_hint_from_exception, load_tool_function
from src.cli.schema_loader import load_tool_schemas


class TestCLICoverageHelpers:
    """Exercise less common branches in CLI code."""

    def test_src_cli_main_wrapper(self) -> None:
        with patch("src.cli.cli_entry.main") as mocked_main:
            src.cli.main()
        mocked_main.assert_called_once()

    def test_load_tool_schemas_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(CLIError) as exc_info:
            load_tool_schemas(tmp_path / "tool_schemas.json", tmp_path / "cli_entry.py")
        assert "Tool schemas not found" in exc_info.value.message

    def test_load_tool_schemas_invalid_json(self, tmp_path: Path) -> None:
        invalid_file = tmp_path / "tool_schemas.json"
        invalid_file.write_text("{invalid json")
        with pytest.raises(CLIError) as exc_info:
            load_tool_schemas(invalid_file, tmp_path / "cli_entry.py")
        assert "Invalid tool schemas JSON" in exc_info.value.message

    def test_format_as_table_list_variants(self) -> None:
        assert format_as_table([]) is not None
        assert format_as_table([{"a": 1}, {"a": 2, "b": 3}]) is not None
        assert format_as_table(["x", "y"]) is not None
        assert format_as_table("value") is not None

    def test_format_as_plain_variants(self) -> None:
        assert "x" in format_as_plain(["x", "y"])
        assert format_as_plain("plain") == "plain"
        assert format_as_plain({"msg": "a\\nb"}).endswith("a\nb")

    def test_format_as_csv_variants(self) -> None:
        assert "value" in format_as_csv([])
        assert "id,name" in format_as_csv([{"id": 1, "name": "Sample"}])
        assert "value" in format_as_csv("single")

    def test_format_output_data_branches(self) -> None:
        with (
            patch.object(cli_entry.console_out, "print_json") as print_json_mock,
            patch.object(cli_entry.console_out, "print") as print_mock,
        ):
            render_output({"ok": True}, "json", cli_entry.console_out)
            render_output({"ok": True}, "table", cli_entry.console_out)
            render_output({"ok": True}, "plain", cli_entry.console_out)
            render_output({"ok": True}, "csv", cli_entry.console_out)
        assert print_json_mock.called
        assert print_mock.called

        with pytest.raises(CLIError):
            render_output({}, "yaml", cli_entry.console_out)

    def test_build_registry_missing_and_extra_schema(self) -> None:
        with pytest.raises(CLIError) as missing:
            build_command_registry({})
        assert "missing" in missing.value.message.lower()

        schemas = load_tool_schemas(cli_entry.TOOL_SCHEMAS_PATH, Path(cli_entry.__file__))
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
        assert "credentials" in error_hint_from_exception(Exception("API_TOKEN not set in environment")).lower()
        assert "permissions" in error_hint_from_exception(Exception("401 unauthorized")).lower()
        assert "parameters" in error_hint_from_exception(Exception("ValidationError: field required")).lower()
        assert "json" in error_hint_from_exception(Exception("invalid json payload")).lower()
        assert "review command parameters" in error_hint_from_exception(Exception("other")).lower()

    def test_first_line_and_example_args(self) -> None:
        assert _first_line("one\ntwo") == "one"
        assert _first_line("   ") == "No description"
        assert _format_action_list(["list", "get"]) == "get, list"
        assert _format_action_list(["list", "get", "create", "delete", "search"]) == "create, delete, get, list, search"
        assert _format_action_list([]) == "-"

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
        render_action_help(spec, cli_entry.console_out)
        out = capsys.readouterr().out
        assert "(no parameters)" in out

    def test_parse_action_options_error_paths(self) -> None:
        options = parse_action_options(["--help"])
        assert options.show_help is True
        csv_options = parse_action_options(["--format", "csv"])
        assert csv_options.output_format == "csv"

        with pytest.raises(CLIError):
            parse_action_options(["--args"])
        with pytest.raises(CLIError):
            parse_action_options(["--format"])
        with pytest.raises(CLIError):
            parse_action_options(["--unknown"])

    def test_load_tool_function_paths(self) -> None:
        assert callable(load_tool_function("create_test_case"))
        assert callable(load_tool_function("delete_test_plan"))
        with pytest.raises(CLIError):
            load_tool_function("tool_that_does_not_exist")

    @pytest.mark.asyncio
    async def test_call_tool_function_extra_branches(self) -> None:
        with patch("src.cli.runtime.load_tool_function", return_value=AsyncMock(side_effect=CLIError("x"))):
            with pytest.raises(CLIError):
                await call_tool_function("a", {})

        with patch(
            "src.cli.runtime.load_tool_function",
            return_value=AsyncMock(side_effect=asyncio.CancelledError()),
        ):
            with pytest.raises(CLIError) as cancelled:
                await call_tool_function("a", {})
        assert "cancelled" in cancelled.value.message.lower()

    def test_run_cli_additional_error_paths(self) -> None:
        with pytest.raises(CLIError):
            run_cli(["test_case", "list", "--format", "yaml"])
        with pytest.raises(CLIError):
            run_cli(["test_case", "list", "--args", "[]"])
        with pytest.raises(CLIError) as output_format_error:
            run_cli(["test_case", "list", "--args", '{"output_format":"plain"}'])
        assert "unknown parameter 'output_format'" in output_format_error.value.message.lower()

        with (
            patch("src.cli.cli_entry.call_tool_function", new=AsyncMock(return_value={"ok": True})),
            patch("src.cli.command_runner.render_output"),
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
        schemas = load_tool_schemas(cli_entry.TOOL_SCHEMAS_PATH, Path(cli_entry.__file__))
        assert schemas["get_test_case_details"]["entity"] == "test_case"
        assert schemas["get_test_case_details"]["action"] == "get"
        assert "example_command" in schemas["get_test_case_details"]
        assert "output_format" not in schemas["get_test_case_details"]["input_schema"]["properties"]

    def test_every_route_tool_signature_supports_output_format(self) -> None:
        for tool_name in all_route_tool_names():
            fn = load_tool_function(tool_name)
            signature = inspect.signature(fn)
            output_param = signature.parameters.get("output_format")
            assert output_param is not None, f"{tool_name} missing output_format"
            assert output_param.default is None

    def test_schema_json_serializable(self) -> None:
        schemas = load_tool_schemas(cli_entry.TOOL_SCHEMAS_PATH, Path(cli_entry.__file__))
        serialized = json.dumps(schemas)
        assert "create_test_case" in serialized

    def test_every_async_tool_in_src_tools_has_output_format_default_structured(self) -> None:
        tools_dir = Path(__file__).resolve().parents[2] / "src" / "tools"
        skip_modules = {"__init__.py", "annotations.py", "test_layers.py", "output_contract.py"}

        for module_path in sorted(tools_dir.glob("*.py")):
            if module_path.name in skip_modules:
                continue

            module = __import__(f"src.tools.{module_path.stem}", fromlist=["*"])
            for _, fn in inspect.getmembers(module, inspect.iscoroutinefunction):
                signature = inspect.signature(fn)
                output_param = signature.parameters.get("output_format")
                assert output_param is not None, f"{module_path.name}:{fn.__name__} missing output_format"
                assert output_param.default is None, f"{module_path.name}:{fn.__name__} default is not structured"

    def test_every_async_tool_docstring_mentions_output_format(self) -> None:
        tools_dir = Path(__file__).resolve().parents[2] / "src" / "tools"
        skip_modules = {"__init__.py", "annotations.py", "test_layers.py", "output_contract.py"}

        for module_path in sorted(tools_dir.glob("*.py")):
            if module_path.name in skip_modules:
                continue

            tree = ast.parse(module_path.read_text(encoding="utf-8"))
            for node in tree.body:
                if not isinstance(node, ast.AsyncFunctionDef):
                    continue

                param_names = [arg.arg for arg in node.args.args] + [arg.arg for arg in node.args.kwonlyargs]
                if "output_format" not in param_names:
                    continue

                docstring = ast.get_docstring(node) or ""
                assert "output_format:" in docstring, (
                    f"{module_path.name}:{node.name} docstring must document output_format"
                )

    def test_every_async_tool_uses_output_format_in_its_body(self) -> None:  # noqa: C901
        tools_dir = Path(__file__).resolve().parents[2] / "src" / "tools"
        skip_modules = {"__init__.py", "annotations.py", "test_layers.py", "output_contract.py"}
        formatter_names = {
            "render_output",
            "render_message_output",
            "render_collection_output",
            "render_confirmation_required",
            "apply_output_contract",
        }

        for module_path in sorted(tools_dir.glob("*.py")):
            if module_path.name in skip_modules:
                continue

            tree = ast.parse(module_path.read_text(encoding="utf-8"))
            for node in tree.body:
                if not isinstance(node, ast.AsyncFunctionDef):
                    continue

                param_names = [arg.arg for arg in node.args.args] + [arg.arg for arg in node.args.kwonlyargs]
                if "output_format" not in param_names:
                    continue

                used = any(isinstance(inner, ast.Name) and inner.id == "output_format" for inner in ast.walk(node))
                assert used, f"{module_path.name}:{node.name} declares output_format but does not use it"

                formatter_called = False
                for inner in ast.walk(node):
                    if not isinstance(inner, ast.Call):
                        continue
                    if isinstance(inner.func, ast.Name) and inner.func.id in formatter_names:
                        for keyword in inner.keywords:
                            if keyword.arg == "output_format" and isinstance(keyword.value, ast.Name):
                                if keyword.value.id == "output_format":
                                    formatter_called = True
                                    break
                    if formatter_called:
                        break
                assert formatter_called, (
                    f"{module_path.name}:{node.name} must pass output_format into output formatter helper"
                )
