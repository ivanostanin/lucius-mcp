"""E2E checks for cleanup tools."""

import asyncio
import re

import pytest

from src.client.exceptions import AllureNotFoundError, TestCaseNotFoundError
from src.services.custom_field_value_service import CustomFieldValueService
from src.services.shared_step_service import SharedStepService
from src.services.test_case_service import TestCaseService
from src.tools.cleanup import (
    DESTRUCTIVE_CONFIRMATION_MESSAGE,
    delete_archived_shared_steps,
    delete_archived_test_cases,
    delete_unused_custom_fields,
)
from tests.e2e.helpers.cleanup import CleanupTracker


def _extract_count(output: str) -> int:
    match = re.search(r"Deleted (\d+)", output)
    assert match, f"Unexpected output format: {output}"
    return int(match.group(1))


async def _project_has_custom_field_id(
    allure_client,
    project_id: int,
    custom_field_id: int,
    page_size: int = 100,
) -> bool:
    page = 0
    while True:
        fields = await allure_client.list_project_custom_fields(
            project_id=project_id,
            page=page,
            size=page_size,
        )
        if not fields:
            return False

        for field in fields:
            custom_field = getattr(field, "custom_field", None)
            if getattr(custom_field, "id", None) == custom_field_id:
                return True

        if len(fields) < page_size:
            return False
        page += 1


async def _is_deleted_test_case_listed(
    allure_client,
    project_id: int,
    test_case_id: int,
    page_size: int = 100,
) -> bool:
    page = 0
    while True:
        result_page = await allure_client.list_deleted_test_cases(
            project_id=project_id,
            page=page,
            size=page_size,
        )
        rows = result_page.content or []
        if not rows:
            return False

        for row in rows:
            if row.id == test_case_id:
                return True

        if len(rows) < page_size:
            return False
        page += 1


async def _wait_until_deleted_case_listed(
    allure_client,
    project_id: int,
    test_case_id: int,
    attempts: int = 10,
    delay_seconds: float = 0.5,
) -> bool:
    for _ in range(attempts):
        if await _is_deleted_test_case_listed(allure_client, project_id, test_case_id):
            return True
        await asyncio.sleep(delay_seconds)
    return False


@pytest.mark.asyncio
async def test_cleanup_archived_test_cases_e2e(
    allure_client,
    project_id: int,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
) -> None:
    service = TestCaseService(client=allure_client)

    created = await service.create_test_case(name=f"[{test_run_id}] cleanup-archived-case")
    assert created.id is not None
    cleanup_tracker.track_test_case(created.id)

    archived = await service.delete_test_case(created.id)
    assert archived.status in {"archived", "already_deleted"}
    assert await _wait_until_deleted_case_listed(allure_client, project_id, created.id)

    output = await delete_archived_test_cases(confirm=True, project_id=project_id, output_format="plain")
    assert _extract_count(output) >= 1

    for _ in range(10):
        try:
            await allure_client.get_test_case(created.id)
        except (AllureNotFoundError, TestCaseNotFoundError):
            break
        await asyncio.sleep(0.5)
    else:
        pytest.fail(f"Test case {created.id} was not permanently deleted after cleanup.")


@pytest.mark.asyncio
async def test_cleanup_archived_shared_steps_e2e(
    allure_client,
    project_id: int,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
) -> None:
    service = SharedStepService(client=allure_client)

    shared_step = await service.create_shared_step(name=f"[{test_run_id}] cleanup-archived-step")
    assert shared_step.id is not None
    cleanup_tracker.track_shared_step(shared_step.id)

    archived = await service.delete_shared_step(shared_step.id)
    assert archived is True

    output = await delete_archived_shared_steps(confirm=True, project_id=project_id, output_format="plain")
    assert _extract_count(output) >= 1

    with pytest.raises(AllureNotFoundError):
        await allure_client.get_shared_step(shared_step.id)


@pytest.mark.asyncio
async def test_delete_unused_custom_fields_requires_confirm() -> None:
    output = await delete_unused_custom_fields(confirm=False, output_format="plain")
    assert output == DESTRUCTIVE_CONFIRMATION_MESSAGE


@pytest.mark.asyncio
async def test_delete_unused_custom_fields_preserves_used_field(
    allure_client,
    project_id: int,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
) -> None:
    service = TestCaseService(client=allure_client)
    cf_value_service = CustomFieldValueService(client=allure_client)

    project_fields = await allure_client.get_custom_fields_with_values(project_id)
    target_field_name: str | None = None
    target_field_id: int | None = None
    for field in project_fields:
        custom_field = getattr(field, "custom_field", None)
        if custom_field is None:
            continue
        if not isinstance(custom_field.id, int) or custom_field.id <= 0:
            continue
        if not isinstance(custom_field.name, str) or not custom_field.name:
            continue
        if custom_field.single_select is not True:
            continue
        target_field_name = custom_field.name
        target_field_id = custom_field.id
        break

    if target_field_name is None or target_field_id is None:
        pytest.skip("No suitable single-select custom field found in project")

    field_value_name = f"cleanup-preserve-{test_run_id}"
    try:
        await cf_value_service.create_custom_field_value(custom_field_name=target_field_name, name=field_value_name)
    except Exception as exc:
        pytest.skip(f"Unable to create temporary custom field value for '{target_field_name}': {exc}")

    cleanup_tracker.track_custom_field_value_name(field_value_name)

    created = await service.create_test_case(
        name=f"[{test_run_id}] cleanup-used-custom-field",
        custom_fields={target_field_name: field_value_name},
    )
    assert created.id is not None
    cleanup_tracker.track_test_case(created.id)

    output = await delete_unused_custom_fields(confirm=True, project_id=project_id, output_format="plain")
    assert _extract_count(output) >= 0

    assert await _project_has_custom_field_id(allure_client, project_id, target_field_id)
