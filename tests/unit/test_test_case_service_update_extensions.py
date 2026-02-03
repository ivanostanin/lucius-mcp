from unittest.mock import AsyncMock, Mock

import pytest

from src.client import AllureClient, BodyStepDtoWithSteps
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError
from src.client.generated.models import (
    SharedStepScenarioDtoStepsInner,
    TestCaseDto,
    TestCaseScenarioV2Dto,
    TestLayerDto,
)
from src.client.generated.models.test_case_patch_v2_dto import TestCasePatchV2Dto
from src.services.test_case_service import TestCaseService, TestCaseUpdate
from src.services.test_layer_service import TestLayerService


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
    clear_calls = [
        call
        for call in mock_client.update_test_case.call_args_list
        if call[0][1].scenario is not None and call[0][1].scenario.steps == []
    ]
    assert len(clear_calls) == 1

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
    clear_calls = [
        call
        for call in mock_client.update_test_case.call_args_list
        if call[0][1].scenario is not None and call[0][1].scenario.steps == []
    ]
    assert len(clear_calls) == 2

    # Verify get_test_case_scenario was called (at least once for backup, likely more for prep)
    assert mock_client.get_test_case_scenario.call_count >= 1


@pytest.mark.asyncio
async def test_update_test_layer_validates_and_patches(mock_client: AsyncMock) -> None:
    service = TestCaseService(client=mock_client, test_layer_service=AsyncMock(spec=TestLayerService))
    test_case_id = 900
    mock_client.get_test_case.return_value = TestCaseDto(id=test_case_id)
    mock_client.update_test_case.return_value = TestCaseDto(id=test_case_id)

    service._test_layer_service.get_test_layer.return_value = TestLayerDto(id=12, name="Layer12")

    data = TestCaseUpdate(test_layer_id=12)
    await service.update_test_case(test_case_id, data)

    service._test_layer_service.get_test_layer.assert_called_once_with(12)
    mock_client.update_test_case.assert_called_once()
    patch_dto: TestCasePatchV2Dto = mock_client.update_test_case.call_args[0][1]
    assert patch_dto.test_layer_id == 12


@pytest.mark.asyncio
async def test_update_test_layer_invalid_raises_error(mock_client: AsyncMock) -> None:
    service = TestCaseService(client=mock_client, test_layer_service=AsyncMock(spec=TestLayerService))
    test_case_id = 901
    mock_client.get_test_case.return_value = TestCaseDto(id=test_case_id)

    service._test_layer_service.get_test_layer.side_effect = AllureNotFoundError("missing")
    service._test_layer_service.list_test_layers.return_value = [
        TestLayerDto(id=1, name="Layer1"),
        TestLayerDto(id=2, name="Layer2"),
    ]

    data = TestCaseUpdate(test_layer_id=123)

    with pytest.raises(AllureValidationError, match="list_test_layers"):
        await service.update_test_case(test_case_id, data)


@pytest.mark.asyncio
async def test_update_test_layer_idempotent_skips_validation(mock_client: AsyncMock) -> None:
    service = TestCaseService(client=mock_client, test_layer_service=AsyncMock(spec=TestLayerService))
    test_case_id = 902
    current_case = TestCaseDto(id=test_case_id, test_layer=TestLayerDto(id=7, name="Layer7"))
    mock_client.get_test_case.return_value = current_case

    data = TestCaseUpdate(test_layer_id=7)

    result = await service.update_test_case(test_case_id, data)

    assert result is current_case
    service._test_layer_service.get_test_layer.assert_not_called()
    mock_client.update_test_case.assert_not_called()


@pytest.mark.asyncio
async def test_update_test_layer_mixed_update_patches_both(mock_client: AsyncMock) -> None:
    service = TestCaseService(client=mock_client, test_layer_service=AsyncMock(spec=TestLayerService))
    test_case_id = 903
    mock_client.get_test_case.return_value = TestCaseDto(id=test_case_id, name="Old")
    mock_client.update_test_case.return_value = TestCaseDto(id=test_case_id)

    service._test_layer_service.get_test_layer.return_value = TestLayerDto(id=20, name="Layer20")

    data = TestCaseUpdate(name="New", test_layer_id=20)
    await service.update_test_case(test_case_id, data)

    service._test_layer_service.get_test_layer.assert_called_once_with(20)
    patch_dto: TestCasePatchV2Dto = mock_client.update_test_case.call_args[0][1]
    assert patch_dto.name == "New"
    assert patch_dto.test_layer_id == 20
