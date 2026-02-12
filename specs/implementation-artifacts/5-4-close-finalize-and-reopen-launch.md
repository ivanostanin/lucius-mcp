# Story 5.4: Close/Finalize & Reopen Launch

Status: review

## Dev Agent Guardrails

- Do not add business logic in tools; services own validation and API calls.
- Keep all HTTP calls async via `httpx`; never use sync clients.
- Use Pydantic v2 strict models and `model_validate` for DTO validation.
- Raise typed exceptions in services; avoid try/except in tools.

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want to finalize a launch and mark it as complete, or reopen a closed launch,
so that I can control the launch lifecycle and make corrections when needed.

## Acceptance Criteria

1. **Given** an open Launch ID, **when** I call `close_launch`, **then** the launch status is updated to "Closed" or "Finalized".
2. **Given** an open Launch ID, **when** I call `close_launch`, **then** Allure TestOps triggers report generation for that launch (as reflected by API response or status fields).
3. **Given** a closed Launch ID, **when** I call `reopen_launch`, **then** the launch status is updated to "Open".
4. **Given** a closed Launch ID, **when** I call `reopen_launch`, **then** subsequent result uploads are accepted by the API (validated in E2E tests if the result-upload path exists in this repo).
5. **Given** an invalid state transition (close an already closed launch or reopen an open launch), **when** I call the tool, **then** a clear error or idempotent no-op is returned consistent with API behavior.

## Tasks / Subtasks

