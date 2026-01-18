from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.search_service import SearchService, TestCaseListResult


async def list_test_cases(
    project_id: Annotated[int, Field(description="Allure TestOps project ID to list test cases from.")],
    page: Annotated[int, Field(description="Zero-based page index.")] = 0,
    size: Annotated[int, Field(description="Number of results per page (max 100).", le=100)] = 20,
    name_filter: Annotated[str | None, Field(description="Optional name/description search.")] = None,
    tags: Annotated[list[str] | None, Field(description="Optional tag filters (exact match).")] = None,
    status: Annotated[str | None, Field(description="Optional status filter (exact match).")] = None,
) -> str:
    """List all test cases in a project.

    Returns a paginated list of test cases with their IDs, names, and tags.
    Use this to review existing test documentation in a project.

    Args:
        project_id: The Allure TestOps project ID to list test cases from.
        page: Page number for pagination (0-indexed). Default: 0.
        size: Number of results per page (max 100). Default: 20.
        name_filter: Optional filter to search by name or description.
        tags: Optional list of tag names to filter by (exact match).
        status: Optional test case status name to filter by (exact match).

    Returns:
        A formatted list of test cases with pagination info.

    Example:
        "Found 45 test cases in project 123 (page 1 of 3):
        - [TC-1] Login Flow (tags: smoke, auth)
        - [TC-2] User Registration (tags: regression)"
    """
    async with AllureClient.from_env() as client:
        service = SearchService(client)
        result = await service.list_test_cases(
            project_id=project_id,
            page=page,
            size=size,
            name_filter=name_filter,
            tags=tags,
            status=status,
        )

    return _format_test_case_list(result)


def _format_test_case_list(result: TestCaseListResult) -> str:
    if not result.items:
        return "No test cases found in this project."

    lines = [f"Found {result.total} test cases (page {result.page + 1} of {result.total_pages}):"]

    for tc in result.items:
        tags = ", ".join([t.name for t in (tc.tags or []) if t.name]) if tc.tags else "none"
        status = tc.status.name if tc.status and tc.status.name else "unknown"
        lines.append(f"- [TC-{tc.id}] {tc.name} (status: {status}; tags: {tags})")

    if result.page < result.total_pages - 1:
        lines.append(f"\nUse page={result.page + 1} to see more results.")

    return "\n".join(lines)
