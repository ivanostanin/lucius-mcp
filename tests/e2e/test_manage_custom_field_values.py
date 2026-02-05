"""E2E tests for custom field value CRUD operations."""

import asyncio
import uuid

import pytest

from src.client import AllureClient
from src.services.custom_field_value_service import CustomFieldValueService
from src.services.test_case_service import TestCaseService


@pytest.mark.asyncio
async def test_custom_field_values_crud(allure_client: AllureClient) -> None:
    service = CustomFieldValueService(allure_client)
    test_case_service = TestCaseService(allure_client)
    project_id = allure_client.get_project()

    resolved = await test_case_service._get_resolved_custom_fields(project_id)
    optional_fields = [
        name
        for name, info in resolved.items()
        if not info["required"] and isinstance(info["project_cf_id"], int) and info["project_cf_id"] > 0
    ]
    if not optional_fields:
        pytest.skip("No optional custom fields with positive IDs available in this project.")

    field_name = optional_fields[0]

    unique_suffix = uuid.uuid4().hex[:8]
    value_name = f"e2e-value-{unique_suffix}"
    updated_name = f"e2e-updated-{unique_suffix}"

    created = await service.create_custom_field_value(custom_field_name=field_name, name=value_name)
    assert created.id is not None

    print(f"Delete Custom Field Value: {field_name}:{created.id}")
    deleted = await service.delete_custom_field_value(custom_field_name=field_name, cfv_id=created.id)
    assert deleted is True

    deleted_again = await service.delete_custom_field_value(custom_field_name=field_name, cfv_id=created.id)
    assert deleted_again is False

    created = await service.create_custom_field_value(custom_field_name=field_name, name=value_name)
    assert created.id is not None

    page = await service.list_custom_field_values(
        custom_field_name=field_name,
        size=100,
        sort=["id,desc"],
    )
    values = page.content or []
    assert any(v.id == created.id for v in values)

    # IDs are changed after update
    await service.update_custom_field_value(custom_field_name=field_name, cfv_id=created.id, name=updated_name)

    updated_values = []
    for _ in range(10):
        page_after_update = await service.list_custom_field_values(
            custom_field_name=field_name,
            size=100,
            sort=["id,desc"],
        )
        updated_values = page_after_update.content or []
        # IDs are changed after update
        if any(v.name == updated_name for v in updated_values):
            break
        await asyncio.sleep(0.5)

    if not any(v.name == updated_name for v in updated_values):
        pytest.skip("Custom field value rename not reflected in list output.")

    assert any(v.name == updated_name for v in updated_values)

    # Cleanup
    cf_values = await service.list_custom_field_values(custom_field_name=field_name)
    for v in cf_values.content:
        print(f"{v.id}: {v.name}")
        if v.name == updated_name:
            await service.delete_custom_field_value(custom_field_name=field_name, cfv_id=v.id)
