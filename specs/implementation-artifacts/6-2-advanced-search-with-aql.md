# Story 6.2: Advanced Search with AQL

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want to perform complex searches using Allure's query language (AQL),
so that I can find test cases using sophisticated filtering patterns.

## Epic Context

- Epic 6 focuses on advanced organization and discovery for large-scale test repositories. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-planning-artifacts/epics.md:431-434]
- Related story: 6.1 introduces test hierarchy management (suites/trees). This story should not implement hierarchy, but should remain compatible with future hierarchy-based filters. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-planning-artifacts/epics.md:435-448]

## Acceptance Criteria

1. Given a complex AQL query (e.g., `status:failed AND tag:regression`), when I call `search_test_cases` with the raw AQL query, the server returns all matching test cases. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-planning-artifacts/epics.md:449-461]
2. `search_test_cases` supports AQL operators `and`, `or`, and `not`, and field-specific filters supported by Allure AQL. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-planning-artifacts/epics.md:457-461]
3. Invalid AQL syntax results in a clear, actionable error message. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-planning-artifacts/epics.md:459-461]
4. The tool accepts parentheses for grouping and respects AQL precedence (`and` > `or`). [Source: https://docs.qameta.io/allure-testops/advanced/aql/]
5. The tool accepts quoted string values, numeric comparisons without quotes, boolean `true`/`false`, and `in` lists as supported by AQL. [Source: https://docs.qameta.io/allure-testops/advanced/aql/]
6. Output is LLM-friendly text (no raw JSON) and includes pagination hints when applicable. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-context.md:45-49] [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/search.py:194-207]
7. Pagination enforces the existing max size constraint (<= 100). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/search_service.py:185-191]

## Non-Goals

- Do not create a new tool; advanced search must be provided via `search_test_cases`. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/search.py:50-115]
- Do not implement test hierarchy management or suite CRUD (Story 6.1). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-planning-artifacts/epics.md:435-448]
- Do not modify generated client code under `src/client/generated/`. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/architecture.md:104-110]

## Tasks / Subtasks

- [x] **Tool: search_test_cases (AQL support)** — Extend `search_test_cases` in `src/tools/search.py` with an optional raw AQL parameter (AC: 1-8). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-context.md:25-37]
  - [x] Validate only basic constraints (non-empty AQL when provided, page/size bounds) in the tool; let service errors bubble to the global handler (AC: 3). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-context.md:33-37]
  - [x] Reuse existing formatting helpers for LLM-friendly output. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/search.py:194-207]

- [x] **Service: search_test_cases (AQL passthrough)** — Extend `SearchService.search_test_cases` to accept optional raw AQL; when present, bypass `SearchQueryParser` and pass raw AQL to the client (AC: 1-8). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/search_service.py:132-168]
  - [x] Optionally call AQL validation before executing the query to surface clearer syntax errors. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/docs/TestCaseSearchControllerApi.md:87-139]

- [x] **Client: AQL search & validation** — Extend `AllureClient` with:
  - [x] `search_test_cases_aql(project_id, rql, page, size, deleted, sort)` mapping to `TestCaseSearchControllerApi.search1` (AC: 1-2). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/docs/TestCaseSearchControllerApi.md:11-64]
  - [x] `validate_test_case_query(project_id, rql, deleted)` mapping to `TestCaseSearchControllerApi.validate_query1` and returning `AqlValidateResponseDto(valid, count)`. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/docs/TestCaseSearchControllerApi.md:87-139] [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/models/aql_validate_response_dto.py:25-31]

- [x] **Tests**
  - [x] Update `tests/e2e/test_search_test_cases.py` to cover AQL queries, invalid syntax handling, and pagination hints. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/implementation-artifacts/3-3-search-test-cases-by-name-or-tag.md:62-67]
  - [x] Add unit tests for `SearchService.search_test_cases` covering raw AQL vs. parsed name/tag queries (including invalid AQL). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-context.md:64-69]
  - [x] Regression tests to confirm existing `search_test_cases` and `list_test_cases` output remains unchanged when AQL is not used. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/search.py:9-115]

## Dev Notes

### Dependencies & Reuse Map

- Reuse the existing search/service/tool patterns: `SearchService` + `AllureClient` + formatting helpers. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/search.py:9-207] [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/search_service.py:69-167]
- Do **not** reuse `SearchQueryParser` for AQL; advanced search must pass raw AQL to the Allure search endpoint. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/search_service.py:35-67]

