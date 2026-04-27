"""Tool for updating a test layer."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output


async def update_test_layer(
    layer_id: Annotated[int, Field(description="ID of the test layer to update.")],
    name: Annotated[str, Field(description="New name for the test layer.")],
    project_id: Annotated[int | None, Field(description="Allure TestOps project ID.")] = None,
    confirm: Annotated[bool, Field(description="Must be set to True to proceed with update. Safety measure.")] = False,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Update an existing test layer's name.
    ⚠️ CAUTION: Destructive.

    Args:
        layer_id: ID of the test layer to update.
        name: New name for the test layer.
        project_id: Optional Allure TestOps project ID override.
        confirm: Must be set to True to proceed with update.
            This is a safety measure to prevent accidental updates.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Confirmation message indicating whether changes were made.
    """
    if not confirm:
        message = (
            "⚠️ Update requires confirmation.\n\n"
            "Renaming a test layer affects all associated test cases. "
            f"Please call again with confirm=True to proceed with updating test layer {layer_id}."
        )
        return render_output(
            plain=message,
            json_payload={
                "requires_confirmation": True,
                "layer_id": layer_id,
                "action": "update_test_layer",
            },
            output_format=output_format,
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = TestLayerService(client)
        updated, changed = await service.update_test_layer(layer_id=layer_id, name=name)

    if changed:
        return render_output(
            plain=f"✅ Test layer {layer_id} updated successfully! New name: {updated.name}",
            json_payload={"id": layer_id, "name": updated.name, "changed": True},
            output_format=output_format,
        )
    return render_output(
        plain=f"[INFO] Test layer {layer_id} already has name '{name}' - no changes made.",
        json_payload={"id": layer_id, "name": name, "changed": False},
        output_format=output_format,
    )
