"""Tool for creating Test Cases in Allure TestOps."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_case_service import TestCaseService


async def create_test_case(
    name: Annotated[str, Field(description="The name of the test case.")],
    description: Annotated[str | None, Field(description="A markdown description of the test case.")] = None,
    steps: Annotated[
        list[dict[str, object]] | None,
        Field(
            description="List of steps. Each step must be a dict with 'action' and 'expected' keys. "
            "Example: [{'action': 'Login', 'expected': 'Dashboard visible'}]"
        ),
    ] = None,
    tags: Annotated[list[str] | None, Field(description="List of tag names.")] = None,
    attachments: Annotated[
        list[dict[str, str]] | None,
        Field(
            description="List of attachments."
            "Example Base64: [{'name': 's.png', 'content': '<base64>', 'content_type': 'image/png'}]"
            "Example URL: [{'name': 'report.pdf', 'url': 'http://example.com/report.pdf', "
            "'content_type': 'application/pdf'}]"
        ),
    ] = None,
    custom_fields: Annotated[
        dict[str, str | list[str]] | None,
        Field(
            description="Dictionary of custom field names and their values (string or list of strings)."
            "Example: {'Layer': 'UI', 'Components': ['Auth', 'DB']}"
        ),
    ] = None,
    test_layer_id: Annotated[
        int | None,
        Field(
            description=(
                "Optional test layer ID to assign (use list_test_layers to find IDs). "
                "If provided, the layer must exist in the project."
            )
        ),
    ] = None,
    test_layer_name: Annotated[
        str | None,
        Field(
            description=(
                "Optional test layer name to assign (exact case-sensitive match). "
                "Mutually exclusive with test_layer_id."
            )
        ),
    ] = None,
    issues: Annotated[
        list[str] | None,
        Field(description="Optional list of issue keys to link (e.g., ['PROJ-123'])."),
    ] = None,
    integration_id: Annotated[
        int | None,
        Field(
            description=(
                "Optional integration ID for issue linking (use list_integrations to find IDs). "
                "Required when multiple integrations exist. Mutually exclusive with integration_name."
            )
        ),
    ] = None,
    integration_name: Annotated[
        str | None,
        Field(
            description=(
                "Optional integration name for issue linking (exact case-sensitive match). "
                "Required when multiple integrations exist. Mutually exclusive with integration_id."
            )
        ),
    ] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
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
        custom_fields: Dictionary of custom field names and their values (string or list of strings).
                       Example: {'Layer': 'UI', 'Components': ['Auth', 'DB']}
        test_layer_name: Optional test layer name to assign (exact case-sensitive match).
        issues: Optional list of issue keys to link (e.g., ['PROJ-123']).
        integration_id: Optional integration ID for issue linking (required when multiple integrations exist).
        integration_name: Optional integration name for issue linking (mutually exclusive with integration_id).
        project_id: Optional override for the default Project ID.

    Returns:
        A message confirming creation with the ID and Name.

    Raises:
        AuthenticationError: If no API token available from environment or arguments.
    """

    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client=client)
        result = await service.create_test_case(
            name=name,
            description=description,
            steps=steps,
            tags=tags,
            attachments=attachments,
            custom_fields=custom_fields,
            test_layer_id=test_layer_id,
            test_layer_name=test_layer_name,
            issues=issues,
            integration_id=integration_id,
            integration_name=integration_name,
        )
        msg = f"Created Test Case ID: {result.id} Name: {result.name}"
        if issues:
            msg += f" with {len(issues)} linked issues: {', '.join(issues)}"
        return msg
