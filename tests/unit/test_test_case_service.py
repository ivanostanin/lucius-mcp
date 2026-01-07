from unittest.mock import AsyncMock, Mock

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
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
    name = "Test Case 1"

    result_mock = Mock(id=100)
    result_mock.name = name
    mock_client.create_test_case.return_value = result_mock

    result = await service.create_test_case(project_id, name)

    assert result.id == 100
    assert result.name == name

    mock_client.create_test_case.assert_called_once()
    call_args = mock_client.create_test_case.call_args
    passed_dto = call_args[0][1]
    assert passed_dto.name == name
    assert passed_dto.project_id == project_id


@pytest.mark.asyncio
async def test_create_test_case_with_steps(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test creating a test case with steps."""
    project_id = 1
    name = "Steps Test"
    steps = [{"action": "A", "expected": "B"}]

    result_mock = Mock(id=101)
    result_mock.name = name
    mock_client.create_test_case.return_value = result_mock

    await service.create_test_case(project_id, name, steps=steps)

    mock_client.create_test_case.assert_called_once()
    passed_dto = mock_client.create_test_case.call_args[0][1]

    assert passed_dto.scenario is not None
    assert len(passed_dto.scenario.steps) == 2
    assert passed_dto.scenario.steps[0].actual_instance.body == "A"
    assert passed_dto.scenario.steps[1].actual_instance.body == "B"


@pytest.mark.asyncio
async def test_create_test_case_with_attachments(
    service: TestCaseService, mock_client: AsyncMock, mock_attachment_service: AsyncMock
) -> None:
    """Test creating a test case with attachments."""
    project_id = 1
    name = "Attachment Test"
    attachments = [{"name": "img.png", "content": "...", "content_type": "image/png"}]

    mock_attachment_service.upload_attachment.return_value = Mock(id=999, name="img.png")
    result_mock = Mock(id=102)
    result_mock.name = name
    mock_client.create_test_case.return_value = result_mock

    await service.create_test_case(project_id, name, attachments=attachments)

    # Verify attachment upload called
    mock_attachment_service.upload_attachment.assert_called_once_with(project_id, attachments[0])

    # Verify create_test_case called with correct DTO
    call_args = mock_client.create_test_case.call_args
    passed_dto = call_args[0][1]

    assert passed_dto.scenario is not None
    assert len(passed_dto.scenario.steps) == 1
    step_wrapper = passed_dto.scenario.steps[0]
    step = step_wrapper.actual_instance
    assert step.attachment_id == 999
    assert step.type == "AttachmentStep"


@pytest.mark.asyncio
async def test_create_test_case_validation_error(service: TestCaseService) -> None:
    """Test validation errors."""
    project_id = 1

    with pytest.raises(AllureValidationError, match="name is required"):
        await service.create_test_case(project_id, "")

    with pytest.raises(AllureValidationError, match="must be 255 characters or less"):
        await service.create_test_case(project_id, "a" * 256)

    with pytest.raises(AllureValidationError, match="Project ID is required"):
        await service.create_test_case(0, "Test")


@pytest.mark.asyncio
async def test_create_test_case_with_custom_fields(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test custom fields mapping."""
    project_id = 1
    name = "CF Test"
    custom_fields = {"Layer": "UI", "Priority": "High"}

    result_mock = Mock(id=103)
    result_mock.name = name
    mock_client.create_test_case.return_value = result_mock

    await service.create_test_case(project_id, name, custom_fields=custom_fields)

    call_args = mock_client.create_test_case.call_args
    passed_dto = call_args[0][1]

    assert passed_dto.custom_fields is not None
    assert len(passed_dto.custom_fields) == 2

    cf_map = {cf.custom_field.name: cf.name for cf in passed_dto.custom_fields}
    assert cf_map["Layer"] == "UI"
    assert cf_map["Priority"] == "High"


@pytest.mark.asyncio
async def test_create_test_case_with_step_attachments(
    service: TestCaseService, mock_client: AsyncMock, mock_attachment_service: AsyncMock
) -> None:
    """Test creating a test case with interleaved step attachments."""
    project_id = 1
    name = "Step Att Test"
    step_att = {"name": "s.png", "content": "x"}
    steps = [{"action": "Act", "expected": "Exp", "attachments": [step_att]}]

    mock_attachment_service.upload_attachment.return_value = Mock(id=888, name="s.png")
    result_mock = Mock(id=104)
    result_mock.name = name
    mock_client.create_test_case.return_value = result_mock

    await service.create_test_case(project_id, name, steps=steps)

    mock_attachment_service.upload_attachment.assert_called_once_with(project_id, step_att)

    call_args = mock_client.create_test_case.call_args
    passed_dto = call_args[0][1]

    # Expect: Action -> Attachment -> Expected
    s_steps = passed_dto.scenario.steps
    assert len(s_steps) == 3
    assert s_steps[0].actual_instance.body == "Act"
    assert s_steps[1].actual_instance.attachment_id == 888
    assert s_steps[2].actual_instance.body == "Exp"
