"""Tool for creating a test layer."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, render_output


async def create_test_layer(
    name: Annotated[str, Field(description="Name of the test layer (e.g., 'Unit', 'Integration', 'E2E').")],
    project_id: Annotated[
        int | None, Field(description="Allure TestOps project ID to create the test layer in.")
    ] = None,
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """Create a new test layer in Allure TestOps.

    Test layers define taxonomy for categorizing test cases. Common examples include
    'Unit', 'Integration', 'E2E', 'UI', 'API', etc.

    Args:
        name: Name of the test layer
        project_id: Optional project ID override
        output_format: Output format: plain (default) or json.

    Returns:
        Confirmation message with the created layer's ID and name
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestLayerService(client)
        layer = await service.create_test_layer(name=name)

    return render_output(
        plain=f"✅ Test layer created successfully! ID: {layer.id}, Name: {layer.name}",
        json_payload={"id": layer.id, "name": layer.name},
        output_format=output_format,
    )
