"""Assign test cases to a hierarchy suite in Allure TestOps.

This tool moves/attaches existing test cases into a target suite path using the
hierarchy assignment API.

⚠️ CAUTION: Destructive.
This operation changes existing hierarchy placement of test cases.
"""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_hierarchy_service import TestHierarchyService


async def assign_test_cases_to_suite(
    suite_id: Annotated[int, Field(description="Target suite/group node ID for assignment.")],
    test_case_ids: Annotated[list[int], Field(description="List of test case IDs to assign to the suite.")],
    project_id: Annotated[int | None, Field(description="Allure TestOps project ID.")] = None,
    tree_id: Annotated[
        int | None, Field(description="Target hierarchy tree ID. If omitted, default project tree is used.")
    ] = None,
) -> str:
    """Assign test cases to a suite path in hierarchy.

    ⚠️ CAUTION: Destructive.
    Reassigning test cases changes their hierarchy location.

    Args:
        suite_id: Target suite/group node ID.
        test_case_ids: List of test case IDs to assign.
        project_id: Optional project override. If omitted, use default project from environment.
        tree_id: Optional hierarchy tree ID. If omitted, the default project tree is used.

    Returns:
        Success message with the number of assigned test cases.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestHierarchyService(client)
        assigned_count = await service.assign_test_cases_to_suite(
            suite_id=suite_id,
            test_case_ids=test_case_ids,
            tree_id=tree_id,
        )

    return f"✅ Assigned {assigned_count} test case(s) to suite {suite_id}."
