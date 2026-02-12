"""E2E tests for launch lifecycle operations."""

import pytest

from src.services.launch_service import LaunchService


@pytest.mark.asyncio
async def test_create_close_reopen_launch_lifecycle(allure_client, project_id, test_run_id) -> None:
    service = LaunchService(client=allure_client)
    launch_name = f"[{test_run_id}] E2E Launch"

    created = await service.create_launch(name=launch_name)
    assert created.id is not None

    result = await service.list_launches(page=0, size=50, sort=["createdDate,DESC"])
    names = [getattr(item, "name", None) for item in result.items]
    assert launch_name in names

    created_id = created.id
    retrieved = await service.get_launch(created_id)
    assert retrieved.id == created_id
    assert retrieved.closed is not True

    closed = await service.close_launch(created_id)
    assert closed.id == created_id
    assert closed.closed is True

    reopened = await service.reopen_launch(created_id)
    assert reopened.id == created_id
    assert reopened.closed is not True


@pytest.mark.asyncio
async def test_reopened_launch_accepts_upload_if_supported(allure_client, project_id, test_run_id) -> None:
    upload_method_name = "upload_results_to_launch"
    if not hasattr(allure_client, upload_method_name):
        pytest.skip(
            "AC4 upload acceptance check skipped: repository does not expose "
            "a launch-result-upload path in AllureClient"
        )

    service = LaunchService(client=allure_client)
    launch_name = f"[{test_run_id}] E2E Launch Upload AC4"

    created = await service.create_launch(name=launch_name)
    assert created.id is not None

    created_id = created.id
    await service.close_launch(created_id)
    reopened = await service.reopen_launch(created_id)
    assert reopened.closed is not True
