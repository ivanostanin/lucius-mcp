# Story 5.2: Get Launch Details

Status: ready-for-dev

## Dev Agent Guardrails

- Do not add business logic in tools; services own validation and API calls.
- Keep all HTTP calls async via `httpx`; never use sync clients.
- Use Pydantic v2 strict models and `model_validate` for DTO validation.
- Raise typed exceptions in services; avoid try/except in tools.

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want to retrieve the full details of a specific launch,
so that I can inspect its status, test results, and execution context.

## Acceptance Criteria

1. **Given** a valid Launch ID, **when** I call `get_launch`, **then** the server returns launch metadata (name, status/state, start/end timestamps, and any summary fields provided by the API).
2. **Given** a valid Launch ID, **when** I call `get_launch`, **then** the tool returns a concise, LLM-friendly summary that includes the Launch ID and status (no raw JSON).
3. **Given** an invalid or non-existent Launch ID, **when** I call `get_launch`, **then** the server returns a clear error message indicating validation or not-found.

## Tasks / Subtasks

- [ ] **Task 1: Define Launch Detail Tool** (AC: #1, #2)
  - [ ] 1.1: Add `get_launch` tool in `src/tools/launches.py` following existing launch tool patterns
  - [ ] 1.2: Add LLM-optimized docstring with args for Launch ID and optional auth override
  - [ ] 1.3: Keep tool thin (validate args, call service, format response)

- [ ] **Task 2: Implement Launch Detail Service** (AC: #1, #2)
  - [ ] 2.1: Add `get_launch()` to `src/services/launch_service.py`
  - [ ] 2.2: Validate Launch ID input and raise `AllureValidationError` for invalid IDs
  - [ ] 2.3: Return structured data for tool formatting (no MCP-specific text)

- [ ] **Task 3: Extend AllureClient** (AC: #1, #2)
  - [ ] 3.1: Add `get_launch()` request to `src/client/client.py`
  - [ ] 3.2: Map response to generated Pydantic models or compatible DTOs

- [ ] **Task 4: Error Handling & Agent Hints** (AC: #2)
  - [ ] 4.1: Ensure not-found/invalid IDs raise `ResourceNotFoundError` or `AllureAPIError`
  - [ ] 4.2: Confirm global error handler formats clear Agent Hints

- [ ] **Task 5: Tests** (AC: #1, #2)
  - [ ] 5.1: Unit tests for `LaunchService.get_launch()` validation and mapping
  - [ ] 5.2: Integration tests for client request/response mapping
  - [ ] 5.3: Tool output tests for LLM-friendly formatting
  - [ ] 5.4: E2E test for get-launch flow (skip when sandbox credentials missing)

## Dev Notes

### Developer Context

- This story extends the Launch tooling introduced in Story 5.1 (create/list).
- Reuse existing launch DTOs and client/service patterns; do not duplicate parsing or pagination helpers.
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

- Unit tests for `LaunchService.get_launch()` validation/mapping.
- Integration tests for client request/response mapping.
- Tool output tests for LLM-friendly formatting (explicitly assert output string format).
- E2E test for get-launch flow (skip when sandbox credentials missing).
- Error-case tests for invalid ID and not-found responses.
- Do not mute lint checks or exclude tests; keep coverage >85% and `mypy --strict` green.

### Previous Story Intelligence (Story 5.1)

- Launch create/list already implemented with launch service + client + tests.
- Patterns include launch DTO validation, LLM-friendly tool outputs, and e2e launch tests.
- Review notes mention `AllureClient.from_env` override handling and launch list oneOf fallback parsing.

### Git Intelligence Summary

- Recent commits focus on launch create/list and test-layer fixes.
- Launch work touched `src/client/client.py`, `src/services/launch_service.py`, and launch tests.

### Latest Technical Information

- Allure TestOps launches must be closed to finalize results; closed launches reject new result uploads.
- Reopen restores the ability to add results (relevant for Story 5.4).
- Validate behavior and endpoints against the instance Swagger/OpenAPI before implementing.

### Project Context Reference

- [Source: specs/project-context.md#Technology Stack & Versions]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: specs/project-context.md#Error Handling Strategy]
- [Source: specs/project-context.md#Development Workflow]

### References

- [Source: specs/project-planning-artifacts/epics.md#Story 5.2]
- [Source: specs/project-planning-artifacts/epics.md#Epic 5]
- [Source: specs/implementation-artifacts/5-1-create-and-list-launches.md#Dev Notes]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: specs/project-context.md#Error Handling Strategy]
- [Source: specs/project-context.md#Development Workflow]

## Dev Agent Record

### Agent Model Used

gpt-5.2-codex

### Debug Log References

- N/A

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- specs/implementation-artifacts/5-2-get-launch-details.md
- specs/implementation-artifacts/sprint-status.yaml
