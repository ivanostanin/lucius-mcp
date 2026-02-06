"""Tool for deleting a test layer schema."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService


async def delete_test_layer_schema(
    schema_id: Annotated[int, Field(description="ID of the test layer schema to delete.")],
    project_id: Annotated[int | None, Field(description="Allure TestOps project ID.")] = None,
    confirm: Annotated[
        bool, Field(description="Must be set to True to proceed with deletion. Safety measure.")
    ] = False,
) -> str:
    """Delete a test layer schema from the project.
    ⚠️ CAUTION: Destructive.

    Args:
        schema_id: ID of the schema to delete.
        project_id: Optional Allure TestOps project ID override.
        confirm: Must be set to True to proceed with deletion.
            This is a safety measure to prevent accidental deletions.

    Returns:
        Confirmation message.
    """
    if not confirm:
        return (
            "⚠️ Deletion requires confirmation.\n\n"
            "Deleting a schema removes the mapping between custom fields and layers. "
            f"Please call again with confirm=True to proceed with deleting test layer schema {schema_id}."
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = TestLayerService(client)
        deleted = await service.delete_test_layer_schema(schema_id=schema_id)

    if deleted:
        return f"✅ Test layer schema {schema_id} deleted successfully!"
    else:
        return f"ℹ️ Test layer schema {schema_id} was already deleted or doesn't exist."  # noqa RUF001
