"""Tool for creating Test Cases in Allure TestOps."""

from typing import Any

from src.client import AllureClient
from src.services.test_case_service import TestCaseService
from src.utils.auth import get_auth_context
from src.utils.config import settings


async def create_test_case(
    project_id: int,
    name: str,
    description: str | None = None,
    steps: list[dict[str, Any]] | None = None,
    tags: list[str] | None = None,
    attachments: list[dict[str, str]] | None = None,
    custom_fields: dict[str, str] | None = None,
    api_token: str | None = None,
) -> str:
    """Create a new test case in Allure TestOps.

    Args:
        project_id: The ID of the project.
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
        api_token: Optional API token override. Uses ALLURE_API_TOKEN if not provided.

    Returns:
        A message confirming creation with the ID and Name.

    Raises:
        AuthenticationError: If no API token available from environment or arguments.
    """

    auth_context = get_auth_context(api_token=api_token, project_id=project_id)

    client = AllureClient(
        base_url=settings.ALLURE_ENDPOINT,
        token=auth_context.api_token,
    )

    async with client:
        service = TestCaseService(auth_context, client=client)
        try:
            result = await service.create_test_case(
                project_id=project_id,
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
