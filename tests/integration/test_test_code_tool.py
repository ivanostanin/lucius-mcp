"""Integration tests for the generate_test_code MCP tool."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.test_code_service import CodeGenerationSelection
from src.tools.test_code import generate_test_code


@pytest.mark.asyncio
async def test_generate_test_code_wires_tool_arguments_to_service() -> None:
    selection = CodeGenerationSelection("TypeScript", "ts", "Playwright", "playwright", ("Name",))
    with patch("src.tools.test_code.AllureClient.from_env") as client_factory:
        client_factory.return_value.__aenter__.return_value = MagicMock()
        with patch("src.tools.test_code.TestCodeService") as service_class:
            service_class.return_value.resolve_selection.return_value = selection
            service_class.return_value.generate_code = AsyncMock(return_value="import test from 'playwright'")

            output = await generate_test_code(
                42, language="ts", framework="playwright", metadata=["Name"], output_format="plain"
            )

    assert output == "import test from 'playwright'"
    service_class.return_value.resolve_selection.assert_called_once_with("ts", "playwright", ["Name"])
    service_class.return_value.generate_code.assert_awaited_once_with(42, "ts", "playwright", ["Name"])


@pytest.mark.asyncio
async def test_generate_test_code_returns_canonical_structured_metadata() -> None:
    selection = CodeGenerationSelection("Python", "python", "Pytest", "pytest", ("Name", "Scenario"))
    with patch("src.tools.test_code.AllureClient.from_env") as client_factory:
        client_factory.return_value.__aenter__.return_value = MagicMock()
        with patch("src.tools.test_code.TestCodeService") as service_class:
            service_class.return_value.resolve_selection.return_value = selection
            service_class.return_value.generate_code = AsyncMock(return_value="def test_login(): pass")

            output = await generate_test_code(
                42, language="python", framework="pytest", metadata=["Scenario", "Name", "Name"]
            )

    assert output.structured_content == {
        "test_case_id": 42,
        "language": "Python",
        "framework": "Pytest",
        "metadata": ["Name", "Scenario"],
        "code": "def test_login(): pass",
    }


@pytest.mark.asyncio
async def test_generate_test_code_preserves_literal_escape_sequences_in_plain_output() -> None:
    code = 'assert response.text == "line1\\\\nline2"'
    selection = CodeGenerationSelection("Python", "python", "Pytest", "pytest", ("Name",))
    with patch("src.tools.test_code.AllureClient.from_env") as client_factory:
        client_factory.return_value.__aenter__.return_value = MagicMock()
        with patch("src.tools.test_code.TestCodeService") as service_class:
            service_class.return_value.resolve_selection.return_value = selection
            service_class.return_value.generate_code = AsyncMock(return_value=code)

            output = await generate_test_code(42, language="python", framework="pytest", output_format="plain")

    assert output == code
