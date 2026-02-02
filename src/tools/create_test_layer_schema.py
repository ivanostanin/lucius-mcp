"""Tool for creating a test layer schema."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService


async def create_test_layer_schema(
    key: Annotated[str, Field(description="The schema key (e.g., custom field name like 'layer' or 'test_layer').")],
    test_layer_id: Annotated[int, Field(description="ID of the test layer to link to this schema.")],
    project_id: Annotated[int, Field(description="Allure TestOps project ID to create the schema in.")],
) -> str:
    """Create a new test layer schema to map a custom field key to a test layer.

    Test layer schemas define the mapping between custom field keys and test layers.
    This allows test cases with specific custom field values to be automatically
    assigned to the correct test layer.

    Args:
        key: Schema key (typically a custom field name)
        test_layer_id: ID of the test layer to link
        project_id: Project ID

    Returns:
        Confirmation message with the created schema's details
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestLayerService(client)
        schema = await service.create_test_layer_schema(
            project_id=project_id,
            test_layer_id=test_layer_id,
            key=key,
        )

    test_layer_name = schema.test_layer.name if schema.test_layer else "N/A"
    return f"✅ Test layer schema created successfully! ID: {schema.id}, Key: {schema.key}, Layer: {test_layer_name}"
