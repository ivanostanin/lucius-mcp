"""E2E tests for test hierarchy management workflows."""

import asyncio
from uuid import uuid4

from src.tools.assign_test_cases_to_suite import assign_test_cases_to_suite
from src.tools.create_test_case import create_test_case
from src.tools.create_test_suite import create_test_suite
from src.tools.delete_test_case import delete_test_case
from src.tools.delete_test_suite import delete_test_suite
from src.tools.get_test_suite_contents import get_test_suite_contents
from src.tools.list_test_suites import list_test_suites
from tests.e2e.helpers.cleanup import CleanupTracker


def _structured_payload(output: object) -> dict[str, object]:
    payload = getattr(output, "structured_content", None)
    assert isinstance(payload, dict)
    return payload


def _suite_ids(nodes: list[object]) -> set[int]:
    """Collect suite IDs from the public list-tool hierarchy payload."""
    ids: set[int] = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if isinstance(node_id, int):
            ids.add(node_id)
        children = node.get("children")
        if isinstance(children, list):
            ids.update(_suite_ids(children))
    return ids


async def _create_suite(
    *,
    name: str,
    project_id: int,
    parent_suite_id: int | None = None,
) -> int:
    output = await create_test_suite(
        name=name,
        project_id=project_id,
        parent_suite_id=parent_suite_id,
        output_format="json",
    )
    suite_id = _structured_payload(output)["id"]
    assert isinstance(suite_id, int)
    return suite_id


async def _create_test_case(*, name: str, project_id: int) -> int:
    output = await create_test_case(name=name, project_id=project_id, output_format="json")
    test_case_id = _structured_payload(output)["id"]
    assert isinstance(test_case_id, int)
    return test_case_id


async def _get_suite_tree_id(*, suite_id: int, project_id: int) -> int:
    """Read a suite through its public tool and pin later operations to that tree."""
    output = await get_test_suite_contents(suite_id=suite_id, project_id=project_id, output_format="json")
    tree_id = _structured_payload(output)["tree_id"]
    assert isinstance(tree_id, int)
    return tree_id


async def _wait_for_suites_absence(
    *,
    suite_ids: set[int],
    project_id: int,
    retries: int = 20,
    delay_seconds: float = 0.5,
) -> bool:
    """Poll the public list tool until all created suite IDs are absent."""
    for _ in range(retries):
        output = await list_test_suites(project_id=project_id, include_empty=True, output_format="json")
        items = _structured_payload(output)["items"]
        assert isinstance(items, list)
        if suite_ids.isdisjoint(_suite_ids(items)):
            return True
        await asyncio.sleep(delay_seconds)
    return False


async def test_e2e_hierarchy_create_and_list_suites(
    project_id: int,
    cleanup_tracker: CleanupTracker,
) -> None:
    """Create root and nested suites, then exercise the public hierarchy list tool."""
    run_id = uuid4().hex[:8]
    root_name = f"E2E-Hierarchy-Root-{project_id}-{run_id}"
    nested_name = f"E2E-Hierarchy-Nested-{project_id}-{run_id}"
    cleanup_tracker.track_custom_field_value_name(root_name)
    cleanup_tracker.track_custom_field_value_name(nested_name)

    root_suite_id = await _create_suite(name=root_name, project_id=project_id)
    cleanup_tracker.track_test_suite(root_suite_id)
    nested_suite_id = await _create_suite(name=nested_name, project_id=project_id, parent_suite_id=root_suite_id)
    cleanup_tracker.track_test_suite(nested_suite_id)

    output = await list_test_suites(project_id=project_id, include_empty=True, output_format="json")
    payload = _structured_payload(output)
    assert isinstance(payload["tree"], dict)
    assert isinstance(payload["items"], list)
    assert {root_suite_id, nested_suite_id}.issubset(_suite_ids(payload["items"]))


async def test_e2e_hierarchy_assign_test_cases_to_suite(
    project_id: int,
    cleanup_tracker: CleanupTracker,
) -> None:
    """Assign a run-unique test case and verify it through the targeted read tool."""
    run_id = uuid4().hex[:8]
    suite_name = f"E2E-Assign-Suite-{project_id}-{run_id}"
    cleanup_tracker.track_custom_field_value_name(suite_name)
    suite_id = await _create_suite(name=suite_name, project_id=project_id)
    cleanup_tracker.track_test_suite(suite_id)

    test_case_id = await _create_test_case(name=f"E2E Hierarchy Assignment Case {run_id}", project_id=project_id)
    cleanup_tracker.track_test_case(test_case_id)

    assigned = await assign_test_cases_to_suite(
        suite_id=suite_id,
        test_case_ids=[test_case_id],
        project_id=project_id,
        output_format="json",
    )
    assert _structured_payload(assigned)["assigned_count"] == 1

    contents = await get_test_suite_contents(
        suite_id=suite_id,
        project_id=project_id,
        output_format="json",
    )
    test_case_ids = _structured_payload(contents)["test_case_ids"]
    assert isinstance(test_case_ids, list)
    assert test_case_id in test_case_ids

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
    """Run the public suite create, contents, list, and assignment workflow."""
    run_id = uuid4().hex[:8]
    suite_name = f"E2E-Tool-Suite-{project_id}-{run_id}"
    cleanup_tracker.track_custom_field_value_name(suite_name)
    suite_id = await _create_suite(name=suite_name, project_id=project_id)
    cleanup_tracker.track_test_suite(suite_id)

    contents = await get_test_suite_contents(
        suite_id=suite_id,
        project_id=project_id,
        output_format="json",
    )
    contents_payload = _structured_payload(contents)
    assert contents_payload["suite_id"] == suite_id
    assert isinstance(contents_payload["tree_id"], int)
    assert contents_payload["test_case_ids"] == []
    assert contents_payload["assigned_count"] == 0

    listed = await list_test_suites(project_id=project_id, output_format="plain")
    assert "Tree:" in listed

    test_case_id = await _create_test_case(name=f"E2E Tool Assign Case {run_id}", project_id=project_id)
    cleanup_tracker.track_test_case(test_case_id)
    assigned = await assign_test_cases_to_suite(
        suite_id=suite_id,
        test_case_ids=[test_case_id],
        project_id=project_id,
        output_format="json",
    )
    assert _structured_payload(assigned)["assigned_count"] == 1

    delete_output = await delete_test_case(
        test_case_id=test_case_id, confirm=True, project_id=project_id, output_format="plain"
    )
    assert "Archived Test Case" in delete_output or "already archived" in delete_output


