"""Unit tests for CustomFieldValueService."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.client.generated.models.custom_field_value_with_cf_dto import CustomFieldValueWithCfDto
from src.client.generated.models.custom_field_value_with_tc_count_dto import CustomFieldValueWithTcCountDto
from src.client.generated.models.page_custom_field_value_with_tc_count_dto import PageCustomFieldValueWithTcCountDto
from src.services.custom_field_value_service import CustomFieldValueService


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock(spec=AllureClient)
    client.get_project.return_value = 1
    client.list_custom_field_values = AsyncMock()
    client.create_custom_field_value = AsyncMock()
    client.update_custom_field_value = AsyncMock()
    client.delete_custom_field_value = AsyncMock()
    return client


@pytest.fixture
def service(mock_client: MagicMock) -> CustomFieldValueService:
    return CustomFieldValueService(client=mock_client)


@pytest.mark.asyncio
async def test_list_custom_field_values_success(service: CustomFieldValueService, mock_client: MagicMock) -> None:
    page = PageCustomFieldValueWithTcCountDto(
        content=[CustomFieldValueWithTcCountDto(id=1, name="Smoke", test_cases_count=3)],
        total_elements=1,
        number=0,
        total_pages=1,
    )
    mock_client.list_custom_field_values.return_value = page
    service._get_resolved_custom_fields = AsyncMock(
        return_value={
            "Priority": {
                "project_cf_id": 10,
                "id": 5,
                "required": False,
                "single_select": True,
                "values": [],
                "values_map": {},
            },
        }
    )

    result = await service.list_custom_field_values(
        custom_field_name="Priority",
        query="Smoke",
        var_global=True,
        test_case_search="smoke",
        page=1,
        size=5,
        sort=["name,asc"],
    )

    assert result.total_elements == 1
    mock_client.list_custom_field_values.assert_called_once_with(
        project_id=1,
        custom_field_id=10,
        query="Smoke",
        var_global=True,
        test_case_search="smoke",
        page=1,
        size=5,
        sort=["name,asc"],
    )


@pytest.mark.asyncio
async def test_list_custom_field_values_invalid_name(service: CustomFieldValueService) -> None:
    service._get_resolved_custom_fields = AsyncMock(
        return_value={
            "Priority": {
                "project_cf_id": 10,
                "id": 5,
                "required": False,
                "single_select": True,
                "values": [],
                "values_map": {},
            },
        }
    )

    with pytest.raises(AllureValidationError, match="Custom field 'Missing' not found"):
        await service.list_custom_field_values(custom_field_name="Missing")


@pytest.mark.asyncio
async def test_list_custom_field_values_invalid_custom_field_id(service: CustomFieldValueService) -> None:
    with pytest.raises(AllureValidationError, match="Custom Field ID must be a non-zero integer"):
        await service.list_custom_field_values(custom_field_id=0)


@pytest.mark.asyncio
async def test_list_custom_field_values_accepts_negative_custom_field_id(
    service: CustomFieldValueService, mock_client: MagicMock
) -> None:
    page = PageCustomFieldValueWithTcCountDto(content=[], total_elements=0)
    mock_client.list_custom_field_values.return_value = page

    result = await service.list_custom_field_values(custom_field_id=-5)

    assert result.total_elements == 0
    mock_client.list_custom_field_values.assert_called_once_with(
        project_id=1,
        custom_field_id=-5,
        query=None,
        var_global=None,
        test_case_search=None,
        page=None,
        size=None,
        sort=None,
    )


@pytest.mark.asyncio
async def test_create_custom_field_value_success(service: CustomFieldValueService, mock_client: MagicMock) -> None:
    created = CustomFieldValueWithCfDto(id=99, name="Regression")
    mock_client.create_custom_field_value.return_value = created
    service._get_resolved_custom_fields = AsyncMock(
        return_value={
            "Priority": {
                "project_cf_id": 10,
                "id": 5,
                "required": False,
                "single_select": True,
                "values": [],
                "values_map": {},
            },
        }
    )

    result = await service.create_custom_field_value(custom_field_name="Priority", name="Regression")

    assert result.id == 99
    mock_client.create_custom_field_value.assert_called_once()


@pytest.mark.asyncio
async def test_create_custom_field_value_duplicate_name(
    service: CustomFieldValueService, mock_client: MagicMock
) -> None:
    service._get_resolved_custom_fields = AsyncMock(
        return_value={
            "Priority": {
                "project_cf_id": 10,
                "id": 5,
                "required": False,
                "single_select": True,
                "values": [],
                "values_map": {},
            },
        }
    )
    mock_client.create_custom_field_value.side_effect = AllureValidationError("Validation error", status_code=409)

    with pytest.raises(AllureValidationError, match="already exists"):
        await service.create_custom_field_value(custom_field_name="Priority", name="Regression")


@pytest.mark.asyncio
async def test_update_custom_field_value_success(service: CustomFieldValueService, mock_client: MagicMock) -> None:
    service._get_resolved_custom_fields = AsyncMock(
        return_value={
            "Priority": {
                "project_cf_id": 10,
                "id": 5,
                "required": False,
                "single_select": True,
                "values": [],
                "values_map": {},
            },
        }
    )

    await service.update_custom_field_value(custom_field_name="Priority", cfv_id=77, name="Updated")

    mock_client.update_custom_field_value.assert_called_once()


@pytest.mark.asyncio
async def test_delete_custom_field_value_idempotent(service: CustomFieldValueService, mock_client: MagicMock) -> None:
    service._get_resolved_custom_fields = AsyncMock(
        return_value={
            "Priority": {
                "project_cf_id": 10,
                "id": 5,
                "required": False,
                "single_select": True,
                "values": [],
                "values_map": {},
            },
        }
    )
    mock_client.delete_custom_field_value.side_effect = AllureNotFoundError("Not found", 404, "{}")

    deleted = await service.delete_custom_field_value(custom_field_name="Priority", cfv_id=77)

    assert deleted is False
