"""Sandbox coverage for the exact TestOps test-result read."""

from __future__ import annotations

import pytest

from src.client import AllureClient
from src.services.launch_service import LaunchService
from src.services.test_result_service import TestResultService
from tests.e2e.helpers.cleanup import CleanupTracker
from tests.e2e.test_launch_manual_execution import _create_launch_with_test_case

pytestmark = pytest.mark.asyncio(loop_scope="module")


async def test_get_test_result_returns_exact_result_with_stable_result_url(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
) -> None:
    launch, test_case = await _create_launch_with_test_case(
        allure_client,
        cleanup_tracker,
        test_run_id,
        suffix="test-result-detail",
        steps=[{"action": "Open detail", "expected": "Detail opens"}],
    )
    session = await LaunchService(allure_client).start_manual_test_session(launch.id)
    submission = await LaunchService(allure_client).submit_manual_test_results(
        session.test_session_id,
        results=[
            {
                "launch_id": launch.id,
                "test_case_id": test_case.id,
                "name": f"[{test_run_id}] Detail Result",
                "full_name": f"[{test_run_id}] Detail Result",
                "status": "passed",
            }
        ],
    )
    result_id = submission.result_ids[0]

    detail = await TestResultService(allure_client).get_test_result(result_id)

    assert detail.test_result_id == result_id
    assert detail.actual_launch_id == launch.id
    assert detail.result_url == f"{allure_client.get_base_url()}/launch/{launch.id}/tree/{result_id}"
    assert "treeId" not in detail.result_url
