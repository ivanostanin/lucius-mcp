"""E2E coverage for manual execution workflows inside launches."""

import pytest

from src.client import AllureClient
from src.client.generated.api.test_plan_controller_api import TestPlanControllerApi
from src.client.generated.models.test_plan_run_request_dto import TestPlanRunRequestDto
from src.services.launch_service import LaunchService
from src.services.plan_service import PlanService
from src.services.test_case_service import TestCaseService
from tests.e2e.helpers.cleanup import CleanupTracker

pytestmark = pytest.mark.asyncio(loop_scope="module")


async def test_manual_launch_execution_workflow(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
) -> None:
    """Verify manual session creation, submission, rerun, and evidence upload."""
    test_case_service = TestCaseService(allure_client)
    plan_service = PlanService(allure_client)
    launch_service = LaunchService(allure_client)

    test_case = await test_case_service.create_test_case(
        name=f"[{test_run_id}] Manual Execution",
        steps=[{"action": "Open app", "expected": "App opens"}],
    )
    assert test_case.id is not None
    cleanup_tracker.track_test_case(test_case.id)

    plan = await plan_service.create_plan(
        name=f"[{test_run_id}] Manual Execution Plan",
        test_case_ids=[test_case.id],
    )
    assert plan.id is not None
    cleanup_tracker.track_test_plan(plan.id)

    plan_api = TestPlanControllerApi(allure_client.api_client)
    launch = await allure_client._call_api(
        plan_api.run3(
            id=plan.id,
            test_plan_run_request_dto=TestPlanRunRequestDto(
                launch_name=f"[{test_run_id}] Manual Execution Launch",
            ),
            _request_timeout=allure_client._timeout,
        )
    )
    assert launch.id is not None
    cleanup_tracker.track_launch(launch.id)

    launch_results = await launch_service.list_launch_test_results(launch.id, manual_only=True)
    assert launch_results.total >= 1
    initial_result = next(item for item in launch_results.items if item.test_case_id == test_case.id)
    assert initial_result.name == test_case.name

    session = await launch_service.start_manual_test_session(launch.id)
    assert session.test_session_id > 0

    submission = await launch_service.submit_manual_test_results(
        session.test_session_id,
        results=[
            {
                "test_case_id": test_case.id,
                "name": test_case.name,
                "status": "failed",
                "start": 1000,
                "stop": 2000,
                "message": "Sandbox manual execution failure",
                "steps": [
                    {
                        "type": "body",
                        "body": "Open app",
                        "status": "failed",
                        "message": "Intentional E2E failure",
                    },
                    {
                        "type": "attachment",
                        "attachment": {
                            "name": "manual-step.txt",
                            "content_type": "text/plain",
                        },
                        "status": "failed",
                    },
                ],
            }
        ],
    )
    assert submission.result_ids
    created_result_id = submission.result_ids[0]

    created_result = await allure_client.get_test_result(created_result_id)
    assert created_result.id == created_result_id
    assert created_result.launch_id == launch.id
    assert created_result.status is not None
    assert created_result.status.value.lower() == "failed"

    rerun = await launch_service.rerun_test_results_manually(
        launch.id,
        result_ids=[created_result_id],
    )
    assert rerun.result_ids == [created_result_id]
    assert rerun.scheduled_count == 1

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
    assert result_attachment.status_code in {200, 202}

    step_attachment = await launch_service.add_test_step_attachment(
        test_result_id=created_result_id,
        step_name="manual-step.txt",
        attachment={
            "name": "manual-step.txt",
            "content_type": "text/plain",
            "content": "U2FuZGJveCBtYW51YWwgc3RlcCBldmlkZW5jZQ==",
        },
    )
    assert step_attachment.target_kind == "test_step"
    assert step_attachment.status_code == 200

    execution = await allure_client.get_test_result_execution(created_result_id)
    attachment_steps = [
        step.actual_instance
        for step in execution.steps or []
        if getattr(step.actual_instance, "attachment_id", None) == step_attachment.target_id
    ]
    assert len(attachment_steps) == 1
    attachment_step = attachment_steps[0]
    attachment = attachment_step.attachment.actual_instance if attachment_step.attachment is not None else None
    assert attachment is not None
    assert attachment.id == step_attachment.target_id
    assert attachment.name == "manual-step.txt"

    attachment_bytes = await allure_client.read_test_result_attachment_content(step_attachment.target_id)
    assert attachment_bytes == b"Sandbox manual step evidence"
