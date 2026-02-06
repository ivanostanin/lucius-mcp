from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.custom_field_value_service import CustomFieldValueService


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
) -> str:
    """Update an existing custom field value.

    Args:
        cfv_id: Custom field value ID to update.
        name: New name for the custom field value.
        custom_field_id: Project-scoped custom field ID (optional, resolves by name if missing).
        custom_field_name: Custom field name to resolve when custom_field_id is not provided.
        project_id: Optional override for the default Project ID.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = CustomFieldValueService(client=client)
        await service.update_custom_field_value(
            project_id=project_id,
            cfv_id=cfv_id,
            custom_field_id=custom_field_id,
            custom_field_name=custom_field_name,
            name=name,
        )

        return f"✅ Custom field value {cfv_id} updated successfully!\nNew name: {name}"
