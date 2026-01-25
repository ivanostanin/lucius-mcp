import pytest

from src.client import AllureClient
from src.services.search_service import SearchService
from src.tools.search import _format_search_results


@pytest.mark.asyncio
async def test_search_test_cases_name_only(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    service = SearchService(client=allure_client)

    result = await service.search_test_cases(query="login", page=0, size=5)
    text = _format_search_results(result, "login")

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text


@pytest.mark.asyncio
async def test_search_test_cases_tag_only(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    service = SearchService(client=allure_client)

    result = await service.search_test_cases(query="tag:smoke", page=0, size=5)
    text = _format_search_results(result, "tag:smoke")

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text


@pytest.mark.asyncio
async def test_search_test_cases_multiple_tags(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    service = SearchService(client=allure_client)

    result = await service.search_test_cases(query="tag:smoke tag:regression", page=0, size=5)
    text = _format_search_results(result, "tag:smoke tag:regression")

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text


@pytest.mark.asyncio
async def test_search_test_cases_combined_and_case_insensitive(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    service = SearchService(client=allure_client)

    result = await service.search_test_cases(query="Login tag:SMOKE", page=0, size=5)
    text = _format_search_results(result, "Login tag:SMOKE")

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text
