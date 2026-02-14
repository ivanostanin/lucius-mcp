"""E2E tests for Defect lifecycle management."""

import pytest

from src.client import AllureClient
from src.tools.defects import (
    create_defect,
    create_defect_matcher,
    delete_defect,
    delete_defect_matcher,
    get_defect,
    list_defect_matchers,
    list_defects,
    update_defect,
)
from tests.e2e.helpers.cleanup import CleanupTracker

pytestmark = pytest.mark.asyncio(loop_scope="module")


async def test_defect_lifecycle(allure_client: AllureClient, cleanup_tracker: CleanupTracker, test_run_id: str) -> None:
    """Verify complete defect lifecycle: Create -> Get -> Update -> List -> Delete."""

    # 1. Create a Defect
    defect_name = f"[{test_run_id}] E2E Defect"
    create_output = await create_defect(name=defect_name, description="E2E description")
    assert "Created Defect #" in create_output

    # Extract ID (format: "Created Defect #<id>: ...")
    defect_id = int(create_output.split("#")[1].split(":")[0])
    cleanup_tracker.track_defect(defect_id)

    # 2. Get Defect
    get_output = await get_defect(defect_id=defect_id)
    assert f"Defect #{defect_id}" in get_output
    assert "Status: Open" in get_output
    assert "E2E description" in get_output

    # 3. Update Defect (rename + close)
    new_name = f"[{test_run_id}] Updated Defect"
    update_output = await update_defect(defect_id=defect_id, name=new_name, closed=True)
    assert f"Updated Defect #{defect_id}" in update_output
    assert "Status: Closed" in update_output

    # 4. List Defects
    list_output = await list_defects()
    assert f"#{defect_id}" in list_output

    # 5. Delete Defect
    delete_output = await delete_defect(defect_id=defect_id, confirm=True)
    assert f"Deleted Defect #{defect_id}" in delete_output


async def test_defect_matcher_lifecycle(
    allure_client: AllureClient, cleanup_tracker: CleanupTracker, test_run_id: str
) -> None:
    """Verify defect matcher lifecycle: Create defect -> Add matcher -> List -> Delete matcher -> Delete defect."""

    # 1. Create parent defect
    create_output = await create_defect(name=f"[{test_run_id}] Matcher Parent")
    defect_id = int(create_output.split("#")[1].split(":")[0])
    cleanup_tracker.track_defect(defect_id)

    # 2. Create a matcher
    matcher_output = await create_defect_matcher(
        defect_id=defect_id,
        name="NPE Auto-Rule",
        message_regex=".*NullPointerException.*",
    )
    assert "Created Defect Matcher #" in matcher_output
    matcher_id = int(matcher_output.split("Matcher #")[1].split(":")[0])

    # 3. List matchers
    list_output = await list_defect_matchers(defect_id=defect_id)
    assert f"#{matcher_id}" in list_output
    assert "NPE Auto-Rule" in list_output

    # 4. Delete matcher
    del_output = await delete_defect_matcher(matcher_id=matcher_id, confirm=True)
    assert f"Deleted Defect Matcher #{matcher_id}" in del_output

    # 5. Verify empty matchers
    empty_list = await list_defect_matchers(defect_id=defect_id)
    assert "No matchers found" in empty_list

    # 6. Cleanup parent defect
    await delete_defect(defect_id=defect_id, confirm=True)
