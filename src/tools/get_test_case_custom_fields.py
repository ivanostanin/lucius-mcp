from typing import Annotated, Any

from pydantic import Field

from src.client import AllureClient
from src.services.test_case_service import TestCaseService


async def get_test_case_custom_fields(
    test_case_id: Annotated[int, Field(description="The ID of the test case to retrieve custom fields for")],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
) -> dict[str, Any]:
    """Retrieve custom field values for a specific test case.

    Args:
        test_case_id: The ID of the test case.
        project_id: Optional project ID override.

    Returns:
        A dictionary where keys are custom field names and values are
        either a single string value or a list of string values.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client=client)
        return await service.get_test_case_custom_fields_values(test_case_id)
