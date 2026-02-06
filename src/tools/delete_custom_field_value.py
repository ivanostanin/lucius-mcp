from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.custom_field_value_service import CustomFieldValueService


async def delete_custom_field_value(
    cfv_id: Annotated[int, Field(description="Custom field value ID to delete.")],
    custom_field_id: Annotated[
        int | None,
        Field(description="Project-scoped custom field ID (optional, resolves by name if missing)."),
    ] = None,
    custom_field_name: Annotated[
        str | None,
        Field(description="Custom field name to resolve when custom_field_id is not provided."),
    ] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    confirm: Annotated[
        bool, Field(description="Must be set to True to proceed with deletion. Safety measure.")
    ] = False,
) -> str:
    """Delete a custom field value.
    ⚠️ CAUTION: Destructive.

    Args:
        cfv_id: Custom field value ID to delete.
        custom_field_id: Project-scoped custom field ID (optional, resolves by name if missing).
        custom_field_name: Custom field name to resolve when custom_field_id is not provided.
        project_id: Optional Allure TestOps project ID override.
        confirm: Must be set to True to proceed with deletion.
            This is a safety measure to prevent accidental deletions.

    Returns:
        Confirmation message.
    """
    if not confirm:
        return (
            "⚠️ Deletion requires confirmation.\n\n"
            "Deleting a custom field value may fail if it is currently in use. "
            f"Please call again with confirm=True to proceed with deleting custom field value {cfv_id}."
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = CustomFieldValueService(client=client)
        deleted = await service.delete_custom_field_value(
            project_id=project_id,
            cfv_id=cfv_id,
            custom_field_id=custom_field_id,
            custom_field_name=custom_field_name,
        )

        if deleted:
            return f"✅ Custom field value {cfv_id} deleted successfully!"

        return f"[INFO] Custom field value {cfv_id} was already removed."
