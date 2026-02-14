"""E2E tests for Test Plan management."""

import pytest

from src.client import AllureClient
from src.tools.plans import (
    create_test_plan,
    delete_test_plan,
    list_test_plans,
    manage_test_plan_content,
    update_test_plan,
)
from tests.e2e.helpers.cleanup import CleanupTracker

pytestmark = pytest.mark.asyncio(loop_scope="module")


async def test_test_plan_lifecycle(
    allure_client: AllureClient, cleanup_tracker: CleanupTracker, test_run_id: str
) -> None:
    """Verify complete test plan lifecycle: Create -> Update -> Content -> List -> Delete."""

    # 1. Create a Test Plan
    plan_name = f"[{test_run_id}] E2E Plan"
    create_output = await create_test_plan(name=plan_name)
    assert "Created Test Plan" in create_output

    # Extract ID (format: "Created Test Plan <id>: ...")
    plan_id = int(create_output.split("Plan ")[1].split(":")[0])
    cleanup_tracker.track_test_plan(plan_id)

    # 2. Update Plan Name
    new_name = f"[{test_run_id}] Updated Plan"
    update_output = await update_test_plan(plan_id=plan_id, name=new_name)
    assert f"Updated Test Plan {plan_id}: '{new_name}'" in update_output

    # 3. List Plans to verify update
    list_output = await list_test_plans(page=0, size=100)
    assert f"[{plan_id}] {new_name}" in list_output

    # 4. Manage Content (No op essentially since we don't have stable TCs here,
    # but exercising the tool)
    # Use a safe query that should be valid syntax-wise
    aql_output = await manage_test_plan_content(plan_id=plan_id, update_aql_filter="id > 0")
    assert f"Updated content for Test Plan {plan_id}" in aql_output

    # 5. Delete Plan
    delete_output = await delete_test_plan(plan_id=plan_id, confirm=True)
    assert f"Successfully deleted Test Plan {plan_id}" in delete_output

    # 6. Verify Deletion
    # Listing again should not show the plan
    final_list = await list_test_plans(page=0, size=100)
    assert f"[{plan_id}]" not in final_list
