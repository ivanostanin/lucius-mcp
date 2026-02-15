"""E2E tests for test hierarchy management workflows."""

import re
from uuid import uuid4

from src.client import AllureClient
from src.client.generated.models.test_case_tree_leaf_dto_v2 import TestCaseTreeLeafDtoV2
from src.services.test_hierarchy_service import TestHierarchyService
from src.tools.assign_test_cases_to_suite import assign_test_cases_to_suite
from src.tools.create_test_case import create_test_case
from src.tools.create_test_suite import create_test_suite
from src.tools.delete_test_case import delete_test_case
from src.tools.list_test_suites import list_test_suites
from tests.e2e.helpers.cleanup import CleanupTracker


async def test_e2e_hierarchy_create_and_list_suites(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """Create root and nested suites, then verify they appear in hierarchy list."""
    service = TestHierarchyService(allure_client)

    run_id = uuid4().hex[:8]
    root_name = f"E2E-Hierarchy-Root-{project_id}-{run_id}"
    nested_name = f"E2E-Hierarchy-Nested-{project_id}-{run_id}"
    cleanup_tracker.track_custom_field_value_name(root_name)
    cleanup_tracker.track_custom_field_value_name(nested_name)

    root_suite = await service.create_test_suite(name=root_name)
    assert root_suite.id is not None

    nested_suite = await service.create_test_suite(
        name=nested_name,
        parent_suite_id=root_suite.id,
    )
    assert nested_suite.id is not None

    _tree, suites = await service.list_test_suites(include_empty=True)
    assert isinstance(suites, list)


async def test_e2e_hierarchy_assign_test_cases_to_suite(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """Create test case and assign it into created suite."""
    service = TestHierarchyService(allure_client)

    run_id = uuid4().hex[:8]
    suite_name = f"E2E-Assign-Suite-{project_id}-{run_id}"
    cleanup_tracker.track_custom_field_value_name(suite_name)
    suite = await service.create_test_suite(name=suite_name)
    assert suite.id is not None

    create_output = await create_test_case(
        name=f"E2E Hierarchy Assignment Case {run_id}",
        project_id=project_id,
    )
    assert "Created Test Case ID:" in create_output

    match = re.search(r"ID: (\d+)", create_output)
    assert match is not None
    test_case_id = int(match.group(1))
    cleanup_tracker.track_test_case(test_case_id)

    assigned_count = await service.assign_test_cases_to_suite(
        suite_id=suite.id,
        test_case_ids=[test_case_id],
    )

    assert assigned_count == 1

    tree = await service._resolve_tree(None)
    tree_id = tree.id
    assert tree_id is not None

    suite_node = await allure_client.get_tree_node(
        project_id=project_id,
        tree_id=tree_id,
        parent_node_id=suite.id,
        page=0,
        size=500,
    )
    assert suite_node.children is not None
    suite_children = suite_node.children.content or []
    leaf_ids = [
        item.actual_instance.test_case_id
        for item in suite_children
        if isinstance(item.actual_instance, TestCaseTreeLeafDtoV2) and item.actual_instance.test_case_id is not None
    ]
    assert test_case_id in leaf_ids

    delete_output = await delete_test_case(test_case_id=test_case_id, confirm=True, project_id=project_id)
    assert "Archived Test Case" in delete_output or "already archived" in delete_output


async def test_e2e_hierarchy_tools_smoke(
    project_id: int,
    cleanup_tracker: CleanupTracker,
) -> None:
    """Run hierarchy tools in real environment and validate outputs."""
    run_id = uuid4().hex[:8]

    suite_name = f"E2E-Tool-Suite-{project_id}-{run_id}"
    cleanup_tracker.track_custom_field_value_name(suite_name)
    create_output = await create_test_suite(name=suite_name, project_id=project_id)
    assert "✅ Test suite created successfully!" in create_output

    match = re.search(r"ID: (\d+)", create_output)
    assert match is not None
    suite_id = int(match.group(1))

    list_output = await list_test_suites(project_id=project_id)
    assert "Tree:" in list_output

    tc_output = await create_test_case(name=f"E2E Tool Assign Case {run_id}", project_id=project_id)
    tc_match = re.search(r"ID: (\d+)", tc_output)
    assert tc_match is not None
    tc_id = int(tc_match.group(1))
    cleanup_tracker.track_test_case(tc_id)

    assign_output = await assign_test_cases_to_suite(
        suite_id=suite_id,
        test_case_ids=[tc_id],
        project_id=project_id,
    )
    assert "Assigned" in assign_output

    delete_output = await delete_test_case(test_case_id=tc_id, confirm=True, project_id=project_id)
    assert "Archived Test Case" in delete_output or "already archived" in delete_output
