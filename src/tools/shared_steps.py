from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.shared_step_service import SharedStepService


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
) -> str:
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
    """

    async with AllureClient.from_env(project=project_id) as client:
        service = SharedStepService(client=client)
        shared_step = await service.create_shared_step(name=name, steps=steps)

        return (
            f"Successfully created Shared Step:\n"
            f"ID: {shared_step.id}\n"
            f"Name: {shared_step.name}\n"
            f"Project ID: {shared_step.project_id}\n"
            f"URL: {client._base_url}/project/{project_id}/settings/shared-steps/{shared_step.id}"
        )


async def list_shared_steps(
    page: Annotated[int, Field(description="Page number (0-based, default 0).")] = 0,
    size: Annotated[int, Field(description="Number of items per page (default 100).")] = 100,
    search: Annotated[str | None, Field(description="Optional search query to filter by name.")] = None,
    archived: Annotated[bool, Field(description="Whether to include archived steps (default False).")] = False,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
) -> str:
    """List shared steps in a project to find existing ones.

    Args:
        page: Page number (0-based, default 0).
        size: Number of items per page (default 100).
        search: Optional search query to filter by name.
        archived: Whether to include archived steps (default False).
        project_id: Optional override for the default Project ID.
    """

    async with AllureClient.from_env(project=project_id) as client:
        service = SharedStepService(client=client)
        steps = await service.list_shared_steps(page=page, size=size, search=search, archived=archived)

        if not steps:
            return f"No shared steps found for project {project_id}."

        output = [f"Found {len(steps)} shared steps for project {project_id}:"]
        for s in steps:
            # Format: [ID: 123] Step Name (X steps)
            count_info = f" ({s.steps_count} steps)" if s.steps_count is not None else ""
            output.append(f"- [ID: {s.id}] {s.name}{count_info}")

        return "\n".join(output)


async def update_shared_step(
    step_id: Annotated[int, Field(description="The shared step ID to update (required).")],
    name: Annotated[str | None, Field(description="New name for the shared step (optional).")] = None,
    description: Annotated[str | None, Field(description="New description (optional).")] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
) -> str:
    """Update an existing shared step.

    ⚠️ IMPORTANT: Changes propagate to ALL test cases using this shared step.

    Only provided fields will be updated. Omitted fields remain unchanged.
    Repeated calls with the same data are idempotent.

    Args:
        step_id: The shared step ID to update (required).
            Found via list_shared_steps or in the Allure URL.
        name: New name for the shared step (optional).
        description: New description (optional).
        project_id: Optional override for the default Project ID.

    Returns:
        Confirmation message with summary of changes.

    Example:
        update_shared_step(
            step_id=789,
            name="Login as Admin (Updated)"
        )
    """

    async with AllureClient.from_env(project=project_id) as client:
        service = SharedStepService(client=client)
        updated, changed = await service.update_shared_step(step_id=step_id, name=name, description=description)

        if not changed:
            return (
                f"No changes needed for Shared Step {step_id}\n\nThe shared step already matches the requested state."
            )

        msg_parts = [f"✅ Updated Shared Step {step_id}: '{updated.name}'", "\nChanges applied:"]
        if name:
            msg_parts.append(f"- name: '{name}'")
        if description:
            msg_parts.append(f"- description: '{description}'")

        return "\n".join(msg_parts)


async def delete_shared_step(
    step_id: Annotated[int, Field(description="The shared step ID to delete (required).")],
    confirm: Annotated[bool, Field(description="Must be True to proceed (safety measure).")] = False,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
) -> str:
    """Delete a shared step from the library.

    ⚠️ CAUTION: If this shared step is used by test cases, deleting it
    will break those references.

    Args:
        step_id: The shared step ID to delete (required).
        confirm: Must be True to proceed (safety measure).
        project_id: Optional override for the default Project ID.

    Returns:
        Confirmation message.

    Example (safe delete):
        delete_shared_step(step_id=789, confirm=True)
        → "🗑️  Archived Shared Step 789"

    Note:
        This performs a soft delete by archiving the shared step.
    """
    if not confirm:
        return (
            "⚠️ Delete confirmation required\n\n"
            "To delete this shared step, set confirm=True.\n\n"
            "WARNING: Deleting a shared step used by test cases will break those references."
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = SharedStepService(client=client)
        deleted = await service.delete_shared_step(step_id=step_id)

        if deleted:
            return f"✅ Archived Shared Step {step_id}\n\nThe shared step has been successfully archived."
        else:
            return f"ℹ️ Shared Step {step_id} was already archived or doesn't exist."  # noqa: RUF001
