"""Tool for creating Test Cases in Allure TestOps."""

from typing import Any

from src.client import AllureClient
from src.services.test_case_service import TestCaseService


async def create_test_case(
    name: str,
    description: str | None = None,
    steps: list[dict[str, Any]] | None = None,
    tags: list[str] | None = None,
    attachments: list[dict[str, str]] | None = None,
    custom_fields: dict[str, str] | None = None,
    project_id: int | None = None,
) -> str:
    """Create a new test case in Allure TestOps.

    Args:
        name: The name of the test case.
        description: A markdown description of the test case.
        steps: List of steps. Each step must be a dict with 'action' and 'expected' keys.
               Example: [{'action': 'Login', 'expected': 'Dashboard visible'}]
        tags: List of tag names.
        attachments: List of attachments.
                     Example Base64: [{'name': 's.png', 'content': '<base64>', 'content_type': 'image/png'}]
                     Example URL: [{'name': 'report.pdf', 'url': 'http://example.com/report.pdf',
                                    'content_type': 'application/pdf'}]
        custom_fields: Dictionary of custom field names and their values.
                       Example: {'Layer': 'UI', 'Component': 'Auth'}
        project_id: Optional override for the default Project ID.

    Returns:
        A message confirming creation with the ID and Name.

    Raises:
        AuthenticationError: If no API token available from environment or arguments.
    """

    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client=client)
        try:
            result = await service.create_test_case(
                name=name,
                description=description,
                steps=steps,
                tags=tags,
                attachments=attachments,
                custom_fields=custom_fields,
            )
            return f"Created Test Case ID: {result.id} Name: {result.name}"
        except Exception as e:
            return f"Error creating test case: {e}"
