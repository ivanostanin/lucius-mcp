"""Integration tests for custom field value tools."""

from unittest.mock import AsyncMock, patch

import pytest

from src.tools.create_custom_field_value import create_custom_field_value
from src.tools.delete_custom_field_value import delete_custom_field_value
from src.tools.list_custom_field_values import list_custom_field_values
from src.tools.update_custom_field_value import update_custom_field_value


@pytest.mark.asyncio
async def test_list_custom_field_values_output_format() -> None:
    mock_values = [
        type("CustomFieldValueWithTcCountDto", (), {"id": 1, "name": "Smoke", "test_cases_count": 2}),
        type("CustomFieldValueWithTcCountDto", (), {"id": 2, "name": "Regression", "test_cases_count": 0}),
    ]
    mock_page = type(
        "PageCustomFieldValueWithTcCountDto",
        (),
        {"content": mock_values, "total_elements": 2, "number": 0, "total_pages": 1},
    )

    with patch("src.tools.list_custom_field_values.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.list_custom_field_values.CustomFieldValueService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.list_custom_field_values = AsyncMock(return_value=mock_page)

            output = await list_custom_field_values(custom_field_id=10)

            assert "Found 2 custom field values" in output
            assert "ID: 1, Name: Smoke" in output
            assert "Test cases: 2" in output
            mock_service.list_custom_field_values.assert_called_once()


@pytest.mark.asyncio
async def test_list_custom_field_values_empty() -> None:
    mock_page = type("PageCustomFieldValueWithTcCountDto", (), {"content": [], "total_elements": 0})

    with patch("src.tools.list_custom_field_values.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.list_custom_field_values.CustomFieldValueService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.list_custom_field_values = AsyncMock(return_value=mock_page)

            output = await list_custom_field_values(custom_field_id=10)

            assert "No custom field values found" in output


@pytest.mark.asyncio
async def test_create_custom_field_value_output() -> None:
    mock_value = type("CustomFieldValueWithCfDto", (), {"id": 99, "name": "Smoke"})

    with patch("src.tools.create_custom_field_value.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.create_custom_field_value.CustomFieldValueService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.create_custom_field_value = AsyncMock(return_value=mock_value)

            output = await create_custom_field_value(custom_field_id=10, name="Smoke")

            assert "✅ Custom field value created successfully!" in output
            assert "ID: 99" in output
            assert "Name: Smoke" in output


@pytest.mark.asyncio
async def test_update_custom_field_value_output() -> None:
    with patch("src.tools.update_custom_field_value.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.update_custom_field_value.CustomFieldValueService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.update_custom_field_value = AsyncMock(return_value=None)

            output = await update_custom_field_value(cfv_id=7, name="Updated", custom_field_id=10)

            assert "✅ Custom field value 7 updated successfully!" in output
            assert "New name: Updated" in output


@pytest.mark.asyncio
async def test_delete_custom_field_value_output_deleted() -> None:
    with patch("src.tools.delete_custom_field_value.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.delete_custom_field_value.CustomFieldValueService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.delete_custom_field_value = AsyncMock(return_value=True)

            output = await delete_custom_field_value(cfv_id=12, custom_field_id=10)

            assert "✅ Custom field value 12 deleted successfully!" in output


@pytest.mark.asyncio
async def test_delete_custom_field_value_output_missing() -> None:
    with patch("src.tools.delete_custom_field_value.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.delete_custom_field_value.CustomFieldValueService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.delete_custom_field_value = AsyncMock(return_value=False)

            output = await delete_custom_field_value(cfv_id=12, custom_field_id=10)

            assert "already removed" in output
