from unittest.mock import AsyncMock, patch

import pytest

from src.tools.get_test_case_custom_fields import get_test_case_custom_fields


@pytest.mark.asyncio
async def test_tool_get_test_case_custom_fields_output_format() -> None:
    with patch("src.tools.get_test_case_custom_fields.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.get_test_case_custom_fields.TestCaseService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.get_test_case_custom_fields_values = AsyncMock(
                return_value={"Layer": "UI", "Component": ["Auth", "API"]}
            )

            output = await get_test_case_custom_fields(test_case_id=123, project_id=1)

            assert "Custom Fields for Test Case 123:" in output
            assert "- Layer: UI" in output
            assert "- Component: Auth, API" in output


@pytest.mark.asyncio
async def test_tool_get_test_case_custom_fields_empty() -> None:
    with patch("src.tools.get_test_case_custom_fields.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.get_test_case_custom_fields.TestCaseService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.get_test_case_custom_fields_values = AsyncMock(return_value={})

            output = await get_test_case_custom_fields(test_case_id=456, project_id=1)

            assert "Test Case 456 has no custom field values set." in output
