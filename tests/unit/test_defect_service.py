"""Unit tests for DefectService."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.client.generated.exceptions import ApiException
from src.client.generated.models.defect_dto import DefectDto
from src.client.generated.models.defect_matcher_dto import DefectMatcherDto
from src.client.generated.models.defect_overview_dto import DefectOverviewDto
from src.client.generated.models.defect_row_dto import DefectRowDto
from src.client.generated.models.issue_dto import IssueDto
from src.client.generated.models.status_dto import StatusDto
from src.client.generated.models.test_case_row_dto import TestCaseRowDto
from src.services.defect_service import DefectService


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock(spec=AllureClient)
    client.api_client = Mock()
    client.get_project.return_value = 1
    return client


@pytest.fixture
def service(mock_client: AsyncMock) -> DefectService:
    return DefectService(mock_client)


# ── Defect CRUD ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_defect(service: DefectService) -> None:
    created = DefectDto(id=10, name="Bug A", project_id=1)

    with patch("src.services.defect_service.DefectControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        mock_api.create45 = AsyncMock(return_value=created)

        result = await service.create_defect(name="Bug A", description="desc")

        assert result.id == 10
        assert result.name == "Bug A"
        dto = mock_api.create45.call_args.kwargs["defect_create_dto"]
        assert dto.name == "Bug A"
        assert dto.description == "desc"
        assert dto.project_id == 1


@pytest.mark.asyncio
async def test_create_defect_empty_name(service: DefectService) -> None:
    with pytest.raises(AllureValidationError, match="required"):
        await service.create_defect(name="")


@pytest.mark.asyncio
async def test_get_defect(service: DefectService) -> None:
    defect = DefectDto(id=10, name="Bug A")

    with patch("src.services.defect_service.DefectControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        mock_api.find_by_id1 = AsyncMock(return_value=defect)

        result = await service.get_defect(10)

        assert result.id == 10
        mock_api.find_by_id1.assert_called_once_with(id=10)


@pytest.mark.asyncio
async def test_get_defect_not_found(service: DefectService) -> None:
    with patch("src.services.defect_service.DefectControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        mock_api.find_by_id1 = AsyncMock(side_effect=ApiException(status=404, reason="Not Found"))

        with pytest.raises(AllureNotFoundError, match="not found"):
            await service.get_defect(999)


@pytest.mark.asyncio
async def test_update_defect(service: DefectService) -> None:
    updated = DefectDto(id=10, name="Renamed", closed=True)

    with patch("src.services.defect_service.DefectControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        mock_api.patch42 = AsyncMock(return_value=updated)

        result = await service.update_defect(10, name="Renamed", closed=True)

        assert result.name == "Renamed"
        assert result.closed is True
        patch_dto = mock_api.patch42.call_args.kwargs["defect_patch_dto"]
        assert patch_dto.name == "Renamed"
        assert patch_dto.closed is True


@pytest.mark.asyncio
async def test_update_defect_no_fields(service: DefectService) -> None:
    with pytest.raises(AllureValidationError, match="At least one field"):
        await service.update_defect(10)


@pytest.mark.asyncio
async def test_delete_defect(service: DefectService) -> None:
    with patch("src.services.defect_service.DefectControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        mock_api.delete37 = AsyncMock(return_value=None)

        await service.delete_defect(10)

        mock_api.delete37.assert_called_once_with(id=10)


@pytest.mark.asyncio
async def test_delete_defect_not_found(service: DefectService) -> None:
    with patch("src.services.defect_service.DefectControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        mock_api.delete37 = AsyncMock(side_effect=ApiException(status=404, reason="Not Found"))

        # Should not raise exception (idempotent)
        await service.delete_defect(999)
        mock_api.delete37.assert_called_once_with(id=999)


@pytest.mark.asyncio
async def test_list_defects(service: DefectService) -> None:
    with patch("src.services.defect_service.DefectControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        page = Mock()
        page.content = [
            DefectRowDto(id=1, name="D1", closed=False),
            DefectRowDto(id=2, name="D2", closed=True),
        ]
        mock_api.find_all_by_project_id = AsyncMock(return_value=page)

        result = await service.list_defects()

        assert len(result) == 2
        assert result[0].name == "D1"
        mock_api.find_all_by_project_id.assert_called_once_with(project_id=1, page=0, size=100)


@pytest.mark.asyncio
async def test_list_defects_empty(service: DefectService) -> None:
    with patch("src.services.defect_service.DefectControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        page = Mock()
        page.content = None
        mock_api.find_all_by_project_id = AsyncMock(return_value=page)

        result = await service.list_defects()

        assert result == []


@pytest.mark.asyncio
async def test_link_defect_to_test_case_explicit_mapping(service: DefectService) -> None:
    with (
        patch("src.services.defect_service.DefectControllerApi") as mock_ctl,
        patch("src.services.defect_service.TestCaseService") as mock_tc_cls,
        patch("src.services.defect_service.IntegrationService") as mock_int_cls,
    ):
        mock_api = mock_ctl.return_value
        mock_api.link_issue = AsyncMock(return_value=DefectOverviewDto(id=10, name="Bug"))

        mock_tc = mock_tc_cls.return_value
        mock_tc.get_test_case = AsyncMock(return_value=Mock(issues=[]))
        mock_tc.add_issues_to_test_case = AsyncMock(return_value=None)

        mock_int = mock_int_cls.return_value
        mock_int.resolve_integration_for_issues = AsyncMock(return_value=7)

        result = await service.link_defect_to_test_case(
            defect_id=10,
            test_case_id=20,
            issue_key="proj-123",
            integration_id=7,
        )

        assert result.defect_id == 10
        assert result.test_case_id == 20
        assert result.issue_key == "PROJ-123"
        assert result.integration_id == 7
        assert result.already_linked is False

        dto = mock_api.link_issue.call_args.kwargs["defect_issue_link_dto"]
        assert dto.name == "PROJ-123"
        assert dto.integration_id == 7
        mock_tc.add_issues_to_test_case.assert_called_once_with(20, ["PROJ-123"], integration_id=7)


@pytest.mark.asyncio
async def test_link_defect_to_test_case_explicit_mapping_by_integration_name(service: DefectService) -> None:
    with (
        patch("src.services.defect_service.DefectControllerApi") as mock_ctl,
        patch("src.services.defect_service.TestCaseService") as mock_tc_cls,
        patch("src.services.defect_service.IntegrationService") as mock_int_cls,
    ):
        mock_api = mock_ctl.return_value
        mock_api.link_issue = AsyncMock(return_value=DefectOverviewDto(id=10, name="Bug"))

        mock_tc = mock_tc_cls.return_value
        mock_tc.get_test_case = AsyncMock(return_value=Mock(issues=[]))
        mock_tc.add_issues_to_test_case = AsyncMock(return_value=None)

        mock_int = mock_int_cls.return_value
        mock_int.resolve_integration_for_issues = AsyncMock(return_value=11)

        result = await service.link_defect_to_test_case(
            defect_id=10,
            test_case_id=20,
            issue_key="proj-123",
            integration_name="Jira",
        )

        assert result.integration_id == 11
        mock_int.resolve_integration_for_issues.assert_called_once_with(
            integration_id=None,
            integration_name="Jira",
        )
        mock_tc.add_issues_to_test_case.assert_called_once_with(20, ["PROJ-123"], integration_id=11)


@pytest.mark.asyncio
async def test_link_defect_to_test_case_idempotent_when_already_linked(service: DefectService) -> None:
    with (
        patch("src.services.defect_service.DefectControllerApi") as mock_ctl,
        patch("src.services.defect_service.TestCaseService") as mock_tc_cls,
        patch("src.services.defect_service.IntegrationService") as mock_int_cls,
    ):
        mock_api = mock_ctl.return_value
        mock_api.link_issue = AsyncMock(return_value=DefectOverviewDto(id=10, name="Bug"))

        mock_tc = mock_tc_cls.return_value
        mock_tc.get_test_case = AsyncMock(return_value=Mock(issues=[IssueDto(name="PROJ-123", integration_id=7)]))
        mock_tc.add_issues_to_test_case = AsyncMock(return_value=None)

        mock_int = mock_int_cls.return_value
        mock_int.resolve_integration_for_issues = AsyncMock(return_value=7)

        result = await service.link_defect_to_test_case(
            defect_id=10,
            test_case_id=20,
            issue_key="PROJ-123",
            integration_id=7,
        )

        assert result.already_linked is True
        mock_tc.add_issues_to_test_case.assert_not_called()


@pytest.mark.asyncio
async def test_link_defect_to_test_case_same_key_different_integration_not_idempotent(service: DefectService) -> None:
    with (
        patch("src.services.defect_service.DefectControllerApi") as mock_ctl,
        patch("src.services.defect_service.TestCaseService") as mock_tc_cls,
        patch("src.services.defect_service.IntegrationService") as mock_int_cls,
    ):
        mock_api = mock_ctl.return_value
        mock_api.link_issue = AsyncMock(return_value=DefectOverviewDto(id=10, name="Bug"))

        mock_tc = mock_tc_cls.return_value
        mock_tc.get_test_case = AsyncMock(return_value=Mock(issues=[IssueDto(name="PROJ-123", integration_id=8)]))
        mock_tc.add_issues_to_test_case = AsyncMock(return_value=None)

        mock_int = mock_int_cls.return_value
        mock_int.resolve_integration_for_issues = AsyncMock(return_value=7)

        result = await service.link_defect_to_test_case(
            defect_id=10,
            test_case_id=20,
            issue_key="PROJ-123",
            integration_id=7,
        )

        assert result.already_linked is False
        mock_tc.add_issues_to_test_case.assert_called_once_with(20, ["PROJ-123"], integration_id=7)


@pytest.mark.asyncio
async def test_link_defect_to_test_case_reuses_existing_defect_issue(service: DefectService) -> None:
    with (
        patch("src.services.defect_service.DefectControllerApi") as mock_ctl,
        patch("src.services.defect_service.TestCaseService") as mock_tc_cls,
        patch.object(
            service,
            "get_defect",
            AsyncMock(
                return_value=DefectOverviewDto(
                    id=10,
                    name="Bug",
                    issue=IssueDto(name="PROJ-456", integration_id=3),
                )
            ),
        ),
    ):
        mock_api = mock_ctl.return_value
        mock_api.link_issue = AsyncMock(return_value=DefectOverviewDto(id=10, name="Bug"))

        mock_tc = mock_tc_cls.return_value
        mock_tc.get_test_case = AsyncMock(return_value=Mock(issues=[]))
        mock_tc.add_issues_to_test_case = AsyncMock(return_value=None)

        result = await service.link_defect_to_test_case(defect_id=10, test_case_id=20)

        assert result.issue_key == "PROJ-456"
        assert result.integration_id == 3
        mock_tc.add_issues_to_test_case.assert_called_once_with(20, ["PROJ-456"], integration_id=3)


@pytest.mark.asyncio
async def test_link_defect_to_test_case_requires_issue_mapping(service: DefectService) -> None:
    with patch.object(service, "get_defect", AsyncMock(return_value=DefectOverviewDto(id=10, name="Bug", issue=None))):
        with pytest.raises(AllureValidationError, match="Issue mapping is required"):
            await service.link_defect_to_test_case(defect_id=10, test_case_id=20)


@pytest.mark.asyncio
async def test_link_defect_to_test_case_integration_ambiguity_propagates_validation_error(
    service: DefectService,
) -> None:
    with (
        patch("src.services.defect_service.DefectControllerApi") as mock_ctl,
        patch("src.services.defect_service.TestCaseService"),
        patch("src.services.defect_service.IntegrationService") as mock_int_cls,
    ):
        mock_api = mock_ctl.return_value
        mock_api.link_issue = AsyncMock()

        mock_int = mock_int_cls.return_value
        mock_int.resolve_integration_for_issues = AsyncMock(
            side_effect=AllureValidationError("Multiple integrations found.")
        )

        with pytest.raises(AllureValidationError, match="Multiple integrations found"):
            await service.link_defect_to_test_case(
                defect_id=10,
                test_case_id=20,
                issue_key="PROJ-123",
            )

        mock_api.link_issue.assert_not_called()


@pytest.mark.asyncio
async def test_link_defect_to_test_case_409_conflict_raises_validation_error(service: DefectService) -> None:
    with (
        patch("src.services.defect_service.DefectControllerApi") as mock_ctl,
        patch("src.services.defect_service.TestCaseService"),
        patch.object(
            service,
            "get_defect",
            AsyncMock(
                return_value=DefectOverviewDto(id=10, name="Bug", issue=IssueDto(name="PROJ-999", integration_id=7))
            ),
        ),
        patch("src.services.defect_service.IntegrationService") as mock_int_cls,
    ):
        mock_api = mock_ctl.return_value
        mock_api.link_issue = AsyncMock(side_effect=ApiException(status=409, reason="Conflict"))

        mock_int = mock_int_cls.return_value
        mock_int.resolve_integration_for_issues = AsyncMock(return_value=7)

        with pytest.raises(AllureValidationError, match="mapping conflict"):
            await service.link_defect_to_test_case(
                defect_id=10,
                test_case_id=20,
                issue_key="PROJ-123",
                integration_id=7,
            )


@pytest.mark.asyncio
async def test_link_defect_to_test_case_409_duplicate_allows_flow(service: DefectService) -> None:
    with (
        patch("src.services.defect_service.DefectControllerApi") as mock_ctl,
        patch("src.services.defect_service.TestCaseService") as mock_tc_cls,
        patch.object(
            service,
            "get_defect",
            AsyncMock(
                return_value=DefectOverviewDto(id=10, name="Bug", issue=IssueDto(name="PROJ-123", integration_id=7))
            ),
        ),
        patch("src.services.defect_service.IntegrationService") as mock_int_cls,
    ):
        mock_api = mock_ctl.return_value
        mock_api.link_issue = AsyncMock(side_effect=ApiException(status=409, reason="Conflict"))

        mock_tc = mock_tc_cls.return_value
        mock_tc.get_test_case = AsyncMock(return_value=Mock(issues=[]))
        mock_tc.add_issues_to_test_case = AsyncMock(return_value=None)

        mock_int = mock_int_cls.return_value
        mock_int.resolve_integration_for_issues = AsyncMock(return_value=7)

        result = await service.link_defect_to_test_case(
            defect_id=10,
            test_case_id=20,
            issue_key="PROJ-123",
            integration_id=7,
        )

        assert result.already_linked is False
        mock_tc.add_issues_to_test_case.assert_called_once_with(20, ["PROJ-123"], integration_id=7)


@pytest.mark.asyncio
async def test_list_defect_test_cases(service: DefectService) -> None:
    with patch("src.services.defect_service.DefectControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        mock_api.get_test_cases2 = AsyncMock(
            return_value=Mock(
                content=[TestCaseRowDto(id=1, name="TC-1", status=StatusDto(name="Draft"))],
                total_elements=1,
                number=0,
                size=20,
                total_pages=1,
            )
        )

        result = await service.list_defect_test_cases(defect_id=10, page=0, size=20)

        assert result.total == 1
        assert result.page == 0
        assert result.size == 20
        assert result.total_pages == 1
        assert len(result.items) == 1
        assert result.items[0].name == "TC-1"
        mock_api.get_test_cases2.assert_called_once_with(id=10, page=0, size=20)


@pytest.mark.asyncio
async def test_list_defect_test_cases_not_found(service: DefectService) -> None:
    with patch("src.services.defect_service.DefectControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        mock_api.get_test_cases2 = AsyncMock(side_effect=ApiException(status=404, reason="Not Found"))

        with pytest.raises(AllureNotFoundError, match="Defect 10 not found"):
            await service.list_defect_test_cases(defect_id=10)


# ── Defect Matcher CRUD ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_defect_matcher(service: DefectService) -> None:
    matcher = DefectMatcherDto(id=20, name="NPE Matcher", defect_id=10)

    with patch("src.services.defect_service.DefectMatcherControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        mock_api.create46 = AsyncMock(return_value=matcher)

        result = await service.create_defect_matcher(
            defect_id=10,
            name="NPE Matcher",
            message_regex="NullPointer.*",
        )

        assert result.id == 20
        dto = mock_api.create46.call_args.kwargs["defect_matcher_create_dto"]
        assert dto.defect_id == 10
        assert dto.name == "NPE Matcher"
        assert dto.message_regex == "NullPointer.*"


@pytest.mark.asyncio
async def test_create_matcher_no_regex(service: DefectService) -> None:
    with pytest.raises(AllureValidationError, match="message_regex or trace_regex"):
        await service.create_defect_matcher(defect_id=10, name="Bad")


@pytest.mark.asyncio
async def test_create_matcher_empty_name(service: DefectService) -> None:
    with pytest.raises(AllureValidationError, match="name is required"):
        await service.create_defect_matcher(defect_id=10, name="", message_regex=".*")


@pytest.mark.asyncio
async def test_update_defect_matcher(service: DefectService) -> None:
    updated = DefectMatcherDto(id=20, name="Updated", message_regex="new.*")

    with patch("src.services.defect_service.DefectMatcherControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        mock_api.patch43 = AsyncMock(return_value=updated)

        result = await service.update_defect_matcher(20, name="Updated")

        assert result.name == "Updated"
        patch_dto = mock_api.patch43.call_args.kwargs["defect_matcher_patch_dto"]
        assert patch_dto.name == "Updated"


@pytest.mark.asyncio
async def test_update_matcher_no_fields(service: DefectService) -> None:
    with pytest.raises(AllureValidationError, match="At least one field"):
        await service.update_defect_matcher(20)


@pytest.mark.asyncio
async def test_delete_defect_matcher(service: DefectService) -> None:
    with patch("src.services.defect_service.DefectMatcherControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        mock_api.delete38 = AsyncMock(return_value=None)

        await service.delete_defect_matcher(20)

        mock_api.delete38.assert_called_once_with(id=20)


@pytest.mark.asyncio
async def test_delete_matcher_not_found(service: DefectService) -> None:
    with patch("src.services.defect_service.DefectMatcherControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        mock_api.delete38 = AsyncMock(side_effect=ApiException(status=404, reason="Not Found"))

        # Should not raise exception (idempotent)
        await service.delete_defect_matcher(999)
        mock_api.delete38.assert_called_once_with(id=999)


@pytest.mark.asyncio
async def test_list_defect_matchers(service: DefectService) -> None:
    with patch("src.services.defect_service.DefectControllerApi") as mock_ctl:
        mock_api = mock_ctl.return_value
        page = Mock()
        page.content = [
            DefectMatcherDto(id=20, name="M1", defect_id=10),
            DefectMatcherDto(id=21, name="M2", defect_id=10),
        ]
        mock_api.get_matchers = AsyncMock(return_value=page)

        result = await service.list_defect_matchers(10)

        assert len(result) == 2
        mock_api.get_matchers.assert_called_once_with(id=10, page=0, size=100)
