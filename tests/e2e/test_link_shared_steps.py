import os
import re
from typing import Any

import pytest

from src.client import AllureClient
from src.tools.create_test_case import create_test_case
from src.tools.link_shared_step import link_shared_step
from src.tools.shared_steps import create_shared_step
from src.tools.unlink_shared_step import unlink_shared_step


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_link_unlink_shared_step_flow(project_id: int, allure_client: AllureClient, cleanup_tracker: Any) -> None:
    """
    E2E Test: Link and Unlink Shared Step.

    Flow:
    1. Create a Shared Step.
    2. Create a Test Case.
    3. Link Shared Step to Test Case.
    4. Verify Link.
    5. Unlink Shared Step from Test Case.
    6. Verify Unlink.
    """
    # 1. Create Shared Step
    ss_name = f"E2E Shared Step {os.urandom(4).hex()}"
    ss_output = await create_shared_step(project_id=project_id, name=ss_name)

    match = re.search(r"ID: (\d+)", ss_output)
    assert match, "Could not extract Shared Step ID"
    shared_step_id = int(match.group(1))
    cleanup_tracker.track_shared_step(shared_step_id)

    # 2. Create Test Case
    tc_name = f"E2E TC with Shared Step {os.urandom(4).hex()}"
    tc_output = await create_test_case(project_id=project_id, name=tc_name)

    match = re.search(r"ID: (\d+)", tc_output)
    assert match, "Could not extract Test Case ID"
    test_case_id = int(match.group(1))
    cleanup_tracker.track_test_case(test_case_id)

    # 3. Link Shared Step
    link_output = await link_shared_step(test_case_id=test_case_id, shared_step_id=shared_step_id)
    assert "✅ Linked Shared Step" in link_output
    assert f"ID: {shared_step_id}" in link_output

    # 4. Verify Link via Service/Client
    # The scenario should contain a step referring to the shared step
    scenario = await allure_client.get_test_case_scenario(test_case_id)
    assert scenario.steps is not None
    assert len(scenario.steps) == 1

    step = scenario.steps[0]
    # Check if it has shared_step_id (via our new DTOs or actual instance)
    # The client returns TestCaseScenarioV2Dto -> SharedStepScenarioDtoStepsInner -> SharedStepStepDtoWithId
    assert step.actual_instance is not None
    # We can check the type or just attributes
    # Note: getattr used because of mypy issues, but runtime attributes exist.
    assert getattr(step.actual_instance, "shared_step_id", None) == shared_step_id

    # 5. Unlink Shared Step
    unlink_output = await unlink_shared_step(test_case_id=test_case_id, shared_step_id=shared_step_id)
    assert "✅ Unlinked Shared Step" in unlink_output

    # 6. Verify Unlink
    scenario_after = await allure_client.get_test_case_scenario(test_case_id)
    # Steps should be empty or not contain the shared step
    # TestCaseScenarioV2Dto defaults steps=[] if empty
    steps = scenario_after.steps or []
    assert len(steps) == 0, f"Expected 0 steps, found {len(steps)}"
