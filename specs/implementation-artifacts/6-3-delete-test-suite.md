# Story 6.3: Delete Test Suite

Status: ready-for-dev

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

- [ ] **0. Regenerate API Client** (Prerequisite)
  - [ ] Check `src/client/generated/api` for tree node delete methods (e.g., `delete_leaf`, `delete_group`).
  - [ ] If missing, add tree controller tags to `scripts/filter_openapi.py`.
  - [ ] Run `scripts/generate_testops_api_client.sh`.
  - [ ] Verify `TreeControllerApi` or `TestCaseTreeControllerV2Api` has valid delete endpoints.

- [ ] **1. Implement Service Layer** (AC 1-4)
  - [ ] Update `src/services/test_hierarchy_service.py`.
  - [ ] Implement `delete_suite(suite_id)` method.
  - [ ] Handle `AllureNotFoundError` using `try/except` to ensure idempotency.
  - [ ] Log deletion actions.

- [ ] **2. Implement MCP Tool** (AC 1-3)
  - [ ] Update `src/tools/test_hierarchy.py` (or create if missing/renamed).
  - [ ] Add `delete_test_suite(suite_id: int, confirm: bool = False)` tool.
  - [ ] Implement the `confirm=False` safeguard check returning strictly formatted warning.
  - [ ] Add comprehensive docstrings with Args/Returns/Example.

- [ ] **3. Register Tool**
  - [ ] Update `src/tools/__init__.py` to export `delete_test_suite`.
  - [ ] Add to `deployment/mcpb/manifest.python.json`.
  - [ ] Add to `deployment/mcpb/manifest.uv.json`.

- [ ] **4. Unit Tests**
  - [ ] Update `tests/unit/test_test_hierarchy_service.py`.
  - [ ] Test `delete_suite` success path.
  - [ ] Test `delete_suite` idempotency (404 handling).
  - [ ] Test service error handling.

- [ ] **5. Integration Tests**
  - [ ] Update `tests/integration/test_test_hierarchy_tools.py`.
  - [ ] Test tool output strings.
  - [ ] Verify safeguard: call without confirm -> check warning message.
  - [ ] Verify safeguard: call with confirm -> check success message.

- [ ] **6. E2E Tests**
  - [ ] Create or update `tests/e2e/test_test_hierarchy_management.py`.
  - [ ] Test Lifecycle: Create Suite -> Assign Cases -> Delete Suite.
  - [ ] Verify suite is gone from list.
  - [ ] Add `track_suite` to `CleanupTracker` in `tests/e2e/helpers/cleanup.py` if not present.

- [ ] **7. Update Agentic Workflow**
  - [ ] Add scenario **Delete Test Suite** to `tests/agentic/agentic-tool-calls-tests.md`.
  - [ ] Include tools: `delete_test_suite`.
  - [ ] Update **Tool inventory** and **Coverage matrix** sections.
  - [ ] Update **Execution plan** section.

- [ ] **8. Update Documentation**
  - [ ] Update `docs/tools.md` hierarchical section.
  - [ ] Update `README.md` tool inventory.

- [ ] **9. Validation**
  - [ ] Run full test suite: `./scripts/full-test-suite.sh`

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

Antigravity (Google DeepMind)

### Completion Notes List
- Story enhanced to match 7.2 structure + request to run full test suite + Review notes added.
