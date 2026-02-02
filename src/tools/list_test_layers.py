"""Tool for listing test layers."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService


async def list_test_layers(
    page: Annotated[int, Field(description="Page number (0-based). Default is 0.")] = 0,
    size: Annotated[int, Field(description="Page size (max 100). Default is 100.")] = 100,
) -> str:
    """List test layers to discover available test layer taxonomy.

    Test layers define the taxonomy for categorizing test cases (e.g., Unit, Integration, E2E).
    Use this to find layer IDs and names before creating or updating test cases.

    Args:
        page: Page number (0-based)
        size: Page size (max 100)

    Returns:
        List of test layers with their IDs and names
    """
    async with AllureClient.from_env() as client:
        service = TestLayerService(client)
        layers = await service.list_test_layers(page=page, size=size)

    if not layers:
        return "No test layers found."

    lines = [f"Found {len(layers)} test layers:"]
    for layer in layers:
        lines.append(f"- ID: {layer.id}, Name: {layer.name}")

    return "\n".join(lines)
