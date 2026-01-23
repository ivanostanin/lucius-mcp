from typing import Annotated

from pydantic import Field

from src.client import AllureClient, AllureValidationError
from src.services.search_service import SearchQueryParser, SearchService, TestCaseDetails, TestCaseListResult
from src.utils.auth import AuthContext, get_auth_context
from src.utils.config import settings


def _build_client(api_token: str | None) -> tuple[AllureClient, AuthContext]:
    auth_context = get_auth_context(api_token=api_token)
    client = AllureClient(
        base_url=settings.ALLURE_ENDPOINT,
        token=auth_context.api_token,
    )
    return client, auth_context


async def list_test_cases(
    project_id: Annotated[int, Field(description="Allure TestOps project ID to list test cases from.")],
    page: Annotated[int, Field(description="Zero-based page index.")] = 0,
    size: Annotated[int, Field(description="Number of results per page (max 100).", le=100)] = 20,
    name_filter: Annotated[str | None, Field(description="Optional name/description search.")] = None,
    tags: Annotated[list[str] | None, Field(description="Optional tag filters (exact match).", max_length=100)] = None,
    status: Annotated[str | None, Field(description="Optional status filter (exact match).", max_length=100)] = None,
    api_token: Annotated[str | None, Field(description="Optional API token override.")] = None,
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
        api_token: Optional override for the default API token.

    Returns:
        A formatted list of test cases with pagination info.

    Raises:
        AuthenticationError: If no API token available from environment or arguments.
    """
    client, auth_context = _build_client(api_token)
    async with client:
        service = SearchService(auth_context, client=client)
        result = await service.list_test_cases(
            project_id=project_id,
            page=page,
            size=size,
            name_filter=name_filter,
            tags=tags,
            status=status,
        )

    return _format_test_case_list(result)


async def search_test_cases(
    project_id: Annotated[int, Field(description="Allure TestOps project ID to search test cases in.")],
    query: Annotated[
        str,
        Field(
            description=(
                "Search query. Examples: 'login flow', 'tag:smoke', "
                "'tag:smoke tag:regression', 'authentication tag:security'."
            )
        ),
    ],
    page: Annotated[int, Field(description="Zero-based page index.")] = 0,
    size: Annotated[int, Field(description="Number of results per page (max 100).", le=100)] = 20,
    api_token: Annotated[str | None, Field(description="Optional API token override.")] = None,
) -> str:
    """Search for test cases by name or tag.

    Find test cases matching your search criteria. Supports name search,
    tag filtering, or both combined.

    Query Syntax:
    - Plain text: Searches in test case names (case-insensitive)
    - tag:value: Filters by exact tag match
    - Combined: "login tag:smoke" finds test cases with "login" in name AND "smoke" tag

    Args:
        project_id: The Allure TestOps project ID to search in.
        query: Search query. Examples:
            - "login flow" (name search)
            - "tag:smoke" (tag filter)
            - "tag:smoke tag:regression" (multiple tags - AND logic)
            - "authentication tag:security" (combined)
        page: Page number (0-indexed). Default: 0.
        size: Results per page (max 100). Default: 20.
        api_token: Optional override for the default API token.

    Returns:
        List of matching test cases or "No test cases found matching query."

    Raises:
        AuthenticationError: If no API token available from environment or arguments.

    Examples:
        search_test_cases(123, "login")
        → "Found 5 test cases matching 'login':
           - [TC-1] User Login Flow (tags: smoke, auth)
           - [TC-2] Admin Login Test (tags: admin)"

        search_test_cases(123, "tag:smoke tag:regression")
        → "Found 12 test cases matching 'tag:smoke tag:regression':
           - [TC-5] Critical Path Test ..."
    """
    if not isinstance(query, str) or not query.strip():
        raise AllureValidationError("Search query must be a non-empty string")

    parsed = SearchQueryParser.parse(query)
    if not parsed.name_query and not parsed.tags:
        raise AllureValidationError("Search query must include a name or tag filter")

    client, auth_context = _build_client(api_token)
    async with client:
        service = SearchService(auth_context, client=client)
        result = await service.search_test_cases(
            project_id=project_id,
            query=query,
            page=page,
            size=size,
        )

    return _format_search_results(result, query)


async def get_test_case_details(
    test_case_id: Annotated[int, Field(description="ID of the test case to retrieve.")],
    api_token: Annotated[str | None, Field(description="Optional API token override.")] = None,
) -> str:
    """Get complete details of a specific test case.

    Retrieves all information about a test case including its steps, tags,
    custom fields, and attachments. Use this before updating a test case to
    understand its current state.

    Args:
        test_case_id: The unique ID of the test case to retrieve.
        api_token: Optional override for the default API token.

    Returns:
        Formatted test case details including all metadata.

    Raises:
        AuthenticationError: If no API token available from environment or arguments.
    """
    if not isinstance(test_case_id, int) or test_case_id <= 0:
        raise AllureValidationError("Test case ID must be a positive integer")

    client, auth_context = _build_client(api_token)
    async with client:
        service = SearchService(auth_context, client=client)
        details = await service.get_test_case_details(test_case_id)

    return _format_test_case_details(details)


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


def _format_test_case_details(details: TestCaseDetails) -> str:
    tc = details.test_case
    scenario = details.scenario

    lines: list[str] = [f"**Test Case TC-{tc.id}: {tc.name}**"]
    status_line = _format_status_line(tc)
    lines.append(status_line)

    if getattr(tc, "description", None):
        desc = tc.description or ""
        lines.extend(["**Description:**", desc, ""])

    if getattr(tc, "precondition", None):
        pre = tc.precondition or ""
        lines.extend(["**Preconditions:**", pre, ""])

    if scenario and getattr(scenario, "steps", None):
        lines.append("**Steps:**")
        for i, step in enumerate(getattr(scenario, "steps", []) or [], 1):
            _format_step(step, str(i), lines)
        lines.append("")

    _append_tags(lines, tc)
    _append_custom_fields(lines, tc)
    _append_attachments(lines, scenario)

    return "\n".join(lines)


def _format_search_results(result: TestCaseListResult, query: str) -> str:
    if not result.items:
        return f"No test cases found matching '{query}'."

    lines = [f"Found {result.total} test cases matching '{query}':"]

    for tc in result.items:
        tags = ", ".join([t.name for t in (tc.tags or []) if t.name]) if tc.tags else "none"
        lines.append(f"- [TC-{tc.id}] {tc.name} (tags: {tags})")

    if result.total_pages > 1:
        lines.append(f"\nShowing page {result.page + 1} of {result.total_pages}")

    return "\n".join(lines)


def _format_status_line(tc: object) -> str:
    status_obj = getattr(tc, "status", None)
    status_name = getattr(status_obj, "name", None) if status_obj is not None else None
    status = status_name or "unknown"

    automation_raw = getattr(tc, "automation_status", None) or getattr(tc, "automated", None)
    if automation_raw is None:
        automation_text = "unknown"
    elif isinstance(automation_raw, str):
        automation_text = automation_raw
    else:
        automation_text = "Automated" if bool(automation_raw) else "Manual"

    return f"Status: {status} | Automation: {automation_text}"


def _get_text(obj: object, names: list[str]) -> str | None:
    for name in names:
        if hasattr(obj, name):
            val = getattr(obj, name)
            if val is not None:
                return str(val)
        if isinstance(obj, dict) and name in obj and obj[name] is not None:
            return str(obj[name])
    return None


def _get_raw(obj: object, names: list[str]) -> object | None:
    for name in names:
        if hasattr(obj, name):
            val: object = getattr(obj, name)
            if val is not None:
                return val
        if isinstance(obj, dict) and name in obj:
            raw_obj: object = obj[name]
            if raw_obj is not None:
                return raw_obj
    return None


def _format_step(step: object, index: str, out: list[str]) -> None:
    actual = _get_raw(step, ["actual_instance"]) or _get_raw(step, ["actual"])
    body = _get_text(actual, ["body", "description", "action"]) or _get_text(step, ["body", "description"]) or "Step"
    expected = _get_text(actual, ["expected", "expected_result", "expectedResult"]) or _get_text(
        step, ["expected", "expected_result", "expectedResult"]
    )
    if expected is not None:
        out.append(f"{index}. {body} → {expected}")
    else:
        out.append(f"{index}. {body}")

    child_steps = _get_raw(actual, ["steps"]) or _get_raw(step, ["steps"])
    if isinstance(child_steps, list):
        for j, child in enumerate(child_steps, 1):
            _format_step(child, f"{index}.{j}", out)


def _append_tags(lines: list[str], tc: object) -> None:
    tags = getattr(tc, "tags", None)
    if not tags:
        return
    tag_names = [t.name for t in tags if getattr(t, "name", None)]
    if tag_names:
        lines.append(f"**Tags:** {', '.join(tag_names)}")


def _append_custom_fields(lines: list[str], tc: object) -> None:
    custom_fields = getattr(tc, "custom_fields", None)
    if not custom_fields:
        return
    formatted = []
    for cf in custom_fields:
        key = _get_text(getattr(cf, "custom_field", None), ["name"]) or _get_text(
            cf, ["custom_field_name", "field_name", "name"]
        )
        value = _get_text(cf, ["value", "value_text", "valueName", "value_name", "name"])
        if key and value:
            formatted.append(f"{key}={value}")
    if formatted:
        lines.append(f"**Custom Fields:** {', '.join(formatted)}")


def _append_attachments(lines: list[str], scenario: object | None) -> None:
    attachments = getattr(scenario, "attachments", None) if scenario else None
    if not attachments:
        return

    parts: list[str] = []
    for att in attachments:
        name = _get_text(att, ["name", "file_name", "filename", "title"]) or "attachment"
        att_id = _get_text(att, ["id", "attachment_id", "attachmentId"])
        if att_id:
            parts.append(f"{name} (id: {att_id})")
        else:
            parts.append(name)

    if parts:
        lines.append("**Attachments:** " + ", ".join(parts))
