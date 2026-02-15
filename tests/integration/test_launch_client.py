"""Integration tests for launch client wiring."""

import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.client.generated.exceptions import ApiException
from src.client.generated.models.aql_validate_response_dto import AqlValidateResponseDto
from src.client.generated.models.find_all29200_response import FindAll29200Response
from src.client.generated.models.launch_create_dto import LaunchCreateDto
from src.client.generated.models.launch_dto import LaunchDto
from src.client.generated.models.launch_upload_response_dto import LaunchUploadResponseDto
from src.client.generated.models.page_launch_dto import PageLaunchDto
from src.client.generated.models.page_launch_preview_dto import PageLaunchPreviewDto
from src.client.generated.rest import RESTResponse


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
async def test_client_close_launch_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    response = MagicMock()
    response.status_code = 204
    client._launch_api.close_with_http_info = AsyncMock(return_value=response)

    status_code = await client.close_launch(launch_id=3)

    assert status_code == 204
    client._launch_api.close_with_http_info.assert_called_once_with(id=3, _request_timeout=client._timeout)


@pytest.mark.asyncio
async def test_client_close_launch_invalid_id_raises() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()

    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await client.close_launch(launch_id=0)


@pytest.mark.asyncio
async def test_client_reopen_launch_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.reopen = AsyncMock(return_value=None)

    await client.reopen_launch(launch_id=4)

    client._launch_api.reopen.assert_called_once_with(id=4, _request_timeout=client._timeout)


@pytest.mark.asyncio
async def test_client_reopen_launch_invalid_id_raises() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()

    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await client.reopen_launch(launch_id=0)


@pytest.mark.asyncio
async def test_client_upload_results_to_launch_uses_multipart_endpoint() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600

    api_client = MagicMock()

    def _param_serialize_side_effect(*args, **kwargs):
        path = kwargs.get("resource_path")
        return ("POST", f"https://example.com{path}", {}, None, [])

    api_client.param_serialize.side_effect = _param_serialize_side_effect

    httpx_response = MagicMock()
    httpx_response.status_code = 202
    httpx_response.reason_phrase = "Accepted"
    httpx_response.text = '{"launchId": 9, "filesCount": 1}'
    httpx_response.json.return_value = {"launchId": 9, "filesCount": 1}

    rest_response = RESTResponse(httpx_response)
    client._api_client = api_client
    api_client.call_api = AsyncMock(return_value=rest_response)

    result = await client.upload_results_to_launch(launch_id=9, files=[("results.json", b"{}")])

    assert isinstance(result, LaunchUploadResponseDto)
    assert result.launch_id == 9
    assert result.files_count == 1

    _, kwargs = api_client.param_serialize.call_args
    assert kwargs["resource_path"] == "/api/launch/9/upload/file"
    assert kwargs["header_params"]["Content-Type"] == "multipart/form-data"
    assert kwargs["files"] == {
        "file": [("results.json", b"{}")],
        "info": ("info.json", b"{}"),
    }


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
async def test_client_delete_launch_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.delete27 = AsyncMock(return_value=None)

    await client.delete_launch(launch_id=12)

    client._launch_api.delete27.assert_called_once_with(id=12, _request_timeout=client._timeout)


@pytest.mark.asyncio
async def test_client_delete_launch_not_found_raises() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.delete27 = AsyncMock(side_effect=ApiException(status=404, reason="Not Found", body="{}"))

    with pytest.raises(AllureNotFoundError, match="Resource not found"):
        await client.delete_launch(launch_id=404)


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
