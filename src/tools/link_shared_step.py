"""Tool for linking Shared Steps to Test Cases."""

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
        # Handle Shared Step
        if step.actual_instance and isinstance(step.actual_instance, SharedStepStepDto):
            output.append(f"{i + 1}. [Shared Step] ID: {step.actual_instance.shared_step_id}")
        else:
            # Inline step
            body = "Step"
            if hasattr(step.actual_instance, "body"):
                body = step.actual_instance.body or "Step"
            output.append(f"{i + 1}. {body}")
    return "\n".join(output)


async def link_shared_step(
    test_case_id: Annotated[int, Field(description="The ID of test case to modify.")],
    shared_step_id: Annotated[int, Field(description="The ID of shared step to link.")],
    position: Annotated[
        int | None,
        Field(
            description="Where to insert the shared step (0-indexed, optional)."
            " 0 = Insert at beginning"
            " None = Append to end (default)"
            " N = Insert after step N (so it becomes the (N+1)th step)"
        ),
    ] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    confirm: Annotated[bool, Field(description="Must be set to True to proceed with linking. Safety measure.")] = False,
) -> str:
    """Link a shared step to a test case.
    ⚠️ CAUTION: Destructive.

    Adds a reference to the shared step in the test case's step list.
    The shared step's actions will expand at execution time.

    Args:
        test_case_id: The ID of test case to modify.
            Found in URL: /testcase/12345
        shared_step_id: The ID of shared step to link.
            Found via list_shared_steps or in Allure UI.
        position: Where to insert the shared step (0-indexed, optional).
            - 0 = Insert at beginning
            - None = Append to end (default)
            - N = Insert after step N (so it becomes the (N+1)th step)
        project_id: Optional override for the default Project ID.
        confirm: Must be set to True to proceed with linking.
            This is a safety measure to prevent accidental linking.

    Returns:
        Confirmation with updated step list preview.

    Example:
        link_shared_step(
            test_case_id=12345,
            shared_step_id=789,  # "Login as Admin"
            position=0,
            confirm=True
        )
    """
    if not confirm:
        return (
            "⚠️ Linking requires confirmation.\n\n"
            "This will add a shared step to the test case scenario. "
            f"Please call again with confirm=True to proceed with linking "
            f"shared step {shared_step_id} to test case {test_case_id}."
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client=client)
        try:
            await service.add_shared_step_to_case(
                test_case_id=test_case_id,
                shared_step_id=shared_step_id,
                position=position,
            )

            scenario = await client.get_test_case_scenario(test_case_id)
            steps_preview = _format_steps(scenario)

            return (
                f"✅ Linked Shared Step {shared_step_id} to Test Case {test_case_id}\n\nUpdated steps:\n{steps_preview}"
            )
        except Exception as e:
            return f"❌ Error linking shared step: {e}"
