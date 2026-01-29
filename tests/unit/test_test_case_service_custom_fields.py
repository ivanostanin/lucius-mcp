from unittest.mock import AsyncMock

import pytest

from src.client import AllureClient
from src.client.generated.models import (
    CustomFieldDto,
    CustomFieldProjectDto,
    CustomFieldProjectWithValuesDto,
    CustomFieldValueDto,
)
from src.services.test_case_service import TestCaseService


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock(spec=AllureClient)
    client.get_project.return_value = 1
    return client


@pytest.fixture
def service(mock_client: AsyncMock) -> TestCaseService:
    return TestCaseService(client=mock_client)


@pytest.mark.asyncio
async def test_get_custom_fields_returns_mapped_data(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test standard retrieval and mapping of custom fields."""
    # Setup mock data
    mock_cf1 = CustomFieldProjectWithValuesDto(
        custom_field=CustomFieldProjectDto(custom_field=CustomFieldDto(name="Layer"), required=True),
        values=[CustomFieldValueDto(name="UI"), CustomFieldValueDto(name="API")],
    )
    mock_cf2 = CustomFieldProjectWithValuesDto(
        custom_field=CustomFieldProjectDto(custom_field=CustomFieldDto(name="Component"), required=False),
        values=[CustomFieldValueDto(name="Auth")],
    )

    # Mock the client method (which doesn't exist yet, so this will fail if we run it before implementing)
    # But we mock it here assuming it will exist
    mock_client.get_custom_fields_with_values = AsyncMock(return_value=[mock_cf1, mock_cf2])

    # Call service method (doesn't exist yet)
    result = await service.get_custom_fields()

    assert len(result) == 2

    # Validate normalization
    assert result[0]["name"] == "Layer"
    assert result[0]["required"] is True
    assert result[0]["values"] == ["UI", "API"]

    assert result[1]["name"] == "Component"
    assert result[1]["required"] is False
    assert result[1]["values"] == ["Auth"]

    mock_client.get_custom_fields_with_values.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_custom_fields_filtering(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test filtering custom fields by name."""
    mock_cf1 = CustomFieldProjectWithValuesDto(
        custom_field=CustomFieldProjectDto(custom_field=CustomFieldDto(name="Layer")), values=[]
    )
    mock_cf2 = CustomFieldProjectWithValuesDto(
        custom_field=CustomFieldProjectDto(custom_field=CustomFieldDto(name="Component")), values=[]
    )

    mock_client.get_custom_fields_with_values = AsyncMock(return_value=[mock_cf1, mock_cf2])

    # Filter for 'layer' (case insensitive)
    result = await service.get_custom_fields(name="layer")

    assert len(result) == 1
    assert result[0]["name"] == "Layer"


@pytest.mark.asyncio
async def test_get_custom_fields_empty(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test empty response handling."""
    mock_client.get_custom_fields_with_values = AsyncMock(return_value=[])

    result = await service.get_custom_fields()
    assert result == []
