"""Integration tests for the generate_test_code MCP tool."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.tools.test_code import generate_test_code


@pytest.mark.asyncio
async def test_generate_test_code_wires_tool_arguments_to_service() -> None:
    with patch("src.tools.test_code.AllureClient.from_env") as client_factory:
        client_factory.return_value.__aenter__.return_value = MagicMock()
        with patch("src.tools.test_code.TestCodeService") as service_class:
            service_class.return_value.generate_code = AsyncMock(return_value="import pytest\n\ndef test_login(): pass")

            output = await generate_test_code(42, language="ts", framework="playwright", output_format="plain")

    assert output == "import pytest\n\ndef test_login(): pass"
    service_class.return_value.generate_code.assert_awaited_once_with(42, "ts", "playwright")


@pytest.mark.asyncio
async def test_generate_test_code_preserves_literal_escape_sequences_in_plain_output() -> None:
    code = 'assert response.text == "line1\\\\nline2"'
    with patch("src.tools.test_code.AllureClient.from_env") as client_factory:
        client_factory.return_value.__aenter__.return_value = MagicMock()
        with patch("src.tools.test_code.TestCodeService") as service_class:
            service_class.return_value.generate_code = AsyncMock(return_value=code)

            output = await generate_test_code(42, output_format="plain")

    assert output == code
