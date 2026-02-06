"""Tool for updating a test layer schema."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService


async def update_test_layer_schema(
    schema_id: Annotated[int, Field(description="ID of the test layer schema to update.")],
    test_layer_id: Annotated[int | None, Field(description="New test layer ID to link to.")] = None,
    key: Annotated[str | None, Field(description="New schema key.")] = None,
    project_id: Annotated[int | None, Field(description="Allure TestOps project ID.")] = None,
    confirm: Annotated[bool, Field(description="Must be set to True to proceed with update. Safety measure.")] = False,
) -> str:
    """Update an existing test layer schema.
    ⚠️ CAUTION: Destructive.

    Args:
        schema_id: ID of the schema to update.
        test_layer_id: Optional new test layer ID to link to.
        key: Optional new schema key.
        project_id: Optional Allure TestOps project ID override.
        confirm: Must be set to True to proceed with update.
            This is a safety measure to prevent accidental updates.

    Returns:
        Confirmation message indicating whether changes were made.
    """
    if not confirm:
        return (
            "⚠️ Update requires confirmation.\n\n"
            "Modifying a schema affects how test layers are automatically assigned. "
            f"Please call again with confirm=True to proceed with updating test layer schema {schema_id}."
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = TestLayerService(client)
        updated, changed = await service.update_test_layer_schema(
            schema_id=schema_id,
            test_layer_id=test_layer_id,
            key=key,
        )

    if changed:
        test_layer_name = updated.test_layer.name if updated.test_layer else "N/A"
        return f"✅ Test layer schema {schema_id} updated successfully! Key: {updated.key}, Layer: {test_layer_name}"
    else:
        return f"[INFO] Test layer schema {schema_id} already has the requested values - no changes made."
