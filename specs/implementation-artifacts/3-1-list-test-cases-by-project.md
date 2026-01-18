# Story 3.1: List Test Cases by Project

Status: ready-for-dev

## Story

As an AI Agent,
I want to list all Test Cases within a specific project,
so that I can get an overview of the existing test documentation.

## Acceptance Criteria

1. **Given** a valid Project ID, **when** I call `list_test_cases`, **then** the tool returns a list of Test Cases (ID, Name, Tags) for that project.
2. The list supports pagination for large result sets (page/size; max size enforced).
3. The list can be filtered by optional query parameters (name, tag, status). Filtering is compatible with the Allure TestOps AQL - https://docs.qameta.io/allure-testops/advanced/aql/
4. Tool returns LLM-friendly text output, not raw JSON.
5. Handles invalid or non-existent Project ID with a clear error hint from the global exception handler.
6. **NFR11 / AC11 (E2E):** End-to-end tests run against a sandbox TestOps instance and validate:
   - `list_test_cases` returns expected items for a known project,
   - pagination works across multiple pages,
   - output formatting is LLM-friendly (no raw JSON),
   - tests skip when sandbox credentials are not configured.

## Tasks / Subtasks

- [x] **Task 1: Define List Test Cases Tool** (AC: #1, #4)
  - [x] 1.1: Create `list_test_cases` tool in `src/tools/search.py`
  - [x] 1.2: Define input model with `project_id` and optional filters
  - [x] 1.3: Add comprehensive Google-style docstring for LLM discovery
  - [x] 1.4: Implement thin wrapper calling service layer

- [x] **Task 2: Implement Search Service** (AC: #1, #2, #3)
  - [x] 2.1: Create `src/services/search_service.py`
  - [x] 2.2: Implement `list_test_cases()` with pagination
  - [x] 2.3: Add optional filters (name, tags, status)
  - [x] 2.4: Return structured data (list + page metadata)

- [x] **Task 3: Extend AllureClient** (AC: #1, #2)
  - [x] 3.1: Add `list_test_cases()` to `src/client/client.py`
  - [x] 3.2: Implement pagination (page/size)
  - [x] 3.3: Map API response to Pydantic models

- [x] **Task 4: Error Handling** (AC: #5)
  - [x] 4.1: Validate `project_id`
  - [x] 4.2: Ensure global exception handler emits Agent Hints

- [x] **Task 5: Unit Tests** (AC: #1, #2, #3)
  - [x] 5.1: Unit tests for pagination and filters using `respx`
- 
- [x] **Task 6: Unit Tests** (AC: #1, #2, #3)
  - [x] 6.1: Add unit tests for `SearchService.list_test_cases()`
  - [x] 6.2: Test pagination edge cases (empty results, single page, multiple pages)
  - [x] 6.3: Test filter combinations
  - [x] 6.4: Mock `AllureClient` responses with `respx`

- [ ] **Task 7: E2E Tests for Listing** (AC: #6)
  - [ ] 7.1: Add `tests/e2e/test_list_test_cases.py`
  - [ ] 7.2: Verify pagination across multiple pages
  - [ ] 7.3: Validate LLM-friendly output format (no raw JSON)
  - [ ] 7.4: Skip gracefully when sandbox credentials are absent

## Dev Notes

### FR10 Coverage
This story addresses **FR10** (list Test Cases filtered by Project ID).

### NFR11 / AC11 Coverage
This story must extend the E2E suite to include `list_test_cases` behavior in a sandbox instance. Use the existing E2E harness from Story 1.6.

### API Endpoint Reference

**Allure TestOps API:**
```
GET /api/rs/testcase
Query Parameters:
  - projectId: integer (REQUIRED)
  - page: integer (default: 0)
  - size: integer (default: 20, max: 100)
  - search: string (optional - name/description search)
```

### Tool Implementation Pattern
- Tools are thin wrappers (no business logic, no try/except).
- Services contain validation and API calls.
- Use `get_auth_context` for runtime overrides (FR14).

Follow the "Thin Tool / Fat Service" pattern:

```python
# src/tools/search.py
from mcp.server.fastmcp import FastMCP
from src.services.search_service import SearchService
from src.utils.auth import get_auth_context

mcp = FastMCP("lucius-mcp")

@mcp.tool
async def list_test_cases(
    project_id: int,
    page: int = 0,
    size: int = 20,
    name_filter: str | None = None,
    api_token: str | None = None,
) -> str:
    """List all test cases in a project.
    
    Returns a paginated list of test cases with their IDs, names, and tags.
    Use this to discover existing test cases before creating new ones.
    
    Args:
        project_id: The Allure TestOps project ID to list test cases from.
        page: Page number for pagination (0-indexed). Default: 0.
        size: Number of results per page (max 100). Default: 20.
        name_filter: Optional filter to search by name.
        api_token: Optional override for the default API token.
    
    Returns:
        A formatted list of test cases with pagination info.
    
    Example:
        "Found 45 test cases in project 123 (page 1 of 3):
        - [TC-1] Login Flow (tags: smoke, auth)
        - [TC-2] User Registration (tags: regression)"
    """
    auth_context = get_auth_context(api_token=api_token)
    service = SearchService(auth_context)
    
    result = await service.list_test_cases(
        project_id=project_id,
        page=page,
        size=size,
        name_filter=name_filter,
    )
    
    # Format as LLM-friendly text
    return _format_test_case_list(result)
```

### Service Implementation

```python
# src/services/search_service.py
from dataclasses import dataclass
from src.client import AllureClient
from src.client.models import TestCaseSummary

@dataclass
class TestCaseListResult:
    """Result of listing test cases."""
    items: list[TestCaseSummary]
    total: int
    page: int
    size: int
    total_pages: int

class SearchService:
    """Service for search and discovery operations."""
    
    def __init__(self, auth_context: AuthContext):
        self._client = AllureClient(auth_context)
    
    async def list_test_cases(
        self,
        project_id: int,
        page: int = 0,
        size: int = 20,
        name_filter: str | None = None,
    ) -> TestCaseListResult:
        """List test cases in a project with pagination."""
        response = await self._client.list_test_cases(
            project_id=project_id,
            page=page,
            size=size,
            search=name_filter,
        )
        
        return TestCaseListResult(
            items=response.content,
            total=response.total_elements,
            page=response.page,
            size=response.size,
            total_pages=response.total_pages,
        )
```

### Response Formatting

```python
def _format_test_case_list(result: TestCaseListResult) -> str:
    """Format test case list as LLM-friendly text."""
    if not result.items:
        return "No test cases found in this project."
    
    lines = [
        f"Found {result.total} test cases (page {result.page + 1} of {result.total_pages}):",
    ]
    
    for tc in result.items:
        tags = ", ".join(tc.tags) if tc.tags else "none"
        lines.append(f"- [TC-{tc.id}] {tc.name} (tags: {tags})")
    
    if result.page < result.total_pages - 1:
        lines.append(f"\nUse page={result.page + 1} to see more results.")
    
    return "\n".join(lines)
```

### Project Structure Notes
```
src/tools/search.py          # NEW - Search/list tools
src/services/search_service.py  # NEW - Search business logic
```

### Dependencies

- Requires `AllureClient` from Story 1.2
- Reuses authentication middleware from Story 1.1
- Extends generated Pydantic models

### Testing Strategy

**Unit Tests:**
```python
# tests/unit/test_search_service.py
import pytest
from unittest.mock import AsyncMock
from src.services.search_service import SearchService

async def test_list_test_cases_returns_paginated_results():
    """Service should return paginated test case list."""
    mock_client = AsyncMock()
    mock_client.list_test_cases.return_value = PagedResponse(
        content=[TestCaseSummary(id=1, name="Test")],
        total_elements=1,
        page=0,
        size=20,
        total_pages=1,
    )
    
    service = SearchService(mock_client)
    result = await service.list_test_cases(project_id=123)
    
    assert len(result.items) == 1
    assert result.total == 1
```

### References
- [Source: specs/project-planning-artifacts/epics.md#Story 3.1]
- [Source: specs/prd.md#NFR11 - End-to-End Tests]
- [Source: specs/architecture.md#Implementation Patterns]
- [Source: specs/project-context.md#Thin Tool / Fat Service Pattern]
- [Source: specs/implementation-artifacts/1-6-comprehensive-end-to-end-tests.md#NFR11 Coverage]

## Dev Agent Record

### Agent Model Used
gpt-5.2-codex

### Completion Notes List

- Implemented list_test_cases tool with LLM-friendly formatting and optional filters.
- Added SearchService to validate inputs and return paginated results.
- Extended AllureClient to list test cases via AQL search with tag/status filters.
- Added unit tests covering pagination, filters, and validation.

### File List

- src/client/__init__.py
- src/client/client.py
- src/services/search_service.py
- src/tools/search.py
- tests/unit/test_search_service.py
