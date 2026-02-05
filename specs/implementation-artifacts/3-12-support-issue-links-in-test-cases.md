# Story 3.12: Support Issue Links in Test Cases

Status: ready-for-dev

<!-- Note: This story extends create_test_case and update_test_case tools to support Jira/GitHub issue linking -->

## User Story

As an AI Agent,
I want to link Jira or GitHub issues to test cases when creating or updating them,
So that I can maintain traceability between test cases and requirements/defects without making separate API calls.

## Acceptance Criteria

**AC #1: Add Issues on Test Case Creation**
**Given** a valid test case payload with `issues` parameter
**When** I call `create_test_case(name="...", issues=["PROJ-123", "PROJ-456"])`
**Then** the tool creates the test case and links the specified issues
**And** returns a confirmation message including linked issue count

**AC #2: Add Issues on Test Case Update**
**Given** an existing test case ID and issues to add
**When** I call `update_test_case(test_case_id=123, issues=["PROJ-789"])`
**Then** the tool adds the specified issues to the test case using the bulk endpoint
**And** existing issues remain linked (additive behavior)

**AC #3: Remove Issues from Test Case**
**Given** an existing test case with linked issues
**When** I call `update_test_case(test_case_id=123, remove_issues=["PROJ-123"])`
**Then** the tool removes the specified issue links from the test case
**And** other linked issues remain unchanged

**AC #4: Clear All Issues**
**Given** an existing test case with linked issues
**When** I call `update_test_case(test_case_id=123, clear_issues=True)`
**Then** the tool removes all issue links from the test case
**And** returns confirmation of cleared issues

**AC #5: Issue Key Validation**
**Given** an invalid issue key format
**When** the tool validates issue keys
**Then** it returns an LLM-friendly error via the global Agent Hint flow
**And** the error lists ALL invalid keys with expected format hint

**AC #6: Integration ID Resolution**
**Given** an issue key like "PROJ-123"
**When** linking the issue to a test case
**Then** the tool resolves the integration ID for the project
**And** creates the IssueDto with correct `integration_id` and `name` fields

**AC #7: Mixed Operations**
**Given** an update request with both `issues` (to add) and `remove_issues`
**When** the tool processes the request
**Then** removals are processed first, then additions
**And** the final state reflects both operations correctly

**AC #8: Idempotent Issue Linking**
**Given** an issue already linked to a test case
**When** I attempt to link the same issue again
**Then** the operation succeeds without error
**And** no duplicate links are created

**AC #9: Tool Output Formatting**
**Given** any issue link operation (add, remove, clear)
**When** the operation completes
**Then** the tool returns concise, actionable LLM-friendly text
**And** includes issue count and specific keys affected

**AC #10: Unit Tests**
**Given** the issue link management logic
**When** running unit tests
**Then** tests cover:
  - Add issues on test case creation
  - Add issues on test case update
  - Remove specific issues
  - Clear all issues
  - Invalid issue key validation
  - Integration ID resolution
  - Idempotent add/remove operations

**AC #11: Integration Tests**
**Given** the issue link tools
**When** running integration tests
**Then** tests verify the formatted output messages for all operations

**AC #12: E2E Tests**
**Given** a sandbox Allure TestOps instance with Jira integration
**When** running E2E tests
**Then** tests cover the full workflow:
  - Create test case with issues linked
  - Verify issues appear in test case details
  - Add more issues via update
  - Remove specific issues
  - Clear all issues
  - Attempt invalid issue key (verify error)

## Tasks / Subtasks

