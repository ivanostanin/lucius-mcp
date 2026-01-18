import pytest

from src.client.client import BodyStepDtoWithSteps, SharedStepStepDtoWithId
from src.client.generated.models.shared_step_scenario_dto_steps_inner import SharedStepScenarioDtoStepsInner


@pytest.fixture
def step_dto_factory():
    """Factory to create SharedStepScenarioDtoStepsInner instances."""

    def _create(step_type="body", id=10, shared_step_id=None, body="Step"):
        if step_type == "body":
            return SharedStepScenarioDtoStepsInner(
                actual_instance=BodyStepDtoWithSteps(type="BodyStepDto", id=id, body=body)
            )
        elif step_type == "shared":
            if shared_step_id is None:
                raise ValueError("shared_step_id is required for shared steps")
            return SharedStepScenarioDtoStepsInner(
                actual_instance=SharedStepStepDtoWithId(type="SharedStepStepDto", id=id, shared_step_id=shared_step_id)
            )
        raise ValueError(f"Unknown type: {step_type}")

    return _create
