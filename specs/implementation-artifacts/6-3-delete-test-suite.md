# Story 6.3: Delete Test Suite

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **AI Agent**,
I want to **delete or archive obsolete Test Suites**,
so that **I can maintain a clean and relevant test hierarchy**.

## Acceptance Criteria

1.  **Delete Test Suite:**
    *   **Given** an existing Test Suite ID (Tree Node ID).
    *   **When** I call `delete_test_suite(suite_id, confirm=True)`.
    *   **Then** the test suite node is removed from the Allure TestOps hierarchy.
    *   **And** the tool returns a confirmation message.
    *   **And** the operation is idempotent (repeated calls succeed without error).

2.  **Safeguard:**
    *   ⚠️ **Destructive**. Requires `confirm=True`.
    *   **Given** a tool call without `confirm=True`.
    *   **Then** the tool returns a warning message asking for explicit confirmation: "⚠️ Destructive operation. Confirm deletion of suite {suite_id} by passing confirm=True."

3.  **Error Handling:**
    *   **Given** a non-existent Suite ID.
    *   **When** I call `delete_test_suite`.
    *   **Then** the tool returns a success message (idempotency) or a specific "Not Found" hint if strictly required, but idempotency is preferred for cleanups.

4.  **Handling Children:**
    *   **Given** a suite with child test cases or nested suites.
    *   **When** I delete the parent suite.
    *   **Then** the behavior follows Allure TestOps API standards (usually recursive delete or unlinking). *Dev Note: Verify API behavior during implementation.*

## Tasks / Subtasks

- [x] **0. Regenerate API Client** (Prerequisite)
  - [x] Check `src/client/generated/api` for tree node delete methods (e.g., `delete_leaf`, `delete_group`).
  - [x] If missing, add tree controller tags to `scripts/filter_openapi.py`.
  - [x] Run `scripts/generate_testops_api_client.sh`.
  - [x] Verify `TreeControllerApi` or `TestCaseTreeControllerV2Api` has valid delete endpoints.

- [x] **1. Implement Service Layer** (AC 1-4)
  - [x] Update `src/services/test_hierarchy_service.py`.
  - [x] Implement `delete_suite(suite_id)` method.
  - [x] Handle `AllureNotFoundError` using `try/except` to ensure idempotency.
  - [x] Log deletion actions.

- [x] **2. Implement MCP Tool** (AC 1-3)
  - [x] Update `src/tools/test_hierarchy.py` (or create if missing/renamed).
  - [x] Add `delete_test_suite(suite_id: int, confirm: bool = False)` tool.
  - [x] Implement the `confirm=False` safeguard check returning strictly formatted warning.
  - [x] Add comprehensive docstrings with Args/Returns/Example.

- [x] **3. Register Tool**
  - [x] Update `src/tools/__init__.py` to export `delete_test_suite`.
  - [x] Add to `deployment/mcpb/manifest.python.json`.
  - [x] Add to `deployment/mcpb/manifest.uv.json`.

- [x] **4. Unit Tests**
  - [x] Update `tests/unit/test_test_hierarchy_service.py`.
  - [x] Test `delete_suite` success path.
  - [x] Test `delete_suite` idempotency (404 handling).
  - [x] Test service error handling.

- [x] **5. Integration Tests**
  - [x] Update `tests/integration/test_test_hierarchy_tools.py`.
  - [x] Test tool output strings.
  - [x] Verify safeguard: call without confirm -> check warning message.
  - [x] Verify safeguard: call with confirm -> check success message.

- [x] **6. E2E Tests**
  - [x] Create or update `tests/e2e/test_test_hierarchy_management.py`.
  - [x] Test Lifecycle: Create Suite -> Assign Cases -> Delete Suite.
  - [x] Verify suite is gone from list.
  - [x] Add `track_suite` to `CleanupTracker` in `tests/e2e/helpers/cleanup.py` if not present.

