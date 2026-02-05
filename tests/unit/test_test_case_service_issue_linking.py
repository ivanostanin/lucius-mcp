from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.client import AllureClient
from src.client.generated.models import TestCaseBulkIssueDto
from src.services.test_case_service import TestCaseService


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
    async def test_add_issues_success(self, mock_bulk_api, service: TestCaseService, mock_client: AsyncMock) -> None:
        """Test adding issues to a test case."""
        test_case_id = 100
        issues = ["PROJ-123", "PROJ-456"]

        # Mock integration fetching
        mock_client.get_integrations = AsyncMock(return_value=[Mock(id=1, name="Jira")])

        # Mock Bulk API
        mock_bulk_instance = mock_bulk_api.return_value
        mock_bulk_instance.issue_add1 = AsyncMock()

        await service.add_issues_to_test_case(test_case_id, issues)

        mock_bulk_instance.issue_add1.assert_called_once()
        call_args = mock_bulk_instance.issue_add1.call_args
        request_dto = call_args[0][0]

        assert isinstance(request_dto, TestCaseBulkIssueDto)
        assert len(request_dto.issues) == 2
        assert request_dto.issues[0].name == "PROJ-123"
        assert request_dto.issues[0].integration_id == 1
        assert request_dto.selection.leafs_include == [test_case_id]

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_remove_issues_success(self, mock_bulk_api, service: TestCaseService, mock_client: AsyncMock) -> None:
        """Test removing issues from a test case."""
        test_case_id = 100
        issues = ["PROJ-123"]

        # Mock integration fetching
        mock_client.get_integrations = AsyncMock(return_value=[Mock(id=1, name="Jira")])

        # Mock current case with issues
        mock_issue = Mock()
        mock_issue.name = "PROJ-123"
        mock_issue.id = 999
        mock_case = Mock(issues=[mock_issue])
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

        # Mock integrations
        mock_client.get_integrations = AsyncMock(return_value=[Mock(id=1, name="Jira")])

        mock_bulk_instance = mock_bulk_api.return_value
        mock_bulk_instance.issue_add1 = AsyncMock()

        await service.create_test_case(name=name, issues=issues)

        mock_client.create_test_case.assert_called_once()
        mock_bulk_instance.issue_add1.assert_called_once()
        request_dto = mock_bulk_instance.issue_add1.call_args[0][0]
        assert request_dto.issues[0].name == "PROJ-123"

    @pytest.mark.asyncio
    @patch("src.client.generated.api.test_case_bulk_controller_api.TestCaseBulkControllerApi")
    async def test_update_test_case_with_issue_ops(
        self, mock_bulk_api, service: TestCaseService, mock_client: AsyncMock
    ) -> None:
        """Test updating a test case with issue operations."""
        test_case_id = 100
        from src.client.generated.models import TestCaseDto
        from src.services.test_case_service import TestCaseUpdate

        mock_bulk_instance = mock_bulk_api.return_value
        mock_bulk_instance.issue_add1 = AsyncMock()
        mock_bulk_instance.issue_remove1 = AsyncMock()

        # Mock integrations
        mock_client.get_integrations = AsyncMock(return_value=[Mock(id=1, name="Jira")])

        # 1. Test Add
        update_data = TestCaseUpdate(issues=["PROJ-123"])

        mock_case = Mock(spec=TestCaseDto)
        mock_case.project_id = 1
        service.get_test_case = AsyncMock(return_value=mock_case)
        service._prepare_field_updates = AsyncMock(return_value=({}, False))
        service._prepare_scenario_update = AsyncMock(return_value=None)

        await service.update_test_case(test_case_id, update_data)

        mock_bulk_instance.issue_add1.assert_called_once()

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
        service.get_test_case = AsyncMock(return_value=mock_case)

        update_data_clear = TestCaseUpdate(clear_issues=True)
        # reset mocks
        mock_bulk_instance.issue_remove1.reset_mock()

        await service.update_test_case(test_case_id, update_data_clear)

        mock_bulk_instance.issue_remove1.assert_called()
        req = mock_bulk_instance.issue_remove1.call_args[0][0]
        assert req.ids[0] == 777
