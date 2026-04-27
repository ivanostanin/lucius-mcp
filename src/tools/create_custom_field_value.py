from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.custom_field_value_service import CustomFieldValueService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output


async def create_custom_field_value(
    name: Annotated[str, Field(description="Name for the new custom field value.")],
    custom_field_id: Annotated[
        int | None,
        Field(description="Project-scoped custom field ID to create a value for."),
    ] = None,
    custom_field_name: Annotated[
        str | None,
        Field(description="Custom field name to resolve when custom_field_id is not provided."),
    ] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Create a new custom field value option.

    Args:
        name: Name for the new custom field value.
        custom_field_id: Project-scoped custom field ID to create a value for.
        custom_field_name: Custom field name to resolve when custom_field_id is not provided.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = CustomFieldValueService(client=client)
        created = await service.create_custom_field_value(
            project_id=project_id,
            custom_field_id=custom_field_id,
            custom_field_name=custom_field_name,
            name=name,
        )

        return render_output(
            plain=f"✅ Custom field value created successfully!\nID: {created.id}\nName: {created.name}",
            json_payload={
                "id": created.id,
                "name": created.name,
                "custom_field_id": custom_field_id,
                "custom_field_name": custom_field_name,
            },
            output_format=output_format,
        )
