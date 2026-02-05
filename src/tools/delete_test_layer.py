"""Tool for deleting a test layer."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService


async def delete_test_layer(
    layer_id: Annotated[int, Field(description="ID of the test layer to delete.")],
    project_id: Annotated[int | None, Field(description="Allure TestOps project ID.")] = None,
) -> str:
    """Delete a test layer from Allure TestOps.

    Args:
        layer_id: ID of the test layer to delete
        project_id: Optional project ID override

    Returns:
        Confirmation message
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestLayerService(client)
        deleted = await service.delete_test_layer(layer_id=layer_id)

    if deleted:
        return f"✅ Test layer {layer_id} deleted successfully!"
    else:
        return f"ℹ️ Test layer {layer_id} was already deleted or doesn't exist."  # noqa: RUF001
