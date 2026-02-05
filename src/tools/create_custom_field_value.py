from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.custom_field_value_service import CustomFieldValueService


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
) -> str:
    """Create a new custom field value option.

    Args:
        name: Name for the new custom field value.
        custom_field_id: Project-scoped custom field ID to create a value for.
        custom_field_name: Custom field name to resolve when custom_field_id is not provided.
        project_id: Optional override for the default Project ID.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = CustomFieldValueService(client=client)
        created = await service.create_custom_field_value(
            project_id=project_id,
            custom_field_id=custom_field_id,
            custom_field_name=custom_field_name,
            name=name,
        )

        return f"✅ Custom field value created successfully!\nID: {created.id}\nName: {created.name}"
