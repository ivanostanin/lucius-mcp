from unittest.mock import AsyncMock, Mock

import pytest

from src.client import AllureClient
from src.client.generated.models import (
    CustomFieldDto,
    CustomFieldProjectDto,
    CustomFieldProjectWithValuesDto,
    CustomFieldValueDto,
    TestCaseDto,
)
from src.services.test_case_service import TestCaseService, TestCaseUpdate


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock(spec=AllureClient)
    client.api_client = Mock()
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


@pytest.mark.asyncio
async def test_get_test_case_custom_fields_values(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test fetching custom field values for a specific test case."""
    test_case_id = 123
    mock_client.get_test_case_custom_fields.return_value = [
        CustomFieldProjectWithValuesDto(
            custom_field=CustomFieldProjectDto(custom_field=CustomFieldDto(id=1, name="Layer")),
            values=[CustomFieldValueDto(name="UI")],
        ),
        CustomFieldProjectWithValuesDto(
            custom_field=CustomFieldProjectDto(custom_field=CustomFieldDto(id=2, name="Component")),
            values=[],  # Empty values
        ),
    ]

    # We need to expose a method for this or use correct service method if it exists
    # Based on plan, we are adding get_test_case_custom_fields_values
    result = await service.get_test_case_custom_fields_values(test_case_id)

    assert len(result) == 2
    assert result["Layer"] == "UI"
    assert result["Component"] == []

    mock_client.get_test_case_custom_fields.assert_called_once_with(test_case_id, 1)


@pytest.mark.asyncio
async def test_update_test_case_custom_fields_only(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test updating only custom fields uses dedicated endpoint."""
    test_case_id = 123
    custom_fields = {"Layer": "API"}

    # Mock get_test_case
    mock_case = TestCaseDto(id=test_case_id, project_id=1, name="Test")
    mock_client.get_test_case.return_value = mock_case

    # Mock custom field resolution
    service._cf_cache[1] = {
        "Layer": {"id": 10, "required": False, "values": ["UI", "API"], "values_map": {"UI": 101, "API": 102}}
    }

    data = TestCaseUpdate(custom_fields=custom_fields)

    await service.update_test_case(test_case_id, data)

    # Verify dedicated endpoint was called
    mock_client.update_cfvs_of_test_case.assert_called_once()
    call_args = mock_client.update_cfvs_of_test_case.call_args
    passed_dtos = call_args[0][1]
    assert len(passed_dtos) == 1
    assert passed_dtos[0].custom_field.id == 10
    assert len(passed_dtos[0].values) == 1
    assert passed_dtos[0].values[0].id == 102


@pytest.mark.asyncio
async def test_update_test_case_mixed_fields(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test updating both regular and custom fields."""
    test_case_id = 123
    custom_fields = {"Layer": "API"}
    update_data = TestCaseUpdate(name="New Name", custom_fields=custom_fields)

    # Mock get_test_case
    mock_client.get_test_case.return_value = TestCaseDto(id=test_case_id, project_id=1, name="Old Name")
    mock_client.update_test_case.return_value = TestCaseDto(id=test_case_id, name="New Name")

    # Mock resolution
    service._cf_cache[1] = {
        "Layer": {"id": 10, "required": False, "values": ["UI", "API"], "values_map": {"UI": 101, "API": 102}}
    }

    await service.update_test_case(test_case_id, update_data)

    # Both endpoints should be called
    mock_client.update_test_case.assert_called_once()  # For name
    mock_client.update_cfvs_of_test_case.assert_called_once()  # For custom fields


@pytest.mark.asyncio
async def test_update_test_case_clear_custom_field(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test clearing a custom field  (sending "[]" as value)."""
    test_case_id = 123
    custom_fields = {"Layer": "[]"}  # Special value to clear

    service._cf_cache[1] = {
        "Layer": {"id": 10, "required": False, "values": ["UI", "API"], "values_map": {"UI": 101, "API": 102}}
    }

    mock_client.get_test_case.return_value = TestCaseDto(id=test_case_id, project_id=1)

    data = TestCaseUpdate(custom_fields=custom_fields)

    await service.update_test_case(test_case_id, data)

    # Dedicated endpoint should be called with empty values
    mock_client.update_cfvs_of_test_case.assert_called_once()
    passed_dtos = mock_client.update_cfvs_of_test_case.call_args[0][1]
    assert len(passed_dtos) == 1
    assert passed_dtos[0].custom_field.id == 10
    assert len(passed_dtos[0].values) == 0  # Empty list for clearing
