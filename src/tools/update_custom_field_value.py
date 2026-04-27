from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.custom_field_value_service import CustomFieldValueService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output


async def update_custom_field_value(
    cfv_id: Annotated[int, Field(description="Custom field value ID to update.")],
    name: Annotated[str, Field(description="New name for the custom field value.")],
    custom_field_id: Annotated[
        int | None,
        Field(description="Project-scoped custom field ID (optional, resolves by name if missing)."),
    ] = None,
    custom_field_name: Annotated[
        str | None,
        Field(description="Custom field name to resolve when custom_field_id is not provided."),
    ] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    confirm: Annotated[bool, Field(description="Must be set to True to proceed with update. Safety measure.")] = False,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Update an existing custom field value.
    ⚠️ CAUTION: Destructive.

    Args:
        cfv_id: Custom field value ID to update.
        name: New name for the custom field value.
        custom_field_id: Project-scoped custom field ID (optional, resolves by name if missing).
        custom_field_name: Custom field name to resolve when custom_field_id is not provided.
        project_id: Optional Allure TestOps project ID override.
        confirm: Must be set to True to proceed with update.
            This is a safety measure to prevent accidental updates.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Confirmation message indicating whether changes were made.
    """
    if not confirm:
        message = (
            "⚠️ Update requires confirmation.\n\n"
            "Updating a custom field value affects all test cases using it. "
            f"Please call again with confirm=True to proceed with updating custom field value {cfv_id}."
        )
        return render_output(
            plain=message,
            json_payload={
                "requires_confirmation": True,
                "cfv_id": cfv_id,
                "action": "update_custom_field_value",
            },
            output_format=output_format,
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = CustomFieldValueService(client=client)
        await service.update_custom_field_value(
            project_id=project_id,
            cfv_id=cfv_id,
            custom_field_id=custom_field_id,
            custom_field_name=custom_field_name,
            name=name,
        )

        return render_output(
            plain=f"✅ Custom field value {cfv_id} updated successfully!\nNew name: {name}",
            json_payload={
                "id": cfv_id,
                "name": name,
                "custom_field_id": custom_field_id,
                "custom_field_name": custom_field_name,
            },
            output_format=output_format,
        )
