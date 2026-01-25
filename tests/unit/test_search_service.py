from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client import AllureClient, PageTestCaseDto, TestCaseDto, TestCaseDtoWithCF, TestCaseScenarioV2Dto
from src.client.exceptions import AllureNotFoundError, AllureValidationError, TestCaseNotFoundError
from src.client.generated.models.custom_field_dto import CustomFieldDto
from src.client.generated.models.custom_field_value_with_cf_dto import CustomFieldValueWithCfDto
from src.client.generated.models.test_tag_dto import TestTagDto
from src.services.search_service import SearchQueryParser, SearchService, TestCaseDetails
from src.tools.search import _format_search_results, _format_test_case_details


@pytest.fixture
def mock_client() -> AllureClient:
    client = MagicMock(spec=AllureClient)
    client.list_test_cases = AsyncMock()
    client.get_test_case = AsyncMock()
    client.get_test_case_scenario = AsyncMock()
    client.get_project.return_value = 123
    return client


@pytest.fixture
def service(mock_client: AllureClient) -> SearchService:
    return SearchService(client=mock_client)


@pytest.mark.asyncio
async def test_get_test_case_details_returns_case_and_scenario(
    service: SearchService, mock_client: AllureClient
) -> None:
    test_case = TestCaseDto(id=123, name="Login", description="d")
    scenario = TestCaseScenarioV2Dto(steps=[])
    mock_client.get_test_case = AsyncMock(return_value=test_case)
    mock_client.get_test_case_scenario = AsyncMock(return_value=scenario)

    details = await service.get_test_case_details(123)

    assert isinstance(details, TestCaseDetails)
    assert details.test_case.id == 123
    assert details.scenario is scenario
    mock_client.get_test_case.assert_awaited_once_with(123)
    mock_client.get_test_case_scenario.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_get_test_case_details_maps_not_found(service: SearchService, mock_client: AllureClient) -> None:
    mock_client.get_test_case = AsyncMock(side_effect=AllureNotFoundError("nf"))
    mock_client.get_test_case_scenario = AsyncMock()

    with pytest.raises(TestCaseNotFoundError):
        await service.get_test_case_details(999)

    mock_client.get_test_case.assert_awaited_once_with(999)
    mock_client.get_test_case_scenario.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_test_case_details_validates_id(service: SearchService) -> None:
    with pytest.raises(AllureValidationError, match="Test case ID must be a positive integer"):
        await service.get_test_case_details(0)


def test_format_test_case_details_handles_fields_and_steps() -> None:
    tc = TestCaseDtoWithCF(
        id=1,
        name="Login",
        description="Desc",
        precondition="Pre",
        tags=[],
    )
    # Simulate nested steps using simple objects to bypass generated validation
    from types import SimpleNamespace

    class SimpleStep(SimpleNamespace):
        def __init__(self, body: str, expected: str | None = None, steps: list | None = None) -> None:
            super().__init__(body=body, expected=expected, steps=steps or [])

    child = SimpleStep("Sub-step", "Outcome")
    parent = SimpleStep("Do X", "See Y", steps=[child])

    scenario = SimpleNamespace(steps=[parent], attachments=[SimpleNamespace(id=10, name="log.txt")])
    tc.custom_fields = [CustomFieldValueWithCfDto(custom_field=CustomFieldDto(name="Layer"), name="UI")]
    details = TestCaseDetails(test_case=tc, scenario=scenario)

    text = _format_test_case_details(details)

    assert "Test Case TC-1: Login" in text
    assert "Description" in text
    assert "Preconditions" in text
    assert "1. Do X → See Y" in text
    assert "1.1. Sub-step → Outcome" in text
    assert "Custom Fields" in text
    assert "Layer=UI" in text
    assert "Attachments" in text
    assert "log.txt" in text
    assert "id: 10" in text


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

    result = await service.list_test_cases()

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
async def test_search_test_cases_parses_query(service: SearchService, mock_client: AllureClient) -> None:
    page = PageTestCaseDto(content=[], total_elements=0, number=0, size=20, total_pages=0)
    mock_client.list_test_cases.return_value = page

    await service.search_test_cases(
        query="login tag:smoke tag:auth",
        page=2,
        size=10,
    )

    mock_client.list_test_cases.assert_called_once_with(
        project_id=123,
        page=2,
        size=10,
        search="login",
        tags=["smoke", "auth"],
        status=None,
    )
    assert SearchService.search_test_cases.__doc__


@pytest.mark.asyncio
async def test_list_test_cases_validates_project_id(service: SearchService) -> None:
    service._project_id = 0
    with pytest.raises(AllureValidationError, match="Project ID is required and must be positive"):
        await service.list_test_cases()


@pytest.mark.asyncio
async def test_list_test_cases_validates_pagination(service: SearchService) -> None:
    with pytest.raises(AllureValidationError, match="Page must be a non-negative integer"):
        await service.list_test_cases(page=-1)

    with pytest.raises(AllureValidationError, match="Size must be a positive integer"):
        await service.list_test_cases(size=0)

    with pytest.raises(AllureValidationError, match="Size must be 100 or less"):
        await service.list_test_cases(size=101)


def test_format_search_results_handles_empty() -> None:
    empty_page = PageTestCaseDto(content=[], total_elements=0, number=0, size=20, total_pages=0)
    mock_client = MagicMock(spec=AllureClient)
    mock_client.get_project.return_value = 1
    empty_result = SearchService(client=mock_client)._build_result(empty_page)

    text = _format_search_results(empty_result, "login tag:auth")

    assert text == "No test cases found matching 'login tag:auth'."


def test_search_query_parser_parses_name_only() -> None:
    parsed = SearchQueryParser.parse("login flow")

    assert parsed.name_query == "login flow"
    assert parsed.tags == []


def test_search_query_parser_parses_single_tag() -> None:
    parsed = SearchQueryParser.parse("tag:smoke")

    assert parsed.name_query is None
    assert parsed.tags == ["smoke"]


def test_search_query_parser_parses_multiple_tags() -> None:
    parsed = SearchQueryParser.parse("tag:smoke tag:auth")

    assert parsed.name_query is None
    assert parsed.tags == ["smoke", "auth"]


def test_search_query_parser_parses_combined() -> None:
    parsed = SearchQueryParser.parse("login tag:auth")

    assert parsed.name_query == "login"
    assert parsed.tags == ["auth"]


def test_search_query_parser_normalizes_case() -> None:
    parsed = SearchQueryParser.parse("tag:SMOKE tag:Auth")

    assert parsed.tags == ["smoke", "auth"]


def test_format_search_results_includes_tags_and_pagination() -> None:
    tag = TestTagDto.model_construct(name="smoke")
    items = [
        TestCaseDto(id=1, name="Login Flow", tags=[tag]),
        TestCaseDto(id=2, name="Logout", tags=[]),
    ]
    page = PageTestCaseDto(content=items, total_elements=2, number=0, size=1, total_pages=2)
    mock_client = MagicMock(spec=AllureClient)
    mock_client.get_project.return_value = 1
    result = SearchService(client=mock_client)._build_result(page)

    text = _format_search_results(result, "login")

    assert "Found 2 test cases matching 'login':" in text
    assert "[TC-1] Login Flow" in text
    assert "tags: smoke" in text
    assert "[TC-2] Logout" in text
    assert "tags: none" in text
    assert "Showing page 1 of 2" in text
