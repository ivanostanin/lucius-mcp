"""
E2E tests for CLI with mocked API responses.

These tests verify CLI tool invocation with Allure API responses mocked
using pytest-asyncio and direct function calls (not subprocess).
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from rich.console import Console

from src.cli.cli_entry import (
    CLIError,
    call_tool_mcp,
    format_as_plain,
    format_as_table,
    format_json,
    load_tool_schemas,
    print_tool_help,
    validate_args_against_schema,
)


def render_table(table: object) -> str:
    """Render a Rich table-like object to text for assertions."""
    console = Console(record=True, width=140)
    console.print(table)
    return console.export_text()


class TestE2EToolCallsWithMockedAPI:
    """
    E2E tests for tool calls with mocked Allure API responses.

    Tests mock the MCP layer to verify CLI handles API responses correctly.
    """

    @pytest.mark.asyncio
    async def test_get_test_case_mocked_success(self) -> None:
        """Test get_test_case with mocked successful API response."""
        # Mock the MCP server
        mock_tool = MagicMock()
        mock_tool.name = "get_test_case"

        mock_result = MagicMock()
        mock_result.content = [
            MagicMock(
                text=json.dumps(
                    {
                        "id": 1234,
                        "name": "Test Login",
                        "description": "Login test case",
                        "status": "active",
                    }
                )
            )
        ]

        with patch("src.main.mcp") as mock_mcp:
            mock_mcp.get_tool = AsyncMock(return_value=mock_tool)
            mock_mcp.call_tool = AsyncMock(return_value=mock_result)

            # Call the tool
            result = await call_tool_mcp("get_test_case", {"id": 1234})

            # Verify result
            assert isinstance(result, dict)
            assert result["id"] == 1234
            assert result["name"] == "Test Login"

            # Verify MCP was called correctly
            mock_mcp.get_tool.assert_called_once_with("get_test_case")
            mock_mcp.call_tool.assert_called_once_with("get_test_case", arguments={"id": 1234})

    @pytest.mark.asyncio
    async def test_list_test_cases_mocked_success(self) -> None:
        """Test list_test_cases with mocked paginated response."""
        mock_tool = MagicMock()
        mock_tool.name = "list_test_cases"

        mock_result = MagicMock()
        mock_result.content = [
            MagicMock(
                text=json.dumps(
                    {
                        "total": 150,
                        "page": 1,
                        "size": 50,
                        "items": [
                            {"id": 1, "name": "Test 1"},
                            {"id": 2, "name": "Test 2"},
                            {"id": 3, "name": "Test 3"},
                        ],
                    }
                )
            )
        ]

        with patch("src.main.mcp") as mock_mcp:
            mock_mcp.get_tool = AsyncMock(return_value=mock_tool)
            mock_mcp.call_tool = AsyncMock(return_value=mock_result)

            result = await call_tool_mcp("list_test_cases", {"page": 1, "size": 50})

            assert isinstance(result, dict)
            assert result["total"] == 150
            assert result["page"] == 1
            assert len(result["items"]) == 3

    @pytest.mark.asyncio
    async def test_create_test_case_mocked_success(self) -> None:
        """Test create_test_case with mocked success response."""
        mock_tool = MagicMock()
        mock_tool.name = "create_test_case"

        mock_result = MagicMock()
        mock_result.content = [
            MagicMock(
                text=json.dumps(
                    {
                        "message": "Test case created successfully",
                        "id": 5678,
                        "name": "New Test Case",
                    }
                )
            )
        ]

        with patch("src.main.mcp") as mock_mcp:
            mock_mcp.get_tool = AsyncMock(return_value=mock_tool)
            mock_mcp.call_tool = AsyncMock(return_value=mock_result)

            args = {
                "name": "New Test Case",
                "description": "Test description",
                "steps": [{"action": "Step 1", "expected": "Result 1"}],
            }

            result = await call_tool_mcp("create_test_case", args)

            assert result["id"] == 5678
            assert result["name"] == "New Test Case"
            assert "message" in result

    @pytest.mark.asyncio
    async def test_tool_not_found_error(self) -> None:
        """Test error handling when tool doesn't exist."""
        mock_tool1 = MagicMock()
        mock_tool1.name = "get_test_case"
        mock_tool2 = MagicMock()
        mock_tool2.name = "list_test_cases"

        with patch("src.main.mcp") as mock_mcp:
            mock_mcp.get_tool = AsyncMock(return_value=None)
            mock_mcp.list_tools = AsyncMock(return_value=[mock_tool1, mock_tool2])

            with pytest.raises(CLIError) as exc_info:
                await call_tool_mcp("nonexistent_tool", {})

            error = exc_info.value
            assert "not found" in error.message.lower()
            assert "Available tools:" in error.hint
            assert error.exit_code == 1

    @pytest.mark.asyncio
    async def test_tool_api_error_with_guidance(self) -> None:
        """Test API error provides guiding message."""
        mock_tool = MagicMock()
        mock_tool.name = "get_test_case"

        # Simulate API error
        with patch("src.main.mcp") as mock_mcp:
            mock_mcp.get_tool = AsyncMock(return_value=mock_tool)
            mock_mcp.call_tool = AsyncMock(side_effect=Exception("401 Unauthorized: Invalid API token"))

            with pytest.raises(CLIError) as exc_info:
                await call_tool_mcp("get_test_case", {"id": 1234})

            error = exc_info.value
            assert "Error" in error.message
            assert "401" in error.message
            assert error.hint
            assert error.exit_code == 1

    @pytest.mark.asyncio
    async def test_tool_validation_error(self) -> None:
        """Test validation error provides guiding message."""
        mock_tool = MagicMock()
        mock_tool.name = "get_test_case"

        # Simulate validation error
        with patch("src.main.mcp") as mock_mcp:
            mock_mcp.get_tool = AsyncMock(return_value=mock_tool)
            mock_mcp.call_tool = AsyncMock(side_effect=Exception("ValidationError: field required"))

            with pytest.raises(CLIError) as exc_info:
                await call_tool_mcp("get_test_case", {})

            error = exc_info.value
            assert "Error" in error.message
            assert error.exit_code == 1


