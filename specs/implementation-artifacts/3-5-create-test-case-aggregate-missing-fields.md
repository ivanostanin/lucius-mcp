# Story 3.5: Create test case aggregate missing fields

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want create_test_case to return all missing custom fields and invalid custom field values in one response,
so that I can correct my request in a single retry without guessing which fields exist in the project.

## Acceptance Criteria

1. **Given** a `create_test_case` request with multiple custom fields that do not exist in the target TestOps project,
   **when** validation runs before API creation,
   **then** the tool returns a single error response listing *all* missing custom field names (not just the first).
2. **Given** a `create_test_case` request with custom fields that exist but values are invalid or missing per TestOps constraints,
   **when** validation fails,
   **then** the tool returns a single error response listing *all* invalid custom field values (including which field/value pair failed).
3. Error responses for missing or invalid custom fields include a guidance block that explicitly tells the agent to exclude all missing custom fields from the request, and to correct all listed invalid values before retrying.
4. Errors remain LLM-friendly (plain text, structured list) and are handled via the global Agent Hint flow (no raw JSON or stack traces).
5. Behavior is covered by tests that assert aggregated error output for multiple missing/invalid custom fields.

## Tasks / Subtasks

- [ ] Task 1: Aggregate custom field validation errors in `TestCaseService.create_test_case` (AC: #1-3)
  - [ ] 1.1: Collect all missing custom field names before raising validation error.
  - [ ] 1.2: Collect all invalid custom field values (if values are validated client-side) before raising validation error.
  - [ ] 1.3: Format error message to list all missing fields and invalid values in one response with guidance to exclude missing fields.
- [ ] Task 2: Ensure Agent Hint formatting is preserved and LLM-friendly (AC: #3-4)
  - [ ] 2.1: Use existing AllureValidationError flow for aggregated messages.
  - [ ] 2.2: Maintain structured text output (bulleted list) with explicit guidance block.
- [ ] Task 3: Add/extend tests for aggregated error output (AC: #5)
  - [ ] 3.1: Unit or integration test that passes multiple missing custom fields and asserts all names listed.
  - [ ] 3.2: Unit or integration test that passes invalid custom field values (if applicable) and asserts all listed.

## Dev Notes

### Current Behavior (Observed)
- `TestCaseService.create_test_case` resolves custom fields and raises immediately on the first missing field (see `src/services/test_case_service.py:119-127`).
- Error handling uses `AllureValidationError` which flows through the global agent hint handler (`src/utils/error.py:93-177`) to render LLM-friendly text responses.
- Schema hints are generated via `generate_schema_hint` (`src/utils/schema_hint.py:6-28`).
- Tools should not use try/except; errors should bubble to the global handler (see `specs/project-context.md:33-37`). Note: `src/tools/create_test_case.py` currently catches generic exceptions; do not add new try/except blocks in tools.

### Expected Error Shape
Provide a single error response containing:
- A list of missing custom fields (all of them).
- A list of invalid custom field values (all of them), if validation exists client-side.
- A guidance block telling the agent to remove missing custom fields and correct all invalid values before retrying.

### Relevant Files & Patterns
- `src/services/test_case_service.py:85-175` for custom field resolution and validation.
- `src/utils/error.py:93-177` for Agent Hint formatting.
- `src/client/exceptions.py:19-22` for `AllureValidationError`.
- Tests asserting validation messaging patterns in `tests/integration/test_error_handling.py:45-223`.

### Constraints & Architecture
- Follow "Thin Tool / Fat Service" (tools are wrappers; services contain logic) (`specs/project-context.md:25-32`).
- Use Pydantic strict models and existing validation helpers (`specs/project-context.md:38-41`).
- Do not introduce global state; prefer local aggregation in service method (`specs/project-context.md:70-73`).

### References
- [Source: specs/project-planning-artifacts/epics.md#Epic 3]
- [Source: specs/project-planning-artifacts/epics.md#Story 1.7]
- [Source: specs/prd.md#FR16 - Descriptive error hints]
- [Source: specs/architecture.md#Communication Patterns]
- [Source: specs/project-context.md#Error Handling Strategy]
- [Source: src/services/test_case_service.py:119-127]
- [Source: src/utils/error.py:93-177]

## Dev Agent Record

### Agent Model Used

gpt-5.2-codex

### Debug Log References

### Completion Notes List

### File List

