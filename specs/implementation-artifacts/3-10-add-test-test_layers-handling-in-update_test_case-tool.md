# Story 3.10: Add test layer handling in update_test_case tool

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want to update test case test layers via update_test_case with proper validation and idempotent behavior,
so that test layer assignments can be safely modified without invalid IDs or unintended updates.

## Acceptance Criteria

**AC #1: Test Layer Update Support**
**Given** the `update_test_case` tool
**When** I supply `test_layer_id`
**Then** the test case is updated with the new test layer
**And** the response message reflects the change

**AC #2: Test Layer Validation**
**Given** a `test_layer_id` is provided
**When** the layer does not exist in the project
**Then** the update fails with an actionable validation error
**And** the error suggests using `list_test_layers` to find valid IDs

**AC #3: Idempotent Updates**
**Given** the test case already has the provided `test_layer_id`
**When** I call `update_test_case` with that same ID
**Then** the tool reports no changes made (idempotent)
**And** no unnecessary update call is performed

**AC #4: Mixed Updates**
**Given** `test_layer_id` is supplied with other fields
**When** I call `update_test_case`
**Then** the tool updates test layer and other fields together via the patch endpoint
**And** test layer updates follow the same validation rules

**AC #5: Backward Compatibility**
**Given** existing callers that do not specify `test_layer_id`
**When** they call `update_test_case`
**Then** behavior is unchanged and no validation runs for test layers

**AC #6: Unit Tests**
**Given** the update logic changes
**When** running unit tests
**Then** tests cover:
- Valid test_layer_id update
- Invalid test_layer_id validation error
- Idempotent update when layer unchanged
- Mixed update path with test_layer_id

**AC #7: Integration Tests**
**Given** the `update_test_case` tool output
**When** integration tests run
**Then** formatted responses include test layer changes when present

**AC #8: E2E Tests**
**Given** a sandbox Allure TestOps instance with configured test layers
**When** running E2E tests
**Then** tests cover updating a test case test layer with a valid ID
**And** invalid test layer updates return an actionable error

## Tasks / Subtasks

- [x] Task 1: Service validation for test layer updates
  - [x] 1.1: Validate `test_layer_id` format (positive int) in update flow
  - [x] 1.2: Validate test layer existence via `TestLayerService.get_test_layer`
  - [x] 1.3: Ensure idempotent short-circuit when layer unchanged

- [x] Task 2: Update tool output formatting
  - [x] 2.1: Include test layer change in summary when applicable
  - [x] 2.2: Preserve existing message format for backward compatibility

- [x] Task 3: Tests
  - [x] 3.1: Unit tests for validation/idempotency
  - [x] 3.2: Integration tests for output formatting
  - [x] 3.3: E2E tests for test layer update flow (NFR11)

## Dev Notes

### Developer Context (Guardrails)

