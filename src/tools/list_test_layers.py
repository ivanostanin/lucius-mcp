"""Tool for listing test layers."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, render_output


async def list_test_layers(
    page: Annotated[int, Field(description="Page number (0-based). Default is 0.")] = 0,
    size: Annotated[int, Field(description="Page size (max 100). Default is 100.")] = 100,
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """List test layers to discover available test layer taxonomy.

    Test layers define the taxonomy for categorizing test cases (e.g., Unit, Integration, E2E).
    Use this to find layer IDs and names before creating or updating test cases.

    Args:
        page: Page number (0-based)
        size: Page size (max 100)
        output_format: Output format: plain (default) or json.

    Returns:
        List of test layers with their IDs and names
    """
    async with AllureClient.from_env() as client:
        service = TestLayerService(client)
        layers = await service.list_test_layers(page=page, size=size)

    if not layers:
        return render_output(
            plain="No test layers found.",
            json_payload={"items": [], "total": 0, "page": page, "size": size},
            output_format=output_format,
        )

    lines = [f"Found {len(layers)} test layers:"]
    items: list[dict[str, object]] = []
    for layer in layers:
        lines.append(f"- ID: {layer.id}, Name: {layer.name}")
        items.append({"id": layer.id, "name": layer.name})

    return render_output(
        plain="\n".join(lines),
        json_payload={"items": items, "total": len(items), "page": page, "size": size},
        output_format=output_format,
    )
