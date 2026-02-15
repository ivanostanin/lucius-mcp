"""E2E tests for launch lifecycle operations."""

import asyncio
from pathlib import Path

import pytest

from src.client.exceptions import LaunchNotFoundError
from src.client.generated.models.launch_upload_response_dto import LaunchUploadResponseDto
from src.services.launch_service import LaunchService
from src.utils.error import AllureAPIError


async def _launch_exists(service: LaunchService, launch_id: int) -> bool:
    try:
        await service.get_launch(launch_id)
        return True
    except LaunchNotFoundError:
        return False


async def _delete_launch_strict(service: LaunchService, launch_id: int) -> None:
    """Delete launch and verify it no longer exists (with short retries)."""
    for _ in range(3):
        await service.delete_launch(launch_id)
        if not await _launch_exists(service, launch_id):
            return
        await asyncio.sleep(0.2)

    raise AssertionError(f"Launch {launch_id} still exists after deletion attempts")


@pytest.mark.asyncio
async def test_create_close_reopen_launch_lifecycle(allure_client, project_id, test_run_id) -> None:
    service = LaunchService(client=allure_client)
    launch_name = f"[{test_run_id}] E2E Launch"
    cleanup_launch_id: int | None = None

    try:
        created = await service.create_launch(name=launch_name)
        assert created.id is not None
        cleanup_launch_id = created.id

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

        cleanup_launch_id = None
    finally:
        if cleanup_launch_id is not None:
            await _delete_launch_strict(service, cleanup_launch_id)


# todo: revise this once launch_upload_controller is in
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
    try:
        await service.close_launch(created_id)
        reopened = await service.reopen_launch(created_id)
        assert reopened.closed is not True

        sample_file = Path(__file__).with_name(f"{test_run_id}-launch-upload.xml")
        sample_file.write_text(
            """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<testsuite name=\"ac4-suite\" tests=\"1\" failures=\"0\" skipped=\"0\" time=\"0.01\">
  <testcase classname=\"ac4\" name=\"upload-after-reopen\" time=\"0.01\" />
</testsuite>
""",
            encoding="utf-8",
        )

        try:
            try:
                upload_result = await service.upload_results_to_launch(launch_id=created_id, files=[str(sample_file)])
            except AllureAPIError as exc:
                if exc.status_code is not None and exc.status_code >= 500:
                    pytest.skip(f"AC4 upload check skipped due to environment/server upload error: {exc}")
                raise
        finally:
            sample_file.unlink(missing_ok=True)
    finally:
        await _delete_launch_strict(service, created_id)

    assert isinstance(upload_result, LaunchUploadResponseDto)
    assert upload_result.launch_id == created_id
    assert upload_result.files_count is None or upload_result.files_count >= 1
