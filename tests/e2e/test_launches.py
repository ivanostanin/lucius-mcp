"""E2E tests for launch create and list."""

import pytest

from src.services.launch_service import LaunchService


@pytest.mark.asyncio
async def test_create_and_list_launches(allure_client, project_id, test_run_id) -> None:
    service = LaunchService(client=allure_client)
    launch_name = f"[{test_run_id}] E2E Launch"

    created = await service.create_launch(name=launch_name)
    assert created.id is not None

    result = await service.list_launches(page=0, size=50, sort=["createdDate,DESC"])
    names = [getattr(item, "name", None) for item in result.items]
    assert launch_name in names
