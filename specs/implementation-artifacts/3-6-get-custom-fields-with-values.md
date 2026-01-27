# Story 3.6: Get custom fields with values

Status: ready-for-dev

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

- [ ] Task 1: Add client/service support for fetching custom fields with values (AC: #1-4)
  - [ ] 1.1: Add a service method to fetch custom fields via `TestCaseCustomFieldControllerApi.get_custom_fields_with_values2` using `TestCaseTreeSelectionDto(project_id=...)`.
  - [ ] 1.2: Normalize response into a simple structure (field name, required flag, values list).
  - [ ] 1.3: Apply optional name filter (case-insensitive) before formatting output.
- [ ] Task 2: Add `get_custom_fields` tool (AC: #1-4)
  - [ ] 2.1: Tool accepts optional `name` filter and `project_id` override.
  - [ ] 2.2: Tool formats output as plain text list with field metadata and allowed values.
- [ ] Task 3: Add tests for aggregation and filtering (AC: #5)
  - [ ] 3.1: Test that filtering by name returns only matching fields.
  - [ ] 3.2: Test output formatting includes required flag and values list when present.

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
- Component (required: false)
  values: Auth, Billing
```

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

gpt-5.2-codex

### Debug Log References

### Completion Notes List

### File List

