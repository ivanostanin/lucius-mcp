from unittest.mock import AsyncMock, Mock

import pytest

from src.client import (
    AllureClient,
    AttachmentStepDtoWithName,
    BodyStepDtoWithSteps,
)
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError
from src.client.generated.models import (
    CustomFieldDto,
    CustomFieldProjectDto,
    CustomFieldProjectWithValuesDto,
    ScenarioStepCreatedResponseDto,
    SharedStepScenarioDtoStepsInner,
    TestCaseDto,
    TestCasePatchV2Dto,
    TestCaseScenarioV2Dto,
)
from src.services.attachment_service import AttachmentService
from src.services.test_case_service import TestCaseService, TestCaseUpdate


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock(spec=AllureClient)
    client.api_client = Mock()
    client.get_project.return_value = 1
    return client


@pytest.fixture
def mock_attachment_service() -> AsyncMock:
    return AsyncMock(spec=AttachmentService)


@pytest.fixture
def service(mock_client: AsyncMock, mock_attachment_service: AsyncMock) -> TestCaseService:
    return TestCaseService(
        client=mock_client,
        attachment_service=mock_attachment_service,
    )


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

    result = await service.create_test_case(name)

    assert result.id == 100
    assert result.name == name

    mock_client.create_test_case.assert_called_once()
    call_args = mock_client.create_test_case.call_args
    passed_dto = call_args[0][0]
    assert passed_dto.name == name
    assert passed_dto.project_id == project_id


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

    await service.create_test_case(name, steps=steps)

    # Test case created first
    mock_client.create_test_case.assert_called_once()
    passed_dto = mock_client.create_test_case.call_args[0][0]
    assert passed_dto.project_id == project_id

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

    await service.create_test_case(name, attachments=attachments)

    # Verify attachment upload called with test_case_id (not project_id)
    test_case_id = 102
    mock_attachment_service.upload_attachment.assert_called_once_with(test_case_id, attachments[0])

    # Verify create_test_case called with project_id
    call_args = mock_client.create_test_case.call_args
    passed_dto = call_args[0][0]
    assert passed_dto.project_id == project_id

    # Verify attachment step was created via separate API call
    mock_client.create_scenario_step.assert_called_once()
    step_call = mock_client.create_scenario_step.call_args
    assert step_call.kwargs["step"].attachment_id == 999


@pytest.mark.asyncio
async def test_create_test_case_validation_error(service: TestCaseService) -> None:
    """Test validation errors."""

    with pytest.raises(AllureValidationError, match="name is required"):
        await service.create_test_case("")

    with pytest.raises(AllureValidationError, match="255 characters or less"):
        await service.create_test_case("a" * 256)

    service._project_id = 0
    with pytest.raises(AllureValidationError, match="Project ID is required"):
        await service.create_test_case("Test")


