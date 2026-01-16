"""Tool for archiving test cases in Allure TestOps."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_case_service import TestCaseService


async def delete_test_case(
    test_case_id: Annotated[int, Field(description="The Allure test case ID to archive.")],
    confirm: Annotated[
        bool, Field(description="Must be set to True to proceed with deletion. Safety measure.")
    ] = False,
) -> str:
    """Archive an obsolete test case.

    This performs a SOFT DELETE (archive). The test case can typically
    be recovered from the Allure UI if needed.

    ⚠️ CAUTION: This action removes the test case from active views.
    Historical data and launch associations may be affected.

    Args:
        test_case_id: The Allure test case ID to archive (required).
            Found in the URL: /testcase/12345 -> test_case_id=12345
        confirm: Must be set to True to proceed with deletion.
            This is a safety measure to prevent accidental deletions.

    Returns:
        Confirmation message with the archived test case details.
    """
    if not confirm:
        return (
            "⚠️ Deletion requires confirmation.\n\n"
            "Please call again with confirm=True to proceed with archiving "
            f"test case {test_case_id}."
        )

    async with AllureClient.from_env() as client:
        service = TestCaseService(client)
        try:
            result = await service.delete_test_case(test_case_id)
        except Exception as e:
            return f"Error archiving test case: {e}"

        if result.status == "already_deleted":
            return f"ℹ️ Test Case {test_case_id} was already archived or doesn't exist."  # noqa: RUF001

        return f"✅ Archived Test Case {result.test_case_id}: '{result.name}'"