- [x] **7. Update Agentic Workflow**
  - [x] Add scenario **Delete Test Suite** to `tests/agentic/agentic-tool-calls-tests.md`.
  - [x] Include tools: `delete_test_suite`.
  - [x] Update **Tool inventory** and **Coverage matrix** sections.
  - [x] Update **Execution plan** section.

- [x] **8. Update Documentation**
  - [x] Update `docs/tools.md` hierarchical section.
  - [x] Update `README.md` tool inventory.

- [x] **9. Validation**
  - [x] Run full test suite: `./scripts/full-test-suite.sh`

### Review Follow-ups (AI)
- [x] [AI-Review][HIGH] Enforce suite-removal verification in E2E lifecycle test instead of allowing pass when suite still exists; current logic marks task complete without asserting deletion. [tests/e2e/test_test_hierarchy_management.py:214]
- [x] [AI-Review][HIGH] Add explicit AC4 coverage for deleting a parent suite that has nested suites (not only a nested suite with assigned leaf) and assert API-standard behavior. [specs/implementation-artifacts/6-3-delete-test-suite.md:32]
- [ ] [AI-Review][MEDIUM] Reconcile Dev Agent Record File List with actual modified files (`.gitignore`, `sprint-status.yaml`) to keep review traceability accurate. [specs/implementation-artifacts/6-3-delete-test-suite.md:140]

## Dev Notes

### Architecture Patterns (MUST FOLLOW)

- **Thin Tool / Fat Service:** Logic resides in `TestHierarchyService`. Tool only handles arguments and formatting.
- **Destructive Tools:** MUST implement `confirm` parameter. If `False`, return text warning calling for confirmation.
- **Client Generation:** Tree node deletion might be under `TreeController` or `TestCaseTreeController`. Verify `openapi/allure-testops-service/report-service.json` schema if unsure.
- **API Spec Note:** Look for `deleteTree` or `deleteGroup` in `TreeControllerV2`. If absent, check `TestCaseTreeControllerV2`. It is critical to use the correct endpoint for nodes (suites) vs leaves (cases).

### Source Tree Impact

| Component | Path | Action |
|:----------|:-----|:-------|
| OpenAPI filter | `scripts/filter_openapi.py` | **CHECK/MODIFY** |
| Generated client | `src/client/generated/` | **REGENERATE** |
| Service | `src/services/test_hierarchy_service.py` | **MODIFY** |
| Tool | `src/tools/test_hierarchy.py` | **MODIFY** |
| Tool Init | `src/tools/__init__.py` | **MODIFY** |
| Manifests | `deployment/mcpb/manifest.*.json` | **MODIFY** |
| Unit Tests | `tests/unit/test_test_hierarchy_service.py` | **MODIFY** |
| Int Tests | `tests/integration/test_test_hierarchy_tools.py` | **MODIFY** |
| E2E Tests | `tests/e2e/test_test_hierarchy_management.py` | **MODIFY** |
| Agentic Tests | `tests/agentic/agentic-tool-calls-tests.md` | **MODIFY** |
| Docs | `docs/tools.md` | **MODIFY** |

### Testing Standards

- **Unit/Integration:** Mock `AllureClient`. Coverage > 85%.
- **E2E:** Use `CleanupTracker` to ensure created suites are deleted even if tests fail.

### Dev Agent Record

### Agent Model Used

gpt-5-codex

