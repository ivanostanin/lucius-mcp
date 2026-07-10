# Story 7.5: Unlink Defects from Test Cases

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **AI Agent**,
I want to **unlink defects or issues from Test Cases**,
so that **I can correct erroneous associations or manage defect resolution status accurately**.

## Acceptance Criteria

1.  **Unlink Defect/Issue:**
    *   **Given** a Test Case ID and a Defect/Issue ID (or the specific Link ID).
    *   **When** I call `unlink_issue_from_test_case(test_case_id, issue_id)`.
    *   **Then** the link is removed in Allure TestOps.
    *   **And** the tool returns a confirmation message: "Successfully unlinked issue {issue_id} from test case {test_case_id}".
    *   **And** the operation is idempotent (repeated calls succeed without error).

2.  **Error Handling:**
    *   **Given** an invalid ID or non-existent link.
    *   **When** I call the unlink tool.
    *   **Then** it returns an appropriate success message (idempotency) or a clear error hint if the test case itself does not exist.

3.  **Input Validation:**
    *   **Given** missing arguments.
    *   **Then** the tool returns a standardized validation error hint.

## Tasks / Subtasks

- [x] **0. Regenerate API Client** (Prerequisite)
  - [x] Investigate valid endpoints for unlinking. The supported endpoint is `POST /api/testcase/bulk/issue/remove`.
  - [x] Verify `scripts/filter_openapi.py` already retains `test-case-bulk-controller`, which owns the endpoint.
  - [x] Run `scripts/generate_testops_api_client.sh`.
  - [x] Verify `api_client` has `TestCaseBulkControllerApi.issue_remove1`.

- [x] **1. Implement Service Layer** (AC 1-2)
  - [x] Update `src/services/test_case_service.py` and `src/services/defect_service.py`.
  - [x] Implement `unlink_issue_from_test_case(test_case_id, issue_id)`.
  - [x] Logic:
    - [x] Fetch test case links and resolve the internal link ID from an issue key or internal ID.
    - [x] Call the bulk issue-removal endpoint.
    - [x] Handle a concurrent 404 gracefully as an idempotent no-op.

- [x] **2. Implement MCP Tool** (AC 1-3)
  - [x] Update `src/tools/defects.py`.
  - [x] Add `unlink_issue_from_test_case` tool.
  - [x] Add Google-style docstrings.

- [x] **3. Register Tool**
  - [x] Update `src/tools/__init__.py` and tool annotations.
  - [x] Update `deployment/mcpb/manifest.python.json`.
  - [x] Update `deployment/mcpb/manifest.uv.json`.

- [x] **4. Unit Tests**
  - [x] Update `tests/unit/test_test_case_service_issue_linking.py` and `tests/unit/test_defect_service.py`.
  - [x] Test issue-key/internal-ID retrieval and unlinking logic.
  - [x] Test idempotency for absent links and concurrent 404 responses.

- [x] **5. Integration Tests**
  - [x] Update `tests/integration/test_defect_tools.py`.
  - [x] Mock service responses.
  - [x] Verify the exact tool confirmation output.

- [x] **6. E2E Tests**
  - [x] Update `tests/e2e/test_defect_testcase_linking.py`.
  - [x] Scenario: Create Defect -> Link to Case -> Verify Link -> Unlink -> Verify Gone.

- [x] **7. Update Agentic Workflow**
  - [x] Add an **Unlink Issues** scenario to `tests/agentic/agentic-tool-calls-tests.md`.
  - [x] Include `unlink_issue_from_test_case`.
  - [x] Update **Tool inventory** and **Coverage matrix** sections.
  - [x] Update **Execution plan** section.

- [x] **8. Update Documentation**
  - [x] Update `docs/tools.md` defect management section.
  - [x] Update `README.md`.

- [x] **9. Validation**
  - [x] Run full test suite: `./scripts/full-test-suite.sh`

### Review Findings

