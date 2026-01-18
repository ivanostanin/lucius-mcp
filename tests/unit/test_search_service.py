from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client import AllureClient, PageTestCaseDto, TestCaseDto
from src.client.exceptions import AllureValidationError
from src.services.search_service import SearchService


@pytest.fixture
def mock_client() -> AllureClient:
    client = MagicMock(spec=AllureClient)
    client.list_test_cases = AsyncMock()
    return client


@pytest.fixture
def service(mock_client: AllureClient) -> SearchService:
    return SearchService(mock_client)


@pytest.mark.asyncio
async def test_list_test_cases_returns_paginated_results(service: SearchService, mock_client: AllureClient) -> None:
    page = PageTestCaseDto(
        content=[TestCaseDto(id=1, name="Login Flow")],
        total_elements=1,
        number=0,
        size=20,
        total_pages=1,
    )
    mock_client.list_test_cases.return_value = page

    result = await service.list_test_cases(project_id=123)

    assert result.total == 1
    assert result.page == 0
    assert result.total_pages == 1
    assert result.items[0].id == 1
    assert result.items[0].name == "Login Flow"
    mock_client.list_test_cases.assert_called_once_with(
        project_id=123,
        page=0,
        size=20,
        search=None,
        tags=None,
        status=None,
    )


@pytest.mark.asyncio
async def test_list_test_cases_passes_filters(service: SearchService, mock_client: AllureClient) -> None:
    page = PageTestCaseDto(content=[], total_elements=0, number=0, size=20, total_pages=0)
    mock_client.list_test_cases.return_value = page

    await service.list_test_cases(
        project_id=123,
        page=1,
        size=50,
        name_filter="login",
        tags=["smoke", "auth"],
        status="Draft",
    )

    mock_client.list_test_cases.assert_called_once_with(
        project_id=123,
        page=1,
        size=50,
        search="login",
        tags=["smoke", "auth"],
        status="Draft",
    )


@pytest.mark.asyncio
async def test_list_test_cases_validates_project_id(service: SearchService) -> None:
    with pytest.raises(AllureValidationError, match="Project ID is required and must be positive"):
        await service.list_test_cases(project_id=0)


@pytest.mark.asyncio
async def test_list_test_cases_validates_pagination(service: SearchService) -> None:
    with pytest.raises(AllureValidationError, match="Page must be a non-negative integer"):
        await service.list_test_cases(project_id=1, page=-1)

    with pytest.raises(AllureValidationError, match="Size must be a positive integer"):
        await service.list_test_cases(project_id=1, size=0)

    with pytest.raises(AllureValidationError, match="Size must be 100 or less"):
        await service.list_test_cases(project_id=1, size=101)
