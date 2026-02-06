from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_case_service import TestCaseService, TestCaseUpdate
from src.utils.links import normalize_links


async def update_test_case(  # noqa: C901
    test_case_id: Annotated[int, Field(description="The ID of the test case to update")],
    name: Annotated[str | None, Field(description="New name for the test case")] = None,
    description: Annotated[str | None, Field(description="New description")] = None,
    precondition: Annotated[str | None, Field(description="New precondition")] = None,
    steps: Annotated[
        list[dict[str, object]] | None,
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
    test_layer_name: Annotated[str | None, Field(description="Name of the test layer")] = None,
    workflow_id: Annotated[int | None, Field(description="ID of the workflow")] = None,
    links: Annotated[
        list[dict[str, str]] | None,
        Field(description="New list of external links. Each dict has 'name', 'url', and optional 'type'."),
    ] = None,
    # Issue Linking
    issues: Annotated[
        list[str] | None,
        Field(description="List of issue keys to ADD (e.g. ['PROJ-123'])."),
    ] = None,
    remove_issues: Annotated[
        list[str] | None,
        Field(description="List of issue keys to REMOVE."),
    ] = None,
    clear_issues: Annotated[
        bool | None,
        Field(description="If True, remove ALL issues from the test case."),
    ] = None,
    integration_id: Annotated[
        int | None,
        Field(
            description=(
                "Optional integration ID for issue linking (use list_integrations to find IDs). "
                "Required when multiple integrations exist and adding issues. Mutually exclusive with integration_name."
            )
        ),
    ] = None,
    integration_name: Annotated[
        str | None,
        Field(
            description=(
                "Optional integration name for issue linking (exact case-sensitive match). "
                "Required when multiple integrations exist and adding issues. Mutually exclusive with integration_id."
            )
        ),
    ] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    confirm: Annotated[bool, Field(description="Must be set to True to proceed with update. Safety measure.")] = False,
) -> str:
    """Update an existing test case in Allure TestOps.
    ⚠️ CAUTION: Destructive.

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
        test_layer_name: Name of the test layer.
        workflow_id: ID of the workflow.
        links: New list of external links. Each dict has ``name``, ``url``,
            and optional ``type``.
        issues: List of issue keys to ADD (e.g. ['PROJ-123']).
        remove_issues: List of issue keys to REMOVE.
        clear_issues: If True, remove ALL issues from the test case.
        integration_id: Optional integration ID for issue linking.
        integration_name: Optional integration name for issue linking.
        project_id: Optional override for the default Project ID.
        confirm: Must be set to True to proceed with update.
            This is a safety measure to prevent accidental updates.

    Returns:
        A confirmation message summarizing the update.

    Raises:
        AuthenticationError: If no API token available from environment or
            arguments.
    """
    if not confirm:
        return (
            "⚠️ Update requires confirmation.\n\n"
            "This will modify test case properties and may overwrite existing data. "
            f"Please call again with confirm=True to proceed with updating test case {test_case_id}."
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client=client)
        current_case = await service.get_test_case(test_case_id)
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
            test_layer_name=test_layer_name,
            workflow_id=workflow_id,
            links=links,
            issues=issues,
            remove_issues=remove_issues,
            clear_issues=clear_issues,
            integration_id=integration_id,
            integration_name=integration_name,
        )

        updated_case = await service.update_test_case(test_case_id, update_data)

        # Build confirmation message
        changes: list[str] = []

        if name is not None and name != getattr(current_case, "name", None):
            changes.append(f"name='{updated_case.name}'")
        if description is not None and description != getattr(current_case, "description", None):
            changes.append("description")
        if steps is not None:
            changes.append("steps updated")

        if tags is not None:
            current_tags = current_case.tags if isinstance(current_case.tags, list) else []
            current_tag_names: list[str] = []
            for tag in current_tags:
                tag_name = getattr(tag, "name", None)
                if isinstance(tag_name, str):
                    current_tag_names.append(tag_name)
            current_tag_names.sort()
            new_tag_names = sorted(tags)
            if current_tag_names != new_tag_names:
                changes.append("tags updated")

        if attachments is not None:
            changes.append("attachments updated")
        if custom_fields is not None:
            changes.append("custom fields updated")
        if automated is not None and automated != getattr(current_case, "automated", None):
            changes.append(f"automated={updated_case.automated}")
        if expected_result is not None and expected_result != getattr(current_case, "expected_result", None):
            changes.append("expected result updated")
        if status_id is not None:
            current_status = getattr(current_case, "status", None)
            current_status_id = getattr(current_status, "id", None) if current_status else None
            if status_id != current_status_id:
                changes.append("status updated")
        if test_layer_id is not None or test_layer_name is not None:
            current_test_layer = getattr(current_case, "test_layer", None)
            current_test_layer_id = getattr(current_test_layer, "id", None) if current_test_layer else None

            updated_test_layer = getattr(updated_case, "test_layer", None)
            updated_test_layer_id = getattr(updated_test_layer, "id", None) if updated_test_layer else None

            if updated_test_layer_id != current_test_layer_id:
                changes.append("test layer updated")
        if workflow_id is not None:
            current_workflow = getattr(current_case, "workflow", None)
            current_workflow_id = getattr(current_workflow, "id", None) if current_workflow else None
            if workflow_id != current_workflow_id:
                changes.append("workflow updated")
        if links is not None:
            current_links = current_case.links if isinstance(current_case.links, list) else []
            if normalize_links(current_links) != normalize_links(links):
                changes.append("links updated")

        if issues:
            changes.append(f"added {len(issues)} issues ({', '.join(issues)})")
        if remove_issues:
            changes.append(f"removed {len(remove_issues)} issues ({', '.join(remove_issues)})")
        if clear_issues:
            changes.append("cleared all issues")

        summary = ", ".join(changes) if changes else "No changes made (idempotent)"

        return f"Test Case {updated_case.id} updated successfully. Changes: {summary}"
