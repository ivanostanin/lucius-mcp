# Story 3.8: Manage custom fields on test cases

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want to update and clear custom field values on existing test cases,
so that I can maintain accurate metadata without rewriting entire test cases.

## Acceptance Criteria

1. **Given** a valid test case ID and a custom field map, **when** I call `update_test_case(custom_fields={...})`, **then** the tool updates those custom fields using the dedicated custom-field-values endpoint (`PATCH /api/testcase/{testCaseId}/cfv`).
2. **Given** a custom field value set to an explicit empty list of values per API contract, **when** I call `update_test_case(custom_fields=...)`, **then** the tool clears that custom field value on the test case.
3. **Given** a test case ID and project context, **when** I call `get_test_case_custom_fields`, **then** the tool returns the test case’s current custom field values using `GET /api/testcase/{testCaseId}/cfv`.
4. **Given** invalid custom field names or values, **when** the tool validates input, **then** it returns an LLM-friendly error via the global Agent Hint flow (no raw JSON), listing all invalid fields or values.
5. Behavior is covered by tests that verify update, clear, and retrieval flows (including error cases).
6. Tool `create_test_case` supports custom fields and verifies if desired custom field and value exists. If not, fires warning to the user. 
7. E2E tests verify tool execution results against a sandbox TestOps instance or project (per NFR11).


## Tasks / Subtasks

- [ ] Task 1: Add service support for test-case custom field value operations (AC: #1-4)
  - [ ] 1.1: Add service method to fetch custom field values for a test case using `get_custom_fields_with_values3`.
  - [ ] 1.2: Add service method to update custom field values using `update_cfvs_of_test_case` with `CustomFieldWithValuesDto` payload and explicit empty values to clear.
  - [ ] 1.3: Validate custom field names against project-level metadata (`get_custom_fields_with_values2`) and aggregate invalid fields before update.
- [ ] Task 2: Add tools for custom field value management (AC: #1-4)
  - [ ] 2.1: Update `update_test_case` to route custom-field-only updates through the custom field value endpoint (avoid patching unrelated fields).
  - [ ] 2.2: Add `get_test_case_custom_fields` tool to return current custom field values for a test case.
- [ ] Task 3: Add tests (AC: #5)
  - [ ] 3.1: Unit test for update/clear custom field values using mocked API client.
  - [ ] 3.2: Unit test for retrieval of test case custom field values.
  - [ ] 3.3: Error case test for invalid custom field names/values with aggregated error output.

## Dev Notes

### Current API Surface
- `TestCaseCustomFieldControllerApi.get_custom_fields_with_values2` (POST `/api/testcase/cfv`) — project-level custom field metadata and allowed values. [Source: src/client/generated/docs/TestCaseCustomFieldControllerApi.md:7-77]
- `TestCaseCustomFieldControllerApi.get_custom_fields_with_values3` (GET `/api/testcase/{testCaseId}/cfv`) — fetch custom field values for a single test case. [Source: src/client/generated/docs/TestCaseCustomFieldControllerApi.md:79-145]
- `TestCaseCustomFieldControllerApi.update_cfvs_of_test_case` (PATCH `/api/testcase/{testCaseId}/cfv`) — update custom field values for a test case. [Source: src/client/generated/docs/TestCaseCustomFieldControllerApi.md:147-209]
- `CustomFieldWithValuesDto` model for PATCH payloads (customField + values). [Source: src/client/generated/models/custom_field_with_values_dto.py:27-33]

### Existing Behavior & Gaps
- `update_test_case` currently patches custom fields by resolving IDs and sending `custom_fields` inside `TestCasePatchV2Dto` (`src/services/test_case_service.py:419-433`). This bypasses the dedicated `/cfv` endpoint and does not support clearing values explicitly.
- `TestCaseService._get_resolved_custom_fields` already resolves project-level custom field name → ID via `/api/testcase/cfv` (`src/services/test_case_service.py:698-718`). This can be reused for validation and ID resolution.

### Relevant Files & Patterns
- `src/services/test_case_service.py` — core custom field resolution and update logic.
- `src/tools/update_test_case.py` — tool interface to update test cases; should remain thin.
- `src/client/generated/docs/TestCaseCustomFieldControllerApi.md` — custom field endpoints and contracts.
- Tests should follow strict async patterns and `respx` for mocking external calls (`specs/project-context.md:64-69`).

### Constraints & Architecture
- **Thin Tool / Fat Service**: Tools only validate and call services (`specs/project-context.md:25-32`).
- **No try/except in tools**: errors must bubble to global handler (`specs/project-context.md:33-37`).
- **Async httpx only** via generated client (`specs/architecture.md:118-121`).
- **No Any** types (global rule).

### References
- [Source: specs/project-planning-artifacts/epics.md#Epic 3]
- [Source: specs/prd.md#FR4 - Custom Fields]
- [Source: specs/prd.md#FR16 - Descriptive error hints]
- [Source: specs/architecture.md#Communication Patterns]
- [Source: specs/project-context.md#Error Handling Strategy]
- [Source: src/client/generated/docs/TestCaseCustomFieldControllerApi.md]
- [Source: src/services/test_case_service.py:419-433]
- [Source: src/services/test_case_service.py:698-718]

## Dev Agent Record

### Agent Model Used

gpt-5.2-codex

### Debug Log References

### Completion Notes List

### File List

- specs/implementation-artifacts/3-7-manage-test-case-custom-fields.md
