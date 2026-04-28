from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.shared_step_service import SharedStepService
from src.tools.output_contract import (
    DEFAULT_OUTPUT_FORMAT,
    OutputFormat,
    ToolOutput,
    render_collection_output,
    render_confirmation_required,
    render_output,
)


async def create_shared_step(
    name: Annotated[str, Field(description='The name of the shared step (e.g., "Login as Admin").')],
    steps: Annotated[
        list[dict[str, object]] | None,
        Field(
            description="Optional list of steps. Each step is a dictionary with:"
            ' - action (str): The step description (e.g., "Enter username").'
            " - expected (str, optional): The expected result."
            " - attachments (list[dict], optional): List of attachments containing:"
            "   - content (str): Base64 encoded content."
            "   - name (str): Filename."
            " - steps (list[dict], optional): Nested steps (recursive structure)."
        ),
    ] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Create a new reusable Shared Step.

    Args:
        name: The name of the shared step (e.g., "Login as Admin").
        steps: Optional list of steps. Each step is a dictionary with:
               - action (str): The step description (e.g., "Enter username").
               - expected (str, optional): The expected result.
               - attachments (list[dict], optional): List of attachments containing:
                 - content (str): Base64 encoded content.
                 - name (str): Filename.
               - steps (list[dict], optional): Nested steps (recursive structure).
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.
    """

    async with AllureClient.from_env(project=project_id) as client:
        service = SharedStepService(client=client)
        shared_step = await service.create_shared_step(name=name, steps=steps)
        if shared_step.id is None:
            raise ValueError("Created shared step is missing an ID")
        shared_step_url = _shared_step_url(client, shared_step.id)

        plain_output = (
            f"Successfully created Shared Step:\n"
            f"ID: {shared_step.id}\n"
            f"Name: {shared_step.name}\n"
            f"Project ID: {shared_step.project_id}\n"
            f"URL: {shared_step_url}"
        )
        return render_output(
            plain=plain_output,
            json_payload={
                "id": shared_step.id,
                "name": shared_step.name,
                "project_id": shared_step.project_id,
                "url": shared_step_url,
            },
            output_format=output_format,
        )


async def list_shared_steps(
    page: Annotated[int, Field(description="Page number (0-based, default 0).")] = 0,
    size: Annotated[int, Field(description="Number of items per page (default 100).")] = 100,
    search: Annotated[str | None, Field(description="Optional search query to filter by name.")] = None,
    archived: Annotated[bool, Field(description="Whether to include archived steps (default False).")] = False,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """List shared steps in a project to find existing ones.

    Args:
        page: Page number (0-based, default 0).
        size: Number of items per page (default 100).
        search: Optional search query to filter by name.
        archived: Whether to include archived steps (default False).
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.
    """

    async with AllureClient.from_env(project=project_id) as client:
        service = SharedStepService(client=client)
        steps = await service.list_shared_steps(page=page, size=size, search=search, archived=archived)
        resolved_project_id = client.get_project()
        payload_items = [
            {
                "id": s.id,
                "name": s.name,
                "steps_count": s.steps_count,
            }
            for s in steps
        ]
        output = [f"Found {len(steps)} shared steps for project {resolved_project_id}:"]
        for s in steps:
            # Format: [ID: 123] Step Name (X steps)
            count_info = f" ({s.steps_count} steps)" if s.steps_count is not None else ""
            output.append(f"- [ID: {s.id}] {s.name}{count_info}")
        return render_collection_output(
            items=payload_items,
            plain_empty=f"No shared steps found for project {resolved_project_id}.",
            plain_lines=output,
            page=page,
            size=size,
            output_format=output_format,
        )


async def update_shared_step(
    step_id: Annotated[int, Field(description="The shared step ID to update (required).")],
    name: Annotated[str | None, Field(description="New name for the shared step (optional).")] = None,
    description: Annotated[str | None, Field(description="New description (optional).")] = None,
    confirm: Annotated[bool, Field(description="Must be set to True to proceed with update. Safety measure.")] = False,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Update an existing shared step.
    ⚠️ CAUTION: Destructive.

    ⚠️ IMPORTANT: Changes propagate to ALL test cases using this shared step.

    Only provided fields will be updated. Omitted fields remain unchanged.
    Repeated calls with the same data are idempotent.

    Args:
        step_id: The shared step ID to update (required).
            Found via list_shared_steps or in the Allure URL.
        name: New name for the shared step (optional).
        description: New description (optional).
        confirm: Must be set to True to proceed with update.
            This is a safety measure to prevent accidental updates.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Confirmation message with summary of changes.

    Example:
        update_shared_step(
            step_id=789,
            name="Login as Admin (Updated)",
            confirm=True
        )
    """
    if not confirm:
        return render_confirmation_required(
            action="update_shared_step",
            plain=(
                "⚠️ Update requires confirmation.\n\n"
                "Changes propagate to ALL test cases using this shared step. "
                f"Please call again with confirm=True to proceed with updating shared step {step_id}."
            ),
            step_id=step_id,
            output_format=output_format,
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = SharedStepService(client=client)
        updated, changed = await service.update_shared_step(step_id=step_id, name=name, description=description)

        if not changed:
            return render_output(
                plain=f"No changes needed for Shared Step {step_id}\n\n"
                "The shared step already matches the requested state.",
                json_payload={
                    "id": step_id,
                    "changed": False,
                    "name": getattr(updated, "name", None),
                },
                output_format=output_format,
            )

        msg_parts = [f"✅ Updated Shared Step {step_id}: '{updated.name}'", "\nChanges applied:"]
        if name:
            msg_parts.append(f"- name: '{name}'")
        if description:
            msg_parts.append(f"- description: '{description}'")

        return render_output(
            plain="\n".join(msg_parts),
            json_payload={
                "id": step_id,
                "name": updated.name,
                "changed": True,
                "updated_fields": [field for field, value in (("name", name), ("description", description)) if value],
            },
            output_format=output_format,
        )


async def delete_shared_step(
    step_id: Annotated[int, Field(description="The shared step ID to delete (required).")],
    confirm: Annotated[bool, Field(description="Must be True to proceed (safety measure).")] = False,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Delete a shared step from the library.
    ⚠️ CAUTION: Destructive.

    ⚠️ CAUTION: If this shared step is used by test cases, deleting it
    will break those references.

    Args:
        step_id: The shared step ID to delete (required).
        confirm: Must be True to proceed (safety measure).
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Confirmation message.

    Example (safe delete):
        delete_shared_step(step_id=789, confirm=True)
        → "🗑️  Archived Shared Step 789"

    Note:
        This performs a soft delete by archiving the shared step.
    """
    if not confirm:
        return render_confirmation_required(
            action="delete_shared_step",
            plain=(
                "⚠️ Deletion requires confirmation.\n\n"
                "Deleting a shared step used by test cases will be breaking those references. "
                f"Please call again with confirm=True to proceed with archiving shared step {step_id}."
            ),
            step_id=step_id,
            output_format=output_format,
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = SharedStepService(client=client)
        deleted = await service.delete_shared_step(step_id=step_id)

        if deleted:
            return render_output(
                plain=f"✅ Archived Shared Step {step_id}\n\nThe shared step has been successfully archived.",
                json_payload={"id": step_id, "status": "archived"},
                output_format=output_format,
            )
        return render_output(
            plain=f"ℹ️ Shared Step {step_id} was already archived or doesn't exist.",  # noqa: RUF001
            json_payload={"id": step_id, "status": "already_archived"},
            output_format=output_format,
        )


def _shared_step_url(client: AllureClient, step_id: int) -> str:
    return f"{client.get_base_url()}/project/{client.get_project()}/settings/shared-steps/{step_id}"
