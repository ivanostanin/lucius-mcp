# Story 3.6: Get custom fields with values

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want a get_custom_fields tool that lists available custom fields and their allowed values for a project,
so that I can build valid create_test_case requests and avoid custom field validation errors.

## Acceptance Criteria

1. **Given** a valid project context, **when** I call `get_custom_fields`, **then** the tool returns all custom fields configured for the project and the allowed values for each field.
2. **Given** a `name` filter, **when** I call `get_custom_fields(name="Layer")`, **then** the tool returns only matching custom fields (case-insensitive match on field name).
3. The response format is LLM-friendly plain text and includes field name, required/optional flag (if available), and a list of allowed values (if provided by the API).
4. Errors follow the global Agent Hint flow (no raw JSON), with clear messages for missing/invalid project context.
5. Behavior is covered by tests (unit or integration) that validate filtering and output formatting.

## Tasks / Subtasks

- [x] Task 1: Add client/service support for fetching custom fields with values (AC: #1-4)
  - [x] 1.1: Add a service method to fetch custom fields via `TestCaseCustomFieldControllerApi.get_custom_fields_with_values2` using `TestCaseTreeSelectionDto(project_id=...)`.
  - [x] 1.2: Normalize response into a simple structure (field name, required flag, values list).
  - [x] 1.3: Apply optional name filter (case-insensitive) before formatting output.
- [x] Task 2: Add `get_custom_fields` tool (AC: #1-4)
  - [x] 2.1: Tool accepts optional `name` filter and `project_id` override.
  - [x] 2.2: Tool formats output as plain text list with field metadata and allowed values.
- [x] Task 3: Add tests for aggregation and filtering (AC: #5)
  - [x] 3.1: Test that filtering by name returns only matching fields.
  - [x] 3.2: Test output formatting includes required flag and values list when present.

## Dev Notes

### Current API Surface
- Generated API supports custom field fetch:
  - `TestCaseCustomFieldControllerApi.get_custom_fields_with_values2` (POST `/api/testcase/cfv`) for project-level custom fields.
  - `TestCaseCustomFieldControllerApi.get_custom_fields_with_values3` (GET `/api/testcase/{testCaseId}/cfv`) for test-case-specific values.
  - See `src/client/generated/docs/TestCaseCustomFieldControllerApi.md:7-145`.
- Generated models for responses:
  - `CustomFieldProjectWithValuesDto` → `customField` (`CustomFieldProjectDto`) + `values` (`CustomFieldValueDto`) (`src/client/generated/models/custom_field_project_with_values_dto.py:27-33`).
  - `CustomFieldProjectDto` contains `name`, `required`, `singleSelect`, and `customField` metadata (`src/client/generated/models/custom_field_project_dto.py:26-41`).

### Expected Output Shape (example)
```
Custom Fields for project 123:
- Layer (required: true)
  values: UI, API, DB
- Component (optional)
  values: Auth, Billing
```

### Implementation Notes
- Uses `TestCaseCustomFieldControllerApi.get_custom_fields_with_values2` (POST `/api/testcase/cfv`)
- Response normalized and cached in `_cf_cache` for performance
- Cache shared between `get_custom_fields` (discovery) and `create_test_case` (validation)
- Caching eliminates duplicate API calls when both methods used in same session

### Relevant Files & Patterns
- `src/client/client.py` for adding a wrapper method if needed (e.g., `get_custom_fields_with_values`) that uses `TestCaseCustomFieldControllerApi`.
- `src/services/...` for new service logic (thin tool, fat service pattern).
- `src/tools/...` for new tool definition and output formatting.
- Tools should not use try/except; errors should bubble to global handler (`specs/project-context.md:33-37`).

### Constraints & Architecture
- Follow "Thin Tool / Fat Service" (tools are wrappers; services contain logic) (`specs/project-context.md:25-32`).
- Use async `httpx` through generated client; no direct HTTP outside `src/client/` (`specs/architecture.md:218-221`).
- No new global state; no wildcard imports; use `uv` commands if dependencies are needed (`specs/project-context.md:65-73`).

### References
- [Source: specs/project-planning-artifacts/epics.md#Epic 3]
- [Source: specs/prd.md#FR16 - Descriptive error hints]
- [Source: specs/architecture.md#Communication Patterns]
- [Source: specs/project-context.md#Error Handling Strategy]
- [Source: src/client/generated/docs/TestCaseCustomFieldControllerApi.md#get_custom_fields_with_values2]
- [Source: src/client/generated/models/custom_field_project_with_values_dto.py:27-33]
- [Source: src/client/generated/models/custom_field_project_dto.py:26-41]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp-01-21

### Debug Log References

### Completion Notes List

- Client method `get_custom_fields_with_values` added to `AllureClient` with proper validation
- Service method `get_custom_fields` implemented with case-insensitive name filtering
- Tool registered in `src/tools/__init__.py` and follows thin tool pattern
- All tests pass: 3 unit, 4 integration, 8 E2E
- Output format is LLM-friendly plain text as specified
- **Performance optimization**: `get_custom_fields` uses shared `_cf_cache` with `create_test_case` to avoid duplicate API calls
- **Cache enhancement**: Added `required` flag to cache structure for complete field information
- **E2E coverage**: Comprehensive sandbox tests cover filtering, output format, cache efficiency, and edge cases

## File List

- src/client/client.py
- src/services/test_case_service.py
- src/tools/get_custom_fields.py
- src/tools/__init__.py
- tests/unit/test_test_case_service_custom_fields.py
- tests/integration/test_custom_fields.py
- tests/integration/test_get_custom_fields_tool.py

## Change Log

| Date | Actor | Description |
| :--- | :--- | :--- |
| 2025-05-23 | Product Owner | Created story |
| 2026-01-29 | Dev Agent | Implemented client/service methods, tool, and tests. |
| 2026-01-29 | Code Review | Fixed missing client export, updated story status and tasks. |

