"""MCP tool for discovering Allure TestOps projects."""

from typing import Annotated

from src.client import AllureClient
from src.services.project_service import ProjectService
from src.tools.output_contract import (
    DEFAULT_OUTPUT_FORMAT,
    OutputFormat,
    ToolOutput,
    render_collection_output,
    render_output,
)
from src.tools.output_schemas import output_fields


@output_fields("id", "name", "description", "abbr", "is_public", "items", "total")
async def get_project(
    name: Annotated[
        str | None,
        "Project name to resolve. Omit it to list all projects available to the authenticated user.",
    ] = None,
    output_format: Annotated[
        OutputFormat | None,
        "Output format: 'json' (default) or 'plain'.",
    ] = DEFAULT_OUTPUT_FORMAT,
) -> ToolOutput:
    """Retrieve one project by name or list accessible projects.

    Name matching is case-insensitive. An exact match is preferred; an
    unambiguous partial match is accepted. Omit ``name`` to discover the
    available project IDs and names before making project-scoped calls.

    Args:
        name: Exact or unique partial project name. Omit to list projects.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        A project record with its ID and details, or a concise list of project
        IDs and names when no name is supplied.
    """
    async with AllureClient.from_env(require_project=False) as client:
        service = ProjectService(client)
        if name is None:
            projects = await service.list_projects()
            items = [{"id": project.id, "name": project.name} for project in projects]
            return render_collection_output(
                items=items,
                total=len(items),
                plain_empty="No projects are available to the authenticated user.",
                plain_lines=[
                    f"Available Projects ({len(items)} found):",
                    *[f"- {item['name'] or '(unnamed)'} (ID: {item['id']})" for item in items],
                ],
                output_format=output_format,
            )

        project = await service.get_project_by_name(name)
        lines = [f"Project #{project.id}: {project.name or '(unnamed)'}"]
        if project.description:
            lines.append(f"Description: {project.description}")
        if project.abbr:
            lines.append(f"Abbreviation: {project.abbr}")
        if project.is_public is not None:
            lines.append(f"Public: {'yes' if project.is_public else 'no'}")
        return render_output(
            plain="\n".join(lines),
            json_payload={
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "abbr": project.abbr,
                "is_public": project.is_public,
            },
            output_format=output_format,
        )
