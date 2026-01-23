from typing import Annotated, Any

from pydantic import Field

from src.client import AllureClient
from src.services.test_case_service import TestCaseService, TestCaseUpdate
from src.utils.auth import get_auth_context
from src.utils.config import settings


async def update_test_case(  # noqa: C901
    test_case_id: Annotated[int, Field(description="The ID of the test case to update")],
    name: Annotated[str | None, Field(description="New name for the test case")] = None,
    description: Annotated[str | None, Field(description="New description")] = None,
    precondition: Annotated[str | None, Field(description="New precondition")] = None,
    steps: Annotated[
        list[dict[str, Any]] | None,
        Field(
            description=(
                "New list of steps. Each step is a dict with 'action', 'expected', and optional 'attachments' list."
            )
        ),
    ] = None,
    tags: Annotated[list[str] | None, Field(description="New list of tags")] = None,
    attachments: Annotated[
        list[dict[str, str]] | None,
        Field(description="New list of global attachments. Each dict has 'name' and 'content' (base64) or 'url'."),
    ] = None,
    custom_fields: Annotated[
        dict[str, str] | None,
        Field(description="Dictionary of custom fields to update (Name -> Value)"),
    ] = None,
    automated: Annotated[bool | None, Field(description="Set whether the test case is automated")] = None,
    expected_result: Annotated[str | None, Field(description="Global expected result for the test case")] = None,
    status_id: Annotated[int | None, Field(description="ID of the test case status")] = None,
    test_layer_id: Annotated[int | None, Field(description="ID of the test layer")] = None,
    workflow_id: Annotated[int | None, Field(description="ID of the workflow")] = None,
    links: Annotated[
        list[dict[str, str]] | None,
        Field(description="New list of external links. Each dict has 'name', 'url', and optional 'type'."),
    ] = None,
    api_token: Annotated[str | None, Field(description="Optional API token override.")] = None,
) -> str:
    """Update an existing test case in Allure TestOps.

    This tool allows partial updates. Only fields that are provided will be updated.
    If 'steps' are provided, they replace all existing steps.
    If 'attachments' are provided, they replace all existing global attachments.
    To preserve existing steps or attachments while updating the other, omit the field you want to preserve.

    Args:
        api_token: Optional override for the default API token.

    Raises:
        AuthenticationError: If no API token available from environment or arguments.
    """
    auth_context = get_auth_context(api_token=api_token)

    client = AllureClient(
        base_url=settings.ALLURE_ENDPOINT,
        token=auth_context.api_token,
    )

    async with client:
        service = TestCaseService(auth_context, client=client)
        update_data = TestCaseUpdate(
            name=name,
            description=description,
            precondition=precondition,
            steps=steps,
            tags=tags,
            attachments=attachments,
            custom_fields=custom_fields,
            automated=automated,
            expected_result=expected_result,
            status_id=status_id,
            test_layer_id=test_layer_id,
            workflow_id=workflow_id,
            links=links,
        )

        updated_case = await service.update_test_case(test_case_id, update_data)

        # Build confirmation message
        changes = []
        if name:
            changes.append(f"name='{updated_case.name}'")
        if description:
            changes.append("description")
        if steps:
            changes.append("steps updated")
        if tags:
            changes.append("tags updated")
        if attachments:
            changes.append("attachments updated")
        if custom_fields:
            changes.append("custom fields updated")
        if automated is not None:
            changes.append(f"automated={updated_case.automated}")
        if expected_result:
            changes.append("expected result updated")
        if status_id:
            changes.append("status updated")
        if test_layer_id:
            changes.append("test layer updated")
        if workflow_id:
            changes.append("workflow updated")
        if links:
            changes.append("links updated")

        summary = ", ".join(changes) if changes else "No changes made (idempotent)"

        return f"Test Case {updated_case.id} updated successfully. Changes: {summary}"
