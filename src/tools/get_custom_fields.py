from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_case_service import TestCaseService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, render_output


async def get_custom_fields(
    name: Annotated[
        str | None, Field(description="Optional case-insensitive name filter to search for specific custom fields.")
    ] = None,
    project_id: Annotated[
        int | None, Field(description="Allure TestOps project ID to fetch custom fields from.")
    ] = None,
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """Get available custom fields and their allowed values for the project.

    Use this tool to discover what custom fields are available (e.g., 'Layer', 'Priority')
    and what values are valid for them (e.g., 'UI', 'High'). This is essential before
    creating or updating test cases to ensure you use valid field names and values.

    Args:
        name: Optional name filter to find a specific field (case-insensitive).
        project_id: Optional project ID override.
        output_format: Output format: plain (default) or json.

    Returns:
        A list of custom fields with their required status and allowed values.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client)
        fields = await service.get_custom_fields(name=name)

    if not fields:
        if name:
            return render_output(
                plain=f"No custom fields found matching '{name}'.",
                json_payload={"items": [], "total": 0, "filter_name": name},
                output_format=output_format,
            )
        return render_output(
            plain="No custom fields found for this project.",
            json_payload={"items": [], "total": 0},
            output_format=output_format,
        )

    lines = [f"Found {len(fields)} custom fields:"]
    items: list[dict[str, object]] = []

    for cf in fields:
        field_name = cf["name"]
        required = "required" if cf["required"] else "optional"
        values_list = cf["values"]
        values = ", ".join(values_list) if values_list else "Any text/No allowed values"

        lines.append(f"- {field_name} ({required}): {values}")
        items.append(
            {
                "name": field_name,
                "required": bool(cf["required"]),
                "values": values_list,
            }
        )

    return render_output(
        plain="\n".join(lines),
        json_payload={"items": items, "total": len(items)},
        output_format=output_format,
    )