- [ ] Task 1: Implement issue link service methods (AC: #1, #2, #3, #4, #6, #7, #8)
  - [ ] 1.1: Add `add_issues_to_test_case()` method to `TestCaseService`
  - [ ] 1.2: Add `remove_issues_from_test_case()` method to `TestCaseService`
  - [ ] 1.3: Add issue linking step in `create_test_case()` after test case creation
  - [ ] 1.4: Implement integration ID resolution using `/api/integration` endpoint
  - [ ] 1.5: Build `TestCaseBulkIssueDto` payloads for bulk API

- [ ] Task 2: Extend create_test_case tool (AC: #1, #5, #9)
  - [ ] 2.1: Add `issues` parameter to `create_test_case` tool signature
  - [ ] 2.2: Add issue key validation logic
  - [ ] 2.3: Call service method after test case creation
  - [ ] 2.4: Update tool docstring with issue parameter documentation
  - [ ] 2.5: Format output to include linked issue count

- [ ] Task 3: Extend update_test_case tool (AC: #2, #3, #4, #5, #7, #9)
  - [ ] 3.1: Add `issues` parameter (issues to add)
  - [ ] 3.2: Add `remove_issues` parameter
  - [ ] 3.3: Add `clear_issues` parameter
  - [ ] 3.4: Implement processing order (remove/clear first, then add)
  - [ ] 3.5: Update tool docstring with issue parameters documentation
  - [ ] 3.6: Format output to include issue operations summary

- [ ] Task 4: Tests (AC: #10, #11, #12)
  - [ ] 4.1: Unit tests for `add_issues_to_test_case()` service method
  - [ ] 4.2: Unit tests for `remove_issues_from_test_case()` service method
  - [ ] 4.3: Unit tests for issue key validation logic
  - [ ] 4.4: Unit tests for integration ID resolution
  - [ ] 4.5: Integration tests for tool output formatting
  - [ ] 4.6: E2E tests covering full issue link lifecycle

## Dev Notes

### API Endpoints

**TestCaseBulkControllerApi:**
- `issue_add1` - POST `/api/testcase/bulk/issue/add` - Add issues to test cases
  - Request: `TestCaseBulkIssueDto` (issues: `List[IssueDto]`, selection: `TestCaseTreeSelectionDto`)
  - Uses bulk API even for single test case (wrap in selection)
  
- `issue_remove1` - POST `/api/testcase/bulk/issue/remove` - Remove issues from test cases
  - Request: `TestCaseBulkIssueDto` (issues: `List[IssueDto]`, selection: `TestCaseTreeSelectionDto`)

**Reference:** [`src/client/generated/api/test_case_bulk_controller_api.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/api/test_case_bulk_controller_api.py) (lines 1905-2400)

### Generated Models

From Allure TestOps OpenAPI spec:
- `IssueDto` - Issue with `id`, `name`, `integration_id`, `url`, `status`, `closed`, `summary`
- `TestCaseBulkIssueDto` - Bulk issue request with `issues: List[IssueDto]` and `selection: TestCaseTreeSelectionDto`
- `TestCaseTreeSelectionDto` - Selection with `projectId`, `groupsInclude`, `leavesInclude`
- `IssueCreateDto` - Create issue with `integration_id` and `name` (for linking)

**Reference:** [`src/client/generated/docs/IssueDto.md`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/docs/IssueDto.md)

### Integration ID Resolution

Issues in Allure TestOps are linked via external integrations (Jira, GitHub Issues, etc.):
1. Get available integrations: `GET /api/integration` or project-specific endpoint
2. Match issue key prefix (e.g., "PROJ" from "PROJ-123") to integration
3. Set `integration_id` on `IssueDto` for linking

**Note:** If project has single integration, use that ID. If multiple, may need to infer from issue key format or project configuration.

### Existing Patterns to Follow

**From Story 3.8 (Custom Fields):**
- Aggregated validation errors pattern (collect all issues before failing)
- Service method returns structured data, tool formats to text
- Idempotent operations (safe to call multiple times)

**From Story 1.3 (Test Case Creation):**
- Post-creation operations pattern (similar to attachments handling)
- Two-phase create: create entity, then add related items

### Implementation Approach

1. **Create first, link second:**
   - `create_test_case` creates the test case normally
   - If `issues` parameter provided, call `issue_add1` bulk API
   - Return combined result message

2. **Selection DTO for single test case:**
   ```python
   selection = TestCaseTreeSelectionDto(
       projectId=project_id,
       groupsInclude=[],  # No groups
       leavesInclude=[test_case_id]  # Single test case
   )
   ```

3. **IssueDto construction:**
   ```python
   issue_dto = IssueDto(
       name="PROJ-123",  # The issue key
       integration_id=123  # Resolved from project integrations
   )
   ```

### Project Structure Notes

- Service logic: `src/services/test_case_service.py` (extend existing class)
- Tool updates: `src/tools/create_test_case.py`, `src/tools/update_test_case.py`
- Client wrapper may need new method for bulk issue API

### Constraints

1. **Thin Tool / Fat Service Pattern:**
   - Tools parse parameters and call service methods
   - All business logic in TestCaseService methods
   - No try/except in tools (per project-context.md)

2. **Error Handling:**
   - Let exceptions bubble to global error handler
   - Service layer raises `AllureValidationError` for validation failures
   - Aggregate validation errors (list all invalid issue keys)

3. **API Sequence:**
   - For updates with remove + add: call `issue_remove1` first, then `issue_add1`
   - For clear: call `issue_remove1` with all current issues first

4. **Issue Key Format:**
   - Typically: `[PROJECT]-[NUMBER]` (e.g., `PROJ-123`, `TICKET-456`)
   - Validate format before API call
   - Accept uppercase and normalize

### Testing Approach

**Unit Tests (mocked API):**
- Mock `TestCaseBulkControllerApi.issue_add1` and `issue_remove1`
- Test service methods with various issue lists
- Test validation logic for invalid keys
- Use `respx` for HTTP mocking

**Integration Tests:**
- Test tool output formatting
- Verify correct message structure

**E2E Tests (sandbox instance):**
- Requires Allure TestOps instance with Jira integration configured
- Create test case → link issues → verify → unlink → verify
- Use existing sandbox project from other E2E tests

### Testing Requirements

- Unit tests for service methods with mocked API responses using `respx`.
- Integration tests for tool output formatting.
- E2E tests for full CRUD lifecycle against sandbox instance.
- Run unit + integration tests:
  - `uv run --env-file .env.test pytest tests/unit/ tests/integration/`
- Run E2E tests:
  - `uv run --env-file .env.test pytest tests/e2e/`
- Run Packaging tests:
  - `uv run pytest tests/packaging/`

### References

**Related Stories:**
- Story 3.8: Custom Fields Management (pattern for aggregated validation)
- Story 1.3: Create Test Case (post-creation operations pattern)
- Story 1.4: Update Test Case (idempotent update pattern)

**Related Files:**
- [`src/services/test_case_service.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/test_case_service.py) - Service to extend
- [`src/tools/create_test_case.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/create_test_case.py) - Tool to modify
- [`src/tools/update_test_case.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/update_test_case.py) - Tool to modify
- [`src/client/generated/api/test_case_bulk_controller_api.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/api/test_case_bulk_controller_api.py) - API for issue operations
- [`specs/project-context.md`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-context.md) - Project coding standards

**Git Intelligence:**
- Recent commits show pattern of extending existing tools (e.g., test layers in create/update)
- Commit `b4e1322` - "feat(tools): test layers in test case crud" shows similar extension pattern

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
