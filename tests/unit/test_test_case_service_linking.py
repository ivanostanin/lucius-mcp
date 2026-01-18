from unittest.mock import AsyncMock, Mock

import pytest

from src.client import AllureClient
from src.client.client import BodyStepDtoWithSteps, SharedStepStepDtoWithId
from src.client.exceptions import AllureValidationError
from src.client.generated.models import (
    TestCaseScenarioV2Dto,
)
from src.client.generated.models.shared_step_scenario_dto_steps_inner import SharedStepScenarioDtoStepsInner
from src.services.attachment_service import AttachmentService
from src.services.test_case_service import TestCaseService


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock(spec=AllureClient)
    client.api_client = Mock()
    return client


@pytest.fixture
def mock_attachment_service() -> AsyncMock:
    return AsyncMock(spec=AttachmentService)


@pytest.fixture
def service(mock_client: AsyncMock, mock_attachment_service: AsyncMock) -> TestCaseService:
    return TestCaseService(mock_client, attachment_service=mock_attachment_service)


class TestAddSharedStepToCase:
    """Tests for add_shared_step_to_case."""

    @pytest.mark.asyncio
    async def test_add_shared_step_append_default(self, service: TestCaseService, mock_client: AsyncMock) -> None:
        """Test appending shared step (position=None)."""
        test_case_id = 100
        shared_step_id = 555

        # Setup existing steps
        existing_step = SharedStepScenarioDtoStepsInner(
            actual_instance=BodyStepDtoWithSteps(type="BodyStepDto", id=10, body="Step 1")
        )
        mock_client.get_test_case_scenario.return_value = TestCaseScenarioV2Dto(steps=[existing_step])

        await service.add_shared_step_to_case(test_case_id, shared_step_id, position=None)

        # Verify call: after_id should be last step ID (10)
        mock_client.create_scenario_step.assert_called_once()
        kwargs = mock_client.create_scenario_step.call_args.kwargs
        assert kwargs["test_case_id"] == test_case_id
        assert kwargs["step"].shared_step_id == shared_step_id
        assert kwargs["after_id"] == 10

    @pytest.mark.asyncio
    async def test_add_shared_step_append_empty(self, service: TestCaseService, mock_client: AsyncMock) -> None:
        """Test appending shared step to empty case."""
        test_case_id = 100
        shared_step_id = 555

        mock_client.get_test_case_scenario.return_value = TestCaseScenarioV2Dto(steps=[])

        await service.add_shared_step_to_case(test_case_id, shared_step_id, position=None)

        # Verify call: after_id should be None (no steps)
        mock_client.create_scenario_step.assert_called_once()
        kwargs = mock_client.create_scenario_step.call_args.kwargs
        assert kwargs["after_id"] is None

    @pytest.mark.asyncio
    async def test_add_shared_step_at_start(self, service: TestCaseService, mock_client: AsyncMock) -> None:
        """Test inserting shared step at start (position=0)."""
        test_case_id = 100
        shared_step_id = 555

        existing_step = SharedStepScenarioDtoStepsInner(
            actual_instance=BodyStepDtoWithSteps(type="BodyStepDto", id=10, body="Step 1")
        )
        mock_client.get_test_case_scenario.return_value = TestCaseScenarioV2Dto(steps=[existing_step])

        await service.add_shared_step_to_case(test_case_id, shared_step_id, position=0)

        # Verify call: after_id should be None (insert before first step/at start)
        mock_client.create_scenario_step.assert_called_once()
        kwargs = mock_client.create_scenario_step.call_args.kwargs
        assert kwargs["after_id"] is None

    @pytest.mark.asyncio
    async def test_add_shared_step_at_index(self, service: TestCaseService, mock_client: AsyncMock) -> None:
        """Test inserting shared step at specific index."""
        test_case_id = 100
        shared_step_id = 555

        # Steps: [ID 10, ID 20]
        step1 = SharedStepScenarioDtoStepsInner(
            actual_instance=BodyStepDtoWithSteps(type="BodyStepDto", id=10, body="S1")
        )
        step2 = SharedStepScenarioDtoStepsInner(
            actual_instance=BodyStepDtoWithSteps(type="BodyStepDto", id=20, body="S2")
        )
        mock_client.get_test_case_scenario.return_value = TestCaseScenarioV2Dto(steps=[step1, step2])

        # Insert at index 1 (between 10 and 20)
        # Position 1 means "become the step at index 1". Original index 1 (ID 20) moves to index 2.
        # So we insert AFTER index 0 (ID 10).
        await service.add_shared_step_to_case(test_case_id, shared_step_id, position=1)

        mock_client.create_scenario_step.assert_called_once()
        kwargs = mock_client.create_scenario_step.call_args.kwargs
        assert kwargs["after_id"] == 10

    @pytest.mark.asyncio
    async def test_add_shared_step_position_out_of_bounds(
        self, service: TestCaseService, mock_client: AsyncMock
    ) -> None:
        """Test position out of bounds validation."""
        test_case_id = 100
        mock_client.get_test_case_scenario.return_value = TestCaseScenarioV2Dto(steps=[])

        with pytest.raises(AllureValidationError, match="out of bounds"):
            await service.add_shared_step_to_case(test_case_id, 555, position=1)  # Length 0, index 1 invalid


