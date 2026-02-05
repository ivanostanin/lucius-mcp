"""Tool for unlinking Shared Steps from Test Cases."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.client.generated.models.shared_step_step_dto import SharedStepStepDto
from src.services.test_case_service import TestCaseService


def _format_steps(scenario: object) -> str:
    """Format steps for display."""
    steps = getattr(scenario, "steps", None)
    if not isinstance(steps, list) or not steps:
        return "No steps."

    output = []
    for i, step in enumerate(steps):
        if step.actual_instance and isinstance(step.actual_instance, SharedStepStepDto):
            output.append(f"{i + 1}. [Shared Step] ID: {step.actual_instance.shared_step_id}")
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
) -> str:
    """Remove a shared step reference from a test case.

    Removes the link to the shared step. The test case will no longer
    include those steps at execution time.

    Args:
        test_case_id: The test case to modify.
        shared_step_id: The shared step to unlink.
        project_id: Optional override for the default Project ID.

    Returns:
        Confirmation with updated step list.

    Note: This only removes the REFERENCE. The shared step itself
    remains in the library and other test cases are unaffected.

    Example:
        unlink_shared_step(test_case_id=12345, shared_step_id=789)
    """

    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client=client)
        try:
            await service.remove_shared_step_from_case(
                test_case_id=test_case_id,
                shared_step_id=shared_step_id,
            )

            scenario = await client.get_test_case_scenario(test_case_id)
            steps_preview = _format_steps(scenario)

            return (
                f"✅ Unlinked Shared Step {shared_step_id} from Test Case {test_case_id}\n\n"
                f"Remaining steps:\n{steps_preview}"
            )
        except Exception as e:
            return f"❌ Error unlinking shared step: {e}"