class TestE2EMultipleOutputFormats:
    """Test output formatting with various data types."""

    def test_format_json_dict(self) -> None:
        """Test JSON formatting of dictionary."""
        data = {"id": 1, "name": "Test", "nested": {"key": "value"}}
        result = format_json(data)

        parsed = json.loads(result)
        assert parsed["id"] == 1
        assert parsed["name"] == "Test"
        assert parsed["nested"]["key"] == "value"

    def test_format_json_list(self) -> None:
        """Test JSON formatting of list."""
        data = [
            {"id": 1, "name": "Test 1"},
            {"id": 2, "name": "Test 2"},
        ]
        result = format_json(data)

        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["id"] == 1

    def test_format_table_tools(self) -> None:
        """Test table formatting of tools list."""
        tools = {
            "create_test_case": {
                "name": "create_test_case",
                "description": "Create a new test case",
                "input_schema": {
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                    },
                },
            },
            "get_test_case": {
                "name": "get_test_case",
                "description": "Get test case details",
                "input_schema": {
                    "properties": {
                        "id": {"type": "number"},
                    },
                },
            },
        }

        result = format_as_table(tools)
        rendered = render_table(result)
        assert "create_test_case" in rendered
        assert "get_test_case" in rendered
        assert "Tool Name" in rendered
        assert "Parameters" in rendered

    def test_format_table_empty_params(self) -> None:
        """Test table formatting with tools without parameters."""
        tools = {
            "no_params_tool": {
                "name": "no_params_tool",
                "description": "Tool with no params",
                "input_schema": {"properties": {}},
            }
        }

        result = format_as_table(tools)
        rendered = render_table(result)
        assert "no_params_tool" in rendered
        assert "(no parameters)" in rendered

    def test_format_table_generic_result_dict(self) -> None:
        """Test table formatting for normal command result dictionaries."""
        result = format_as_table({"id": 123, "name": "Sample"})
        rendered = render_table(result)
        assert "id" in rendered
        assert "123" in rendered
        assert "name" in rendered
        assert "Sample" in rendered

    def test_format_plain_dict(self) -> None:
        """Test plain text formatting of dictionary."""
        data = {"id": 1, "name": "Test", "status": "active"}
        result = format_as_plain(data)

        assert "id: 1" in result
        assert "name: Test" in result
        assert "status: active" in result

    def test_format_plain_list(self) -> None:
        """Test plain text formatting of list."""
        data = ["Item 1", "Item 2", "Item 3"]
        result = format_as_plain(data)

        assert "Item 1" in result
        assert "Item 2" in result
        assert "Item 3" in result

    def test_format_plain_string(self) -> None:
        """Test plain text formatting of string."""
        data = "Just a string"
        result = format_as_plain(data)

        assert result == "Just a string"


