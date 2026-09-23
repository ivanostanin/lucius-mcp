"""E2E coverage for manual execution workflows inside launches."""

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError
from src.client.generated.models.test_result_create_v2_dto import TestResultCreateV2Dto
from src.services.launch_service import LaunchService
from src.services.test_case_service import TestCaseService
from tests.e2e.helpers.cleanup import CleanupTracker

pytestmark = pytest.mark.asyncio(loop_scope="module")


async def test_manual_launch_submission_creates_new_result(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
) -> None:
    """Verify explicit launch/test-case submission creates a new manual result."""
    launch_service = LaunchService(allure_client)

    launch, test_case = await _create_launch_with_test_case(
        allure_client,
        cleanup_tracker,
        test_run_id,
        suffix="new-result",
        steps=[{"action": "Open app", "expected": "App opens"}],
    )

    session = await launch_service.start_manual_test_session(launch.id)
    assert session.test_session_id > 0

    submission = await launch_service.submit_manual_test_results(
        session.test_session_id,
        results=[
            {
                "launch_id": launch.id,
                "test_case_id": test_case.id,
                "name": f"[{test_run_id}] New Manual Result",
                "full_name": f"[{test_run_id}] New Manual Result",
                "status": "failed",
                "message": "Created as a brand-new manual result",
            }
        ],
    )
    assert submission.result_ids

    created_result_id = submission.result_ids[0]
    created_result = await allure_client.get_test_result(created_result_id)
    assert created_result.id == created_result_id
    assert created_result.launch_id == launch.id
    assert created_result.test_case_id == test_case.id
    assert created_result.manual is True
    assert created_result.external is False
    assert created_result.hidden is not True
    assert created_result.status is not None
    assert created_result.status.value.lower() == "failed"

    launch_results = await launch_service.list_launch_test_results(launch.id, manual_only=True)
    matching_result_ids = {item.result_id for item in launch_results.items if item.test_case_id == test_case.id}
    assert created_result_id in matching_result_ids


async def test_upload_results_to_launch_creates_results_in_one_bulk_submission(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
) -> None:
    """Verify the launch-scoped upload tool creates multiple external results."""
    launch_service = LaunchService(allure_client)
    launch, test_case = await _create_launch_with_test_case(
        allure_client,
        cleanup_tracker,
        test_run_id,
        suffix="bulk-upload",
        steps=[{"action": "Open app", "expected": "App opens"}],
    )

    upload = await launch_service.add_results(
        launch.id,
        results=[
            {
                "test_case_id": test_case.id,
                "status": "passed",
                "message": "Uploaded by launch-scoped API",
            },
            {
                "test_case_id": test_case.id,
                "status": "failed",
                "duration": 100,
                "message": "Second externally reported result",
            },
        ],
    )

    assert upload.launch_id == launch.id
    assert upload.uploaded_count == 2
    assert len(upload.result_ids) == 2
    for result_id in upload.result_ids:
        created_result = await allure_client.get_test_result(result_id)
        assert created_result.launch_id == launch.id
        assert created_result.test_case_id == test_case.id

    refreshed_launch = await launch_service.get_launch(launch.id)
    assert refreshed_launch.id == launch.id
    closed_launch = await launch_service.close_launch(launch.id)
    assert closed_launch.closed is True


