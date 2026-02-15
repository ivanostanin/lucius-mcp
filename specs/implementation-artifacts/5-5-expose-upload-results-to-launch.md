# Story 5.5: Expose upload_results_to_launch as a tool

Status: ready-for-dev

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

- [ ] **0. Regenerate API Client** (Prerequisite)
  - [ ] Check for result upload endpoints (e.g., `TestResultController`).
  - [ ] Update `scripts/filter_openapi.py` to include `test-result-controller` if needed.
  - [ ] Run `scripts/generate_testops_api_client.sh`.

- [ ] **1. Implement Service Layer** (AC 1-3)
  - [ ] Update `src/services/launch_service.py`.
  - [ ] Implement `add_results(launch_id, results: list[dict])`.
  - [ ] Map simplified dict inputs to `TestResultCreateDto` (or equivalent).
    - [ ] Auto-generate `uuid` if missing.
    - [ ] Auto-generate `historyId` (or use testCaseId hashing) if missing.
    - [ ] Validate `status` enum mapping.
  - [ ] Handle API call loop or bulk endpoint.

- [ ] **2. Implement MCP Tool** (AC 1-2)
  - [ ] Update `src/tools/launches.py`.
  - [ ] Add `upload_test_results(launch_id: int, results: list[dict])`.
  - [ ] Define helper schema for `result` dict in docstring:
    - `test_case_id` (required, int)
    - `status` (required, str)
    - `start` (optional, int timestamp)
    - `stop` (optional, int timestamp)
    - `message` (optional, str)

- [ ] **3. Register Tool**
  - [ ] Update `src/tools/__init__.py`.
  - [ ] Update `deployment/mcpb/manifest.python.json`.
  - [ ] Update `deployment/mcpb/manifest.uv.json`.

- [ ] **4. Unit Tests**
  - [ ] Update `tests/unit/test_launch_service.py`.
  - [ ] Test DTO mapping.
  - [ ] Test failure scenarios.

- [ ] **5. Integration Tests**
  - [ ] Update `tests/integration/test_launch_tools.py`.
  - [ ] verify JSON parsing of `results` argument.

- [ ] **6. E2E Tests**
  - [ ] Update `tests/e2e/test_execution_management.py` (or similar).
  - [ ] Scenario: Create Launch -> Upload Results -> Get Launch (verify stats) -> Close Launch.

- [ ] **7. Update Agentic Workflow**
  - [ ] Add scenario **Upload Results** to `tests/agentic/agentic-tool-calls-tests.md`.
  - [ ] Include tools: `upload_test_results`.
  - [ ] Update **Tool inventory** and **Coverage matrix** sections.
  - [ ] Update **Execution plan** section.

- [ ] **8. Update Documentation**
  - [ ] Update `docs/tools.md`.
  - [ ] Update `README.md`.

- [ ] **9. Validation**
  - [ ] Run full test suite: `./scripts/full-test-suite.sh`

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

Antigravity (Google DeepMind)

### Completion Notes List
- Story enhanced to match 7.2 structure + request to run full test suite + Review notes added.
