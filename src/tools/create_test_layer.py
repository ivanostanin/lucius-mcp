"""Tool for creating a test layer."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService


async def create_test_layer(
    name: Annotated[str, Field(description="Name of the test layer (e.g., 'Unit', 'Integration', 'E2E').")],
    project_id: Annotated[
        int | None, Field(description="Allure TestOps project ID to create the test layer in.")
    ] = None,
) -> str:
    """Create a new test layer in Allure TestOps.

    Test layers define taxonomy for categorizing test cases. Common examples include
    'Unit', 'Integration', 'E2E', 'UI', 'API', etc.

    Args:
        name: Name of the test layer
        project_id: Optional project ID override

    Returns:
        Confirmation message with the created layer's ID and name
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestLayerService(client)
        layer = await service.create_test_layer(name=name)

    return f"✅ Test layer created successfully! ID: {layer.id}, Name: {layer.name}"