async def test_manual_rerun_of_automated_result_resolves_existing_test_run(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
) -> None:
    """Verify a manual rerun of an automated result resolves the active rerun placeholder in place."""
    launch_service = LaunchService(allure_client)

    launch, test_case = await _create_launch_with_test_case(
        allure_client,
        cleanup_tracker,
        test_run_id,
        suffix="automated-rerun",
        steps=[
            {"action": "Retry app", "expected": "App opens after rerun"},
            {"action": "Confirm state", "expected": "State is restored"},
        ],
    )

    automated_result = await allure_client.create_test_result(
        TestResultCreateV2Dto(
            launch_id=launch.id,
            test_case_id=test_case.id,
            name=f"[{test_run_id}] Automated Failure",
            full_name=f"[{test_run_id}] Automated Failure",
            status="failed",
            manual=False,
            external=False,
            start=1000,
            stop=2000,
            message="Initial automated failure",
        )
    )
    assert automated_result.id is not None

    rerun = await launch_service.rerun_test_results_manually(
        launch.id,
        result_ids=[automated_result.id],
    )
    assert rerun.result_ids == [automated_result.id]
    assert rerun.scheduled_count == 1

    active_rerun_result = await launch_service.resolve_launch_test_result_for_test_case(
        launch.id,
        test_case_id=test_case.id,
        status=None,
    )
    assert active_rerun_result.result_id is not None
    assert active_rerun_result.result_id != automated_result.id

    rerun_session = await launch_service.start_manual_test_session(launch.id)
    assert rerun_session.test_session_id > 0

    step_attachment = await launch_service.add_test_result_attachment(
        active_rerun_result.result_id,
        attachment={
            "name": "active-manual-step.png",
            "content_type": "image/png",
            "content": (
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScL6xQAAAABJRU5ErkJggg=="
            ),
        },
    )
    assert step_attachment.attachment_ids
    second_step_attachment = await launch_service.add_test_result_attachment(
        active_rerun_result.result_id,
        attachment={
            "name": "active-manual-step-02.png",
            "content_type": "image/png",
            "content": (
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScL6xQAAAABJRU5ErkJggg=="
            ),
        },
    )
    assert second_step_attachment.attachment_ids

    submission = await launch_service.submit_manual_test_results(
        rerun_session.test_session_id,
        results=[
            {
                "result_id": active_rerun_result.result_id,
                "status": "passed",
                "steps": [
                    {
                        "type": "body",
                        "body": "Retry app",
                        "status": "passed",
                        "steps": [
                            {
                                "type": "expected",
                                "body": "App opens after rerun",
                                "status": "passed",
                            },
                            {
                                "type": "attachment",
                                "status": "passed",
                                "attachment_id": step_attachment.attachment_ids[0],
                            },
                        ],
                    },
                    {
                        "type": "body",
                        "body": "Confirm state",
                        "status": "passed",
                        "steps": [
                            {
                                "type": "expected",
                                "body": "State is restored",
                                "status": "passed",
                            },
                            {
                                "type": "attachment",
                                "status": "passed",
                                "attachment_id": second_step_attachment.attachment_ids[0],
                            },
                        ],
                    },
                ],
            }
        ],
    )
    assert submission.result_ids == [active_rerun_result.result_id]

    execution_after_attachment = await allure_client.get_test_result_execution_raw(
        active_rerun_result.result_id,
        v2=True,
    )
    first_attachment_step = execution_after_attachment["steps"][0]["expectedResultSteps"][-1]
    second_attachment_step = execution_after_attachment["steps"][1]["expectedResultSteps"][-1]
    assert first_attachment_step["type"] == second_attachment_step["type"] == "attachment"
    assert first_attachment_step["attachmentId"] == step_attachment.attachment_ids[0]
    assert second_attachment_step["attachmentId"] == second_step_attachment.attachment_ids[0]

    rerun_result = await allure_client.get_test_result(active_rerun_result.result_id)
    assert rerun_result.manual is True
    assert rerun_result.hidden is not True
    assert rerun_result.status is not None
    assert rerun_result.status.value.lower() == "passed"
    visible_passed_result = await launch_service.resolve_launch_test_result_for_test_case(
        launch.id,
        test_case_id=test_case.id,
        status="passed",
    )
    assert visible_passed_result.result_id == active_rerun_result.result_id
    with pytest.raises(AllureNotFoundError, match="No visible manual launch result found"):
        await launch_service.resolve_launch_test_result_for_test_case(
            launch.id,
            test_case_id=test_case.id,
            status=None,
        )


async def test_manual_launch_submission_creates_complete_new_result(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
) -> None:
    """Verify explicit launch/test-case submission can create a complete new result with attachments."""
    launch_service = LaunchService(allure_client)

    launch, test_case = await _create_launch_with_test_case(
        allure_client,
        cleanup_tracker,
        test_run_id,
        suffix="complete-new-result",
        steps=[{"action": "Open app", "expected": "App opens"}],
    )

    session = await launch_service.start_manual_test_session(launch.id)
    assert session.test_session_id > 0

    submission = await launch_service.submit_manual_test_results(
        session.test_session_id,
        results=[
            {
                "launch_id": launch.id,
                "test_case_id": test_case.id,
                "name": f"[{test_run_id}] Complete Manual Result",
                "full_name": f"[{test_run_id}] Complete Manual Result",
                "status": "unknown",
                "start": 1000,
                "stop": 2000,
                "message": "Standalone manual completion",
                "steps": [
                    {
                        "type": "body",
                        "body": "Open app",
                        "status": "unknown",
                        "message": "Completed successfully",
                    }
                ],
            }
        ],
    )
    assert submission.result_ids

    created_result_id = submission.result_ids[0]
    created_result = await allure_client.get_test_result(created_result_id)
    assert created_result.manual is True
    assert created_result.hidden is not True
    assert created_result.status is not None
    assert created_result.status.value.lower() == "unknown"

    result_attachment = await launch_service.add_test_result_attachment(
        created_result_id,
        attachment={
            "name": "manual-result.txt",
            "content_type": "text/plain",
            "content": "U2FuZGJveCBtYW51YWwgcmVzdWx0IGV2aWRlbmNl",
        },
    )
    assert result_attachment.target_kind == "test_result"
    assert result_attachment.target_id == created_result_id
    assert result_attachment.status_code == 200

    result_attachments = await allure_client.list_test_result_attachments(created_result_id, size=50)
    attachment_rows = result_attachments.content or []
    assert any(attachment.name == "manual-result.txt" for attachment in attachment_rows)

    attachment_bytes = await allure_client.read_test_result_attachment_content(result_attachments.content[0].id)
    assert attachment_bytes == b"Sandbox manual result evidence"


async def _create_launch_with_test_case(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
    *,
    suffix: str,
    steps: list[dict[str, str]],
) -> tuple[object, object]:
    launch_service = LaunchService(allure_client)
    test_case_service = TestCaseService(allure_client)

    test_case = await test_case_service.create_test_case(
        name=f"[{test_run_id}] {suffix}",
        steps=steps,
    )
    assert test_case.id is not None
    cleanup_tracker.track_test_case(test_case.id)

    launch = await launch_service.create_launch(name=f"[{test_run_id}] {suffix} launch")
    assert launch.id is not None
    cleanup_tracker.track_launch(launch.id)
    return launch, test_case
