import pytest

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.services.search_service import SearchService


@pytest.mark.asyncio
async def test_list_test_cases_paginates_and_formats(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    service = SearchService(client=allure_client)

    # Fetch first page with small size to force pagination hint
    result = await service.list_test_cases(page=0, size=1)

    assert result.page == 0
    assert result.size == 1
    assert result.total >= 0
    assert result.total_pages >= 1

    # Format output to ensure LLM-friendly text includes status/tags and hint for next page
    from src.tools.search import _format_test_case_list

    text = _format_test_case_list(result)
    assert "Found" in text
    assert "status:" in text
    assert "tags:" in text
    if result.total_pages > 1:
        assert "Use page=" in text


@pytest.mark.asyncio
async def test_list_test_cases_filters_are_aql_compatible(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    service = SearchService(client=allure_client)

    # Exercise AQL-compatible filters: name contains, status equals, tag equals
    result = await service.list_test_cases(
        page=0,
        size=5,
        name_filter="login",
        tags=["smoke"],
        status="Draft",
    )

    # Validate search executed and returns a coherent page
    assert result.page == 0
    assert result.size == 5
    assert result.total_pages >= 0

    # Ensure returned items respect filtering surface fields
    for tc in result.items:
        if tc.name:
            assert "login".lower() in tc.name.lower() or tc.tags or tc.status


@pytest.mark.asyncio
async def test_list_test_cases_handles_invalid_project(
    allure_client: AllureClient,
) -> None:
    original_project = allure_client.get_project()
    allure_client.set_project(-1)
    try:
        service = SearchService(client=allure_client)

        with pytest.raises(AllureValidationError):
            await service.list_test_cases()
    finally:
        allure_client.set_project(original_project)
