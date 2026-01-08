from unittest.mock import AsyncMock, Mock

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.generated.models import ScenarioStepCreatedResponseDto
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


@pytest.fixture
def mock_step_response() -> ScenarioStepCreatedResponseDto:
    """Mock response for create_scenario_step calls."""
    return ScenarioStepCreatedResponseDto(created_step_id=1000, scenario=None)


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
    # Scenario should be None since steps are added separately
    assert passed_dto.scenario is None


@pytest.mark.asyncio
async def test_create_test_case_with_steps(
    service: TestCaseService, mock_client: AsyncMock, mock_step_response: ScenarioStepCreatedResponseDto
) -> None:
    """Test creating a test case with steps (via separate API calls)."""
    project_id = 1
    name = "Steps Test"
    steps = [{"action": "A", "expected": "B"}]

    result_mock = Mock(id=101)
    result_mock.name = name
    mock_client.create_test_case.return_value = result_mock
    mock_client.create_scenario_step.return_value = mock_step_response

    await service.create_test_case(project_id, name, steps=steps)

    # Test case created first
    mock_client.create_test_case.assert_called_once()
    passed_dto = mock_client.create_test_case.call_args[0][1]
    assert passed_dto.scenario is None  # Steps added separately

    # Steps added via separate API calls (1 action + 1 expected = 2 calls)
    assert mock_client.create_scenario_step.call_count == 2

    # First call: action step
    first_call = mock_client.create_scenario_step.call_args_list[0]
    assert first_call.kwargs["test_case_id"] == 101
    assert first_call.kwargs["step"].body == "A"
    assert first_call.kwargs["after_id"] is None  # First step

    # Second call: expected step (child of action)
    second_call = mock_client.create_scenario_step.call_args_list[1]
    assert second_call.kwargs["test_case_id"] == 101
    assert second_call.kwargs["step"].body == "B"
    assert second_call.kwargs["step"].parent_id == 1000  # Parent is the action step


@pytest.mark.asyncio
async def test_create_test_case_with_attachments(
    service: TestCaseService,
    mock_client: AsyncMock,
    mock_attachment_service: AsyncMock,
    mock_step_response: ScenarioStepCreatedResponseDto,
) -> None:
    """Test creating a test case with attachments."""
    project_id = 1
    name = "Attachment Test"
    attachments = [{"name": "img.png", "content": "...", "content_type": "image/png"}]

    mock_attachment_service.upload_attachment.return_value = Mock(id=999, name="img.png")
    result_mock = Mock(id=102)
    result_mock.name = name
    mock_client.create_test_case.return_value = result_mock
    mock_client.create_scenario_step.return_value = mock_step_response

    await service.create_test_case(project_id, name, attachments=attachments)

    # Verify attachment upload called with test_case_id (not project_id)
    test_case_id = 102
    mock_attachment_service.upload_attachment.assert_called_once_with(test_case_id, attachments[0])

    # Verify create_test_case called (scenario is None)
    call_args = mock_client.create_test_case.call_args
    passed_dto = call_args[0][1]
    assert passed_dto.scenario is None

    # Verify attachment step was created via separate API call
    mock_client.create_scenario_step.assert_called_once()
    step_call = mock_client.create_scenario_step.call_args
    assert step_call.kwargs["step"].attachment_id == 999


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
    service: TestCaseService,
    mock_client: AsyncMock,
    mock_attachment_service: AsyncMock,
    mock_step_response: ScenarioStepCreatedResponseDto,
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
    mock_client.create_scenario_step.return_value = mock_step_response

    await service.create_test_case(project_id, name, steps=steps)

    # Verify attachment upload called with test_case_id (not project_id)
    test_case_id = 104
    mock_attachment_service.upload_attachment.assert_called_once_with(test_case_id, step_att)

    # Expect: Action -> Expected -> Attachment (3 separate create_scenario_step calls)
    assert mock_client.create_scenario_step.call_count == 3

    # Verify the order and nesting: action, expected (child), attachment (child)
    calls = mock_client.create_scenario_step.call_args_list
    
    # 1. Action
    assert calls[0].kwargs["step"].body == "Act"
    assert calls[0].kwargs["step"].parent_id is None
    
    # 2. Expected (child of Action)
    assert calls[1].kwargs["step"].body == "Exp"
    assert calls[1].kwargs["step"].parent_id == 1000
    assert calls[1].kwargs["after_id"] is None
    
    # 3. Attachment (child of Action, after Expected)
    assert calls[2].kwargs["step"].attachment_id == 888
    assert calls[2].kwargs["step"].parent_id == 1000
    assert calls[2].kwargs["after_id"] == 1000


