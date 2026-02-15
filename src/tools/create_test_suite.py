"""Create a hierarchy suite in Allure TestOps.

This tool creates a suite (group node) in a project tree. It can create either:
- a top-level suite under the tree root (`parent_suite_id` omitted), or
- a nested suite under an existing parent suite (`parent_suite_id` provided).

This operation creates new hierarchy structure and is not destructive.
"""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_hierarchy_service import TestHierarchyService


async def create_test_suite(
    name: Annotated[str, Field(description="Suite name to create in hierarchy.")],
    project_id: Annotated[int | None, Field(description="Allure TestOps project ID.")] = None,
    tree_id: Annotated[
        int | None, Field(description="Target hierarchy tree ID. If omitted, default project tree is used.")
    ] = None,
    parent_suite_id: Annotated[
        int | None, Field(description="Parent suite/group node ID for nested suite creation.")
    ] = None,
) -> str:
    """Create a new test suite node in the hierarchy tree.

    Args:
        name: Suite name to create.
        project_id: Optional project override. If omitted, use default project from environment.
        tree_id: Optional hierarchy tree ID. If omitted, the default project tree is used.
        parent_suite_id: Optional parent suite ID. Provide to create a nested suite.

    Returns:
        Success message containing created suite ID and name.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestHierarchyService(client)
        suite = await service.create_test_suite(
            name=name,
            tree_id=tree_id,
            parent_suite_id=parent_suite_id,
        )

    return f"✅ Test suite created successfully! ID: {suite.id}, Name: {suite.name}"
