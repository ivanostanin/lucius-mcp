from unittest.mock import AsyncMock

import pytest

from src.client import AllureClient
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
async def test_get_custom_fields_returns_mapped_data(service: TestCaseService) -> None:
    """Test standard retrieval and mapping of custom fields."""
    # Pre-populate the cache with test data
    service._cf_cache[1] = {
        "Layer": {"id": 1, "required": True, "values": ["UI", "API"]},
        "Component": {"id": 2, "required": False, "values": ["Auth"]},
    }

    # Call service method
    result = await service.get_custom_fields()

    assert len(result) == 2

    # Validate normalization (order may vary since dict iteration)
    layer_field = next((f for f in result if f["name"] == "Layer"), None)
    component_field = next((f for f in result if f["name"] == "Component"), None)

    assert layer_field is not None
    assert layer_field["required"] is True
    assert layer_field["values"] == ["UI", "API"]

    assert component_field is not None
    assert component_field["required"] is False
    assert component_field["values"] == ["Auth"]


@pytest.mark.asyncio
async def test_get_custom_fields_filtering(service: TestCaseService) -> None:
    """Test filtering custom fields by name."""
    # Pre-populate cache
    service._cf_cache[1] = {
        "Layer": {"id": 1, "required": False, "values": []},
        "Component": {"id": 2, "required": False, "values": []},
    }

    # Filter for 'layer' (case insensitive)
    result = await service.get_custom_fields(name="layer")

    assert len(result) == 1
    assert result[0]["name"] == "Layer"


@pytest.mark.asyncio
async def test_get_custom_fields_empty(service: TestCaseService) -> None:
    """Test empty response handling."""
    # Pre-populate with empty cache
    service._cf_cache[1] = {}

    result = await service.get_custom_fields()
    assert result == []