# ==========================================
# Input Validation Tests
# ==========================================


class TestProjectIdValidation:
    """Tests for project_id validation."""

    @pytest.mark.asyncio
    async def test_project_id_zero_raises_error(self, service: TestCaseService) -> None:
        """Zero project_id should raise validation error."""
        with pytest.raises(AllureValidationError, match="Project ID is required"):
            await service.create_test_case(0, "Test")

    @pytest.mark.asyncio
    async def test_project_id_negative_raises_error(self, service: TestCaseService) -> None:
        """Negative project_id should raise validation error."""
        with pytest.raises(AllureValidationError, match="Project ID is required"):
            await service.create_test_case(-1, "Test")


class TestNameValidation:
    """Tests for test case name validation."""

    @pytest.mark.asyncio
    async def test_empty_name_raises_error(self, service: TestCaseService) -> None:
        """Empty name should raise validation error."""
        with pytest.raises(AllureValidationError, match="name is required"):
            await service.create_test_case(1, "")

    @pytest.mark.asyncio
    async def test_whitespace_only_name_raises_error(self, service: TestCaseService) -> None:
        """Whitespace-only name should raise validation error."""
        with pytest.raises(AllureValidationError, match="name is required"):
            await service.create_test_case(1, "   ")

    @pytest.mark.asyncio
    async def test_name_too_long_raises_error(self, service: TestCaseService) -> None:
        """Name exceeding 255 characters should raise validation error."""
        with pytest.raises(AllureValidationError, match="must be 255 characters or less"):
            await service.create_test_case(1, "a" * 256)


class TestStepsValidation:
    """Tests for steps validation."""

    @pytest.mark.asyncio
    async def test_steps_not_list_raises_error(self, service: TestCaseService) -> None:
        """Non-list steps should raise validation error."""
        with pytest.raises(AllureValidationError, match="Steps must be a list"):
            await service.create_test_case(1, "Test", steps="not a list")  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_step_not_dict_raises_error(self, service: TestCaseService) -> None:
        """Non-dict step should raise validation error."""
        with pytest.raises(AllureValidationError, match="Step at index 0 must be a dictionary"):
            await service.create_test_case(1, "Test", steps=["not a dict"])  # type: ignore[list-item]

    @pytest.mark.asyncio
    async def test_step_action_not_string_raises_error(self, service: TestCaseService) -> None:
        """Non-string action should raise validation error."""
        with pytest.raises(AllureValidationError, match="'action' must be a string"):
            await service.create_test_case(1, "Test", steps=[{"action": 123}])

    @pytest.mark.asyncio
    async def test_step_expected_not_string_raises_error(self, service: TestCaseService) -> None:
        """Non-string expected should raise validation error."""
        with pytest.raises(AllureValidationError, match="'expected' must be a string"):
            await service.create_test_case(1, "Test", steps=[{"action": "A", "expected": 123}])

    @pytest.mark.asyncio
    async def test_step_attachments_not_list_raises_error(self, service: TestCaseService) -> None:
        """Non-list step attachments should raise validation error."""
        with pytest.raises(AllureValidationError, match="'attachments' must be a list"):
            await service.create_test_case(1, "Test", steps=[{"action": "A", "attachments": "not a list"}])

    @pytest.mark.asyncio
    async def test_step_action_too_long_raises_error(self, service: TestCaseService) -> None:
        """Action exceeding 10000 characters should raise validation error."""
        with pytest.raises(AllureValidationError, match="'action' must be 10000 characters or less"):
            await service.create_test_case(1, "Test", steps=[{"action": "x" * 10001}])


