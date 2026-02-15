# Story 6.4: Delete Archived Test Cases

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **AI Agent**,
I want to **permanently delete archived entities (Test Cases, Shared Steps, Custom Fields)**,
so that **I can maintain a valid and clean project state and remove technical debt**.

## Acceptance Criteria

1.  **Delete Archived Test Cases:**
    *   **Given** a command to clean up archived cases.
    *   **When** I call `delete_archived_test_cases(confirm=True)`.
    *   **Then** the system finds all test cases in the project with "Deleted" or "Archived" status.
    *   **And** it permanently deletes them.
    *   **And** returns a count of deleted items.

2.  **Delete Archived Shared Steps:**
    *   **When** I call `delete_archived_shared_steps(confirm=True)`.
    *   **Then** archived shared steps are permanently removed.
    *   **And** returns a count.

3.  **Delete Unused Custom Fields:**
    *   **When** I call `delete_unused_custom_fields(confirm=True)`.
    *   **Then** custom fields that are not assigned to any test case in the project are identified and removed.
    *   **And** returns a count.

4.  **Safeguard:**
    *   ⚠️ **Destructive**. All tools require `confirm=True`.
    *   **Given** missing confirm.
    *   **Then** returns warning: "⚠️ Destructive operation. Pass confirm=True to proceed."

## Tasks / Subtasks

- [ ] **0. Regenerate API Client** (Prerequisite)
  - [ ] Verify endpoints for listing deleted/archived items and permanent deletion.
  - [ ] Update `scripts/filter_openapi.py` if needed.
  - [ ] Run `scripts/generate_testops_api_client.sh`.

- [ ] **1. Implement Service Layer** (AC 1-3)
  - [ ] Update `src/services/test_case_service.py`: `cleanup_archived()`.
  - [ ] Update `src/services/shared_step_service.py`: `cleanup_archived()`.
  - [ ] Create/Update `src/services/custom_field_service.py`: `cleanup_unused()`.
    - [ ] **Strategy:** Fetch all unused fields if API supports it.
    - [ ] **Fallback:** If no direct API, fetch all fields + all test cases (expensive!). *Dev Note: If expensive fallback is required, implement a limit/warning or skip this part for V1.*

- [ ] **2. Implement MCP Tool** (AC 1-4)
  - [ ] Create/Update `src/tools/cleanup.py` (New module likely needed for general cleanup, or add to respective modules).
  - [ ] Tools: `delete_archived_test_cases`, `delete_archived_shared_steps`, `delete_unused_custom_fields`.
  - [ ] Implement safeguards.

- [ ] **3. Register Tools**
  - [ ] Update `src/tools/__init__.py`.
  - [ ] Update manifests.

- [ ] **4. Unit Tests**
  - [ ] Update `tests/unit/test_test_case_service.py`.
  - [ ] Update `tests/unit/test_shared_step_service.py`.
  - [ ] Update `tests/unit/test_custom_field_service.py`.
  - [ ] Test filtering logic and deletion loops.

- [ ] **5. Integration Tests**
  - [ ] Create `tests/integration/test_cleanup_tools.py`.
  - [ ] Verify safeguard messages.

- [ ] **6. E2E Tests**
  - [ ] Create `tests/e2e/test_cleanup_lifecycle.py`.
  - [ ] Scenario: Create Case -> Archive Case -> Run Cleanup -> Verify Case Gone.
  - [ ] Scenario: Create Field -> Unused -> Run Cleanup -> Verify Field Gone.

- [ ] **7. Update Agentic Workflow**
  - [ ] Add scenario **Cleanup Archived Entities** to `tests/agentic/agentic-tool-calls-tests.md`.
  - [ ] Include tools: `delete_archived_test_cases`, `delete_archived_shared_steps`, `delete_unused_custom_fields`.
  - [ ] Update **Tool inventory** and **Coverage matrix** sections.
  - [ ] Update **Execution plan** section.

- [ ] **8. Update Documentation**
  - [ ] Update `docs/tools.md`.
  - [ ] Update `README.md`.

- [ ] **9. Validation**
  - [ ] Run full test suite: `./scripts/full-test-suite.sh`

## Dev Notes

### Architecture Patterns (MUST FOLLOW)

- **Destructive Tools:** Strict `confirm=True` requirement.
- **Performance:** If deleting thousands of items, consider batch size or timeouts. For now, simple loop is acceptable for MVP, but consider adding `limit` arg.
- **Service Boundaries:** `cleanup_archived_cases` logic belongs in `TestCaseService`, `cleanup_archived_steps` in `SharedStepService`. Do not create a god "CleanupService" unless it just orchestrates others.
- **Unused Fields Scale:** Be cautious implementing `delete_unused_custom_fields`. If it requires iterating 100k test cases to check usage, DO NOT implement it without a dedicated API endpoint. If no such endpoint exists, mark that part of the story as "Blocked by API limitations" and proceed with other cleanup tasks.

### Source Tree Impact

| Component | Path | Action |
|:----------|:-----|:-------|
| Generated client | `src/client/generated/` | **REGENERATE** |
| Services | `src/services/*_service.py` | **MODIFY** |
| Tools | `src/tools/cases.py` etc | **MODIFY** |
| Manifests | `deployment/mcpb/manifest.*.json` | **MODIFY** |
| Tests | `tests/unit/`, `tests/e2e/` | **MODIFY/NEW** |
| Agentic Tests | `tests/agentic/agentic-tool-calls-tests.md` | **MODIFY** |

### Testing Standards

- **E2E:** Critical to verify "Unused" logic for custom fields doesn't delete used fields.

### Dev Agent Record

### Agent Model Used

Antigravity (Google DeepMind)

### Completion Notes List
- Story enhanced to match 7.2 structure + request to run full test suite + Review notes added.
