from unittest.mock import AsyncMock, patch

import pytest

from src.tools.get_custom_fields import get_custom_fields


@pytest.mark.asyncio
async def test_tool_get_custom_fields_output_format() -> None:
    """Test tool output text formatting."""
    # Mock data
    mock_files = [
        {"name": "Layer", "required": True, "values": ["UI", "API"]},
        {"name": "Priority", "required": False, "values": []},
    ]

    with patch("src.tools.get_custom_fields.AllureClient.from_env") as mock_client_ctx:
        # Setup context manager mock
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        # Patch TestCaseService to return our mock data
        with patch("src.tools.get_custom_fields.TestCaseService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.get_custom_fields = AsyncMock(return_value=mock_files)

            # verify output
            output = await get_custom_fields(project_id=1)

            assert "Found 2 custom fields:" in output
            assert "- Layer (required): UI, API" in output
            assert "- Priority (optional): Any text/No allowed values" in output

            # Verify filtering pass-through
            await get_custom_fields(name="Lay", project_id=1)
            mock_service.get_custom_fields.assert_called_with(name="Lay")


@pytest.mark.asyncio
async def test_tool_get_custom_fields_empty() -> None:
    """Test tool output when no fields found."""
    with patch("src.tools.get_custom_fields.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.get_custom_fields.TestCaseService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.get_custom_fields = AsyncMock(return_value=[])

            output = await get_custom_fields(project_id=1)
            assert "No custom fields found for this project." in output

            output_filtered = await get_custom_fields(name="Missing", project_id=1)
            assert "No custom fields found matching 'Missing'." in output_filtered
