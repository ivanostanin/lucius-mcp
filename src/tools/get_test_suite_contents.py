"""Read the test cases directly assigned to one hierarchy suite."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_hierarchy_service import TestHierarchyService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output
from src.tools.output_schemas import output_fields


@output_fields("suite_id", "tree_id", "test_case_ids", "assigned_count")
async def get_test_suite_contents(
    suite_id: Annotated[int, Field(description="Suite/group node ID to inspect in hierarchy.")],
    project_id: Annotated[int | None, Field(description="Optional Allure TestOps project ID override.")] = None,
    tree_id: Annotated[
        int | None,
        Field(description="Optional hierarchy tree ID. If omitted, the default project tree is used."),
    ] = None,
    expected_suite_name: Annotated[
        str | None,
        Field(description="Optional exact suite name used to confirm the target before reading its contents."),
    ] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Get test cases directly assigned to one test suite.

    This is a targeted hierarchy read. It does not enumerate unrelated suites
    or recursively traverse the project tree.

    Args:
        suite_id: Existing suite/group node ID to inspect.
        project_id: Optional Allure TestOps project override.
        tree_id: Optional hierarchy tree containing the suite.
        expected_suite_name: Optional exact name of the target suite. Supply it when available to avoid reading a
            missing node after an asynchronous deletion.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        The suite ID, tree context, and directly assigned test-case IDs.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestHierarchyService(client)
        contents = await service.get_suite_contents(
            suite_id=suite_id,
            tree_id=tree_id,
            expected_suite_name=expected_suite_name,
        )

    assigned_count = len(contents.test_case_ids)
    plain = (
        f"Suite {suite_id} has no directly assigned test cases."
        if not contents.test_case_ids
        else (
            f"Suite {suite_id} directly contains {assigned_count} test case(s): "
            f"{', '.join(map(str, contents.test_case_ids))}."
        )
    )
    return render_output(
        plain=plain,
        json_payload={
            "suite_id": suite_id,
            "tree_id": contents.tree_id,
            "test_case_ids": contents.test_case_ids,
            "assigned_count": assigned_count,
        },
        output_format=output_format,
    )
