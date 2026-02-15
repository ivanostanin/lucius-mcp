# Story 7.5: Unlink Defects from Test Cases

Status: ready-for-dev

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

- [ ] **0. Regenerate API Client** (Prerequisite)
  - [ ] Investigate valid endpoints for unlinking. Likely `DELETE /api/v2/test-case/{id}/link/{linkId}` or similar.
  - [ ] Update `scripts/filter_openapi.py` to ensure `IssueLinkController` or `TestLinkController` tags are included.
  - [ ] Run `scripts/generate_testops_api_client.sh`.
  - [ ] Verify `api_client` has the unlinking method.

- [ ] **1. Implement Service Layer** (AC 1-2)
  - [ ] Update `src/services/test_case_service.py` (or `integration_service.py` based on where linking logic lives).
  - [ ] Implement `unlink_issue(test_case_id, issue_id)`.
  - [ ] Logic:
    - [ ] Fetch test case links to find the specific `linkId` for the given `issue_id` (if API requires internal link ID).
    - [ ] Call delete endpoint.
    - [ ] Handle 404s gracefully.

- [ ] **2. Implement MCP Tool** (AC 1-3)
  - [ ] Update `src/tools/defects.py` (or `cases.py`).
  - [ ] Add `unlink_issue_from_test_case` tool.
  - [ ] Add Google-style docstrings.

- [ ] **3. Register Tool**
  - [ ] Update `src/tools/__init__.py`.
  - [ ] Update `deployment/mcpb/manifest.python.json`.
  - [ ] Update `deployment/mcpb/manifest.uv.json`.

- [ ] **4. Unit Tests**
  - [ ] Update `tests/unit/test_test_case_service.py`.
  - [ ] Test linking retrieval and unlinking logic.
  - [ ] Test idempotency (link not found).

- [ ] **5. Integration Tests**
  - [ ] Update `tests/integration/test_defect_tools.py` (or `test_case_tools.py`).
  - [ ] Mock service responses.
  - [ ] Verify tool output formats.

- [ ] **6. E2E Tests**
  - [ ] Update `tests/e2e/test_defect_management.py`.
  - [ ] Scenario: Create Defect -> Link to Case -> Verify Link -> Unlink -> Verify Gone.

- [ ] **7. Update Agentic Workflow**
  - [ ] Add scenario **Unlink Issues** to `tests/agentic/agentic-tool-calls-tests.md`.
  - [ ] Include tools: `unlink_issue_from_test_case`.
  - [ ] Update **Tool inventory** and **Coverage matrix** sections.
  - [ ] Update **Execution plan** section.

- [ ] **8. Update Documentation**
  - [ ] Update `docs/tools.md` defect management section.
  - [ ] Update `README.md`.

- [ ] **9. Validation**
  - [ ] Run full test suite: `./scripts/full-test-suite.sh`

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

### Completion Notes List
- Story enhanced to match 7.2 structure + request to run full test suite + Review notes added.
