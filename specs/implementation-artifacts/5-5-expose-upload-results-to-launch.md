# Story 5.5: Expose upload_results_to_launch as a tool

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **AI Agent**,
I want to **upload test results to an existing launch**,
so that **I can report execution outcomes from external sources, manual runs, or agent-driven validations**.

## Acceptance Criteria

1.  **Upload Test Result:**
    *   **Given** a valid Launch ID and a list of result objects (Test Case ID + Status + optional duration/message).
    *   **When** I call `upload_test_results(launch_id, results=[...])`.
    *   **Then** the results are appended to the specified launch in Allure TestOps.
    *   **And** the launch statistics are updated.
    *   **And** the tool returns a summary: "Successfully uploaded X results to launch {launch_id}".

2.  **Input Validation:**
    *   **Given** invalid result status (e.g., "Kinda Passed").
    *   **Then** the tool returns a validation error listing allowed statuses (passed, failed, broken, skipped, unknown).
    *   **Given** a non-existent Launch ID.
    *   **Then** the tool returns a "Launch not found" error hint.

3.  **Bulk Handling:**
    *   **When** I provide multiple results.
    *   **Then** they are processed efficiently (bulk API usage if available, or concurrent calls).

## Tasks / Subtasks

- [x] **0. Regenerate API Client** (Prerequisite)
  - [x] Check for result upload endpoints (e.g., `TestResultController`).
  - [x] Update `scripts/filter_openapi.py` to include `test-result-controller` if needed.
  - [x] Run `scripts/generate_testops_api_client.sh`.

- [x] **1. Implement Service Layer** (AC 1-3)
  - [x] Update `src/services/launch_service.py`.
  - [x] Implement `add_results(launch_id, results: list[dict])`.
  - [x] Map simplified dict inputs to `TestResultCreateDto` (or equivalent).
    - [x] Auto-generate `uuid` if missing.
    - [x] Auto-generate `historyId` (or use testCaseId hashing) if missing.
    - [x] Validate `status` enum mapping.
  - [x] Handle API call loop or bulk endpoint.

- [x] **2. Implement MCP Tool** (AC 1-2)
  - [x] Update `src/tools/launches.py`.
  - [x] Add `upload_test_results(launch_id: int, results: list[dict])`.
  - [x] Define helper schema for `result` dict in docstring:
    - [x] `test_case_id` (required, int)
    - [x] `status` (required, str)
    - [x] `start` (optional, int timestamp)
    - [x] `stop` (optional, int timestamp)
    - [x] `message` (optional, str)

- [x] **3. Register Tool**
  - [x] Update `src/tools/__init__.py`.
  - [x] Update `deployment/mcpb/manifest.python.json`.
  - [x] Update `deployment/mcpb/manifest.uv.json`.

- [x] **4. Unit Tests**
  - [x] Update `tests/unit/test_launch_service.py`.
  - [x] Test DTO mapping.
  - [x] Test failure scenarios.

- [x] **5. Integration Tests**
  - [x] Update `tests/integration/test_launch_tools.py`.
  - [x] verify JSON parsing of `results` argument.

- [x] **6. E2E Tests**
  - [x] Update `tests/e2e/test_execution_management.py` (or similar).
  - [x] Scenario: Create Launch -> Upload Results -> Get Launch (verify stats) -> Close Launch.

- [x] **7. Update Agentic Workflow**
  - [x] Add scenario **Upload Results** to `tests/agentic/agentic-tool-calls-tests.md`.
  - [x] Include tools: `upload_test_results`.
  - [x] Update **Tool inventory** and **Coverage matrix** sections.
  - [x] Update **Execution plan** section.

- [x] **8. Update Documentation**
  - [x] Update `docs/tools.md`.
  - [x] Update `README.md`.

- [x] **9. Validation**
  - [x] Run full test suite: `./scripts/full-test-suite.sh`

## Dev Notes

### Architecture Patterns (MUST FOLLOW)

- **Thin Tool / Fat Service:** Logic in service.
- **Complex Args:** The `results` argument is a list of objects. Ensure the MCP tool definition handles complex types correctly (e.g., JSON string parsing if MCP has issues with nested objects, though Python SDK usually handles lists of dicts ok).
- **DTO Mapping:** Service layer is responsible for converting friendly inputs (dict) to strict Pydantic DTOs required by the generated client.
- **Data Integrity:** `TestResultCreateDto` often requires specific fields like `uuid` or `historyId`. If the user (agent) doesn't provide them, the service MUST generate sensible defaults to ensure the result is accepted by TestOps.

### Source Tree Impact

| Component | Path | Action |
|:----------|:-----|:-------|
| OpenAPI filter | `scripts/filter_openapi.py` | **CHECK/MODIFY** |
| Generated client | `src/client/generated/` | **REGENERATE** |
| Service | `src/services/launch_service.py` | **MODIFY** |
| Tool | `src/tools/launches.py` | **MODIFY** |
| Manifests | `deployment/mcpb/manifest.*.json` | **MODIFY** |
| Unit Tests | `tests/unit/test_launch_service.py` | **MODIFY** |
| E2E Tests | `tests/e2e/test_execution_management.py` | **MODIFY** |
| Agentic Tests | `tests/agentic/agentic-tool-calls-tests.md` | **MODIFY** |

### Testing Standards

- **Coverage:** > 85%.

### Dev Agent Record

### Agent Model Used

GPT-5 (Codex)

### Implementation Plan

- Reuse the existing native TestOps test-result API and expose a launch-scoped bulk convenience method.
- Validate and map the entire result batch before concurrently creating the launch-linked results.
- Preserve the existing manual session and result-management APIs unchanged.

### Debug Log

- Confirmed the filtered OpenAPI spec includes the required upload controller and DTOs, then regenerated the API client successfully; regeneration produced no generated-source diff.
- Regenerated `docs/mcp_manifest.json` after registering the MCP tool.
- Ran `./scripts/full-test-suite.sh`: 914 unit/integration tests passed (90.11% coverage); 19 documentation tests passed.

### Completion Notes List
- Added `upload_test_results`, which accepts a launch ID and simplified result objects, maps them to native launch-linked result DTOs, and submits the full batch concurrently.
- Missing UUIDs are generated, history IDs are deterministically derived from test case IDs, optional durations are supported, and invalid statuses return the lowercase allowed-status hint.
- Added unit, integration, E2E, MCP manifest, agentic-workflow, and documentation coverage without changing existing launch/manual-result behavior.

### File List

- README.md
- deployment/mcpb/manifest.python.json
- deployment/mcpb/manifest.uv.json
- docs/mcp_manifest.json
- docs/tools.md
- specs/implementation-artifacts/5-5-expose-upload-results-to-launch.md
- specs/implementation-artifacts/sprint-status.yaml
- src/services/launch_service.py
- src/tools/__init__.py
- src/tools/annotations.py
- src/tools/launches.py
- tests/agentic/agentic-tool-calls-tests.md
- tests/e2e/test_launch_manual_execution.py
- tests/integration/test_launch_tools.py
- tests/unit/test_launch_service.py

### Change Log

- 2026-07-09: Implemented launch-scoped bulk test-result upload with validation, registration, documentation, and regression coverage.
