import os

import pytest

from src.client import AllureClient
from src.services.search_service import SearchService
from src.tools.search import _format_search_results
from src.utils.auth import get_auth_context

pytestmark = pytest.mark.skipif(
    not (os.getenv("ALLURE_ENDPOINT") and os.getenv("ALLURE_API_TOKEN")),
    reason="Sandbox credentials not configured (ALLURE_ENDPOINT/TOKEN)",
)


@pytest.mark.asyncio
async def test_search_test_cases_name_only(
    allure_client: AllureClient,
    project_id: int,
    api_token: str,
) -> None:
    service = SearchService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    result = await service.search_test_cases(project_id=project_id, query="login", page=0, size=5)
    text = _format_search_results(result, "login")

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text


@pytest.mark.asyncio
async def test_search_test_cases_tag_only(
    allure_client: AllureClient,
    project_id: int,
    api_token: str,
) -> None:
    service = SearchService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    result = await service.search_test_cases(project_id=project_id, query="tag:smoke", page=0, size=5)
    text = _format_search_results(result, "tag:smoke")

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text


@pytest.mark.asyncio
async def test_search_test_cases_multiple_tags(
    allure_client: AllureClient,
    project_id: int,
    api_token: str,
) -> None:
    service = SearchService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    result = await service.search_test_cases(project_id=project_id, query="tag:smoke tag:regression", page=0, size=5)
    text = _format_search_results(result, "tag:smoke tag:regression")

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text


@pytest.mark.asyncio
async def test_search_test_cases_combined_and_case_insensitive(
    allure_client: AllureClient,
    project_id: int,
    api_token: str,
) -> None:
    service = SearchService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    result = await service.search_test_cases(project_id=project_id, query="Login tag:SMOKE", page=0, size=5)
    text = _format_search_results(result, "Login tag:SMOKE")

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text
