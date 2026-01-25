"""Tool for linking Shared Steps to Test Cases."""

from typing import Any

from src.client import AllureClient
from src.client.generated.models.shared_step_step_dto import SharedStepStepDto
from src.services.test_case_service import TestCaseService


def _format_steps(scenario: Any) -> str:
    """Format steps for display."""
    if not scenario or not scenario.steps:
        return "No steps."

    output = []
    for i, step in enumerate(scenario.steps):
        # Handle Shared Step
        if step.actual_instance and isinstance(step.actual_instance, SharedStepStepDto):
            # Ideally we would have the name, but DTO might only have ID if not enriched.
            # SharedStepStepDto has 'sharedStepId'.
            # Does it have 'name'? The scenarios steps in 'get_test_case_scenario'
            # might not have name enriched unless we fetched it or denormalized it.
            # The _denormalize_to_v2_from_dict doesn't currently inject name.
            # For now, just show ID.
            output.append(f"{i + 1}. [Shared Step] ID: {step.actual_instance.shared_step_id}")
        else:
            # Inline step
            # We assume it has some description or body
            body = "Step"
            if hasattr(step.actual_instance, "body"):
                body = step.actual_instance.body or "Step"
            output.append(f"{i + 1}. {body}")
    return "\n".join(output)


async def link_shared_step(
    test_case_id: int,
    shared_step_id: int,
    position: int | None = None,
    project_id: int | None = None,
) -> str:
    """Link a shared step to a test case.

    Adds a reference to the shared step in the test case's step list.
    The shared step's actions will expand at execution time.

    Args:
        test_case_id: The test case to modify.
            Found in URL: /testcase/12345
        shared_step_id: The shared step to link.
            Found via list_shared_steps or in Allure UI.
        position: Where to insert the shared step (0-indexed, optional).
            - 0 = Insert at beginning
            - None = Append to end (default)
            - N = Insert after step N (so it becomes the (N+1)th step)
        project_id: Optional override for the default Project ID.

    Returns:
        Confirmation with updated step list preview.

    Example:
        link_shared_step(
            test_case_id=12345,
            shared_step_id=789,  # "Login as Admin"
            position=0  # Insert at beginning
        )
    """

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
