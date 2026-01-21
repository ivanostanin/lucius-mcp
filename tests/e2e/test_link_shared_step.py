import logging
import os
import re

import pytest

from src.client import AllureClient
from src.tools.create_test_case import create_test_case
from src.tools.link_shared_step import link_shared_step
from src.tools.shared_steps import create_shared_step
from src.tools.unlink_shared_step import unlink_shared_step
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.test_id("story-2.3-e2e-link-unlink-shared-step")
@pytest.mark.asyncio
async def test_link_shared_step_flow(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    api_token: str,
) -> None:
    """
    E2E for Story 2.3: Link Shared Step to Test Case.

    Flow:
    1. Create a Shared Step
    2. Create a Test Case
    3. Link Shared Step to Test Case
    4. Verify Link
    5. Unlink Shared Step
    6. Verify Unlink
    """

    # 1. Create Shared Step
    ss_name = "E2E Shared Step for Linking"
    ss_steps = [{"action": "Shared Action 1", "expected": "Shared Expected 1"}]

    ss_result = await create_shared_step(
        project_id=project_id,
        name=ss_name,
        steps=ss_steps,
        api_token=api_token,
    )

    ss_match = re.search(r"ID: (\d+)", ss_result)
    assert ss_match, "Could not extract Shared Step ID"
    shared_step_id = int(ss_match.group(1))

    # Track for cleanup (though create_shared_step doesn't have auto-cleanup in tool yet,
    # we should track it if possible, or manual clean in finally)
    # Note: CleanupTracker currently focuses on Test Cases.
    # We'll rely on sandbox cleanup or implementing shared step cleanup if needed.

    test_case_id = None

    try:
        # 2. Create Test Case
        tc_name = "E2E Test Case for Linking"
        tc_steps = [{"action": "Step 1", "expected": "Exp 1"}]

        tc_result = await create_test_case(
            project_id=project_id,
            name=tc_name,
            steps=tc_steps,
            api_token=api_token,
        )

        tc_match = re.search(r"ID: (\d+)", tc_result)
        assert tc_match, "Could not extract Test Case ID"
        test_case_id = int(tc_match.group(1))

        cleanup_tracker.track_test_case(test_case_id)

        # 3. Link Shared Step
        link_result = await link_shared_step(
            test_case_id=test_case_id,
            shared_step_id=shared_step_id,
            position=None,  # Append
            api_token=api_token,
        )

        assert "Linked Shared Step" in link_result
        assert str(shared_step_id) in link_result

        # 4. Verify Link in Allure
        scenario = await allure_client.get_test_case_scenario(test_case_id)

        found_link = False
        for step in scenario.steps:
            # Check if step is a shared step reference
            if step.actual_instance and hasattr(step.actual_instance, "shared_step_id"):
                if step.actual_instance.shared_step_id == shared_step_id:
                    found_link = True
                    break

        assert found_link, f"Shared Step {shared_step_id} not found in Test Case {test_case_id} steps"

        # 5. Unlink Shared Step
        unlink_result = await unlink_shared_step(
            test_case_id=test_case_id,
            shared_step_id=shared_step_id,
            api_token=api_token,
        )

        assert "Unlinked Shared Step" in unlink_result

        # 6. Verify Unlink
        scenario_after = await allure_client.get_test_case_scenario(test_case_id)

        found_link_after = False
        for step in scenario_after.steps:
            if step.actual_instance and hasattr(step.actual_instance, "shared_step_id"):
                if step.actual_instance.shared_step_id == shared_step_id:
                    found_link_after = True
                    break

        assert not found_link_after, "Shared Step reference should have been removed"

    finally:
        # Cleanup Shared Step manually since tracker might not cover it yet
        logger = logging.getLogger(__name__)
        try:
            await allure_client.delete_shared_step(shared_step_id)
        except Exception as e:
            logger.warning(f"Failed to cleanup shared step {shared_step_id}: {e}")