### API Contract (Allure AQL)

- **Search endpoint:** `GET /api/testcase/__search` via `TestCaseSearchControllerApi.search1` with parameters:
  - `project_id` (required), `rql` (AQL string, required), `deleted` (optional), `page` (optional), `size` (optional), `sort` (optional). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/docs/TestCaseSearchControllerApi.md:11-64]
- **Validation endpoint:** `GET /api/testcase/query/validate` via `validate_query1` with `project_id`, `rql`, `deleted`; response includes `valid` and `count`. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/docs/TestCaseSearchControllerApi.md:87-139] [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/models/aql_validate_response_dto.py:25-31]

### AQL Syntax Cheat Sheet (for docstrings/examples)

- Operators: `and`, `or`, `not`.
- Precedence: `and` before `or`; use parentheses to group. [Source: https://docs.qameta.io/allure-testops/advanced/aql/]
- Strings are double-quoted; numbers are unquoted; booleans are `true`/`false`; `in` accepts lists. [Source: https://docs.qameta.io/allure-testops/advanced/aql/]
- Example: `(createdBy = "John" or createdBy = "Jane") and name ~= "test"`.

### Security & Performance Constraints

- Input must be sanitized; API tokens must be masked in logs. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/prd.md:275-277]
- Tool execution overhead must remain under 50ms. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/prd.md:267-269]
- Use global error handling; do not add try/except in tools. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-context.md:33-37]

### Regression Safeguards

- Preserve existing name/tag parsing for non-AQL queries and do not change default filter semantics. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/search_service.py:132-168]
- Ensure existing list/search outputs still pass E2E expectations (LLM-friendly formatting, pagination hints). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/tests/e2e/test_search_test_cases.py:1-67]

### Project Structure Notes

- Tools: `src/tools/search.py` (thin wrappers). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-context.md:55-57]
- Services: `src/services/search_service.py` (business logic). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-context.md:57-58]
- Client wrapper: `src/client/client.py` (extend here; do not edit generated client). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/architecture.md:104-110]

### Completion Checklist

- `search_test_cases` supports raw AQL passthrough and LLM-friendly output.
- AQL validation wired to `validate_query1` and invalid queries yield actionable errors.
- Unit + E2E tests added/updated (including invalid AQL and pagination).
- `ruff` and `mypy --strict` pass; async-only code preserved. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-context.md:15-22]

### References

- Epic 6.2 story and acceptance criteria. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-planning-artifacts/epics.md:449-461]
- Epic 6 scope and Story 6.1 context. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-planning-artifacts/epics.md:431-448]
- Allure AQL endpoints and validation API. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/docs/TestCaseSearchControllerApi.md:11-139]
- Allure AQL syntax reference. [Source: https://docs.qameta.io/allure-testops/advanced/aql/]
- Search tool/service patterns. [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/search.py:9-207] [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/search_service.py:69-167]
- Project rules (thin tool/fat service, error handling, testing). [Source: /Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-context.md:25-69]

## Dev Agent Record

### Agent Model Used

gpt-5.2-codex

### Debug Log References

### Completion Notes List

- Story updated to extend `search_test_cases` instead of adding a new tool.
- Implemented `search_test_cases_aql` and `validate_test_case_query` methods in `AllureClient`.
- Extended `SearchService.search_test_cases` with optional `aql` parameter that bypasses query parser.
- AQL validation is performed before query execution, providing clear error messages for invalid syntax.
- Added comprehensive docstrings with AQL syntax examples in the tool layer.
- All 162 unit/integration tests pass, including 7 new AQL-specific unit tests.
- All 9 E2E search tests pass, including 5 new AQL-specific E2E tests.
- `ruff` and `mypy --strict` pass.

### File List

- src/client/client.py (added `search_test_cases_aql`, `validate_test_case_query`)
- src/services/search_service.py (extended `search_test_cases` with `aql` parameter)
- src/tools/search.py (added optional `aql` parameter to `search_test_cases`)
- tests/unit/test_search_service.py (added 7 AQL unit tests)
- tests/e2e/test_search_test_cases.py (added 5 AQL E2E tests)
- specs/implementation-artifacts/6-2-advanced-search-with-aql.md
- specs/implementation-artifacts/sprint-status.yaml
