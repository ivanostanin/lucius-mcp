from typing import Any

from fastmcp import FastMCP

from src.client import AllureClient
from src.services.shared_step_service import SharedStepService


async def create_shared_step(
    name: str,
    project_id: int,
    steps: list[dict[str, Any]] | None = None,
) -> str:
    """Create a new reusable Shared Step.

    Args:
        name: The name of the shared step (e.g., "Login as Admin").
        project_id: The ID of the project where the shared step will be created.
        steps: Optional list of steps. Each step is a dictionary with:
               - action (str): The step description (e.g., "Enter username").
               - expected (str, optional): The expected result.
               - attachments (list[dict], optional): List of attachments containing:
                 - content (str): Base64 encoded content.
                 - name (str): Filename.
               - steps (list[dict], optional): Nested steps (recursive structure).
    """
    async with AllureClient.from_env() as client:
        service = SharedStepService(client)
        shared_step = await service.create_shared_step(project_id=project_id, name=name, steps=steps)

        return (
            f"Successfully created Shared Step:\n"
            f"ID: {shared_step.id}\n"
            f"Name: {shared_step.name}\n"
            f"Project ID: {shared_step.project_id}\n"
            f"URL: {client._base_url}/project/{project_id}/settings/shared-steps/{shared_step.id}"
        )


async def list_shared_steps(
    project_id: int,
    page: int = 0,
    size: int = 100,
    search: str | None = None,
    archived: bool = False,
) -> str:
    """List shared steps in a project to find existing ones.

    Args:
        project_id: The ID of the project.
        page: Page number (0-based, default 0).
        size: Number of items per page (default 100).
        search: Optional search query to filter by name.
        archived: Whether to include archived steps (default False).
    """
    async with AllureClient.from_env() as client:
        service = SharedStepService(client)
        steps = await service.list_shared_steps(
            project_id=project_id, page=page, size=size, search=search, archived=archived
        )

        if not steps:
            return f"No shared steps found for project {project_id}."

        output = [f"Found {len(steps)} shared steps for project {project_id}:"]
        for s in steps:
            # Format: [ID: 123] Step Name (X steps)
            count_info = f" ({s.steps_count} steps)" if s.steps_count is not None else ""
            output.append(f"- [ID: {s.id}] {s.name}{count_info}")

        return "\n".join(output)


async def update_shared_step(
    step_id: int,
    name: str | None = None,
    description: str | None = None,
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

    Returns:
        Confirmation message with summary of changes.

    Example:
        update_shared_step(
            step_id=789,
            name="Login as Admin (Updated)"
        )
    """
    async with AllureClient.from_env() as client:
        service = SharedStepService(client)
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
    step_id: int,
    confirm: bool = False,
) -> str:
    """Delete a shared step from the library.

    ⚠️ CAUTION: If this shared step is used by test cases, deleting it
    will break those references.

    Args:
        step_id: The shared step ID to delete (required).
        confirm: Must be True to proceed (safety measure).

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

    async with AllureClient.from_env() as client:
        service = SharedStepService(client)
        await service.delete_shared_step(step_id=step_id)

        return f"🗑️  Archived Shared Step {step_id}\n\nThe shared step has been successfully archived."


def register(mcp: FastMCP) -> None:
    """Register Shared Step tools with the MCP server."""
    mcp.tool()(create_shared_step)
    mcp.tool()(list_shared_steps)
    mcp.tool()(update_shared_step)
    mcp.tool()(delete_shared_step)
