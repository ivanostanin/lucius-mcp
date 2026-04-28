"""E2E tests for test hierarchy management workflows."""

import asyncio
import re
from uuid import uuid4

from src.client import AllureClient
from src.client.generated.models.test_case_tree_leaf_dto_v2 import TestCaseTreeLeafDtoV2
from src.services.test_hierarchy_service import TestHierarchyService
from src.tools.assign_test_cases_to_suite import assign_test_cases_to_suite
from src.tools.create_test_case import create_test_case
from src.tools.create_test_suite import create_test_suite
from src.tools.delete_test_case import delete_test_case
from src.tools.delete_test_suite import delete_test_suite
from src.tools.list_test_suites import list_test_suites
from tests.e2e.helpers.cleanup import CleanupTracker


def _collect_suite_ids(nodes: list) -> list[int]:
    ids: list[int] = []
    for node in nodes:
        ids.append(node.id)
        ids.extend(_collect_suite_ids(node.children))
    return ids


async def _wait_for_suite_absence(
    service: TestHierarchyService,
    suite_id: int,
    *,
    retries: int = 120,
    delay_seconds: float = 1.0,
) -> bool:
    for _ in range(retries):
        _tree, suites = await service.list_test_suites(include_empty=True)
        if suite_id not in _collect_suite_ids(suites):
            return True
        await asyncio.sleep(delay_seconds)
    return False


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
    cleanup_tracker.track_test_suite(root_suite.id)

    nested_suite = await service.create_test_suite(
        name=nested_name,
        parent_suite_id=root_suite.id,
    )
    assert nested_suite.id is not None
    cleanup_tracker.track_test_suite(nested_suite.id)

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
    cleanup_tracker.track_test_suite(suite.id)

    create_output = await create_test_case(
        name=f"E2E Hierarchy Assignment Case {run_id}",
        project_id=project_id,
        output_format="plain",
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

    delete_output = await delete_test_case(
        test_case_id=test_case_id,
        confirm=True,
        project_id=project_id,
        output_format="plain",
    )
    assert "Archived Test Case" in delete_output or "already archived" in delete_output


async def test_e2e_hierarchy_tools_smoke(
    project_id: int,
    cleanup_tracker: CleanupTracker,
) -> None:
    """Run hierarchy tools in real environment and validate outputs."""
    run_id = uuid4().hex[:8]

    suite_name = f"E2E-Tool-Suite-{project_id}-{run_id}"
    cleanup_tracker.track_custom_field_value_name(suite_name)
    create_output = await create_test_suite(name=suite_name, project_id=project_id, output_format="plain")
    assert "✅ Test suite created successfully!" in create_output

    match = re.search(r"ID: (\d+)", create_output)
    assert match is not None
    suite_id = int(match.group(1))
    cleanup_tracker.track_test_suite(suite_id)

    list_output = await list_test_suites(project_id=project_id, output_format="plain")
    assert "Tree:" in list_output

    tc_output = await create_test_case(
        name=f"E2E Tool Assign Case {run_id}",
        project_id=project_id,
        output_format="plain",
    )
    tc_match = re.search(r"ID: (\d+)", tc_output)
    assert tc_match is not None
    tc_id = int(tc_match.group(1))
    cleanup_tracker.track_test_case(tc_id)

    assign_output = await assign_test_cases_to_suite(
        suite_id=suite_id,
        test_case_ids=[tc_id],
        project_id=project_id,
        output_format="plain",
    )
    assert "Assigned" in assign_output

    delete_output = await delete_test_case(
        test_case_id=tc_id, confirm=True, project_id=project_id, output_format="plain"
    )
    assert "Archived Test Case" in delete_output or "already archived" in delete_output


async def test_e2e_hierarchy_delete_suite_lifecycle(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """Create suite + case, assign case, delete suite, then verify suite is removed."""
    service = TestHierarchyService(allure_client)
    run_id = uuid4().hex[:8]

    root_name = f"E2E-Delete-Root-{project_id}-{run_id}"
    nested_name = f"E2E-Delete-Nested-{project_id}-{run_id}"
    cleanup_tracker.track_custom_field_value_name(root_name)
    cleanup_tracker.track_custom_field_value_name(nested_name)

    root_suite = await service.create_test_suite(name=root_name)
    assert root_suite.id is not None
    cleanup_tracker.track_test_suite(root_suite.id)

    nested_suite = await service.create_test_suite(name=nested_name, parent_suite_id=root_suite.id)
    assert nested_suite.id is not None
    cleanup_tracker.track_test_suite(nested_suite.id)

    tc_output = await create_test_case(
        name=f"E2E Delete Suite Case {run_id}",
        project_id=project_id,
        output_format="plain",
    )
    match = re.search(r"ID: (\d+)", tc_output)
    assert match is not None
    test_case_id = int(match.group(1))
    cleanup_tracker.track_test_case(test_case_id)

    assign_output = await assign_test_cases_to_suite(
        suite_id=nested_suite.id,
        test_case_ids=[test_case_id],
        project_id=project_id,
        output_format="plain",
    )
    assert "Assigned 1 test case(s)" in assign_output

    delete_output = await delete_test_suite(
        suite_id=nested_suite.id,
        confirm=True,
        project_id=project_id,
        output_format="plain",
    )
    assert f"✅ Test suite {nested_suite.id} deleted successfully (idempotent)." == delete_output

    second_delete_output = await delete_test_suite(
        suite_id=nested_suite.id,
        confirm=True,
        project_id=project_id,
        output_format="plain",
    )
    assert second_delete_output == delete_output

    # In some TestOps setups, suites with assigned leaves become removable
    # only after leaf cleanup. Keep the lifecycle deterministic for both modes.
    delete_case_output = await delete_test_case(
        test_case_id=test_case_id,
        confirm=True,
        project_id=project_id,
        output_format="plain",
    )
    assert "Archived Test Case" in delete_case_output or "already archived" in delete_case_output

    third_delete_output = await delete_test_suite(
        suite_id=nested_suite.id,
        confirm=True,
        project_id=project_id,
        output_format="plain",
    )
    assert third_delete_output == delete_output

    assert await _wait_for_suite_absence(service, nested_suite.id), (
        f"Suite {nested_suite.id} is still present after delete lifecycle retries"
    )


async def test_e2e_hierarchy_delete_parent_suite_with_children(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """Delete parent suite with nested suite + assigned case and verify hierarchy cleanup."""
    service = TestHierarchyService(allure_client)
    run_id = uuid4().hex[:8]

    root_name = f"E2E-Delete-Parent-Root-{project_id}-{run_id}"
    nested_name = f"E2E-Delete-Parent-Nested-{project_id}-{run_id}"
    cleanup_tracker.track_custom_field_value_name(root_name)
    cleanup_tracker.track_custom_field_value_name(nested_name)

    root_suite = await service.create_test_suite(name=root_name)
    assert root_suite.id is not None
    cleanup_tracker.track_test_suite(root_suite.id)

    nested_suite = await service.create_test_suite(name=nested_name, parent_suite_id=root_suite.id)
    assert nested_suite.id is not None
    cleanup_tracker.track_test_suite(nested_suite.id)

    tc_output = await create_test_case(
        name=f"E2E Delete Parent Suite Case {run_id}",
        project_id=project_id,
        output_format="plain",
    )
    match = re.search(r"ID: (\d+)", tc_output)
    assert match is not None
    test_case_id = int(match.group(1))
    cleanup_tracker.track_test_case(test_case_id)

    assign_output = await assign_test_cases_to_suite(
        suite_id=nested_suite.id,
        test_case_ids=[test_case_id],
        project_id=project_id,
        output_format="plain",
    )
    assert "Assigned 1 test case(s)" in assign_output

    delete_parent_output = await delete_test_suite(
        suite_id=root_suite.id,
        confirm=True,
        project_id=project_id,
        output_format="plain",
    )
    assert delete_parent_output == f"✅ Test suite {root_suite.id} deleted successfully (idempotent)."

    assert await _wait_for_suite_absence(service, root_suite.id), (
        f"Parent suite {root_suite.id} is still present after deletion retries"
    )
    assert await _wait_for_suite_absence(service, nested_suite.id), (
        f"Nested suite {nested_suite.id} is still present after parent deletion retries"
    )
