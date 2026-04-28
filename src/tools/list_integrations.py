"""Tool for listing available integrations in Allure TestOps."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.integration_service import IntegrationService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output


async def list_integrations(
    project_id: Annotated[
        int | None,
        Field(
            description=(
                "Optional override for the default Project ID. "
                "When provided (or from environment default), integrations are filtered "
                "to those available for that project."
            )
        ),
    ] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """List available integrations (issue trackers) in Allure TestOps.

    Use this tool to discover which integrations (Jira, GitHub, etc.) are
    configured and available for linking issues to test cases.

    Args:
        project_id: Optional override for the default Project ID.
            When provided (or from environment default), integrations are filtered
            to those available for that project.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        A formatted list of available integrations with their IDs and names.
        If no integrations are configured, returns an informative message.

    Examples:
        >>> list_integrations()
        "📋 Available Integrations (3 found):
         • Github Integration (ID: 1) [github]
         • Noxtua Jira Integration (ID: 2) [jira]
         • TestOps TMS (ID: 3) [tms]

         Hint: Use 'integration_id' or 'integration_name' when creating/updating
         test cases with issues to specify which integration to use."
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = IntegrationService(client)
        integrations = await service.list_integrations(project_id=client.get_project())

        if not integrations:
            plain_output = (
                "📋 No integrations configured.\n\n"
                "Integrations connect Allure TestOps to external issue trackers "
                "(Jira, GitHub, etc.). Contact your Allure admin to configure integrations."
            )
            return render_output(
                plain=plain_output,
                json_payload={"items": [], "total": 0},
                output_format=output_format,
            )

        # Format output
        lines: list[str] = [f"📋 **Available Integrations** ({len(integrations)} found):\n"]
        items: list[dict[str, object]] = []

        for integration in integrations:
            name = integration.name or "(unnamed)"
            int_id = integration.id or "N/A"
            info_type = ""
            if integration.info and hasattr(integration.info, "type") and integration.info.type:
                # Handle enum or string; since IntegrationTypeDto is (str, Enum), .value works or its just the str
                info_type = getattr(integration.info.type, "value", str(integration.info.type))
                info_type = f" [{info_type.lower()}]"
            lines.append(f"• **{name}** (ID: {int_id}){info_type}")
            items.append(
                {
                    "id": integration.id,
                    "name": name,
                    "type": info_type.strip(" []") if info_type else None,
                }
            )

        lines.append("")
        lines.append(
            "**Hint:** Use `integration_id` or `integration_name` when creating/updating "
            "test cases with issues to specify which integration to use."
        )

        return render_output(
            plain="\n".join(lines),
            json_payload={"items": items, "total": len(items)},
            output_format=output_format,
        )
