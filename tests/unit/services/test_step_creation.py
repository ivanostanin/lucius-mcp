from unittest.mock import AsyncMock

import pytest

from src.client import AllureClient
from src.client.client import StepWithExpected
from src.client.generated.models.normalized_scenario_dto import NormalizedScenarioDto
from src.client.generated.models.normalized_scenario_step_dto import NormalizedScenarioStepDto
from src.client.generated.models.scenario_step_created_response_dto import ScenarioStepCreatedResponseDto
from src.client.generated.models.shared_step_scenario_dto_steps_inner import SharedStepScenarioDtoStepsInner
from src.services.test_case_service import TestCaseService


@pytest.mark.asyncio
async def test_add_steps_with_expected_result_logic():
    # Setup
    mock_client = AsyncMock(spec=AllureClient)
    service = TestCaseService(mock_client)

    # Mock create_scenario_step response for Action Step
    # The first call (create Action) should return a response containing the scenario
    # with the created step populated with expectedResultId
    mock_response = ScenarioStepCreatedResponseDto(
        createdStepId=100,
        scenario=NormalizedScenarioDto(scenarioSteps={"100": NormalizedScenarioStepDto(id=100, expectedResultId=101)}),
    )
    mock_client.create_scenario_step.return_value = mock_response

    # Define steps
    steps = [{"action": "Action", "expected": "Result"}]

    # Execution
    await service._add_steps(test_case_id=1, steps=steps, last_step_id=None)

    # Verification
    # 1. Verify Action step creation was called with with_expected_result=True
    # Capture calls to verify arguments
    calls = mock_client.create_scenario_step.call_args_list
    assert len(calls) == 2, "Should have made 2 create_scenario_step calls"

    # Check first call (Action Step)
    _args1, kwargs1 = calls[0]
    assert kwargs1.get("test_case_id") == 1
    assert kwargs1.get("step").body == "Action"
    assert kwargs1.get("with_expected_result") is True

    # Check second call (Expected Result Step)
    _args2, kwargs2 = calls[1]
    assert kwargs2.get("test_case_id") == 1
    assert kwargs2.get("step").body == "Result"
    assert kwargs2.get("step").parent_id == 101  # Should be linked to expectedResultId
    assert (
        kwargs2.get("after_id") is None
    )  # Expected result text usually appended without specific ordering within the Expected Result container


@pytest.mark.asyncio
async def test_add_steps_without_expected_result():
    # Setup
    mock_client = AsyncMock(spec=AllureClient)
    service = TestCaseService(mock_client)

    mock_response = ScenarioStepCreatedResponseDto(createdStepId=200)
    mock_client.create_scenario_step.return_value = mock_response

    steps = [{"action": "Just Action"}]

    # Execution
    await service._add_steps(test_case_id=1, steps=steps, last_step_id=None)

    # Verification
    mock_client.create_scenario_step.assert_called_once()
    _args, kwargs = mock_client.create_scenario_step.call_args
    assert kwargs.get("with_expected_result") is False
    assert kwargs.get("step").body == "Just Action"


@pytest.mark.asyncio
async def test_recursive_add_step_with_expected_result():
    # Setup
    mock_client = AsyncMock(spec=AllureClient)
    service = TestCaseService(mock_client)

    mock_response = ScenarioStepCreatedResponseDto(
        createdStepId=300,
        scenario=NormalizedScenarioDto(scenarioSteps={"300": NormalizedScenarioStepDto(id=300, expectedResultId=301)}),
    )
    mock_client.create_scenario_step.return_value = mock_response

    # Construct the DTO that _recursive_add_step expects
    # It uses SharedStepScenarioDtoStepsInner -> actual_instance (BodyStepDto/StepWithExpected)
    # Note: We need to use StepWithExpected to pass expected_result attribute check
    step_input = SharedStepScenarioDtoStepsInner(
        actual_instance=StepWithExpected(
            type="BodyStepDto", body="Recursive Action", expectedResult="Recursive Expected", steps=[]
        )
    )

    # Execution
    await service._recursive_add_step(test_case_id=1, step=step_input)

    # Verification
    calls = mock_client.create_scenario_step.call_args_list
    assert len(calls) == 2, "Should have made 2 create_scenario_step calls"

    # Action Step
    _args1, kwargs1 = calls[0]
    # Check arguments
    assert kwargs1.get("step").body == "Recursive Action"
    assert kwargs1.get("with_expected_result") is True

    # Expected Result Child Step
    _args2, kwargs2 = calls[1]
    assert kwargs2.get("step").body == "Recursive Expected"
    assert kwargs2.get("step").parent_id == 301
