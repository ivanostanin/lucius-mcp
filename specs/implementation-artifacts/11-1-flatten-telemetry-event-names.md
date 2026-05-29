# Story 11.1: Flatten Telemetry Event Names

Status: review

## Story

As a Lucius maintainer,
I want telemetry events to use flat top-level names such as `startup`, `tool_use`, and `tool_error`,
so that downstream dashboards can group events consistently while keeping the same runtime properties in the payload.

## Acceptance Criteria

1. **Startup event name is flat**
   - **Given** Lucius emits a startup telemetry event
   - **When** telemetry is enabled
   - **Then** the event name is exactly `startup`
   - **And** the payload still includes `deployment_method`, `mcp_mode`, `server_version`, and the rest of the current startup properties.

2. **Successful tool event name is flat**
   - **Given** Lucius emits a successful tool telemetry event
   - **When** any tool finishes successfully
   - **Then** the event name is exactly `tool_use`
   - **And** the payload still includes `tool_name`, `outcome`, `duration_bucket`, and the current runtime context fields.

3. **Failed tool event name is flat**
   - **Given** Lucius emits a failed tool telemetry event
   - **When** validation, auth, API, or unexpected failures occur
   - **Then** the event name is exactly `tool_error`
   - **And** the payload still includes `tool_name`, `outcome`, and `error_category`
   - **And** the implementation does not add replacement sublevels such as `tool_error.validation`.

4. **Existing properties remain queryable**
   - **Given** dashboards or tests need deployment method, tool identity, or error class
   - **When** they read the payload
   - **Then** those dimensions are still available as properties
   - **And** no existing telemetry property is removed solely because the event name was flattened.

5. **Tests and docs reflect the new contract**
   - **Given** maintainers review the telemetry behavior
   - **When** they read docs or run tests
   - **Then** docs explicitly describe the flat event taxonomy
   - **And** unit, integration, and e2e tests assert the new names while preserving payload assertions.

## Tasks / Subtasks

- [x] **Task 1: Flatten event names in the telemetry service** (AC: 1, 2, 3, 4)
  - [x] 1.1 Change startup event emission in `src/services/telemetry_service.py` from `startup.<deployment_method>` to `startup`.
  - [x] 1.2 Change successful tool event emission from `tool_use.<tool_name>` to `tool_use`.
  - [x] 1.3 Change failed tool event emission from `tool_error.<category>.<tool_name>` to `tool_error`.
  - [x] 1.4 Keep `deployment_method`, `tool_name`, and `error_category` in the payload unchanged.

- [x] **Task 2: Update automated coverage** (AC: 1, 2, 3, 4, 5)
  - [x] 2.1 Update `tests/unit/test_telemetry_service.py` for flat startup/tool event names.
  - [x] 2.2 Update `tests/integration/test_telemetry_integration.py` for flat event names.
  - [x] 2.3 Update `tests/e2e/test_telemetry_collection_e2e.py` to select events by flat name plus payload fields.

- [x] **Task 3: Update telemetry docs** (AC: 5)
  - [x] 3.1 Update `docs/telemetry.md` to document the flat event taxonomy and note that dimensionality stays in payload fields.

- [x] **Review Follow-ups (AI)**
  - [x] [AI-Review][Medium] Add unit coverage proving auth- and API-classified failures still emit the flat `tool_error` event name while preserving `error_category`.
  - [x] [AI-Review][Medium] Add integration coverage that emits a failing tool event and asserts the flattened `tool_error` contract at the transport boundary.

## Dev Notes

### Scope

- This is a telemetry contract simplification only.
- Do not remove or rename existing payload properties.
- Do not change opt-out, hashing, transport, or error-swallowing behavior.

### References

