"""Unit tests for LaunchService."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client import AllureClient, LaunchUploadResponseDto
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError, LaunchNotFoundError
from src.client.generated.models.find_all29200_response import FindAll29200Response
from src.client.generated.models.launch_dto import LaunchDto
from src.client.generated.models.launch_preview_dto import LaunchPreviewDto
from src.client.generated.models.page_launch_dto import PageLaunchDto
from src.client.generated.models.page_launch_preview_dto import PageLaunchPreviewDto
from src.services.launch_service import LaunchDeleteResult, LaunchService


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock(spec=AllureClient)
    client.get_project.return_value = 1
    client.create_launch = AsyncMock()
    client.list_launches = AsyncMock()
    client.search_launches_aql = AsyncMock()
    client.validate_launch_query = AsyncMock(return_value=(True, 0))
    client.get_launch = AsyncMock()
    client.delete_launch = AsyncMock()
    client.close_launch = AsyncMock()
    client.reopen_launch = AsyncMock()
    return client


@pytest.fixture
def service(mock_client: MagicMock) -> LaunchService:
    return LaunchService(client=mock_client)


@pytest.mark.asyncio
async def test_create_launch_minimal(service: LaunchService, mock_client: MagicMock) -> None:
    launch = LaunchDto(id=10, name="Launch 1", project_id=1)
    mock_client.create_launch.return_value = launch

    result = await service.create_launch(name="Launch 1")

    assert result.id == 10
    assert result.name == "Launch 1"
    mock_client.create_launch.assert_called_once()


@pytest.mark.asyncio
async def test_create_launch_invalid_name(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Launch name is required"):
        await service.create_launch(name="")


@pytest.mark.asyncio
async def test_create_launch_invalid_tag_type(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Tags must be a list"):
        await service.create_launch(name="Launch", tags="tag")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_list_launches_page_launch_dto(service: LaunchService, mock_client: MagicMock) -> None:
    page = PageLaunchDto(content=[LaunchDto(id=1, name="L1")], total_elements=1, number=0, size=20, total_pages=1)
    response = FindAll29200Response(page)
    mock_client.list_launches.return_value = response

    result = await service.list_launches(page=0, size=20)

    assert result.total == 1
    assert result.items[0].name == "L1"
    assert result.page == 0
    assert result.size == 20
    assert result.total_pages == 1


@pytest.mark.asyncio
async def test_list_launches_page_launch_preview_dto(service: LaunchService, mock_client: MagicMock) -> None:
    page = PageLaunchPreviewDto(
        content=[LaunchPreviewDto(id=2, name="Preview")], total_elements=1, number=0, size=20, total_pages=1
    )
    response = FindAll29200Response(page)
    mock_client.list_launches.return_value = response

    result = await service.list_launches(page=0, size=20)

    assert result.total == 1
    assert result.items[0].name == "Preview"
    assert result.page == 0
    assert result.size == 20
    assert result.total_pages == 1


@pytest.mark.asyncio
async def test_search_launches_aql(service: LaunchService, mock_client: MagicMock) -> None:
    page = PageLaunchDto(content=[LaunchDto(id=3, name="AQL")], total_elements=1, number=0, size=20, total_pages=1)
    mock_client.search_launches_aql.return_value = page

    result = await service.search_launches_aql(rql='name="AQL"')

    assert result.total == 1
    assert result.items[0].name == "AQL"
    assert result.page == 0
    assert result.size == 20
    assert result.total_pages == 1
    mock_client.search_launches_aql.assert_called_once()


@pytest.mark.asyncio
async def test_list_launches_invalid_project_id(service: LaunchService) -> None:
    service._project_id = 0
    with pytest.raises(AllureValidationError, match="Project ID is required"):
        await service.list_launches()


@pytest.mark.asyncio
async def test_get_launch_valid(service: LaunchService, mock_client: MagicMock) -> None:
    launch = LaunchDto(id=12, name="Launch")
    mock_client.get_launch.return_value = launch

    result = await service.get_launch(12)

    assert result.id == 12
    mock_client.get_launch.assert_called_once_with(12)


@pytest.mark.asyncio
async def test_get_launch_invalid_id(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await service.get_launch(0)


@pytest.mark.asyncio
async def test_get_launch_not_found_maps_error(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.get_launch.side_effect = AllureNotFoundError("Not found", status_code=404, response_body="{}")

    with pytest.raises(LaunchNotFoundError, match="Launch ID 99 not found"):
        await service.get_launch(99)


@pytest.mark.asyncio
async def test_delete_launch_success(service: LaunchService, mock_client: MagicMock) -> None:
    launch = LaunchDto(id=88, name="To Delete")
    mock_client.get_launch.return_value = launch

    result = await service.delete_launch(88)

    assert isinstance(result, LaunchDeleteResult)
    assert result.launch_id == 88
    assert result.status == "archived"
    assert result.name == "To Delete"
    mock_client.delete_launch.assert_called_once_with(88)


@pytest.mark.asyncio
async def test_delete_launch_invalid_id(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await service.delete_launch(0)


@pytest.mark.asyncio
async def test_delete_launch_already_deleted(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.get_launch.side_effect = AllureNotFoundError("Not found", status_code=404, response_body="{}")

    result = await service.delete_launch(99)

    assert result.launch_id == 99
    assert result.status == "already_deleted"
    assert "already archived" in result.message
    mock_client.delete_launch.assert_not_called()


@pytest.mark.asyncio
async def test_close_launch_valid(service: LaunchService, mock_client: MagicMock) -> None:
    open_launch = LaunchDto(id=15, name="Launch 15", closed=False)
    closed_launch = LaunchDto(id=15, name="Launch 15", closed=True)
    mock_client.get_launch.side_effect = [open_launch, closed_launch]

    result = await service.close_launch(15)

    assert result.id == 15
    assert result.closed is True
    assert getattr(result, "close_report_generation", None) == "scheduled"
    mock_client.close_launch.assert_called_once_with(15)
    assert mock_client.get_launch.call_count == 2


@pytest.mark.asyncio
async def test_close_launch_when_already_closed_marks_report_state(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    already_closed = LaunchDto(id=18, name="Launch 18", closed=True)
    mock_client.get_launch.side_effect = [already_closed, already_closed]

    result = await service.close_launch(18)

    assert result.closed is True
    assert getattr(result, "close_report_generation", None) == "already-closed"


@pytest.mark.asyncio
async def test_close_launch_invalid_id(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await service.close_launch(0)


@pytest.mark.asyncio
async def test_close_launch_not_found_maps_error(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.close_launch.side_effect = AllureNotFoundError("Not found", status_code=404, response_body="{}")

    with pytest.raises(LaunchNotFoundError, match="Launch ID 41 not found"):
        await service.close_launch(41)


@pytest.mark.asyncio
async def test_close_launch_invalid_transition_bubbles_api_error(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.close_launch.side_effect = AllureAPIError(
        "API request failed: Launch is already closed",
        status_code=409,
        response_body='{"message":"already closed"}',
    )

    with pytest.raises(AllureAPIError, match="already closed"):
        await service.close_launch(20)


@pytest.mark.asyncio
async def test_reopen_launch_valid(service: LaunchService, mock_client: MagicMock) -> None:
    reopened_launch = LaunchDto(id=16, name="Launch 16", closed=False)
    mock_client.get_launch.return_value = reopened_launch

    result = await service.reopen_launch(16)

    assert result.id == 16
    assert result.closed is False
    mock_client.reopen_launch.assert_called_once_with(16)
    mock_client.get_launch.assert_called_once_with(16)


@pytest.mark.asyncio
async def test_reopen_launch_unexpectedly_closed_raises(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.get_launch.return_value = LaunchDto(id=17, name="Launch 17", closed=True)

    with pytest.raises(AllureAPIError, match="was not reopened by API"):
        await service.reopen_launch(17)


@pytest.mark.asyncio
async def test_reopen_launch_invalid_id(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await service.reopen_launch(0)


@pytest.mark.asyncio
async def test_reopen_launch_not_found_maps_error(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.reopen_launch.side_effect = AllureNotFoundError("Not found", status_code=404, response_body="{}")

    with pytest.raises(LaunchNotFoundError, match="Launch ID 42 not found"):
        await service.reopen_launch(42)


@pytest.mark.asyncio
async def test_reopen_launch_invalid_transition_bubbles_api_error(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.reopen_launch.side_effect = AllureAPIError(
        "API request failed: Launch is already open",
        status_code=409,
        response_body='{"message":"already open"}',
    )

    with pytest.raises(AllureAPIError, match="already open"):
        await service.reopen_launch(21)


@pytest.mark.asyncio
async def test_upload_results_to_launch_calls_client(service: LaunchService, mock_client: MagicMock) -> None:
    upload_response = LaunchUploadResponseDto(launch_id=22, files_count=2)
    mock_client.upload_results_to_launch = AsyncMock(return_value=upload_response)

    result = await service.upload_results_to_launch(launch_id=22, files=[("a.json", b"{}")])

    assert result.launch_id == 22
    assert result.files_count == 2
    mock_client.upload_results_to_launch.assert_called_once()


@pytest.mark.asyncio
async def test_upload_results_to_launch_requires_files(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="files must be a non-empty list"):
        await service.upload_results_to_launch(launch_id=22, files=[])
