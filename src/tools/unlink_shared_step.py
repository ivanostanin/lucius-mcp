"""Tool for unlinking Shared Steps from Test Cases."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.client.generated.models.shared_step_step_dto import SharedStepStepDto
from src.services.test_case_service import TestCaseService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output
from src.utils.links import shared_step_url, test_case_url


def _format_steps(scenario: object, *, base_url: str, project_id: int) -> str:
    """Format steps for display."""
    steps = getattr(scenario, "steps", None)
    if not isinstance(steps, list) or not steps:
        return "No steps."

    output = []
    for i, step in enumerate(steps):
        if step.actual_instance and isinstance(step.actual_instance, SharedStepStepDto):
            nested_shared_step_id = step.actual_instance.shared_step_id
            line = f"{i + 1}. [Shared Step] ID: {nested_shared_step_id}"
            if isinstance(nested_shared_step_id, int):
                line += f" (URL: {shared_step_url(base_url, project_id, nested_shared_step_id)})"
            output.append(line)
        else:
            body = "Step"
            if hasattr(step.actual_instance, "body"):
                body = step.actual_instance.body or "Step"
            output.append(f"{i + 1}. {body}")
    return "\n".join(output)


async def unlink_shared_step(
    test_case_id: Annotated[int, Field(description="The test case to modify.")],
    shared_step_id: Annotated[int, Field(description="The shared step to unlink.")],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    confirm: Annotated[
        bool, Field(description="Must be set to True to proceed with unlinking. Safety measure.")
    ] = False,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Remove a shared step reference from a test case.
    ⚠️ CAUTION: Destructive.

    Removes the link to the shared step. The test case will no longer
    include those steps at execution time.

    Args:
        test_case_id: The test case to modify.
        shared_step_id: The shared step to unlink.
        project_id: Optional override for the default Project ID.
        confirm: Must be set to True to proceed with unlinking.
            This is a safety measure to prevent accidental unlinking.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Confirmation with updated step list.

    Note: This only removes the REFERENCE. The shared step itself
    remains in the library and other test cases are unaffected.

    Example:
        unlink_shared_step(test_case_id=12345, shared_step_id=789, confirm=True)
    """
    if not confirm:
        message = (
            "⚠️ Unlinking requires confirmation.\n\n"
            "This will remove a shared step from the test case scenario. "
            f"Please call again with confirm=True to proceed with unlinking "
            f"shared step {shared_step_id} from test case {test_case_id}."
        )
        return render_output(
            plain=message,
            json_payload={
                "requires_confirmation": True,
                "test_case_id": test_case_id,
                "shared_step_id": shared_step_id,
                "action": "unlink_shared_step",
            },
            output_format=output_format,
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client=client)
        base_url = client.get_base_url()
        resolved_project_id = client.get_project()
        test_case_link = test_case_url(base_url, resolved_project_id, test_case_id)
        shared_step_link = shared_step_url(base_url, resolved_project_id, shared_step_id)
        try:
            await service.remove_shared_step_from_case(
                test_case_id=test_case_id,
                shared_step_id=shared_step_id,
            )

            scenario = await client.get_test_case_scenario(test_case_id)
            steps_preview = _format_steps(scenario, base_url=base_url, project_id=resolved_project_id)
            message = (
                f"✅ Unlinked Shared Step {shared_step_id} from Test Case {test_case_id}\n\n"
                f"Shared Step URL: {shared_step_link}\n"
                f"Test Case URL: {test_case_link}\n\n"
                f"Remaining steps:\n{steps_preview}"
            )
            return render_output(
                plain=message,
                json_payload={
                    "test_case_id": test_case_id,
                    "test_case_url": test_case_link,
                    "shared_step_id": shared_step_id,
                    "shared_step_url": shared_step_link,
                    "steps": _serialize_steps(scenario, base_url=base_url, project_id=resolved_project_id),
                },
                output_format=output_format,
            )
        except Exception as e:
            return render_output(
                plain=(
                    f"❌ Error unlinking shared step: {e}\n"
                    f"Shared Step URL: {shared_step_link}\n"
                    f"Test Case URL: {test_case_link}"
                ),
                json_payload={
                    "test_case_id": test_case_id,
                    "test_case_url": test_case_link,
                    "shared_step_id": shared_step_id,
                    "shared_step_url": shared_step_link,
                    "status": "error",
                    "error": str(e),
                },
                output_format=output_format,
            )


def _serialize_steps(scenario: object, *, base_url: str, project_id: int) -> list[dict[str, object]]:
    steps = getattr(scenario, "steps", None)
    if not isinstance(steps, list):
        return []

    serialized: list[dict[str, object]] = []
    for index, step in enumerate(steps, 1):
        if step.actual_instance and isinstance(step.actual_instance, SharedStepStepDto):
            nested_shared_step_id = step.actual_instance.shared_step_id
            payload: dict[str, object] = {
                "index": index,
                "type": "shared_step",
                "shared_step_id": nested_shared_step_id,
            }
            if isinstance(nested_shared_step_id, int):
                payload["shared_step_url"] = shared_step_url(base_url, project_id, nested_shared_step_id)
            serialized.append(payload)
            continue

        body = "Step"
        if hasattr(step.actual_instance, "body"):
            body = step.actual_instance.body or "Step"
        serialized.append({"index": index, "type": "inline", "action": body})
    return serialized