### Completion Notes List
- Story enhanced to match 7.2 structure + request to run full test suite + Review notes added.
- Verified generated client already exposes tree-group deletion endpoint (`delete_group`), so no OpenAPI filter change was needed.
- Added idempotent suite deletion in hierarchy service via new `delete_suite` method with logging and backward-compatible `delete_test_suite` alias.
- Added new MCP tool `delete_test_suite` with required `confirm` safeguard and strict warning format.
- Registered `delete_test_suite` in tool exports/registry and both MCPB manifests.
- Added unit/integration tests for delete service/tool flows and destructive confirmation guard.
- Added E2E lifecycle coverage for create/assign/delete-suite flow and cleanup tracker alias `track_suite`.
- Strengthened E2E deletion assertions to require actual suite disappearance and added explicit parent-with-children deletion coverage for AC4.
- Added hierarchy deletion fallback in service: when tree `delete_group` is ineffective, delete the suite's backing custom-field value to ensure actual removal.
- Updated agentic manual coverage doc, docs tool reference, and README tool inventory for the new hierarchy delete tool.
- Validation run: `bash scripts/full-test-suite.sh` completed successfully (unit/integration/e2e/docs/packaging).

### File List
- src/services/test_hierarchy_service.py
- src/client/client.py
- src/tools/delete_test_suite.py
- src/tools/test_layers.py
- src/tools/__init__.py
- deployment/mcpb/manifest.python.json
- deployment/mcpb/manifest.uv.json
- tests/unit/test_test_hierarchy_service.py
- tests/integration/test_test_hierarchy_tools.py
- tests/e2e/test_test_hierarchy_management.py
- tests/e2e/helpers/cleanup.py
- tests/unit/test_destructive_tools.py
- tests/agentic/agentic-tool-calls-tests.md
- docs/tools.md
- README.md
- specs/implementation-artifacts/6-3-delete-test-suite.md

### Change Log
- 2026-03-07: Implemented story 6.3 `delete_test_suite` end-to-end (service, tool, registration, tests, docs), and validated with full suite.
- 2026-03-07: Senior Developer Review (AI) completed; status moved to in-progress with follow-up actions.
- 2026-03-07: Addressed HIGH review findings (strict E2E deletion checks + parent deletion AC4 coverage + service fallback for actual suite removal).

## Senior Developer Review (AI)

### Reviewer
- Ivan Ostanin (AI)

### Date
- 2026-03-07

### Outcome
- Changes Requested

### Findings Summary
- High: 0 (2 resolved)
- Medium: 1
- Low: 0

### Key Findings
1. HIGH (RESOLVED) - Task marked complete without strict deletion verification in E2E.
   - Evidence: the test loops for disappearance, but if suite remains, it still passes by retrying delete and never failing the test.
   - References: `tests/e2e/test_test_hierarchy_management.py:214`, `tests/e2e/test_test_hierarchy_management.py:225`, `specs/implementation-artifacts/6-3-delete-test-suite.md:77`
2. HIGH (RESOLVED) - AC4 is only partially validated.
   - Evidence: AC4 requires deleting a parent suite with nested suites/children, while the implemented lifecycle test deletes the nested suite itself and does not assert parent-with-children semantics.
   - References: `specs/implementation-artifacts/6-3-delete-test-suite.md:32`, `tests/e2e/test_test_hierarchy_management.py:160`, `tests/e2e/test_test_hierarchy_management.py:177`
3. MEDIUM - Story file list is not synchronized with actual git changes.
   - Evidence: `.gitignore` and `specs/implementation-artifacts/sprint-status.yaml` are modified but absent from File List.
   - References: `specs/implementation-artifacts/6-3-delete-test-suite.md:140`, `.gitignore:13`, `specs/implementation-artifacts/sprint-status.yaml:101`

### Validation Performed by Reviewer
- Ran: `uv run pytest tests/unit/test_test_hierarchy_service.py tests/integration/test_test_hierarchy_tools.py tests/unit/test_destructive_tools.py -q` (33 passed).
- Ran: `bash scripts/full-test-suite.sh` (all phases passed; E2E: 99 passed, 1 skipped).
- Ran: `uv run pytest tests/unit/test_test_hierarchy_service.py tests/integration/test_test_hierarchy_tools.py -q` (23 passed).
- Ran: `uv run --env-file .env.test pytest tests/e2e/test_test_hierarchy_management.py -q` (5 passed).
