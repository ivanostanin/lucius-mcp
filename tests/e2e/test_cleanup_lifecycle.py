"""E2E checks for cleanup tools."""

import re

import pytest

from src.client.exceptions import AllureNotFoundError
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

    output = await delete_archived_test_cases(confirm=True, project_id=project_id)
    assert _extract_count(output) >= 1

    with pytest.raises(AllureNotFoundError):
        await allure_client.get_test_case(created.id)


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

    output = await delete_archived_shared_steps(confirm=True, project_id=project_id)
    assert _extract_count(output) >= 1

    with pytest.raises(AllureNotFoundError):
        await allure_client.get_shared_step(shared_step.id)


@pytest.mark.asyncio
async def test_delete_unused_custom_fields_requires_confirm() -> None:
    output = await delete_unused_custom_fields(confirm=False)
    assert output == DESTRUCTIVE_CONFIRMATION_MESSAGE
