from unittest.mock import AsyncMock, Mock

import pytest

from src.client import AllureClient, BodyStepDtoWithSteps
from src.client.exceptions import AllureAPIError
from src.client.generated.models import (
    SharedStepScenarioDtoStepsInner,
    TestCaseDto,
    TestCasePatchV2Dto,
    TestCaseScenarioV2Dto,
)
from src.services.test_case_service import TestCaseService, TestCaseUpdate


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock(spec=AllureClient)
    client.api_client = Mock()
    client.get_project.return_value = 1
    return client


@pytest.fixture
def mock_scenario_response() -> TestCaseScenarioV2Dto:
    """Mock response for get_test_case_scenario."""
    # minimal mock
    return TestCaseScenarioV2Dto(steps=[])


@pytest.mark.asyncio
async def test_update_nested_steps_fix(mock_client: AsyncMock, mock_scenario_response: TestCaseScenarioV2Dto) -> None:
    """Test updating steps with nested hierarchy."""
    service = TestCaseService(client=mock_client)
    test_case_id = 999
    mock_client.get_test_case.return_value = TestCaseDto(id=test_case_id)
    mock_client.get_test_case_scenario.return_value = mock_scenario_response
    mock_client.update_test_case.return_value = TestCaseDto(id=test_case_id)

    # Mock create_scenario_step to return a valid ID
    mock_step_resp = Mock()
    mock_step_resp.created_step_id = 123
    mock_client.create_scenario_step.return_value = mock_step_resp

    # Nested Steps Structure
    steps = [
        {
            "action": "Parent",
            "steps": [{"action": "Child 1"}, {"action": "Child 2", "steps": [{"action": "Grandchild"}]}],
        }
    ]
    data = TestCaseUpdate(steps=steps)

    await service.update_test_case(test_case_id, data)

    # Verify existing scenario cleared first
    mock_client.update_test_case.assert_called_once()
    patch_dto: TestCasePatchV2Dto = mock_client.update_test_case.call_args[0][1]
    assert patch_dto.scenario is not None
    assert patch_dto.scenario.steps == []

    # Verify steps creation via create_scenario_step
    # Expect 4 calls: Parent, Child 1, Child 2, Grandchild
    assert mock_client.create_scenario_step.call_count == 4

    calls = mock_client.create_scenario_step.call_args_list

    # 1. Parent
    parent_call = calls[0]
    assert parent_call.kwargs["step"].body == "Parent"
    assert parent_call.kwargs["step"].parent_id is None

    # 2. Child 1 (Parent ID = 123 from mock)
    child1_call = calls[1]
    assert child1_call.kwargs["step"].body == "Child 1"
    assert child1_call.kwargs["step"].parent_id == 123

    # 3. Child 2 (Parent ID = 123)
    child2_call = calls[2]
    assert child2_call.kwargs["step"].body == "Child 2"
    assert child2_call.kwargs["step"].parent_id == 123

    # 4. Grandchild (Parent ID = 123 from Child 2 creation)
    grandchild_call = calls[3]
    assert grandchild_call.kwargs["step"].body == "Grandchild"
    assert grandchild_call.kwargs["step"].parent_id == 123


@pytest.mark.asyncio
async def test_recreate_scenario_rollback_fix(mock_client: AsyncMock) -> None:
    """Test scenario recreation rollback on failure."""
    service = TestCaseService(client=mock_client)
    test_case_id = 999

    # 1. Setup mock current scenario (to be restored)
    step = SharedStepScenarioDtoStepsInner(actual_instance=BodyStepDtoWithSteps(type="BodyStepDto", body="Old Step"))
    current_scenario = TestCaseScenarioV2Dto(steps=[step])
    mock_client.get_test_case_scenario.return_value = current_scenario

    # 2. Mock update_test_case for clearing (success first time, success on rollback)
    mock_client.update_test_case.return_value = TestCaseDto(id=test_case_id)

    # 3. Mock recursive add step to fail
    # This mocks the creation of the NEW steps failing
    service._recursive_add_step = AsyncMock(side_effect=Exception("API Fail"))  # type: ignore

    # 4. Call update with new steps
    data = TestCaseUpdate(steps=[{"action": "New Step"}])

    with pytest.raises(AllureAPIError, match="Failed to recreate scenario"):
        await service.update_test_case(test_case_id, data)

    # 5. Verify Rollback behavior
    # Should have called update_test_case to clear execution twice:
    # 1. Initial clear
    # 2. Rollback clear
    assert mock_client.update_test_case.call_count == 2

    # Verify get_test_case_scenario was called (at least once for backup, likely more for prep)
    assert mock_client.get_test_case_scenario.call_count >= 1
