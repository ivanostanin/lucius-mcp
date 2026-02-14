"""Unit tests for DefectService."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.client.generated.exceptions import ApiException
from src.client.generated.models.defect_dto import DefectDto
from src.client.generated.models.defect_matcher_dto import DefectMatcherDto
from src.client.generated.models.defect_row_dto import DefectRowDto
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