@pytest.mark.asyncio
async def test_create_test_case_with_custom_fields(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test custom fields mapping with resolution."""
    name = "CF Test"
    custom_fields = {"Layer": "UI", "Priority": "High"}

    # Mock custom field resolution directly on the client
    mock_client.get_custom_fields_with_values.return_value = [
        CustomFieldProjectWithValuesDto(
            custom_field=CustomFieldProjectDto(custom_field=CustomFieldDto(id=10, name="Layer"))
        ),
        CustomFieldProjectWithValuesDto(
            custom_field=CustomFieldProjectDto(custom_field=CustomFieldDto(id=20, name="Priority"))
        ),
    ]

    result_mock = Mock(id=103)
    result_mock.name = name
    mock_client.create_test_case.return_value = result_mock

    await service.create_test_case(name, custom_fields=custom_fields)

    # Verify resolution call
    mock_client.get_custom_fields_with_values.assert_called_once_with(1)

    # Verify test case creation DTO
    call_args = mock_client.create_test_case.call_args
    passed_dto = call_args[0][0]

    assert passed_dto.custom_fields is not None
    assert len(passed_dto.custom_fields) == 2

    cf_map = {cf.custom_field.name: (cf.custom_field.id, cf.name) for cf in passed_dto.custom_fields}
    assert cf_map["Layer"] == (10, "UI")
    assert cf_map["Priority"] == (20, "High")


@pytest.mark.asyncio
async def test_create_test_case_custom_field_not_found(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test error when custom field is not found in project."""
    name = "CF Fail"
    custom_fields = {"Unknown": "Value"}

    # Mock custom field resolution directly on the client
    mock_client.get_custom_fields_with_values.return_value = []

    # Expect the new aggregated error format
    with pytest.raises(AllureValidationError, match="The following custom fields were not found"):
        await service.create_test_case(name, custom_fields=custom_fields)


@pytest.mark.asyncio
async def test_create_test_case_with_step_attachments(
    service: TestCaseService,
    mock_client: AsyncMock,
    mock_attachment_service: AsyncMock,
    mock_step_response: ScenarioStepCreatedResponseDto,
) -> None:
    """Test creating a test case with interleaved step attachments."""
    name = "Step Att Test"
    step_att = {"name": "s.png", "content": "x"}
    steps = [{"action": "Act", "expected": "Exp", "attachments": [step_att]}]

    mock_attachment_service.upload_attachment.return_value = Mock(id=888, name="s.png")
    result_mock = Mock(id=104)
    result_mock.name = name
    mock_client.create_test_case.return_value = result_mock
    mock_client.create_scenario_step.return_value = mock_step_response

    await service.create_test_case(name, steps=steps)

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
        service._project_id = 0
        with pytest.raises(AllureValidationError, match="Project ID is required"):
            await service.create_test_case("Test")

    @pytest.mark.asyncio
    async def test_project_id_negative_raises_error(self, service: TestCaseService) -> None:
        """Negative project_id should raise validation error."""
        service._project_id = -1
        with pytest.raises(AllureValidationError, match="Project ID is required"):
            await service.create_test_case("Test")


class TestNameValidation:
    """Tests for test case name validation."""

    @pytest.mark.asyncio
    async def test_empty_name_raises_error(self, service: TestCaseService) -> None:
        """Empty name should raise validation error."""
        with pytest.raises(AllureValidationError, match="name is required"):
            await service.create_test_case("")

    @pytest.mark.asyncio
    async def test_whitespace_only_name_raises_error(self, service: TestCaseService) -> None:
        """Whitespace-only name should raise validation error."""
        with pytest.raises(AllureValidationError, match="name is required"):
            await service.create_test_case("   ")

    @pytest.mark.asyncio
    async def test_name_too_long_raises_error(self, service: TestCaseService) -> None:
        """Name exceeding 255 characters should raise validation error."""
        with pytest.raises(AllureValidationError, match="255 characters or less"):
            await service.create_test_case("a" * 256)


class TestStepsValidation:
    """Tests for steps validation."""

    @pytest.mark.asyncio
    async def test_steps_not_list_raises_error(self, service: TestCaseService) -> None:
        """Non-list steps should raise validation error."""
        with pytest.raises(AllureValidationError, match="Steps must be a list"):
            await service.create_test_case("Test", steps="not a list")  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_step_not_dict_raises_error(self, service: TestCaseService) -> None:
        """Non-dict step should raise validation error."""
        with pytest.raises(AllureValidationError, match="Step at index 0 must be a dictionary"):
            await service.create_test_case("Test", steps=["not a dict"])  # type: ignore[list-item]

    @pytest.mark.asyncio
    async def test_step_action_not_string_raises_error(self, service: TestCaseService) -> None:
        """Non-string action should raise validation error."""
        with pytest.raises(AllureValidationError, match="'action' must be a string"):
            await service.create_test_case("Test", steps=[{"action": 123}])

    @pytest.mark.asyncio
    async def test_step_expected_not_string_raises_error(self, service: TestCaseService) -> None:
        """Non-string expected should raise validation error."""
        with pytest.raises(AllureValidationError, match="'expected' must be a string"):
            await service.create_test_case("Test", steps=[{"action": "A", "expected": 123}])

    @pytest.mark.asyncio
    async def test_step_attachments_not_list_raises_error(self, service: TestCaseService) -> None:
        """Non-list step attachments should raise validation error."""
        with pytest.raises(AllureValidationError, match="'attachments' must be a list"):
            await service.create_test_case("Test", steps=[{"action": "A", "attachments": "not a list"}])

    @pytest.mark.asyncio
    async def test_step_action_too_long_raises_error(self, service: TestCaseService) -> None:
        """Action exceeding 10000 characters should raise validation error."""
        with pytest.raises(AllureValidationError, match="'action' must be 10000 characters or less"):
            await service.create_test_case("Test", steps=[{"action": "x" * 10001}])


class TestTagsValidation:
    """Tests for tags validation."""

    @pytest.mark.asyncio
    async def test_tags_not_list_raises_error(self, service: TestCaseService) -> None:
        """Non-list tags should raise validation error."""
        with pytest.raises(AllureValidationError, match="Tags must be a list"):
            await service.create_test_case("Test", tags="not a list")  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_tag_not_string_raises_error(self, service: TestCaseService) -> None:
        """Non-string tag should raise validation error."""
        with pytest.raises(AllureValidationError, match="Tag at index 0 must be a string"):
            await service.create_test_case("Test", tags=[123])  # type: ignore[list-item]

    @pytest.mark.asyncio
    async def test_tag_empty_raises_error(self, service: TestCaseService) -> None:
        """Empty tag should raise validation error."""
        with pytest.raises(AllureValidationError, match="Tag at index 0 cannot be empty"):
            await service.create_test_case("Test", tags=[""])

    @pytest.mark.asyncio
    async def test_tag_too_long_raises_error(self, service: TestCaseService) -> None:
        """Tag exceeding 255 characters should raise validation error."""
        with pytest.raises(AllureValidationError, match="Tag at index 0 must be 255 characters or less"):
            await service.create_test_case("Test", tags=["t" * 256])


class TestAttachmentsValidation:
    """Tests for attachments validation."""

    @pytest.mark.asyncio
    async def test_attachments_not_list_raises_error(self, service: TestCaseService) -> None:
        """Non-list attachments should raise validation error."""
        with pytest.raises(AllureValidationError, match="Attachments must be a list"):
            await service.create_test_case("Test", attachments="not a list")  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_attachment_not_dict_raises_error(self, service: TestCaseService) -> None:
        """Non-dict attachment should raise validation error."""
        with pytest.raises(AllureValidationError, match="Attachment at index 0 must be a dictionary"):
            await service.create_test_case("Test", attachments=["not a dict"])  # type: ignore[list-item]

    @pytest.mark.asyncio
    async def test_attachment_missing_content_and_url_raises_error(self, service: TestCaseService) -> None:
        """Attachment without content or url should raise validation error."""
        with pytest.raises(AllureValidationError, match="must have either 'content' or 'url' key"):
            await service.create_test_case("Test", attachments=[{"name": "file.txt"}])

    @pytest.mark.asyncio
    async def test_attachment_content_without_name_raises_error(self, service: TestCaseService) -> None:
        """Attachment with content but no name should raise validation error."""
        with pytest.raises(AllureValidationError, match="must also have 'name'"):
            await service.create_test_case("Test", attachments=[{"content": "base64data"}])


class TestCustomFieldsValidation:
    """Tests for custom fields validation."""

    @pytest.mark.asyncio
    async def test_custom_fields_not_dict_raises_error(self, service: TestCaseService) -> None:
        """Non-dict custom_fields should raise validation error."""
        with pytest.raises(AllureValidationError, match="Custom fields must be a dictionary"):
            await service.create_test_case("Test", custom_fields=["not a dict"])  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_custom_field_value_not_string_raises_error(self, service: TestCaseService) -> None:
        """Non-string custom field value should raise validation error."""
        with pytest.raises(AllureValidationError, match="must be a string"):
            await service.create_test_case("Test", custom_fields={"key": 123})  # type: ignore[dict-item]

    @pytest.mark.asyncio
    async def test_custom_field_empty_key_raises_error(self, service: TestCaseService) -> None:
        """Empty custom field key should raise validation error."""
        with pytest.raises(AllureValidationError, match="Custom field key cannot be empty"):
            await service.create_test_case("Test", custom_fields={"": "value"})


@pytest.mark.asyncio
async def test_create_test_case_rollback_on_failure(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test that test case is deleted (rolled back) if step creation fails."""
    name = "Rollback Test"
    steps = [{"action": "Fail", "expected": "Soon"}]

    # 1. Successful test case creation
    result_mock = Mock(id=500)
    result_mock.name = name
    mock_client.create_test_case.return_value = result_mock

    # 2. Failed step creation
    mock_client.create_scenario_step.side_effect = Exception("API Error during step creation")

    # 3. Call and expect rollback error
    with pytest.raises(AllureAPIError, match="Test case creation failed and was rolled back"):
        await service.create_test_case(name, steps=steps)

    # 4. Verify original creation AND rollback deletion were called
    mock_client.create_test_case.assert_called_once()
    mock_client.delete_test_case.assert_called_once_with(500)


@pytest.fixture
def mock_scenario_response() -> TestCaseScenarioV2Dto:
    """Mock response for get_test_case_scenario."""
    body_step = SharedStepScenarioDtoStepsInner(
        actual_instance=BodyStepDtoWithSteps(type="BodyStepDto", body="Existing Step")
    )
    att_step = SharedStepScenarioDtoStepsInner(
        actual_instance=AttachmentStepDtoWithName(type="AttachmentStepDto", attachment_id=1, name="Existing Att")
    )
    return TestCaseScenarioV2Dto(steps=[body_step, att_step])


class TestUpdateTestCase:
    """Tests for updating test cases."""

    @pytest.mark.asyncio
    async def test_update_simple_fields(self, service: TestCaseService, mock_client: AsyncMock) -> None:
        """Test updating simple fields (name, description)."""
        test_case_id = 999
        current_case = TestCaseDto(id=test_case_id, name="Old Name", description="Old Desc")
        mock_client.get_test_case.return_value = current_case
        mock_client.update_test_case.return_value = TestCaseDto(
            id=test_case_id, name="New Name", description="New Desc"
        )

        data = TestCaseUpdate(name="New Name", description="New Desc")
        result = await service.update_test_case(test_case_id, data)

        assert result.name == "New Name"

        # Verify call
        mock_client.update_test_case.assert_called_once()
        patch_dto: TestCasePatchV2Dto = mock_client.update_test_case.call_args[0][1]
        assert patch_dto.name == "New Name"
        assert patch_dto.description == "New Desc"
        assert patch_dto.scenario is None  # Scenario untouched

    @pytest.mark.asyncio
    async def test_update_idempotency_no_changes(self, service: TestCaseService, mock_client: AsyncMock) -> None:
        """Test that update is skipped if no changes are detected."""
        test_case_id = 999
        current_case = TestCaseDto(id=test_case_id, name="Same Name")
        mock_client.get_test_case.return_value = current_case

        data = TestCaseUpdate(name="Same Name")
        result = await service.update_test_case(test_case_id, data)

        assert result is current_case
        mock_client.update_test_case.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_steps_preserves_attachments(
        self, service: TestCaseService, mock_client: AsyncMock, mock_scenario_response: TestCaseScenarioV2Dto
    ) -> None:
        """Test updating steps only preserve existing global attachments."""
        test_case_id = 999
        mock_client.get_test_case.return_value = TestCaseDto(id=test_case_id)
        mock_client.get_test_case_scenario.return_value = mock_scenario_response
        mock_client.update_test_case.return_value = TestCaseDto(id=test_case_id)
        mock_client.create_scenario_step.return_value = ScenarioStepCreatedResponseDto(
            created_step_id=1000, scenario=None
        )

        # New Steps
        steps = [{"action": "New Action"}]
        data = TestCaseUpdate(steps=steps)

        await service.update_test_case(test_case_id, data)

        # get_test_case_scenario is called twice: once in _get_existing_steps_to_preserve
        # and once in _recreate_scenario for rollback backup
        assert mock_client.get_test_case_scenario.call_count == 2

        # Verify scenario was cleared in update_test_case (called in _recreate_scenario)
        assert mock_client.update_test_case.call_count >= 1
        # First call clears scenario
        clear_call = mock_client.update_test_case.call_args_list[0]
        clear_dto: TestCasePatchV2Dto = clear_call[0][1]
        assert clear_dto.scenario is not None
        assert clear_dto.scenario.steps == []

        # Verify create_scenario_step was called for new action and preserved attachment
        assert mock_client.create_scenario_step.call_count == 2

    @pytest.mark.asyncio
    async def test_update_attachments_preserves_steps(
        self,
        service: TestCaseService,
        mock_client: AsyncMock,
        mock_scenario_response: TestCaseScenarioV2Dto,
        mock_attachment_service: AsyncMock,
    ) -> None:
        """Test updating attachments only preserves existing steps."""
        test_case_id = 999
        mock_client.get_test_case.return_value = TestCaseDto(id=test_case_id)
        mock_client.get_test_case_scenario.return_value = mock_scenario_response
        mock_client.update_test_case.return_value = TestCaseDto(id=test_case_id)
        mock_client.create_scenario_step.return_value = ScenarioStepCreatedResponseDto(
            created_step_id=1001, scenario=None
        )

        mock_attachment_service.upload_attachment.return_value = Mock(id=200, name="New Att")

        # New Attachments
        attachments = [{"name": "new.png", "content": "base64"}]
        data = TestCaseUpdate(attachments=attachments)

        await service.update_test_case(test_case_id, data)

        # Verify scenario was cleared
        assert mock_client.update_test_case.call_count >= 1
        clear_call = mock_client.update_test_case.call_args_list[0]
        clear_dto: TestCasePatchV2Dto = clear_call[0][1]
        assert clear_dto.scenario is not None
        assert clear_dto.scenario.steps == []

        # Verify attachment was uploaded
        mock_attachment_service.upload_attachment.assert_called_once()

        # Verify create_scenario_step was called:
        # Existing body steps are preserved, and one new attachment step is added.
        # We expect 2 calls: preserved body step + new attachment step.
        assert mock_client.create_scenario_step.call_count == 2

    @pytest.mark.asyncio
    async def test_update_nested_steps(
        self, service: TestCaseService, mock_client: AsyncMock, mock_scenario_response: TestCaseScenarioV2Dto
    ) -> None:
        """Test updating steps with nested hierarchy."""
        test_case_id = 999
        mock_client.get_test_case.return_value = TestCaseDto(id=test_case_id)
        mock_client.get_test_case_scenario.return_value = mock_scenario_response
        mock_client.update_test_case.return_value = TestCaseDto(id=test_case_id)

        # Setup mock for create_scenario_step to return increasing IDs
        step_id_counter = [2000]  # Use list to allow mutation in nested function

        def create_step_side_effect(*args, **kwargs):
            step_id = step_id_counter[0]
            step_id_counter[0] += 1
            return ScenarioStepCreatedResponseDto(created_step_id=step_id, scenario=None)

        mock_client.create_scenario_step.side_effect = create_step_side_effect

        # Nested Steps Structure
        steps = [
            {
                "action": "Parent",
                "steps": [{"action": "Child 1"}, {"action": "Child 2", "steps": [{"action": "Grandchild"}]}],
            }
        ]
        data = TestCaseUpdate(steps=steps)

        await service.update_test_case(test_case_id, data)

        # Verify scenario was cleared
        assert mock_client.update_test_case.call_count >= 1

        # Verify create_scenario_step was called for Parent, Child 1, Child 2, Grandchild, and preserved attachment
        # Total: 5 calls
        assert mock_client.create_scenario_step.call_count == 5

        # Verify the hierarchy by checking parent_id relationships
        calls = mock_client.create_scenario_step.call_args_list

        # Parent should have no parent_id
        parent_call = calls[0]
        assert parent_call.kwargs["step"].parent_id is None
        assert parent_call.kwargs["step"].body == "Parent"

        # Child 1 should have Parent as parent
        child1_call = calls[1]
        assert child1_call.kwargs["step"].parent_id == 2000  # Parent's ID
        assert child1_call.kwargs["step"].body == "Child 1"

        # Child 2 should have Parent as parent
        child2_call = calls[2]
        assert child2_call.kwargs["step"].parent_id == 2000  # Parent's ID
        assert child2_call.kwargs["step"].body == "Child 2"

        # Grandchild should have Child 2 as parent
        grandchild_call = calls[3]
        assert grandchild_call.kwargs["step"].parent_id == 2002  # Child 2's ID
        assert grandchild_call.kwargs["step"].body == "Grandchild"

        # Final call preserves existing attachment
        preserved_call = calls[4]
        assert preserved_call.kwargs["step"].attachment_id == 1

    @pytest.mark.asyncio
    async def test_recreate_scenario_rollback(self, service: TestCaseService, mock_client: AsyncMock) -> None:
        """Test scenario recreation rollback on failure."""
        test_case_id = 999

        # 1. Setup mock current scenario (to be restored)
        step = SharedStepScenarioDtoStepsInner(
            actual_instance=BodyStepDtoWithSteps(type="BodyStepDto", body="Old Step")
        )
        current_scenario = TestCaseScenarioV2Dto(steps=[step])
        mock_client.get_test_case_scenario.return_value = current_scenario

        # 2. Mock update_test_case for clearing (success first time, success on rollback)
        mock_client.update_test_case.return_value = TestCaseDto(id=test_case_id)

        # 3. Mock recursive add step to fail
        # This mocks the creation of the NEW steps failing
        service._recursive_add_step = AsyncMock(side_effect=Exception("API Fail"))  # type: ignore[method-assign]

        # 4. Call update with new steps
        data = TestCaseUpdate(steps=[{"action": "New Step"}])

        with pytest.raises(AllureAPIError, match="Failed to recreate scenario"):
            await service.update_test_case(test_case_id, data)

        # 5. Verify Rollback behavior
        # Should have called update_test_case to clear scenario twice:
        # 1. Initial clear
        # 2. Rollback clear
        assert mock_client.update_test_case.call_count == 2

        # Verify get_test_case_scenario was called twice:
        # 1. In _get_existing_steps_to_preserve (to check for steps to preserve)
        # 2. In _recreate_scenario (to fetch backup scenario)
        assert mock_client.get_test_case_scenario.call_count == 2


@pytest.mark.asyncio
@pytest.mark.test_id("1.5-UNIT-001")
async def test_delete_test_case_success(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test ID: 1.5-UNIT-001 - Successful deletion of a test case (P1)"""
    test_case_id = 123
    mock_client.get_test_case.return_value = TestCaseDto(id=test_case_id, name="To Delete")
    mock_client.delete_test_case.return_value = None

    result = await service.delete_test_case(test_case_id)

    assert result.test_case_id == test_case_id
    assert result.status == "archived"
    assert result.name == "To Delete"
    assert "archived" in result.message

    mock_client.get_test_case.assert_called_once_with(test_case_id)
    mock_client.delete_test_case.assert_called_once_with(test_case_id)


@pytest.mark.asyncio
@pytest.mark.test_id("1.5-UNIT-002")
async def test_delete_test_case_already_deleted(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test ID: 1.5-UNIT-002 - Idempotency of Delete (already deleted via 404) (P1)"""
    test_case_id = 123

    # Simulate API 404
    mock_client.get_test_case.side_effect = AllureNotFoundError("Not found")

    result = await service.delete_test_case(test_case_id)

    assert result.test_case_id == test_case_id
    assert result.status == "already_deleted"
    assert "already archived" in result.message

    mock_client.get_test_case.assert_called_once_with(test_case_id)
    mock_client.delete_test_case.assert_not_called()

    mock_client.get_test_case.assert_called_once_with(test_case_id)
    mock_client.delete_test_case.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.test_id("1.5-UNIT-003")
async def test_delete_test_case_already_archived_status(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test ID: 1.5-UNIT-003 - Idempotency when test case has 'Archived' status (P1)"""
    test_case_id = 124
    # Mock existing but archived case
    archived_case = Mock(spec=TestCaseDto)
    archived_case.id = test_case_id
    archived_case.name = "Archived Case"
    archived_case.status = Mock()
    archived_case.status.name = "Archived"

    mock_client.get_test_case.return_value = archived_case

    result = await service.delete_test_case(test_case_id)

    assert result.status == "already_deleted"
    assert "already archived" in result.message

    mock_client.get_test_case.assert_called_once_with(test_case_id)
    # importantly, delete should NOT be called
    mock_client.delete_test_case.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.test_id("1.5-UNIT-004")
async def test_delete_test_case_failure(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test ID: 1.5-UNIT-004 - Failure during deletion (error handling) (P1)"""
    test_case_id = 123
    mock_client.get_test_case.return_value = TestCaseDto(id=test_case_id, name="Fail Delete")
    mock_client.delete_test_case.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        await service.delete_test_case(test_case_id)
