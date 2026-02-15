"""E2E tests for launch lifecycle operations."""

import json
import time
import uuid

import pytest

from src.client.generated.models.launch_upload_response_dto import LaunchUploadResponseDto
from src.services.launch_service import LaunchService


@pytest.mark.asyncio
async def test_create_close_reopen_launch_lifecycle(allure_client, project_id, test_run_id, cleanup_tracker) -> None:
    service = LaunchService(client=allure_client)
    launch_name = f"[{test_run_id}] E2E Launch"
    created_id: int | None = None

    try:
        created = await service.create_launch(name=launch_name)
        assert created.id is not None
        cleanup_tracker.track_launch(created.id)

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

        result = await service.list_launches(page=0, size=50, sort=["createdDate,DESC"])
        names = [getattr(item, "name", None) for item in result.items]
        assert launch_name in names

        deleted = await service.delete_launch(created.id)
        assert deleted.launch_id == created.id
        assert deleted.status == "archived"

        deleted_again = await service.delete_launch(created.id)
        assert deleted_again.launch_id == created.id
        assert deleted_again.status == "already_deleted"
    finally:
        if created_id is not None:
            await cleanup_tracker.delete_launch_strict(created_id)


# todo: revise this once launch_upload_controller is in
@pytest.mark.asyncio
async def test_reopened_launch_accepts_upload_if_supported(
    allure_client, project_id, test_run_id, cleanup_tracker
) -> None:
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
    cleanup_tracker.track_launch(created.id)

    created_id = created.id
    await service.close_launch(created_id)
    reopened = await service.reopen_launch(created_id)
    assert reopened.closed is not True

    now_ms = int(time.time() * 1000)
    result_uuid = str(uuid.uuid4())
    container_uuid = str(uuid.uuid4())
    allure_result_payload = {
        "uuid": result_uuid,
        "historyId": result_uuid,
        "name": "upload-after-reopen",
        "fullName": "ac4.upload-after-reopen",
        "status": "passed",
        "stage": "finished",
        "start": now_ms,
        "stop": now_ms + 10,
        "labels": [
            {"name": "host", "value": "e2e-runner"},
            {"name": "thread", "value": test_run_id},
            {"name": "language", "value": "python"},
            {"name": "suite", "value": "ac4-suite"},
            {"name": "framework", "value": "pytest"},
        ],
    }
    allure_container_payload = {
        "uuid": container_uuid,
        "children": [result_uuid],
        "start": now_ms,
        "stop": now_ms + 10,
    }

    result_file_name = f"{result_uuid}-result.json"
    result_file_bytes = json.dumps(allure_result_payload).encode("utf-8")
    container_file_name = f"{container_uuid}-container.json"
    container_file_bytes = json.dumps(allure_container_payload).encode("utf-8")

    upload_result = await service.upload_results_to_launch(
        launch_id=created_id,
        files=[
            (result_file_name, result_file_bytes),
            (container_file_name, container_file_bytes),
        ],
    )

    assert isinstance(upload_result, LaunchUploadResponseDto)
    assert upload_result.launch_id == created_id
    assert upload_result.files_count is None or upload_result.files_count >= 1
