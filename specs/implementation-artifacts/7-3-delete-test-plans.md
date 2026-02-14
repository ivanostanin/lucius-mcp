# Story 7.3: Delete Test Plans

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want to delete or archive obsolete Test Plans,
so that I can maintain a clean and relevant test planning repository.

## Acceptance Criteria

1. **Delete Test Plan**
   - **Given** an existing Test Plan ID
   - **When** I call `delete_test_plan`
   - **Then** the test plan is removed or archived in Allure TestOps
   - **And** the tool returns a confirmation message
   - **And** the operation is idempotent (repeated calls succeed without error)

2. **Error Handling**
   - **Given** a non-existent Test Plan ID
   - **When** I call `delete_test_plan`
   - **Then** the tool returns a clear error message stating the plan was not found (or success if treating delete as "ensure absent")

## Tasks / Subtasks

- [x] Tasks / Subtasks
  - [x] Regenerate API Client (AC: #1)
    - [x] Run `scripts/generate_testops_api_client.sh` to update client with latest methods
    - [x] Verify `delete_plan` (or equivalent) exists in `src/client/generated`
  - [x] Implement Service Layer (AC: #1, #2)
    - [x] Add `delete_plan` method to `src/services/plan_service.py`
    - [x] Handle `404 Not Found` and other errors
  - [x] Implement Tool (AC: #1, #2)
    - [x] Add `delete_test_plan` tool to `src/tools/plans.py`
    - [x] Ensure proper docstrings and argument validation
  - [x] Tests
    - [x] Add unit tests for `delete_plan` in `tests/unit/test_plan_service.py`
    - [x] Add integration tests for `delete_test_plan` in `tests/integration/test_plan_tools.py`
    - [x] Add E2E tests for plan lifecycle in `tests/e2e/test_plan_management.py`

## Dev Notes

- **Client Regeneration:** The `delete_plan` method might be missing in the current generated client. You MUST run `scripts/generate_testops_api_client.sh` to regenerate the client from the OpenAPI spec.
- **Service Logic:** The service should handle the API call and basic error translation.
- **Tool Logic:** The tool should be a thin wrapper around the service.

### Project Structure Notes

- **Tools:** `src/tools/plans.py`
- **Services:** `src/services/plan_service.py`
- **Tests:** `tests/unit/` and `tests/integration/`

### References

- [Source: specs/project-planning-artifacts/epics.md](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/specs/project-planning-artifacts/epics.md)
- [Source: scripts/generate_testops_api_client.sh](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/scripts/generate_testops_api_client.sh)

## Dev Agent Record

### Agent Model Used

Antigravity (Google Deepmind)

### Debug Log References

- Checked `src/client` for `delete_plan` - not found.
- Checked `scripts/filter_openapi.py` - `test-plan-controller` is included.

### Completion Notes List

- Story created based on user request and Epic 7 context.
- Added explicit task to regenerate client.
- Regenerated API client using `scripts/generate_testops_api_client.sh`.
- Identified `delete7` method in generated client.
- Implemented `PlanService.delete_plan` with idempotent 404 handling.
- Implemented `delete_test_plan` tool in `src/tools/plans.py`.
- Added unit tests in `tests/unit/test_plan_service.py`.
- Added integration tests in `tests/integration/test_plan_tools.py`.
- Added E2E tests in `tests/e2e/test_plan_management.py`.
- Verified all tests pass (unit + integration + regression).

### File List

- src/tools/plans.py
- src/services/plan_service.py
- src/services/__init__.py
- tests/unit/test_plan_service.py
- tests/integration/test_plan_tools.py
- tests/e2e/test_plan_management.py
- tests/e2e/helpers/cleanup.py
- tests/agentic/agentic-tool-calls-tests.md
- README.md
- docs/tools.md
- src/client/generated/api/test_plan_controller_api.py (generated)
