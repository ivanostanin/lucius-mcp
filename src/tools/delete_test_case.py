"""Tool for archiving test cases in Allure TestOps."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_case_service import TestCaseService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output


async def delete_test_case(
    test_case_id: Annotated[int, Field(description="The Allure test case ID to archive.")],
    confirm: Annotated[
        bool, Field(description="Must be set to True to proceed with deletion. Safety measure.")
    ] = False,
    project_id: Annotated[int | None, Field(description="Optional Allure TestOps project ID override.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Archive an obsolete test case.
    ⚠️ CAUTION: Destructive.

    This performs a SOFT DELETE (archive). The test case can typically
    be recovered from the Allure UI if needed.

    ⚠️ CAUTION: This action removes the test case from active views.
    Historical data and launch associations may be affected.

    Args:
        test_case_id: The Allure test case ID to archive.
            Found in the URL: /testcase/12345 -> test_case_id=12345
        confirm: Must be set to True to proceed with deletion.
            This is a safety measure to prevent accidental deletions.
        project_id: Optional Allure TestOps project ID override.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Confirmation message with the archived test case details.
    """
    if not confirm:
        message = (
            "⚠️ Deletion requires confirmation.\n\n"
            "Archiving test cases removes them from active views. "
            f"Please call again with confirm=True to proceed with archiving test case {test_case_id}."
        )
        return render_output(
            plain=message,
            json_payload={
                "requires_confirmation": True,
                "test_case_id": test_case_id,
                "action": "delete_test_case",
            },
            output_format=output_format,
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client=client)
        try:
            result = await service.delete_test_case(test_case_id)
        except Exception as e:
            return render_output(
                plain=f"Error archiving test case: {e}",
                json_payload={"test_case_id": test_case_id, "status": "error", "error": str(e)},
                output_format=output_format,
            )

        if result.status == "already_deleted":
            return render_output(
                plain=f"ℹ️ Test Case {test_case_id} was already archived or doesn't exist.",  # noqa: RUF001
                json_payload={"test_case_id": test_case_id, "status": "already_archived"},
                output_format=output_format,
            )

        return render_output(
            plain=f"✅ Archived Test Case {result.test_case_id}: '{result.name}'",
            json_payload={"test_case_id": result.test_case_id, "name": result.name, "status": "archived"},
            output_format=output_format,
        )