- [Source: specs/project-planning-artifacts/epics.md#Epic 11]
- [Source: specs/implementation-artifacts/8-5-implement-telemetry-collection.md]
- [Source: src/services/telemetry_service.py]
- [Source: docs/telemetry.md]
- [Source: tests/unit/test_telemetry_service.py]
- [Source: tests/integration/test_telemetry_integration.py]
- [Source: tests/e2e/test_telemetry_collection_e2e.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### File List

- `src/services/telemetry_service.py`
- `tests/unit/test_telemetry_service.py`
- `tests/integration/test_telemetry_integration.py`
- `tests/e2e/test_telemetry_collection_e2e.py`
- `docs/telemetry.md`
- `AGENTS.md`
- `specs/project-planning-artifacts/epics.md`
- `specs/implementation-artifacts/11-1-flatten-telemetry-event-names.md`
- `specs/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-05-29: Story 11.1 created and implementation/tests/docs updated for flat telemetry event names.
- 2026-05-29: BMAD `code-review` workflow run against Story 11.1; review outcome was Changes Requested and the story moved back to `in-progress`.
- 2026-05-29: Added auth/API telemetry regression coverage, transport-boundary failure coverage, and repo `AGENTS.md` guidance; story moved back to `review`.

## Senior Developer Review (AI)

**Review Date:** 2026-05-29
**Reviewer:** Codex via BMAD `code-review` workflow
**Workflow Artifacts:** `/home/node/.openclaw/bmad-method/src/bmm/workflows/4-implementation/code-review/{workflow.yaml,instructions.xml,checklist.md}`
**Outcome:** Changes Requested

### Summary

The telemetry implementation itself matches the flattening requirement, and the story's changed-file inventory now matches the git diff. The remaining gaps are in regression coverage: Acceptance Criterion 3 explicitly calls out validation, auth, API, and unexpected failures, but the updated review branch only proves the flattened `tool_error` name for validation and unexpected paths, and integration coverage never exercises an error event at all.

### Findings

1. **Medium:** AC 3 is only partially verified in automated coverage. The updated tests prove `tool_error` for validation and unexpected failures, but there is still no assertion covering auth- or API-classified failures after the event-name flattening change. Evidence: [src/services/telemetry_service.py](/home/node/.openclaw/codespaces/lucius-mcp-change-tracking/src/services/telemetry_service.py:431), [tests/unit/test_telemetry_service.py](/home/node/.openclaw/codespaces/lucius-mcp-change-tracking/tests/unit/test_telemetry_service.py:53), [tests/e2e/test_telemetry_collection_e2e.py](/home/node/.openclaw/codespaces/lucius-mcp-change-tracking/tests/e2e/test_telemetry_collection_e2e.py:157).
2. **Medium:** Integration coverage no longer validates any failing telemetry emission, so the flat `tool_error` contract is not exercised at the HTTP transport boundary. The only integration assertions are for `startup` and a successful `tool_use` event. Evidence: [tests/integration/test_telemetry_integration.py](/home/node/.openclaw/codespaces/lucius-mcp-change-tracking/tests/integration/test_telemetry_integration.py:13).
3. **Low:** The story entered review without a Dev Agent Record `File List` or `Change Log`, so changed-file traceability had to be reconstructed from `git diff main...HEAD` instead of the story artifact itself. This review updated those sections, but future submissions should include them before moving to `review`. Evidence: [specs/implementation-artifacts/11-1-flatten-telemetry-event-names.md](/home/node/.openclaw/codespaces/lucius-mcp-change-tracking/specs/implementation-artifacts/11-1-flatten-telemetry-event-names.md:1).

### Verification Notes

- BMAD resolver confirmed the official workflow path: `python3 /home/node/.openclaw/workspace/bin/bmad_resolver.py resolve code-review`.
- Git-reviewed files matched the implementation scope: `docs/telemetry.md`, `src/services/telemetry_service.py`, telemetry tests, epic/story artifacts, and sprint status.
- Runtime test execution could not be completed in this environment because only `python3` 3.11 is present and `pytest` is not installed (`python3 -m pytest ...` fails with `No module named pytest`), while the project requires Python 3.13+ in [pyproject.toml](/home/node/.openclaw/codespaces/lucius-mcp-change-tracking/pyproject.toml:1).