- Keep tools thin; all validation and API logic belongs in `TestCaseService`. [Source: specs/project-context.md#The-"Thin-Tool-/-Fat-Service"-Pattern]
- No try/except in tools; let exceptions bubble to the global handler. [Source: specs/project-context.md#Error-Handling-Strategy]
- Avoid `Any` in new code and tests; use precise types like `dict[str, object]` or dedicated DTOs. [Source: ~/.claude/CLAUDE.md]
- Do not mute lint checks or exclude tests. [Source: ~/.claude/CLAUDE.md]

### Technical Requirements

- Validate `test_layer_id` format using `_validate_test_layer_id` before attempting updates. [Source: src/services/test_case_service.py:878]
- Validate existence via `_validate_test_layer_exists` (uses `TestLayerService.get_test_layer`). [Source: src/services/test_case_service.py:885]
- Only call existence validation when the requested ID differs from the current layer to preserve idempotency and avoid extra API calls. [Source: src/services/test_case_service.py:562]
- Ensure the update summary uses `is not None` checks (not truthiness) for `test_layer_id` so updates are reported consistently. [Source: src/tools/update_test_case.py:96]
- Preserve the custom-field-only update path; do not route CF-only updates through the patch endpoint. [Source: src/services/test_case_service.py:327]

### Architecture Compliance

- Reuse `TestLayerService` (no duplicate test layer logic). [Source: specs/implementation-artifacts/3-9-test-layer-validation-in-create-test-case.md#Implementation-Constraints]
- Use the existing service update flow (`update_test_case` → `_prepare_field_updates`). [Source: src/services/test_case_service.py:313]
- Keep patch payload minimal to avoid unintended updates. [Source: src/services/test_case_service.py:562]

### Library/Framework Requirements

- Python 3.14, Pydantic v2 strict mode, async `httpx`, pytest, respx. [Source: specs/project-context.md#Technology-Stack-&-Versions]
- Use existing generated client models and DTOs; no new dependencies.

### File Structure Requirements

- `src/services/test_case_service.py` (update validation and idempotency)
- `src/services/test_layer_service.py` (reuse existing API calls)
- `src/tools/update_test_case.py` (summary formatting only)
- Tests: `tests/unit/test_test_case_service_update_extensions.py`, `tests/integration/*`, `tests/e2e/test_update_test_case*.py`

### Testing Requirements

- Unit tests for validation/idempotency, using AsyncMock and no `Any` usage.
- Integration tests for tool summary formatting.
- E2E tests for updating test layer with a valid ID and failing on invalid IDs (NFR11 coverage).
- Run unit + integration tests:
  - `uv run --env-file .env.test pytest tests/unit/ tests/integration/`
- Run E2E tests in parallel:
  - `uv run --env-file .env.test pytest tests/e2e/ -n auto --dist loadfile`

### Previous Story Intelligence

- Story 3.9 established test layer validation in `create_test_case`; reuse the same validation patterns and error messaging conventions. [Source: specs/implementation-artifacts/3-9-test-layer-validation-in-create-test-case.md]
- Story 3.8 introduced dedicated custom-field endpoints and validation; avoid regressing CF-only update behavior in `update_test_case`. [Source: specs/implementation-artifacts/3-8-manage-test-case-custom-fields.md]

### Git Intelligence Summary

- Recent commits show changes in `test_case_service` for custom fields and test layer CRUD; align new changes with those patterns and existing tests. [Source: git log -5]

### Latest Tech Information

- No external research required; rely on existing generated client and project patterns.

### Project Context Reference

- Project rules and patterns are in `specs/project-context.md` and must be followed for all updates.

### References

- Update flow: src/services/test_case_service.py:313
- Field patching/idempotency: src/services/test_case_service.py:562
- Test layer validation helpers: src/services/test_case_service.py:878
- Update tool summary formatting: src/tools/update_test_case.py:96
- Test layer validation requirements: specs/implementation-artifacts/3-9-test-layer-validation-in-create-test-case.md
- Custom field update constraints: specs/implementation-artifacts/3-8-manage-test-case-custom-fields.md

## Story Completion Status

- Status: done
- Completion note: Implemented test layer update validation/idempotency, updated tool summary, and added coverage in unit/integration/e2e tests.

## Dev Agent Record

### Agent Model Used

gpt-5.2-codex

### Debug Log References

- Unit/integration: `uv run --env-file .env.test pytest tests/unit/ tests/integration/`
- E2E (parallel): `uv run --env-file .env.test pytest tests/e2e/ -n auto --dist loadfile`
- E2E (sequential): `uv run --env-file .env.test pytest tests/e2e/`

### Completion Notes List

- Added test layer validation + idempotent update handling in update_test_case.
- Updated tool summary formatting to reflect test layer changes when provided.
- Added unit/integration/e2e coverage for test layer update behavior and errors.

### File List

- src/services/test_case_service.py
- src/services/test_layer_service.py
- src/tools/update_test_case.py
- tests/unit/test_test_case_service_update_extensions.py
- tests/integration/test_tool_hints.py
- tests/e2e/test_update_test_case.py
- specs/implementation-artifacts/3-10-add-test-test_layers-handling-in-update_test_case-tool.md

### Change Log

- Added test layer existence validation for update_test_case with idempotent skip.
- Updated update_test_case tool summary guard for test_layer_id/status_id.
- Added unit/integration/e2e coverage for test layer updates and errors.
- Ensured test layer lookup maps 404s to AllureNotFoundError.
