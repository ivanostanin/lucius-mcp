"""Integration tests for launch client wiring."""

import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError
from src.client.generated.exceptions import ApiException
from src.client.generated.models.aql_validate_response_dto import AqlValidateResponseDto
from src.client.generated.models.find_all29200_response import FindAll29200Response
from src.client.generated.models.launch_create_dto import LaunchCreateDto
from src.client.generated.models.launch_dto import LaunchDto
from src.client.generated.models.page_launch_dto import PageLaunchDto
from src.client.generated.models.page_launch_preview_dto import PageLaunchPreviewDto


@pytest.mark.asyncio
async def test_client_create_launch_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.create31 = AsyncMock(return_value=LaunchDto(id=1, name="Launch"))

    data = LaunchCreateDto(name="Launch", project_id=1)
    result = await client.create_launch(data)

    assert result.id == 1
    client._launch_api.create31.assert_called_once()


@pytest.mark.asyncio
async def test_client_list_launches_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    page = PageLaunchDto(content=[LaunchDto(id=1, name="Launch")])
    client._launch_api.find_all29 = AsyncMock(return_value=FindAll29200Response(page))

    result = await client.list_launches(project_id=1, page=0, size=20)

    assert result.actual_instance is not None
    client._launch_api.find_all29.assert_called_once()
    client._launch_api.find_all29_without_preload_content.assert_not_called()


@pytest.mark.asyncio
async def test_client_list_launches_falls_back_on_oneof() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.find_all29 = AsyncMock(side_effect=ValueError("oneOf conflict"))
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "content": [{"id": 1, "name": "Launch"}],
        "number": 0,
        "size": 20,
        "totalElements": 1,
        "totalPages": 1,
    }
    client._launch_api.find_all29_without_preload_content = AsyncMock(return_value=response)

    result = await client.list_launches(project_id=1, page=0, size=20)

    assert result.actual_instance is not None
    assert isinstance(result.actual_instance, (PageLaunchDto, PageLaunchPreviewDto))
    client._launch_api.find_all29.assert_called_once()
    client._launch_api.find_all29_without_preload_content.assert_called_once()


@pytest.mark.asyncio
async def test_client_get_launch_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.find_one23 = AsyncMock(return_value=LaunchDto(id=2, name="Launch"))

    result = await client.get_launch(launch_id=2)

    assert result.id == 2
    client._launch_api.find_one23.assert_called_once()


@pytest.mark.asyncio
async def test_client_get_launch_not_found_raises() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.find_one23 = AsyncMock(side_effect=ApiException(status=404, reason="Not Found", body="{}"))

    with pytest.raises(AllureNotFoundError, match="Resource not found"):
        await client.get_launch(launch_id=404)


@pytest.mark.asyncio
async def test_client_search_launches_aql_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_search_api = MagicMock()
    client._launch_search_api.search2 = AsyncMock(return_value=PageLaunchDto(content=[]))

    result = await client.search_launches_aql(project_id=1, rql='name="Launch"')

    assert result.content == []
    client._launch_search_api.search2.assert_called_once()


@pytest.mark.asyncio
async def test_client_validate_launch_query_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_search_api = MagicMock()
    client._launch_search_api.validate_query2 = AsyncMock(return_value=AqlValidateResponseDto(valid=True, count=1))

    result = await client.validate_launch_query(project_id=1, rql='name="Launch"')

    assert result.valid is True
    client._launch_search_api.validate_query2.assert_called_once()