async def test_e2e_hierarchy_delete_suite_lifecycle(
    project_id: int,
    cleanup_tracker: CleanupTracker,
) -> None:
    """Delete a nested suite and verify its exact ID is eventually absent."""
    run_id = uuid4().hex[:8]
    root_name = f"E2E-Delete-Root-{project_id}-{run_id}"
    nested_name = f"E2E-Delete-Nested-{project_id}-{run_id}"
    cleanup_tracker.track_custom_field_value_name(root_name)
    cleanup_tracker.track_custom_field_value_name(nested_name)

    root_suite_id = await _create_suite(name=root_name, project_id=project_id)
    cleanup_tracker.track_test_suite(root_suite_id)
    nested_suite_id = await _create_suite(name=nested_name, project_id=project_id, parent_suite_id=root_suite_id)
    cleanup_tracker.track_test_suite(nested_suite_id)

    test_case_id = await _create_test_case(name=f"E2E Delete Suite Case {run_id}", project_id=project_id)
    cleanup_tracker.track_test_case(test_case_id)
    assigned = await assign_test_cases_to_suite(
        suite_id=nested_suite_id,
        test_case_ids=[test_case_id],
        project_id=project_id,
        output_format="json",
    )
    assert _structured_payload(assigned)["assigned_count"] == 1

    tree_id = await _get_suite_tree_id(suite_id=nested_suite_id, project_id=project_id)

    delete_case_output = await delete_test_case(
        test_case_id=test_case_id,
        confirm=True,
        project_id=project_id,
        output_format="plain",
    )
    assert "Archived Test Case" in delete_case_output or "already archived" in delete_case_output

    delete_output = await delete_test_suite(
        suite_id=nested_suite_id,
        tree_id=tree_id,
        confirm=True,
        project_id=project_id,
        output_format="plain",
    )
    assert delete_output == f"✅ Test suite {nested_suite_id} deleted successfully (idempotent)."

    assert await _wait_for_suites_absence(
        suite_ids={nested_suite_id},
        project_id=project_id,
    ), f"Suite {nested_suite_id} is still present after delete lifecycle retries"


async def test_e2e_hierarchy_delete_parent_suite_with_children(
    project_id: int,
    cleanup_tracker: CleanupTracker,
) -> None:
    """Delete a parent suite and verify parent and child IDs through the public read tool."""
    run_id = uuid4().hex[:8]
    root_name = f"E2E-Delete-Parent-Root-{project_id}-{run_id}"
    nested_name = f"E2E-Delete-Parent-Nested-{project_id}-{run_id}"
    cleanup_tracker.track_custom_field_value_name(root_name)
    cleanup_tracker.track_custom_field_value_name(nested_name)

    root_suite_id = await _create_suite(name=root_name, project_id=project_id)
    cleanup_tracker.track_test_suite(root_suite_id)
    nested_suite_id = await _create_suite(name=nested_name, project_id=project_id, parent_suite_id=root_suite_id)
    cleanup_tracker.track_test_suite(nested_suite_id)

    test_case_id = await _create_test_case(name=f"E2E Delete Parent Suite Case {run_id}", project_id=project_id)
    cleanup_tracker.track_test_case(test_case_id)
    assigned = await assign_test_cases_to_suite(
        suite_id=nested_suite_id,
        test_case_ids=[test_case_id],
        project_id=project_id,
        output_format="json",
    )
    assert _structured_payload(assigned)["assigned_count"] == 1

    tree_id = await _get_suite_tree_id(suite_id=root_suite_id, project_id=project_id)

    delete_case_output = await delete_test_case(
        test_case_id=test_case_id,
        confirm=True,
        project_id=project_id,
        output_format="plain",
    )
    assert "Archived Test Case" in delete_case_output or "already archived" in delete_case_output

    delete_output = await delete_test_suite(
        suite_id=root_suite_id,
        tree_id=tree_id,
        confirm=True,
        project_id=project_id,
        output_format="plain",
    )
    assert delete_output == f"✅ Test suite {root_suite_id} deleted successfully (idempotent)."
    assert await _wait_for_suites_absence(
        suite_ids={root_suite_id, nested_suite_id},
        project_id=project_id,
    ), f"Parent or nested suite ({root_suite_id}, {nested_suite_id}) is still present after deletion retries"
