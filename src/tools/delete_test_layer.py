"""Tool for deleting a test layer."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, render_output


async def delete_test_layer(
    layer_id: Annotated[int, Field(description="ID of the test layer to delete.")],
    project_id: Annotated[int | None, Field(description="Allure TestOps project ID.")] = None,
    confirm: Annotated[
        bool, Field(description="Must be set to True to proceed with deletion. Safety measure.")
    ] = False,
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """Delete a test layer from Allure TestOps.
    ⚠️ CAUTION: Destructive.

    Args:
        layer_id: ID of the test layer to delete.
        project_id: Optional Allure TestOps project ID override.
        confirm: Must be set to True to proceed with deletion.
            This is a safety measure to prevent accidental deletions.
        output_format: Output format: plain (default) or json.

    Returns:
        Confirmation message.
    """
    if not confirm:
        message = (
            "⚠️ Deletion requires confirmation.\n\n"
            "Deleting a test layer may affect test case categorization. "
            f"Please call again with confirm=True to proceed with deleting test layer {layer_id}."
        )
        return render_output(
            plain=message,
            json_payload={
                "requires_confirmation": True,
                "layer_id": layer_id,
                "action": "delete_test_layer",
            },
            output_format=output_format,
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = TestLayerService(client)
        deleted = await service.delete_test_layer(layer_id=layer_id)

    if deleted:
        return render_output(
            plain=f"✅ Test layer {layer_id} deleted successfully!",
            json_payload={"id": layer_id, "status": "deleted"},
            output_format=output_format,
        )
    return render_output(
        plain=f"ℹ️ Test layer {layer_id} was already deleted or doesn't exist.",  # noqa: RUF001
        json_payload={"id": layer_id, "status": "already_deleted"},
        output_format=output_format,
    )
