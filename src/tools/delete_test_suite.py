"""Tool for deleting hierarchy test suites in Allure TestOps."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_hierarchy_service import TestHierarchyService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, render_output


async def delete_test_suite(
    suite_id: Annotated[int, Field(description="Suite/group node ID to delete from hierarchy.")],
    confirm: Annotated[
        bool,
        Field(description="Must be set to True to proceed with deletion. Safety measure."),
    ] = False,
    project_id: Annotated[int | None, Field(description="Optional Allure TestOps project ID override.")] = None,
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """Delete a test suite node from hierarchy.
    ⚠️ CAUTION: Destructive.

    This operation removes a hierarchy suite/group node. Allure TestOps handles
    nested entities according to its API behavior for tree groups.

    Args:
        suite_id: Existing suite (tree node) ID to delete.
        confirm: Must be set to True to proceed.
            This safety flag prevents accidental destructive actions.
        project_id: Optional Allure TestOps project override.
        output_format: Output format: plain (default) or json.

    Returns:
        A confirmation or safety warning message.

    Example:
        delete_test_suite(suite_id=12345, confirm=True)
        -> "✅ Test suite 12345 deleted successfully (idempotent)."
    """
    if not confirm:
        return render_output(
            plain=f"⚠️ Destructive operation. Confirm deletion of suite {suite_id} by passing confirm=True.",
            json_payload={
                "requires_confirmation": True,
                "suite_id": suite_id,
                "action": "delete_test_suite",
            },
            output_format=output_format,
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = TestHierarchyService(client)
        await service.delete_suite(suite_id=suite_id)

    return render_output(
        plain=f"✅ Test suite {suite_id} deleted successfully (idempotent).",
        json_payload={"suite_id": suite_id, "status": "deleted"},
        output_format=output_format,
    )