- [x] **Task 1: Define Close/Reopen Tools** (AC: #1-#4)
  - [x] 1.1: Add `close_launch` tool in `src/tools/launches.py` following existing launch tool patterns
  - [x] 1.2: Add `reopen_launch` tool in `src/tools/launches.py`
  - [x] 1.3: Add LLM-optimized docstrings with args for Launch ID and optional auth override
  - [x] 1.4: Keep tools thin (validate args, call service, format response)

- [x] **Task 2: Implement Launch Lifecycle Service** (AC: #1-#4)
  - [x] 2.1: Add `close_launch()` and `reopen_launch()` to `src/services/launch_service.py`
  - [x] 2.2: Validate Launch ID input and raise `AllureValidationError` for invalid IDs
  - [x] 2.3: Map close/reopen responses to structured data for tool formatting

- [x] **Task 3: Extend AllureClient** (AC: #1-#4)
  - [x] 3.1: Add `close_launch()` and `reopen_launch()` requests to `src/client/client.py`
  - [x] 3.2: Map responses to generated Pydantic models or compatible DTOs

- [x] **Task 4: Error Handling & Agent Hints** (AC: #3)
  - [x] 4.1: Ensure invalid state transitions raise `AllureAPIError`
  - [x] 4.2: Confirm global error handler formats clear Agent Hints

- [x] **Task 5: Tests** (AC: #1-#4)
  - [x] 5.1: Unit tests for `LaunchService.close_launch()` and `LaunchService.reopen_launch()`
  - [x] 5.2: Integration tests for client request/response mapping
  - [x] 5.3: Tool output tests for LLM-friendly formatting
  - [x] 5.4: E2E test for close/reopen flows (skip when sandbox credentials missing)

## Dev Notes

### Developer Context

- This story extends the Launch tooling introduced in Story 5.1 (create/list), 5.2 (get), and 5.3 (delete).
- Reuse existing launch DTOs and client/service patterns; do not duplicate request helpers.
- Use `get_auth_context` to honor runtime auth overrides (FR14).

### Technical Requirements

- Python 3.14 with `uv`; async-only `httpx` for all HTTP calls.
- Pydantic v2 strict models; use `model_validate` for DTO validation.
- Do not use `typing.Any` in new code; keep `mypy --strict` clean.
- No try/except in tools; raise typed exceptions in services and rely on the global handler.
- Use structured logging; do not use `print()`.

### Architecture Compliance

- **Thin tool / fat service**: tools only validate arguments, call the service, and format output.
- Services perform API calls via `AllureClient` and return structured data (no MCP-formatted text).
- Do not edit generated client models in `src/client/`.

### Library / Framework Requirements

- FastMCP v2 on Starlette, Pydantic v2, httpx (async), ruff, mypy.

### File Structure Requirements

- Tools: `src/tools/launches.py` (or existing launch tool module).
- Services: `src/services/launch_service.py`.
- Client: `src/client/client.py`.
- Tests: `tests/unit/`, `tests/integration/`, `tests/e2e/`.

### Testing Requirements

- Unit tests for `LaunchService.close_launch()` and `LaunchService.reopen_launch()`.
- Integration tests for client request/response mapping.
- Tool output tests for LLM-friendly formatting (explicitly assert output string format).
- E2E test for close/reopen flows (skip when sandbox credentials missing).
- Error-case tests for invalid state transitions.
- Do not mute lint checks or exclude tests; keep coverage >85% and `mypy --strict` green.

### Previous Story Intelligence (Story 5.3)

- Delete launch patterns should be reused for ID validation and error messaging.
- LLM-friendly output formatting established for launch tools.

### Git Intelligence Summary

- Recent commits focus on launch create/list and related client/service/test updates.
- Launch work touched `src/client/client.py`, `src/services/launch_service.py`, and launch tests.

### Latest Technical Information

- Allure TestOps launches are open while results are uploaded; closing finalizes the launch and triggers report processing.
- Closed launches reject new results; reopening restores the ability to add results.
- Confirm close/reopen endpoints and response fields in the instance Swagger/OpenAPI before implementing.

### Project Context Reference

- [Source: specs/project-context.md#Technology Stack & Versions]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: specs/project-context.md#Error Handling Strategy]
- [Source: specs/project-context.md#Development Workflow]

### References

- [Source: specs/project-planning-artifacts/epics.md#Story 5.4]
- [Source: specs/project-planning-artifacts/epics.md#Epic 5]
- [Source: specs/implementation-artifacts/5-1-create-and-list-launches.md#Dev Notes]
- [Source: specs/implementation-artifacts/5-2-get-launch-details.md#Dev Notes]

## Dev Agent Record

### Agent Model Used

gpt-5.2-codex

### Debug Log References

- Focused launch suites: `uv run --extra dev --env-file .env.test pytest tests/unit/test_launch_service.py tests/unit/test_launch_tools.py tests/integration/test_launch_client.py tests/integration/test_launch_tools.py` (pass)
- Story E2E file: `uv run --extra dev --env-file .env.test pytest tests/e2e/test_launches.py` (blocked by sandbox connectivity in this environment)
- Required broader suites:
  - `uv run --extra dev --env-file .env.test pytest tests/unit/ tests/integration/` (pass)
  - `uv run --extra dev --env-file .env.test pytest tests/e2e/ -n auto --dist loadfile` (fails due to sandbox endpoint DNS/connectivity)
  - reran failing story E2E tests one-by-one:
    - `uv run --extra dev --env-file .env.test pytest tests/e2e/test_launches.py::test_create_close_reopen_launch_lifecycle`
    - `uv run --extra dev --env-file .env.test pytest tests/e2e/test_launches.py::test_reopened_launch_accepts_upload_if_supported`
- Quality gates:
  - `uv run --extra dev ruff check src/client/client.py src/services/launch_service.py src/tools/launches.py src/tools/__init__.py tests/unit/test_launch_service.py tests/unit/test_launch_tools.py tests/integration/test_launch_client.py tests/integration/test_launch_tools.py tests/e2e/test_launches.py` (pass)
  - `uv run --extra dev mypy --strict src/` (pass)

### Completion Notes List

- Implemented launch lifecycle wrappers in `AllureClient`: `close_launch` and `reopen_launch` with launch ID validation and `_call_api` typed error propagation.
- Implemented service lifecycle operations in `LaunchService`: `close_launch` and `reopen_launch`, reusing existing validators and mapping `AllureNotFoundError` to `LaunchNotFoundError` consistently with `get_launch`.
- Added thin MCP tools `close_launch` and `reopen_launch` with optional `project_id` and `api_token` runtime override support via `get_auth_context`, and lifecycle-first formatted output while reusing `_format_launch_detail`.
- Registered lifecycle tools in `src/tools/__init__.py` (`imports`, `__all__`, and `all_tools`).
- Added/updated tests across unit, integration, and e2e files for client/service/tool lifecycle behavior, invalid IDs, not-found mapping, invalid transitions, and lifecycle output formatting.
- AC4 handling is implemented as conditional in E2E: when a launch-result-upload path is not exposed in this repo client surface, assertion is explicitly skipped with reason.
- Local environment note: E2E execution is currently blocked by sandbox connectivity (`AllureAPIError` from token exchange DNS/connect failure), so E2E remains pending external environment validation.

### File List

- specs/implementation-artifacts/5-4-close-finalize-and-reopen-launch.md
- specs/implementation-artifacts/sprint-status.yaml
- src/client/client.py
- src/services/launch_service.py
- src/tools/launches.py
- src/tools/__init__.py
- tests/unit/test_launch_service.py
- tests/unit/test_launch_tools.py
- tests/integration/test_launch_client.py
- tests/integration/test_launch_tools.py
- tests/e2e/test_launches.py

### Change Log

- Added launch lifecycle support (`close_launch`, `reopen_launch`) across client, service, and MCP tools.
- Registered new lifecycle tools in tool exports and auto-registration list.
- Extended launch test coverage in unit/integration suites and lifecycle E2E scenarios (with conditional AC4 upload-path check).
- Updated story status and implementation record for review handoff.
