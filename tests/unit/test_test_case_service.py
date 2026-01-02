from unittest.mock import AsyncMock, Mock

import pytest

from src.client import AllureClient
from src.client.generated.models import TestCaseCreateV2Dto, TestCaseScenarioV2Dto
from src.services.attachment_service import AttachmentService
from src.services.test_case_service import TestCaseService


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=AllureClient)


@pytest.fixture
def mock_attachment_service() -> AsyncMock:
    return AsyncMock(spec=AttachmentService)


@pytest.fixture
def service(mock_client: AsyncMock, mock_attachment_service: AsyncMock) -> TestCaseService:
    return TestCaseService(mock_client, attachment_service=mock_attachment_service)


@pytest.mark.asyncio
async def test_create_test_case_success_minimal(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test creating a test case with minimal required fields."""
    project_id = 1
    data = TestCaseCreateV2Dto(name="Test Case 1", project_id=project_id, automation="manual")
    result_mock = Mock(id=100)
    result_mock.name = "Test Case 1"
    mock_client.create_test_case.return_value = result_mock

    result = await service.create_test_case(project_id, data)

    assert result.id == 100
    assert result.name == "Test Case 1"
    mock_client.create_test_case.assert_called_once_with(project_id, data)


@pytest.mark.asyncio
async def test_create_test_case_with_steps(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test creating a test case with steps."""
    project_id = 1
    # We construct the DTO directly in the test to verify mapping
    scenario = TestCaseScenarioV2Dto(steps=[])

    data = TestCaseCreateV2Dto(name="Steps Test", project_id=project_id, scenario=scenario)

    result_mock = Mock(id=101)
    result_mock.name = "Steps Test"
    mock_client.create_test_case.return_value = result_mock

    await service.create_test_case(project_id, data)

    mock_client.create_test_case.assert_called_once()
    assert mock_client.create_test_case.call_args[0][1].scenario == scenario


@pytest.mark.asyncio
async def test_create_test_case_with_attachments(
    service: TestCaseService, mock_client: AsyncMock, mock_attachment_service: AsyncMock
) -> None:
    """Test creating a test case with attachments."""
    project_id = 1
    data = TestCaseCreateV2Dto(name="Attachment Test", project_id=project_id, automation="manual")
    attachments = [{"name": "img.png", "content": "...", "content_type": "image/png"}]

    mock_attachment_service.upload_attachment.return_value = Mock(id=999, name="img.png")
    result_mock = Mock(id=102)
    result_mock.name = "Attachment Test"
    mock_client.create_test_case.return_value = result_mock

    await service.create_test_case(project_id, data, attachments=attachments)

    # Verify attachment upload called
    mock_attachment_service.upload_attachment.assert_called_once_with(project_id, attachments[0])

    # Verify create_test_case called with modified data
    call_args = mock_client.create_test_case.call_args
    called_data = call_args[0][1]

    assert called_data.scenario is not None
    assert len(called_data.scenario.steps) == 1
    # Check if the step added is an attachment step
    step_wrapper = called_data.scenario.steps[0]
    step = step_wrapper.actual_instance
    assert step.attachment_id == 999
    assert step.type == "AttachmentStep"
