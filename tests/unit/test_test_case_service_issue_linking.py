from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureAPIError, AllureValidationError, TestCaseNotFoundError
from src.client.generated.exceptions import ApiException
from src.client.generated.models import TestCaseDto
from src.services.test_case_service import TestCaseService, TestCaseUpdate


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock(spec=AllureClient)
    client.api_client = Mock()
    client.get_project.return_value = 1
    return client


@pytest.fixture
def service(mock_client: AsyncMock) -> TestCaseService:
    return TestCaseService(client=mock_client)


class TestIssueLinking:
    """Tests for add_issues_to_test_case and remove_issues_from_test_case."""

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    @patch("src.services.integration_service.IntegrationService")
    async def test_add_issues_success_single_integration(
        self, mock_integration_service, mock_bulk_api, service: TestCaseService, mock_client: AsyncMock
    ) -> None:
        """Test adding issues to a test case with a single integration (auto-select)."""
        test_case_id = 100
        issues = ["PROJ-123"]

        # Mock resolve_integration_for_issues to return ID 1
        mock_int_service_instance = mock_integration_service.return_value
        mock_int_service_instance.resolve_integration_for_issues = AsyncMock(return_value=1)

        # Mock Bulk API
        mock_bulk_instance = mock_bulk_api.return_value
        mock_bulk_instance.issue_add1 = AsyncMock()
        service.get_test_case = AsyncMock(return_value=Mock(issues=[], project_id=1))

        await service.add_issues_to_test_case(test_case_id, issues)

        mock_int_service_instance.resolve_integration_for_issues.assert_called_once_with(
            integration_id=None,
            integration_name=None,
            project_id=1,
        )
        mock_bulk_instance.issue_add1.assert_called_once()
        request_dto = mock_bulk_instance.issue_add1.call_args[0][0]
        assert request_dto.issues[0].integration_id == 1

    @pytest.mark.asyncio
    @patch("src.services.integration_service.IntegrationService")
    async def test_add_issues_multiple_integrations_no_selection_fails(
        self, mock_integration_service, service: TestCaseService
    ) -> None:
        """Test error when multiple integrations exist and no selection is made (AC#7)."""
        mock_int_service_instance = mock_integration_service.return_value
        mock_int_service_instance.resolve_integration_for_issues = AsyncMock(
            side_effect=AllureValidationError("Multiple integrations found. Please specify which integration to use")
        )

        with pytest.raises(AllureValidationError, match="Multiple integrations found"):
            await service.add_issues_to_test_case(100, ["PROJ-123"])

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    @patch("src.services.integration_service.IntegrationService")
    async def test_add_issues_explicit_integration_id(
        self, mock_integration_service, mock_bulk_api, service: TestCaseService
    ) -> None:
        """Test adding issues with explicit integration_id."""
        mock_int_service_instance = mock_integration_service.return_value
        mock_int_service_instance.resolve_integration_for_issues = AsyncMock(return_value=2)
        mock_bulk_api.return_value.issue_add1 = AsyncMock()
        service.get_test_case = AsyncMock(return_value=Mock(issues=[], project_id=1))

        await service.add_issues_to_test_case(100, ["PROJ-123"], integration_id=2)

        mock_int_service_instance.resolve_integration_for_issues.assert_called_once_with(
            integration_id=2,
            integration_name=None,
            project_id=1,
        )
        request_dto = mock_bulk_api.return_value.issue_add1.call_args[0][0]
        assert request_dto.issues[0].integration_id == 2

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    @patch("src.services.integration_service.IntegrationService")
    async def test_add_issues_uses_test_case_project_context(
        self, mock_integration_service, mock_bulk_api, service: TestCaseService
    ) -> None:
        mock_case = Mock(issues=[], project_id=166)
        service.get_test_case = AsyncMock(return_value=mock_case)

        mock_int_service_instance = mock_integration_service.return_value
        mock_int_service_instance.resolve_integration_for_issues = AsyncMock(return_value=2)
        mock_bulk_api.return_value.issue_add1 = AsyncMock()

        await service.add_issues_to_test_case(100, ["PROJ-123"])

        mock_int_service_instance.resolve_integration_for_issues.assert_called_once_with(
            integration_id=None,
            integration_name=None,
            project_id=166,
        )
        request_dto = mock_bulk_api.return_value.issue_add1.call_args[0][0]
        assert request_dto.selection.project_id == 166

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_remove_issues_success(self, mock_bulk_api, service: TestCaseService, mock_client: AsyncMock) -> None:
        """Test removing issues from a test case."""
        test_case_id = 100
        issues = ["PROJ-123"]

        # Mock current case with issues
        mock_issue = Mock()
        mock_issue.name = "PROJ-123"
        mock_issue.id = 999
        mock_case = Mock(issues=[mock_issue], project_id=166)
        service.get_test_case = AsyncMock(return_value=mock_case)

        mock_bulk_instance = mock_bulk_api.return_value
        mock_bulk_instance.issue_remove1 = AsyncMock()

        await service.remove_issues_from_test_case(test_case_id, issues)

        mock_bulk_instance.issue_remove1.assert_called_once()
        request_dto = mock_bulk_instance.issue_remove1.call_args[0][0]
        # Verify IDs are passed
        from src.client.generated.models.test_case_bulk_entity_ids_dto import TestCaseBulkEntityIdsDto

        assert isinstance(request_dto, TestCaseBulkEntityIdsDto)
        assert request_dto.ids == [999]
        assert request_dto.selection.leafs_include == [test_case_id]
        assert request_dto.selection.project_id == 166

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_unlink_issue_from_test_case_matches_issue_key(self, mock_bulk_api, service: TestCaseService) -> None:
        """Unlinking resolves an issue key to its internal link ID."""
        linked_issue = Mock()
        linked_issue.id = 999
        linked_issue.name = "PROJ-123"
        service.get_test_case = AsyncMock(return_value=Mock(issues=[linked_issue], project_id=166))
        mock_bulk_api.return_value.issue_remove1 = AsyncMock()

        removed = await service.unlink_issue_from_test_case(100, "proj-123")

        assert removed is True
        request_dto = mock_bulk_api.return_value.issue_remove1.call_args.args[0]
        assert request_dto.ids == [999]
        assert request_dto.selection.leafs_include == [100]
        assert request_dto.selection.project_id == 166

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_unlink_issue_from_test_case_matches_internal_link_id(
        self, mock_bulk_api, service: TestCaseService
    ) -> None:
        """An internal issue link ID is accepted as an alternative to its key."""
        linked_issue = Mock()
        linked_issue.id = 999
        linked_issue.name = "PROJ-123"
        service.get_test_case = AsyncMock(return_value=Mock(issues=[linked_issue], project_id=166))
        mock_bulk_api.return_value.issue_remove1 = AsyncMock()

        removed = await service.unlink_issue_from_test_case(100, 999)

        assert removed is True
        assert mock_bulk_api.return_value.issue_remove1.await_count == 1

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_unlink_issue_from_test_case_rejects_ambiguous_issue_key(
        self, mock_bulk_api, service: TestCaseService
    ) -> None:
        """A duplicate issue key requires the caller to supply a link ID."""
        first_issue = Mock()
        first_issue.id = 999
        first_issue.name = "PROJ-123"
        first_issue.integration_id = 1
        second_issue = Mock()
        second_issue.id = 1000
        second_issue.name = "PROJ-123"
        second_issue.integration_id = 2
        service.get_test_case = AsyncMock(return_value=Mock(issues=[first_issue, second_issue], project_id=166))

        with pytest.raises(AllureValidationError, match="matches multiple links"):
            await service.unlink_issue_from_test_case(100, "PROJ-123")

        mock_bulk_api.return_value.issue_remove1.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_unlink_issue_from_test_case_is_idempotent_when_link_is_missing(
        self, mock_bulk_api, service: TestCaseService
    ) -> None:
        """A missing issue link is treated as an already-completed unlink."""
        service.get_test_case = AsyncMock(return_value=Mock(issues=[], project_id=166))

        removed = await service.unlink_issue_from_test_case(100, "PROJ-123")

        assert removed is False
        mock_bulk_api.return_value.issue_remove1.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_unlink_issue_from_test_case_treats_racing_404_as_idempotent(
        self, mock_bulk_api, service: TestCaseService
    ) -> None:
        """A link removed after retrieval still produces a successful no-op."""
        linked_issue = Mock()
        linked_issue.id = 999
        linked_issue.name = "PROJ-123"
        service.get_test_case = AsyncMock(
            side_effect=[
                Mock(issues=[linked_issue], project_id=166),
                Mock(issues=[], project_id=166),
            ]
        )
        mock_bulk_api.return_value.issue_remove1 = AsyncMock(side_effect=ApiException(status=404, reason="Not Found"))

        removed = await service.unlink_issue_from_test_case(100, "PROJ-123")

        assert removed is False

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_unlink_issue_from_test_case_raises_when_link_remains_after_404(
        self, mock_bulk_api, service: TestCaseService
    ) -> None:
        """A 404 is not idempotent when the refreshed case still has the link."""
        linked_issue = Mock()
        linked_issue.id = 999
        linked_issue.name = "PROJ-123"
        service.get_test_case = AsyncMock(
            side_effect=[
                Mock(issues=[linked_issue], project_id=166),
                Mock(issues=[linked_issue], project_id=166),
            ]
        )
        mock_bulk_api.return_value.issue_remove1 = AsyncMock(side_effect=ApiException(status=404, reason="Not Found"))

        with pytest.raises(AllureAPIError, match="is still linked"):
            await service.unlink_issue_from_test_case(100, "PROJ-123")

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_unlink_issue_from_test_case_propagates_racing_test_case_deletion(
        self, mock_bulk_api, service: TestCaseService
    ) -> None:
        """A 404 caused by test-case deletion is not mistaken for an absent link."""
        linked_issue = Mock()
        linked_issue.id = 999
        linked_issue.name = "PROJ-123"
        service.get_test_case = AsyncMock(
            side_effect=[
                Mock(issues=[linked_issue], project_id=166),
                TestCaseNotFoundError(test_case_id=100),
            ]
        )
        mock_bulk_api.return_value.issue_remove1 = AsyncMock(side_effect=ApiException(status=404, reason="Not Found"))

        with pytest.raises(TestCaseNotFoundError):
            await service.unlink_issue_from_test_case(100, "PROJ-123")

    @pytest.mark.asyncio
    async def test_unlink_issue_from_test_case_rejects_unavailable_issue_links(self, service: TestCaseService) -> None:
        """A missing overview must not be reported as a successful idempotent unlink."""
        service.get_test_case = AsyncMock(return_value=Mock(issues=None, project_id=166))

        with pytest.raises(AllureAPIError, match="Unable to retrieve issue links"):
            await service.unlink_issue_from_test_case(100, "PROJ-123")

    @pytest.mark.asyncio
    async def test_unlink_issue_from_test_case_validates_identifiers(self, service: TestCaseService) -> None:
        """The service rejects invalid required identifiers before calling Allure."""
        with pytest.raises(AllureValidationError, match="Test case ID"):
            await service.unlink_issue_from_test_case(0, "PROJ-123")

        with pytest.raises(AllureValidationError, match="Test case ID"):
            await service.unlink_issue_from_test_case(True, "PROJ-123")

        with pytest.raises(AllureValidationError, match="Issue ID"):
            await service.unlink_issue_from_test_case(100, " ")

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_create_test_case_with_issues(
        self, mock_bulk_api, service: TestCaseService, mock_client: AsyncMock
    ) -> None:
        """Test creating a test case with issues."""
        name = "TC with Issues"
        issues = ["PROJ-123"]

        created_case = Mock(id=100)
        mock_client.create_test_case = AsyncMock(return_value=created_case)
        service._validate_project_id = Mock()
        service._validate_name = Mock()
        service._validate_steps = Mock()
        service._validate_tags = Mock()
        service._validate_attachments = Mock()
        service._validate_custom_fields = Mock()
        service._validate_test_layer = AsyncMock(return_value=None)
        service._add_steps = AsyncMock()
        service._add_global_attachments = AsyncMock()
        service.get_test_case = AsyncMock(return_value=Mock(issues=[], project_id=1))

        # Mock integrations via IntegrationService
        with patch("src.services.integration_service.IntegrationService") as mock_integration_service:
            mock_int_service_instance = mock_integration_service.return_value
            mock_int_service_instance.resolve_integration_for_issues = AsyncMock(return_value=1)

            mock_bulk_instance = mock_bulk_api.return_value
            mock_bulk_instance.issue_add1 = AsyncMock()

            await service.create_test_case(name=name, issues=issues)

        mock_client.create_test_case.assert_called_once()
        mock_bulk_instance.issue_add1.assert_called_once()
        request_dto = mock_bulk_instance.issue_add1.call_args[0][0]
        assert request_dto.issues[0].name == "PROJ-123"
        assert request_dto.issues[0].integration_id == 1

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_update_test_case_with_issue_ops(
        self, mock_bulk_api, service: TestCaseService, mock_client: AsyncMock
    ) -> None:
        """Test updating a test case with issue operations."""
        test_case_id = 100
        mock_bulk_instance = mock_bulk_api.return_value
        mock_bulk_instance.issue_add1 = AsyncMock()
        mock_bulk_instance.issue_remove1 = AsyncMock()

        # 1. Test Add
        update_data = TestCaseUpdate(issues=["PROJ-123"])

        mock_case = Mock(spec=TestCaseDto)
        mock_case.project_id = 1
        mock_case.issues = []
        service.get_test_case = AsyncMock(return_value=mock_case)
        service._prepare_field_updates = AsyncMock(return_value=({}, False))

        # Mock integrations via IntegrationService
        with patch("src.services.integration_service.IntegrationService") as mock_integration_service:
            mock_int_service_instance = mock_integration_service.return_value
            mock_int_service_instance.resolve_integration_for_issues = AsyncMock(return_value=1)

            await service.update_test_case(test_case_id, update_data)

        mock_bulk_instance.issue_add1.assert_called_once()
        request_dto = mock_bulk_instance.issue_add1.call_args[0][0]
        assert request_dto.issues[0].integration_id == 1

        # 2. Test Remove
        mock_issue_remove = Mock()
        mock_issue_remove.name = "PROJ-456"
        mock_issue_remove.id = 888
        mock_case.issues = [mock_issue_remove]
        service.get_test_case = AsyncMock(return_value=mock_case)

        update_data_remove = TestCaseUpdate(remove_issues=["PROJ-456"])
        await service.update_test_case(test_case_id, update_data_remove)
        mock_bulk_instance.issue_remove1.assert_called_once()

        # 3. Test Clear
        issue_old = Mock()
        issue_old.name = "PROJ-789"
        issue_old.id = 777
        mock_case.issues = [issue_old]
        mock_case.project_id = 1  # Ensure all required attributes for update_test_case
        service.get_test_case = AsyncMock(return_value=mock_case)

        update_data_clear = TestCaseUpdate(clear_issues=True)
        # reset mocks
        mock_bulk_instance.issue_remove1.reset_mock()

        await service.update_test_case(test_case_id, update_data_clear)

        mock_bulk_instance.issue_remove1.assert_called()
        req = mock_bulk_instance.issue_remove1.call_args[0][0]
        assert req.ids[0] == 777

    @pytest.mark.asyncio
    async def test_validate_issue_keys_invalid_format(self, service: TestCaseService) -> None:
        """Test that invalid issue keys raise AllureValidationError (AC#5)."""
        invalid_keys = ["PROJ123", "PROJ-", "123-PROJ", "INVALID_KEY"]

        with pytest.raises(AllureValidationError) as exc:
            await service._build_issue_dtos(invalid_keys)

        assert "Invalid issue keys provided" in str(exc.value)
        assert "expected PROJECT-123" in str(exc.value)
        for key in invalid_keys:
            assert key in str(exc.value)

    @pytest.mark.asyncio
    async def test_validate_issue_keys_too_long(self, service: TestCaseService) -> None:
        """Test that too long issue keys raise AllureValidationError."""
        long_key = "A" * 51 + "-123"

        with pytest.raises(AllureValidationError, match="too long"):
            await service._build_issue_dtos([long_key])

    @pytest.mark.asyncio
    @patch("src.services.integration_service.IntegrationService")
    async def test_build_issue_dtos_normalizes_to_uppercase(
        self, mock_integration_service, service: TestCaseService
    ) -> None:
        """Test that issue keys are normalized to uppercase."""
        mock_int_service_instance = mock_integration_service.return_value
        mock_int_service_instance.resolve_integration_for_issues = AsyncMock(return_value=1)

        dtos = await service._build_issue_dtos(["proj-123", "abc-456"])
        assert dtos[0].name == "PROJ-123"
        assert dtos[1].name == "ABC-456"

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_add_issues_idempotency(self, mock_bulk_api, service: TestCaseService) -> None:
        """Test that already linked issues are filtered out (AC#8)."""
        test_case_id = 100
        issues = ["PROJ-123", "NEW-456"]

        # Mock current case with PROJ-123 already linked
        mock_issue = Mock()
        mock_issue.name = "PROJ-123"
        mock_issue.integration_id = 1
        mock_issue.id = 999
        mock_case = Mock(issues=[mock_issue], project_id=1)
        service.get_test_case = AsyncMock(return_value=mock_case)

        mock_bulk_instance = mock_bulk_api.return_value
        mock_bulk_instance.issue_add1 = AsyncMock()

        # Mock build_issue_dtos to return DTOs for both
        with patch.object(service, "_build_issue_dtos") as mock_build:
            from src.client.generated.models import IssueDto

            mock_build.return_value = [
                IssueDto(name="PROJ-123", integration_id=1),
                IssueDto(name="NEW-456", integration_id=1),
            ]

            await service.add_issues_to_test_case(test_case_id, issues)

        # Should only call bulk API with NEW-456
        mock_bulk_instance.issue_add1.assert_called_once()
        request_dto = mock_bulk_instance.issue_add1.call_args[0][0]
        assert len(request_dto.issues) == 1
        assert request_dto.issues[0].name == "NEW-456"

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_add_issues_same_key_different_integration_not_filtered(
        self, mock_bulk_api, service: TestCaseService
    ) -> None:
        """Test that idempotency comparison includes integration_id."""
        test_case_id = 100
        issues = ["PROJ-123"]

        mock_issue = Mock()
        mock_issue.name = "PROJ-123"
        mock_issue.integration_id = 2
        mock_case = Mock(issues=[mock_issue], project_id=1)
        service.get_test_case = AsyncMock(return_value=mock_case)

        mock_bulk_instance = mock_bulk_api.return_value
        mock_bulk_instance.issue_add1 = AsyncMock()

        with patch.object(service, "_build_issue_dtos") as mock_build:
            from src.client.generated.models import IssueDto

            mock_build.return_value = [IssueDto(name="PROJ-123", integration_id=1)]

            await service.add_issues_to_test_case(test_case_id, issues)

        mock_bulk_instance.issue_add1.assert_called_once()
        request_dto = mock_bulk_instance.issue_add1.call_args[0][0]
        assert len(request_dto.issues) == 1
        assert request_dto.issues[0].name == "PROJ-123"
        assert request_dto.issues[0].integration_id == 1

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_clear_issues_uses_test_case_project_context(self, mock_bulk_api, service: TestCaseService) -> None:
        """clear_issues should use the test case's own project_id for the bulk API call."""
        test_case_id = 100

        issue1 = Mock()
        issue1.name = "PROJ-100"
        issue1.id = 1001
        issue2 = Mock()
        issue2.name = "PROJ-200"
        issue2.id = 2001

        mock_case = Mock(issues=[issue1, issue2], project_id=166)
        mock_case.test_layer = None
        mock_case.description = None
        mock_case.precondition = None
        mock_case.tags = None
        mock_case.custom_fields = None
        mock_case.automated = None
        mock_case.status = None
        mock_case.workflow_id = None
        mock_case.links = None
        mock_case.expected_result = None
        mock_case.attachments = None
        mock_case.name = "Test"
        mock_case.id = test_case_id
        service.get_test_case = AsyncMock(return_value=mock_case)
        service._prepare_field_updates = AsyncMock(return_value=({}, False))

        mock_bulk_instance = mock_bulk_api.return_value
        mock_bulk_instance.issue_remove1 = AsyncMock()

        update_data = TestCaseUpdate(clear_issues=True)
        await service.update_test_case(test_case_id, update_data)

        mock_bulk_instance.issue_remove1.assert_called_once()
        req = mock_bulk_instance.issue_remove1.call_args[0][0]
        assert req.selection.project_id == 166
        assert sorted(req.ids) == [1001, 2001]

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_remove_issues_uses_test_case_project_context(self, mock_bulk_api, service: TestCaseService) -> None:
        """remove_issues should use the test case's own project_id for the bulk API call."""
        test_case_id = 100

        mock_issue = Mock()
        mock_issue.name = "PROJ-123"
        mock_issue.id = 999
        mock_case = Mock(issues=[mock_issue], project_id=166)
        mock_case.test_layer = None
        mock_case.description = None
        mock_case.precondition = None
        mock_case.tags = None
        mock_case.custom_fields = None
        mock_case.automated = None
        mock_case.status = None
        mock_case.workflow_id = None
        mock_case.links = None
        mock_case.expected_result = None
        mock_case.attachments = None
        mock_case.name = "Test"
        mock_case.id = test_case_id
        service.get_test_case = AsyncMock(return_value=mock_case)
        service._prepare_field_updates = AsyncMock(return_value=({}, False))

        mock_bulk_instance = mock_bulk_api.return_value
        mock_bulk_instance.issue_remove1 = AsyncMock()

        update_data = TestCaseUpdate(remove_issues=["PROJ-123"])
        await service.update_test_case(test_case_id, update_data)

        mock_bulk_instance.issue_remove1.assert_called_once()
        req = mock_bulk_instance.issue_remove1.call_args[0][0]
        assert req.selection.project_id == 166

    @pytest.mark.asyncio
    @patch("src.services.integration_service.IntegrationService")
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_add_issues_in_update_uses_test_case_project_context(
        self, mock_bulk_api, mock_integration_service, service: TestCaseService
    ) -> None:
        """add_issues in update_test_case should use the test case's own project_id."""
        test_case_id = 100

        mock_case = Mock(issues=[], project_id=166)
        mock_case.test_layer = None
        mock_case.description = None
        mock_case.precondition = None
        mock_case.tags = None
        mock_case.custom_fields = None
        mock_case.automated = None
        mock_case.status = None
        mock_case.workflow_id = None
        mock_case.links = None
        mock_case.expected_result = None
        mock_case.attachments = None
        mock_case.name = "Test"
        mock_case.id = test_case_id
        service.get_test_case = AsyncMock(return_value=mock_case)
        service._prepare_field_updates = AsyncMock(return_value=({}, False))

        mock_int_service_instance = mock_integration_service.return_value
        mock_int_service_instance.resolve_integration_for_issues = AsyncMock(return_value=1)
        mock_bulk_instance = mock_bulk_api.return_value
        mock_bulk_instance.issue_add1 = AsyncMock()

        update_data = TestCaseUpdate(issues=["PROJ-123"])
        await service.update_test_case(test_case_id, update_data)

        # Integration resolution should use project_id=166 from the test case
        mock_int_service_instance.resolve_integration_for_issues.assert_called_once_with(
            integration_id=None,
            integration_name=None,
            project_id=166,
        )
        req = mock_bulk_instance.issue_add1.call_args[0][0]
        assert req.selection.project_id == 166