class TestTagsValidation:
    """Tests for tags validation."""

    @pytest.mark.asyncio
    async def test_tags_not_list_raises_error(self, service: TestCaseService) -> None:
        """Non-list tags should raise validation error."""
        with pytest.raises(AllureValidationError, match="Tags must be a list"):
            await service.create_test_case(1, "Test", tags="not a list")  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_tag_not_string_raises_error(self, service: TestCaseService) -> None:
        """Non-string tag should raise validation error."""
        with pytest.raises(AllureValidationError, match="Tag at index 0 must be a string"):
            await service.create_test_case(1, "Test", tags=[123])  # type: ignore[list-item]

    @pytest.mark.asyncio
    async def test_tag_empty_raises_error(self, service: TestCaseService) -> None:
        """Empty tag should raise validation error."""
        with pytest.raises(AllureValidationError, match="Tag at index 0 cannot be empty"):
            await service.create_test_case(1, "Test", tags=[""])

    @pytest.mark.asyncio
    async def test_tag_too_long_raises_error(self, service: TestCaseService) -> None:
        """Tag exceeding 255 characters should raise validation error."""
        with pytest.raises(AllureValidationError, match="Tag at index 0 must be 255 characters or less"):
            await service.create_test_case(1, "Test", tags=["t" * 256])


class TestAttachmentsValidation:
    """Tests for attachments validation."""

    @pytest.mark.asyncio
    async def test_attachments_not_list_raises_error(self, service: TestCaseService) -> None:
        """Non-list attachments should raise validation error."""
        with pytest.raises(AllureValidationError, match="Attachments must be a list"):
            await service.create_test_case(1, "Test", attachments="not a list")  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_attachment_not_dict_raises_error(self, service: TestCaseService) -> None:
        """Non-dict attachment should raise validation error."""
        with pytest.raises(AllureValidationError, match="Attachment at index 0 must be a dictionary"):
            await service.create_test_case(1, "Test", attachments=["not a dict"])  # type: ignore[list-item]

    @pytest.mark.asyncio
    async def test_attachment_missing_content_and_url_raises_error(self, service: TestCaseService) -> None:
        """Attachment without content or url should raise validation error."""
        with pytest.raises(AllureValidationError, match="must have either 'content' or 'url' key"):
            await service.create_test_case(1, "Test", attachments=[{"name": "file.txt"}])

    @pytest.mark.asyncio
    async def test_attachment_content_without_name_raises_error(self, service: TestCaseService) -> None:
        """Attachment with content but no name should raise validation error."""
        with pytest.raises(AllureValidationError, match="must also have 'name'"):
            await service.create_test_case(1, "Test", attachments=[{"content": "base64data"}])


class TestCustomFieldsValidation:
    """Tests for custom fields validation."""

    @pytest.mark.asyncio
    async def test_custom_fields_not_dict_raises_error(self, service: TestCaseService) -> None:
        """Non-dict custom_fields should raise validation error."""
        with pytest.raises(AllureValidationError, match="Custom fields must be a dictionary"):
            await service.create_test_case(1, "Test", custom_fields=["not a dict"])  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_custom_field_value_not_string_raises_error(self, service: TestCaseService) -> None:
        """Non-string custom field value should raise validation error."""
        with pytest.raises(AllureValidationError, match="must be a string"):
            await service.create_test_case(1, "Test", custom_fields={"key": 123})  # type: ignore[dict-item]

    @pytest.mark.asyncio
    async def test_custom_field_empty_key_raises_error(self, service: TestCaseService) -> None:
        """Empty custom field key should raise validation error."""
        with pytest.raises(AllureValidationError, match="Custom field key cannot be empty"):
            await service.create_test_case(1, "Test", custom_fields={"": "value"})