class TestRemoveSharedStepFromCase:
    """Tests for remove_shared_step_from_case."""

    @pytest.mark.asyncio
    async def test_remove_shared_step_success(self, service: TestCaseService, mock_client: AsyncMock) -> None:
        """Test removing existing shared step references."""
        test_case_id = 100
        shared_step_id = 555

        # Steps: [Inline(10), Shared(20, ref=555)]
        step1 = SharedStepScenarioDtoStepsInner(actual_instance=BodyStepDtoWithSteps(type="BodyStepDto", id=10))

        step2 = SharedStepScenarioDtoStepsInner(
            actual_instance=SharedStepStepDtoWithId(type="SharedStepStepDto", id=20, shared_step_id=555)
        )

        mock_client.get_test_case_scenario.return_value = TestCaseScenarioV2Dto(steps=[step1, step2])

        await service.remove_shared_step_from_case(test_case_id, shared_step_id)

        mock_client.delete_scenario_step.assert_called_once_with(20)

    @pytest.mark.asyncio
    async def test_remove_shared_step_multiple_references(
        self, service: TestCaseService, mock_client: AsyncMock
    ) -> None:
        """Test removing multiple references to same shared step."""
        test_case_id = 100
        shared_step_id = 555

        # Steps: [Shared(20, ref=555), Shared(30, ref=555)]
        step1 = SharedStepScenarioDtoStepsInner(
            actual_instance=SharedStepStepDtoWithId(type="SharedStepStepDto", id=20, shared_step_id=555)
        )
        step2 = SharedStepScenarioDtoStepsInner(
            actual_instance=SharedStepStepDtoWithId(type="SharedStepStepDto", id=30, shared_step_id=555)
        )

        mock_client.get_test_case_scenario.return_value = TestCaseScenarioV2Dto(steps=[step1, step2])

        await service.remove_shared_step_from_case(test_case_id, shared_step_id)

        assert mock_client.delete_scenario_step.call_count == 2
        mock_client.delete_scenario_step.assert_any_call(20)
        mock_client.delete_scenario_step.assert_any_call(30)

    @pytest.mark.asyncio
    async def test_remove_shared_step_not_found(self, service: TestCaseService, mock_client: AsyncMock) -> None:
        """Test validation error when shared step not found."""
        test_case_id = 100
        # Provide steps so it doesn't return early
        step1 = SharedStepScenarioDtoStepsInner(actual_instance=BodyStepDtoWithSteps(type="BodyStepDto", id=10))
        mock_client.get_test_case_scenario.return_value = TestCaseScenarioV2Dto(steps=[step1])

        with pytest.raises(AllureValidationError, match="not found in Test Case"):
            await service.remove_shared_step_from_case(test_case_id, 999)
