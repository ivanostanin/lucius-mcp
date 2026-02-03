"""Integration tests for launch client wiring."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr

from src.client import AllureClient
from src.client.generated.models.aql_validate_response_dto import AqlValidateResponseDto
from src.client.generated.models.find_all29200_response import FindAll29200Response
from src.client.generated.models.launch_create_dto import LaunchCreateDto
from src.client.generated.models.launch_dto import LaunchDto
from src.client.generated.models.page_launch_dto import PageLaunchDto


@pytest.mark.asyncio
async def test_client_create_launch_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
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
    client._launch_api = MagicMock()
    page = PageLaunchDto(content=[LaunchDto(id=1, name="Launch")])
    client._launch_api.find_all29 = AsyncMock(return_value=FindAll29200Response(page))

    result = await client.list_launches(project_id=1, page=0, size=20)

    assert result.actual_instance is not None
    client._launch_api.find_all29.assert_called_once()


@pytest.mark.asyncio
async def test_client_search_launches_aql_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._launch_search_api = MagicMock()
    client._launch_search_api.search2 = AsyncMock(return_value=PageLaunchDto(content=[]))

    result = await client.search_launches_aql(project_id=1, rql='name="Launch"')

    assert result.content == []
    client._launch_search_api.search2.assert_called_once()


@pytest.mark.asyncio
async def test_client_validate_launch_query_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._launch_search_api = MagicMock()
    client._launch_search_api.validate_query2 = AsyncMock(return_value=AqlValidateResponseDto(valid=True, count=1))

    result = await client.validate_launch_query(project_id=1, rql='name="Launch"')

    assert result.valid is True
    client._launch_search_api.validate_query2.assert_called_once()
