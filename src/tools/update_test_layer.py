"""Tool for updating a test layer."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService


async def update_test_layer(
    layer_id: Annotated[int, Field(description="ID of the test layer to update.")],
    name: Annotated[str, Field(description="New name for the test layer.")],
    project_id: Annotated[int | None, Field(description="Allure TestOps project ID.")] = None,
) -> str:
    """Update an existing test layer's name.

    Args:
        layer_id: ID of the test layer to update
        name: New name for the test layer
        project_id: Optional project ID override

    Returns:
        Confirmation message indicating whether changes were made
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestLayerService(client)
        updated, changed = await service.update_test_layer(layer_id=layer_id, name=name)

    if changed:
        return f"✅ Test layer {layer_id} updated successfully! New name: {updated.name}"
    else:
        return f"[INFO] Test layer {layer_id} already has name '{name}' - no changes made."
