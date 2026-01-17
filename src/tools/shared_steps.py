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


def register(mcp: FastMCP) -> None:
    """Register Shared Step tools with the MCP server."""
    mcp.tool()(create_shared_step)
    mcp.tool()(list_shared_steps)
