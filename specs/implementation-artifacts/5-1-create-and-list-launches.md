# Story 5.1: Create & List Launches

Status: ready-for-dev

## Story

As an AI Agent,
I want to create new test launches and list existing ones,
so that I can organize test execution sessions in Allure TestOps.

## Acceptance Criteria

1. **Given** a valid Project ID, **when** I call `create_launch` with a name and optional metadata, **then** a new launch is created in Allure TestOps.
2. **Given** a valid Project ID, **when** I call `list_launches`, **then** it returns all launches for the project including the newly created one.

## Tasks / Subtasks

- [x] **Task 1: Define Launch Tools** (AC: #1, #2)
  - [x] 1.1: Add `create_launch` tool in `src/tools/launches.py` (or `src/tools/launch.py` following existing patterns)
  - [x] 1.2: Add `list_launches` tool with pagination and optional filters
  - [x] 1.3: Add LLM-optimized docstrings for both tools
  - [x] 1.4: Use thin tool / fat service pattern with service calls only

- [x] **Task 2: Implement Launch Service** (AC: #1, #2)
  - [x] 2.1: Create `src/services/launch_service.py`
  - [x] 2.2: Implement `create_launch()` with input validation
  - [x] 2.3: Implement `list_launches()` with pagination
  - [x] 2.4: Return structured results for formatting

- [x] **Task 3: Extend AllureClient** (AC: #1, #2)
  - [x] 3.1: Add `create_launch()` to `src/client/client.py`
  - [x] 3.2: Add `list_launches()` to `src/client/client.py`
  - [x] 3.3: Map responses to generated Pydantic models

- [x] **Task 4: Error Handling** (AC: #1, #2)
  - [x] 4.1: Validate required fields (project_id, name)
  - [x] 4.2: Ensure global exception handler emits Agent Hints

- [x] **Task 5: Unit + Integration Tests** (AC: #1, #2)
  - [x] 5.1: Unit tests for service logic and validation
  - [x] 5.2: Unit tests for tools formatting (LLM-friendly output)
  - [x] 5.3: Integration tests for client request/response mapping

- [x] **Task 6: E2E Tests (if required by NFR11)**
  - [x] 6.1: Add e2e tests for creating and listing launches
  - [x] 6.2: Skip tests when sandbox credentials are missing

## Dev Notes

- Follow the existing tool/service split: tools are thin wrappers, services handle validation and API calls.
- Use `get_auth_context` for runtime auth overrides (FR14).
- Ensure output formatting is LLM-friendly (no raw JSON).

### Project Structure Notes

- Add new launch-related tools under `src/tools/` following existing tool modules.
- Add launch service under `src/services/`.

### References

- [Source: specs/project-planning-artifacts/epics.md#Story 5.1]
- [Source: specs/project-planning-artifacts/epics.md#Epic 5]
- [Source: specs/implementation-artifacts/3-1-list-test-cases-by-project.md#Dev Notes]

## Dev Agent Record

### Agent Model Used

gpt-5.2-codex

### Debug Log References
- N/A

### Completion Notes List
- Added launch client APIs, launch service, launch tools, and tests for create/list flow.

### File List
- src/client/client.py
- src/client/__init__.py
- src/services/launch_service.py
- src/tools/launches.py
- src/tools/__init__.py
- tests/unit/test_launch_service.py
- tests/unit/test_launch_tools.py
- tests/integration/test_launch_tools.py
- tests/integration/test_launch_client.py
- tests/e2e/test_launches.py