- [x] [Review][Patch] Resolve duplicate issue keys deterministically or reject ambiguous key-based unlink requests [src/services/test_case_service.py:803]
- [x] [Review][Patch] Reject boolean values for `test_case_id` with the standardized validation error [src/services/test_case_service.py:793]
- [x] [Review][Patch] Distinguish a concurrent test-case deletion from an already-unlinked issue after a bulk-remove 404 [src/services/test_case_service.py:822]
- [x] [Review][Patch] Do not return an unlink confirmation when the issue-link overview could not be retrieved [src/services/test_case_service.py:802]
- [x] [Review][Patch] Revert unrelated Epic 5, 6, 9, 10-2, and 11-1 status transitions from this story branch [specs/implementation-artifacts/sprint-status.yaml:90]

## Dev Notes

### Architecture Patterns (MUST FOLLOW)

- **Thin Tool / Fat Service:** Logic in service. The tool should not perform the "search link ID by issue ID" logic; the service should validation this.
- **Async:** Use `await`.
- **Link IDs:** Allure often uses internal IDs for links (e.g., `link.id` vs `link.name`/`link.url`). The user inputs the *Issue ID* (e.g., "JIRA-123"). The service MUST first fetch the test case's links to find the `link.id` that corresponds to "JIRA-123" before calling the delete endpoint. If the user provides the internal ID, handle that case too.
- **Endpoint Discovery:** Check `TestLinkController` for `delete` or `unlink` methods. It might require `testCaseId` and `linkId` as path parameters.

### Source Tree Impact

| Component | Path | Action |
|:----------|:-----|:-------|
| OpenAPI filter | `scripts/filter_openapi.py` | **CHECK/MODIFY** |
| Generated client | `src/client/generated/` | **REGENERATE** |
| Service | `src/services/test_case_service.py` | **MODIFY** |
| Tool | `src/tools/defects.py` | **MODIFY** |
| Manifests | `deployment/mcpb/manifest.*.json` | **MODIFY** |
| Unit Tests | `tests/unit/test_test_case_service.py` | **MODIFY** |
| E2E Tests | `tests/e2e/test_defect_management.py` | **MODIFY** |
| Agentic Tests | `tests/agentic/agentic-tool-calls-tests.md` | **MODIFY** |

### Testing Standards

- **Coverage:** > 85%.
- **E2E:** Cleanup is handled by deleting the test case and defect; unlinking is an intermediate step.

### Dev Agent Record

### Agent Model Used

Antigravity (Google DeepMind)

### Implementation Plan

- Reuse the retained Test Case Bulk API to resolve and remove one issue link by issue key or internal link ID.
- Keep the MCP tool thin, delegate behavior to services, and make missing/racing links idempotent.
- Cover the service, tool output, environment-backed workflow, registry, manifests, and documentation.

### Completion Notes List
- Story enhanced to match 7.2 structure + request to run full test suite + Review notes added.
- Implemented `unlink_issue_from_test_case` with issue-key/internal-link-ID resolution, idempotent missing-link behavior, and graceful handling of a racing 404.
- Registered the tool and its destructive/idempotent annotations, added MCPB manifest entries, documentation, and agentic coverage.
- Validation passed: regenerated API client, `./scripts/full-test-suite.sh` (925 tests; 90.15% coverage), including configured E2E tests.

### File List

- README.md
- deployment/mcpb/manifest.python.json
- deployment/mcpb/manifest.uv.json
- docs/mcp_manifest.json
- docs/tools.md
- specs/implementation-artifacts/7-5-unlink-defects-from-test-cases.md
- specs/implementation-artifacts/sprint-status.yaml
- src/services/defect_service.py
- src/services/test_case_service.py
- src/tools/__init__.py
- src/tools/annotations.py
- src/tools/defects.py
- tests/agentic/agentic-tool-calls-tests.md
- tests/e2e/test_defect_testcase_linking.py
- tests/integration/test_defect_tools.py
- tests/unit/test_defect_service.py
- tests/unit/test_test_case_service_issue_linking.py

### Change Log

- 2026-07-10: Implemented idempotent issue unlinking for test cases and completed Story 7.5 validation.
