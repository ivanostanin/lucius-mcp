# Story 3.3: Search Test Cases by Name or Tag

Status: in-progress

## Story

As an AI Agent,
I want to search for Test Cases using keywords in their name or by specific tags,
so that I can quickly find relevant test documentation.

## Acceptance Criteria

1. **Given** a search query (e.g., "login flow" or "tag:smoke"), **when** I call `search_test_cases`, **then** the tool returns a list of matching Test Cases.
2. Search is case-insensitive for both names and tags.
3. Supports searching by name substring.
4. Supports searching by exact tag match using `tag:` prefix.
5. Supports combined search (name AND tag).
6. Returns paginated results for large result sets.
7. Returns clear message when no matches found.
8. **NFR11 / AC11 (E2E):** End-to-end tests run against a sandbox TestOps instance and validate:
   - name-only search results,
   - tag-only search results (single and multiple tags),
   - combined name+tag queries,
   - case-insensitive behavior,
   - output formatting is LLM-friendly (no raw JSON),
   - tests skip when sandbox credentials are not configured.

## Tasks / Subtasks

- [x] **Task 1: Define Search Test Cases Tool** (AC: #1, #7)
  - [x] 1.1: Create `search_test_cases` tool in `src/tools/search.py`
  - [x] 1.2: Define search query parameter with LLM-friendly examples
  - [x] 1.3: Add pagination parameters (page, size)
  - [x] 1.4: Add comprehensive docstring with query syntax examples

- [x] **Task 2: Implement Search Query Parser** (AC: #3, #4, #5)
  - [x] 2.1: Create `SearchQueryParser` class in `src/services/search_service.py`
  - [x] 2.2: Parse `tag:value` syntax for tag filtering
  - [x] 2.3: Handle plain text as name search
  - [x] 2.4: Support multiple tags (e.g., "tag:smoke tag:auth")
  - [x] 2.5: Support combined name+tag (e.g., "login tag:auth")

- [x] **Task 3: Extend Search Service** (AC: #1, #2, #6)
  - [x] 3.1: Add `search_test_cases()` method
  - [x] 3.2: Implement case-insensitive search logic
  - [x] 3.3: Combine API filters based on parsed query
  - [x] 3.4: Return paginated results

- [x] **Task 4: Extend AllureClient** (AC: #1, #4)
  - [x] 4.1: Add search endpoint support with filters
  - [x] 4.2: Support tag filtering query parameter
  - [x] 4.3: Handle API-level case sensitivity

- [x] **Task 5: Unit Tests** (AC: #1-7)
  - [x] 5.1: Test name-only search
  - [x] 5.2: Test tag-only search (single and multiple)
  - [x] 5.3: Test combined name+tag search
  - [x] 5.4: Test case-insensitivity
  - [x] 5.5: Test empty results handling
  - [x] 5.6: Test query parser independently

- [x] **Task 6: E2E Tests for Search** (AC: #8)
  - [x] 6.1: Add `tests/e2e/test_search_test_cases.py`
  - [x] 6.2: Verify name-only and tag-only queries in sandbox
  - [x] 6.3: Verify combined queries and case-insensitivity
  - [x] 6.4: Validate LLM-friendly output (no raw JSON)
  - [x] 6.5: Skip gracefully when sandbox credentials are absent

## Dev Notes

### FR12 Coverage
This story addresses **FR12** (search by name or tag).

### NFR11 / AC11 Coverage
This story must extend the E2E suite to include `search_test_cases` behavior using the sandbox instance (Story 1.6 harness).

### Search Query Syntax
| Query Type | Example | Description |
|------------|---------|-------------|
| Name search | `login flow` | Searches test case names |
| Tag search | `tag:smoke` | Filters by exact tag |
| Multiple tags | `tag:smoke tag:regression` | Must have ALL tags |
| Combined | `login tag:auth` | Name contains "login" AND has "auth" tag |

### API Endpoint Reference
GET /api/rs/testcase (query: projectId, search, tag)

**Allure TestOps API:**
```
GET /api/rs/testcase
Query Parameters:
  - projectId: integer (REQUIRED)
  - search: string (name/description search)
  - tag: string (can be repeated for multiple tags)
```

### Tool Implementation

```python
# src/tools/search.py

@mcp.tool
async def search_test_cases(
    project_id: int,
    query: str,
    page: int = 0,
    size: int = 20,
    api_token: str | None = None,
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
    
    Examples:
        search_test_cases(123, "login")
        → "Found 5 test cases matching 'login':
           - [TC-1] User Login Flow (tags: smoke, auth)
           - [TC-2] Admin Login Test (tags: admin)"
        
        search_test_cases(123, "tag:smoke tag:regression")
        → "Found 12 test cases with tags [smoke, regression]:
           - [TC-5] Critical Path Test ..."
    """
    auth_context = get_auth_context(api_token=api_token)
    service = SearchService(auth_context)
    
    parsed = SearchQueryParser.parse(query)
    result = await service.search_test_cases(
        project_id=project_id,
        name_filter=parsed.name_query,
        tags=parsed.tags,
        page=page,
        size=size,
    )
    
    return _format_search_results(result, query)
```

### Query Parser Implementation

```python
# src/services/search_service.py
import re
from dataclasses import dataclass

@dataclass
class ParsedQuery:
    """Parsed search query components."""
    name_query: str | None
    tags: list[str]

class SearchQueryParser:
    """Parses search queries into structured components."""
    
    TAG_PATTERN = re.compile(r"tag:(\S+)", re.IGNORECASE)
    
    @classmethod
    def parse(cls, query: str) -> ParsedQuery:
        """Parse a search query into name and tag components.
        
        Args:
            query: Raw search query string.
        
        Returns:
            ParsedQuery with separated name and tag filters.
        
        Examples:
            >>> SearchQueryParser.parse("login flow")
            ParsedQuery(name_query="login flow", tags=[])
            
            >>> SearchQueryParser.parse("tag:smoke tag:auth")
            ParsedQuery(name_query=None, tags=["smoke", "auth"])
            
            >>> SearchQueryParser.parse("login tag:auth")
            ParsedQuery(name_query="login", tags=["auth"])
        """
        tags = cls.TAG_PATTERN.findall(query)
        name_query = cls.TAG_PATTERN.sub("", query).strip()
        
        return ParsedQuery(
            name_query=name_query if name_query else None,
            tags=[t.lower() for t in tags],  # Case-insensitive
        )
```

### Service Extension

```python
# src/services/search_service.py

async def search_test_cases(
    self,
    project_id: int,
    name_filter: str | None = None,
    tags: list[str] | None = None,
    page: int = 0,
    size: int = 20,
) -> TestCaseListResult:
    """Search test cases by name and/or tags."""
    response = await self._client.search_test_cases(
        project_id=project_id,
        search=name_filter,
        tags=tags,
        page=page,
        size=size,
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
def _format_search_results(result: TestCaseListResult, query: str) -> str:
    """Format search results with query context."""
    if not result.items:
        return f"No test cases found matching '{query}'."
    
    lines = [f"Found {result.total} test cases matching '{query}':"]
    
    for tc in result.items:
        tags = ", ".join(tc.tags) if tc.tags else "none"
        lines.append(f"- [TC-{tc.id}] {tc.name} (tags: {tags})")
    
    if result.total_pages > 1:
        lines.append(f"\nShowing page {result.page + 1} of {result.total_pages}")
    
    return "\n".join(lines)
```

### Project Structure Notes

Files modified:
- `src/tools/search.py` - Add `search_test_cases` tool
- `src/services/search_service.py` - Add query parser and search method
- `src/client/client.py` - Add search endpoint support

### Testing Strategy

```python
# tests/unit/test_query_parser.py

class TestSearchQueryParser:
    def test_parse_name_only(self):
        result = SearchQueryParser.parse("login flow")
        assert result.name_query == "login flow"
        assert result.tags == []
    
    def test_parse_single_tag(self):
        result = SearchQueryParser.parse("tag:smoke")
        assert result.name_query is None
        assert result.tags == ["smoke"]
    
    def test_parse_multiple_tags(self):
        result = SearchQueryParser.parse("tag:smoke tag:regression")
        assert result.name_query is None
        assert result.tags == ["smoke", "regression"]
    
    def test_parse_combined(self):
        result = SearchQueryParser.parse("login tag:auth")
        assert result.name_query == "login"
        assert result.tags == ["auth"]
    
    def test_parse_case_insensitive_tags(self):
        result = SearchQueryParser.parse("tag:SMOKE tag:Auth")
        assert result.tags == ["smoke", "auth"]
```
```
src/tools/search.py
src/services/search_service.py
tests/unit/test_query_parser.py
tests/e2e/test_search_test_cases.py   # new
```

### References
- [Source: specs/project-planning-artifacts/epics.md#Story 3.3]
- [Source: specs/prd.md#NFR11 - End-to-End Tests]
- [Source: specs/architecture.md#Communication Patterns]
- [Source: specs/project-context.md#Naming Patterns]
- [Source: specs/implementation-artifacts/1-6-comprehensive-end-to-end-tests.md#NFR11 Coverage]

## Senior Developer Review (AI)

### Findings Summary
- ✅ Addressed E2E multi-tag coverage for AC8.
- ✅ Restored thin-tool boundary by moving validation fully into the service.
- ✅ Removed duplicate validation logic.

### Review Notes
- Updated `tests/e2e/test_search_test_cases.py` to include multi-tag scenario.
- Removed tool-level query validation in `src/tools/search.py`; validation remains in service.
- Story status set to `in-progress` pending re-review after fixes.

### Change Log
- Added multi-tag E2E coverage for `search_test_cases`.
- Removed tool-level query validation to comply with thin-tool pattern.
- Updated story file list to reflect actual modified files.

## Dev Agent Record

### Agent Model Used
gpt-5.2-codex

### Completion Notes List
- Implemented search_test_cases tool with query parsing and LLM-friendly formatting.
- Added SearchQueryParser and SearchService.search_test_cases for name/tag filtering.
- Added unit tests for parser/formatter and E2E search tests (skip without sandbox creds).
- [AI Review] Moved search query validation fully into SearchService to keep tools thin.
- [AI Review] Added E2E multi-tag coverage for search queries.
- Tests: `uv run --env-file .env.test pytest tests/unit/ tests/integration/`

### File List
- specs/implementation-artifacts/3-3-search-test-cases-by-name-or-tag.md
- src/services/search_service.py
- src/tools/search.py
- tests/e2e/test_search_test_cases.py
