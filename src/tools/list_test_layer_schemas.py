"""Tool for listing test layer schemas."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService


async def list_test_layer_schemas(
    project_id: Annotated[
        int | None, Field(description="Allure TestOps project ID to fetch test layer schemas from.")
    ] = None,
    page: Annotated[int, Field(description="Page number (0-based). Default is 0.")] = 0,
    size: Annotated[int, Field(description="Page size (max 100). Default is 100.")] = 100,
) -> str:
    """List test layer schemas for a project.

    Test layer schemas map custom field keys to test layers within a project.
    They determine which test layer is assigned when a specific custom field value is used.

    Args:
        project_id: Optional project ID override
        page: Page number (0-based)
        size: Page size (max 100)

    Returns:
        List of test layer schemas with their IDs, keys, and linked test layers
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestLayerService(client)
        schemas = await service.list_test_layer_schemas(project_id=project_id, page=page, size=size)

    if not schemas:
        return "No test layer schemas found."

    lines = [f"Found {len(schemas)} test layer schemas:"]
    for schema in schemas:
        test_layer_name = schema.test_layer.name if schema.test_layer else "N/A"
        lines.append(f"- ID: {schema.id}, Key: {schema.key}, Layer: {test_layer_name}")

    return "\n".join(lines)
