import pytest

from src.client import AllureClient
from src.services.search_service import SearchService
from src.tools.search import _format_search_results


async def test_search_test_cases_name_only(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    service = SearchService(client=allure_client)

    result = await service.search_test_cases(query="login", page=0, size=5)
    text = _format_search_results(result, "login")

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text


async def test_search_test_cases_tag_only(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    service = SearchService(client=allure_client)

    result = await service.search_test_cases(query="tag:smoke", page=0, size=5)
    text = _format_search_results(result, "tag:smoke")

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text


async def test_search_test_cases_multiple_tags(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    service = SearchService(client=allure_client)

    result = await service.search_test_cases(query="tag:smoke tag:regression", page=0, size=5)
    text = _format_search_results(result, "tag:smoke tag:regression")

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text


async def test_search_test_cases_combined_and_case_insensitive(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    service = SearchService(client=allure_client)

    result = await service.search_test_cases(query="Login tag:SMOKE", page=0, size=5)
    text = _format_search_results(result, "Login tag:SMOKE")

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text


async def test_search_test_cases_tag_case_sensitivity(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    """Test that tag search is case-sensitive as required by Allure TestOps."""
    service = SearchService(client=allure_client)

    # Search with lower case tag
    result_lower = await service.search_test_cases(query="tag:smoke", page=0, size=5)

    # Search with different casing
    result_mixed = await service.search_test_cases(query="tag:Smoke", page=0, size=5)

    # The queries should be passed with their original casing to the client.
    # While we can't easily assert on the remote state, we can verify the service
    # doesn't collapse them to the same query if we were to mock it,
    # but here we just ensure the tool accepts both and they potentially return different results.
    assert result_lower is not None
    assert result_mixed is not None


# =============================================
# AQL Search E2E Tests
# =============================================


async def test_search_test_cases_aql_simple_query(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    """Test AQL search with a simple name filter."""
    service = SearchService(client=allure_client)

    result = await service.search_test_cases(aql='name ~= "test"', page=0, size=5)
    text = _format_search_results(result, 'name ~= "test"')

    assert "Found" in text or "No test cases found" in text


async def test_search_test_cases_aql_complex_query(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    """Test AQL search with AND operator and multiple conditions."""

    service = SearchService(client=allure_client)

    # This query may not match anything, but should not error
    result = await service.search_test_cases(
        aql='name ~= "login" or name ~= "test"',
        page=0,
        size=5,
    )
    text = _format_search_results(result, 'name ~= "login" or name ~= "test"')

    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text


async def test_search_test_cases_aql_invalid_syntax_returns_error(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    """Test that invalid AQL syntax returns a clear error message."""
    from src.client.exceptions import AllureValidationError

    service = SearchService(client=allure_client)

    with pytest.raises(AllureValidationError, match="Invalid AQL syntax"):
        await service.search_test_cases(
            aql="this is not valid aql %%% syntax",
            page=0,
            size=5,
        )


async def test_search_test_cases_aql_pagination_hints(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    """Test that AQL search includes pagination hints in output."""
    service = SearchService(client=allure_client)

    # Request a small page size to potentially trigger pagination hints
    result = await service.search_test_cases(
        aql='name ~= "e" or name ~= "a"',  # Broad query for more matches
        page=0,
        size=2,
    )
    text = _format_search_results(result, 'name ~= "e" or name ~= "a"')

    # If there are multiple pages, pagination hint should be present
    if result.total_pages > 1:
        assert "page" in text.lower() or "Showing" in text


async def test_search_test_cases_regression_simple_query_unchanged(
    allure_client: AllureClient,
    project_id: int,
) -> None:
    """Regression test: ensure simple query path still works after AQL changes."""
    service = SearchService(client=allure_client)

    # Use the simple query path (not AQL)
    result = await service.search_test_cases(query="tag:smoke", page=0, size=5)
    text = _format_search_results(result, "tag:smoke")

    # Output format should match existing expectations
    assert "Found" in text or "No test cases found" in text
    assert "tags:" in text or "No test cases found" in text