class TestE2EValidationAndSchemas:
    """Test schema validation and argument handling."""

    def test_validate_args_required_param_missing(self) -> None:
        """Test validation fails when required parameter missing."""
        tool_schema = {
            "name": "get_test_case",
            "input_schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "number"},
                },
                "required": ["id"],
            },
        }

        with pytest.raises(CLIError) as exc_info:
            validate_args_against_schema({}, "get_test_case", tool_schema)

        error = exc_info.value
        assert "requires parameter 'id'" in error.message
        assert "--args" in error.hint
        assert error.exit_code == 1

    def test_validate_args_unknown_param(self) -> None:
        """Test validation fails with unknown parameter."""
        tool_schema = {
            "name": "get_test_case",
            "input_schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "number"},
                },
                "required": ["id"],
            },
        }

        with pytest.raises(CLIError) as exc_info:
            validate_args_against_schema(
                {"id": 123, "unknown_param": "value"},
                "get_test_case",
                tool_schema,
            )

        error = exc_info.value
        assert "Unknown parameter 'unknown_param'" in error.message
        assert "Valid parameters:" in error.hint
        assert error.exit_code == 1

    def test_validate_args_success(self) -> None:
        """Test validation succeeds with valid arguments."""
        tool_schema = {
            "name": "get_test_case",
            "input_schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "number"},
                    "name": {"type": "string"},
                },
                "required": ["id"],
            },
        }

        # Should not raise
        validate_args_against_schema({"id": 123, "name": "Test"}, "get_test_case", tool_schema)

    def test_load_tool_schemas(self) -> None:
        """Test loading tool schemas from static JSON."""
        schemas = load_tool_schemas()

        assert isinstance(schemas, dict)
        assert len(schemas) > 0

        # Verify schema structure
        for _tool_name, schema in schemas.items():
            assert "name" in schema
            assert "description" in schema
            assert "input_schema" in schema


class TestE2EToolHelpIsolation:
    """Test isolated tool help generation."""

    def test_print_tool_help_basic(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test tool help prints correct information."""
        tool_schema = {
            "name": "get_test_case",
            "description": "Get test case details by ID",
            "input_schema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "number",
                        "description": "Test case ID",
                    },
                    "project_id": {
                        "type": "number",
                        "description": "Project ID (optional)",
                    },
                },
                "required": ["id"],
            },
        }

        print_tool_help("get_test_case", tool_schema)

        captured = capsys.readouterr()
        output = captured.out

        assert "Tool: get_test_case" in output
        assert "Get test case details by ID" in output
        assert "Parameters:" in output
        assert "id" in output
        assert "Test case ID" in output
        assert "(required)" in output
        assert "Example usage:" in output

    def test_print_tool_help_no_params(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test tool help with no parameters."""
        tool_schema = {
            "name": "list_projects",
            "description": "List all projects",
            "input_schema": {
                "type": "object",
                "properties": {},
            },
        }

        print_tool_help("list_projects", tool_schema)

        captured = capsys.readouterr()
        output = captured.out

        assert "(no parameters)" in output
        assert "Example usage:" in output

    def test_print_tool_help_with_nested_params(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test tool help with complex nested parameters."""
        tool_schema = {
            "name": "create_test_case",
            "description": "Create a new test case",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Test case name"},
                    "steps": {
                        "type": "array",
                        "description": "Test steps",
                    },
                },
                "required": ["name"],
            },
        }

        print_tool_help("create_test_case", tool_schema)

        captured = capsys.readouterr()
        output = captured.out

        assert "name" in output
        assert "steps" in output
        assert "(required)" in output  # for name


class TestE2EErrorMessagesWithGuidance:
    """Test user-friendly error messages with hints."""

    def test_cli_error_with_hint(self) -> None:
        """Test CLIError includes hint."""
        error = CLIError(
            "Tool not found",
            hint="Available tools: get_test_case, list_test_cases",
            exit_code=1,
        )

        assert error.message == "Tool not found"
        assert "Available tools:" in error.hint
        assert error.exit_code == 1

    def test_format_output_invalid_format(self, capsys: pytest.CaptureFixture[str]):
        """Test invalid format shows helpful error."""
        from src.cli.cli_entry import format_output_data

        with pytest.raises(CLIError) as exc_info:
            format_output_data({}, "invalid_format")

        error = exc_info.value
        assert "Invalid output format" in error.message
        assert "json|table|plain" in error.hint
