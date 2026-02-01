from typing import Annotated, Any

from pydantic import Field

from src.client import AllureClient
from src.services.test_case_service import TestCaseService, TestCaseUpdate


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
        dict[str, str | list[str]] | None,
        Field(description="Dictionary of custom fields to update (Name -> Value or list of values)"),
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
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
) -> str:
    """Update an existing test case in Allure TestOps.

    Performs a partial update: only supplied fields are sent to the API. When
    provided, ``steps`` replace all existing steps, and ``attachments`` replace
    all existing global attachments. Omit a field to preserve its current value.

    Args:
        test_case_id: The ID of the test case to update.
        name: New name for the test case.
        description: New description for the test case.
        precondition: New precondition text.
        steps: New list of steps. Each step is a dict with ``action``,
            ``expected``, and optional ``attachments`` list.
        tags: New list of tags.
        attachments: New list of global attachments. Each dict has ``name`` and
            either ``content`` (base64) or ``url``.
        custom_fields: Custom field updates as a name-to-value (or list of values) mapping.
        automated: Whether the test case is automated.
        expected_result: Global expected result for the test case.
        status_id: ID of the test case status.
        test_layer_id: ID of the test layer.
        workflow_id: ID of the workflow.
        links: New list of external links. Each dict has ``name``, ``url``,
            and optional ``type``.
        project_id: Optional override for the default Project ID.

    Returns:
        A confirmation message summarizing the update.

    Raises:
        AuthenticationError: If no API token available from environment or
            arguments.
    """

    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client=client)
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
