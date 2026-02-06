# Story 3.9: Test Layer Validation in create_test_case

Status: done

<!-- Note: This story addresses AC #12 from Story 3.7 which was deferred during implementation -->

## User Story

As an AI Agent,
I want the `create_test_case` tool to validate test layer assignments and warn me if a test layer doesn't exist,
So that I can ensure test cases are properly categorized and avoid creating test cases with invalid test layer references.

## Acceptance Criteria

**AC #1: Test Layer Parameter Support**
**Given** the `create_test_case` tool
**When** I call it with a `test_layer_id` or `test_layer_name` parameter
**Then** the parameter is accepted and validated before test case creation

**AC #2: Test Layer Existence Validation**
**Given** a `test_layer_id` or `test_layer_name` is provided
**When** the test layer does not exist in the project
**Then** the tool fires a clear warning message to the user before proceeding
**And** the warning includes available test layers for reference

**AC #3: Test Layer by ID**
**Given** a valid `test_layer_id`
**When** I create a test case with this ID
**Then** the test case is created with the test layer correctly assigned

**AC #4: Test Layer by Name**
**Given** a valid `test_layer_name`
**When** I create a test case with this name
**Then** the tool resolves the name to the corresponding test layer ID
**And** the test case is created with the test layer correctly assigned

**AC #5: Multiple Test Layers Available**
**Given** multiple test layers exist with similar names
**When** I provide a test_layer_name that matches multiple layers
**Then** the tool provides a clear error listing all matching options
**And** suggests using `test_layer_id` for disambiguation

**AC #6: Graceful Degradation**
**Given** no test_layer parameter is provided
**When** I create a test case
**Then** the tool behaves as before (no test layer assigned)
**And** no validation errors occur

**AC #7: Error Message Quality**
**Given** an invalid test_layer_id or test_layer_name
**When** validation fails
**Then** the error message is actionable and includes:
  - What was wrong (layer not found)
  - Available test layers (first 10 with pagination hint)
  - How to fix it (use `list_test_layers` or provide valid ID/name)

**AC #8: Integration with TestLayerService**
**Given** the `TestLayerService` from Story 3.7
**When** validating test layers
**Then** the `create_test_case` service method uses `TestLayerService.list_test_layers()` or `TestLayerService.get_test_layer()`
**And** no duplicate test layer logic is implemented

**AC #9: Unit Tests**
**Given** the new validation logic
**When** running unit tests
**Then** tests cover:
  - Valid test_layer_id assignment
  - Valid test_layer_name resolution
  - Invalid test_layer_id error
  - Invalid test_layer_name error
  - Ambiguous test_layer_name error
  - No test_layer provided (graceful degradation)

**AC #10: Integration Tests**
**Given** the `create_test_case` tool with test layer support
**When** running integration tests
**Then** tests verify the formatted output messages for all validation scenarios

**AC #11: E2E Tests**
**Given** a sandbox Allure TestOps instance with configured test layers
**When** running E2E tests
**Then** tests cover the full workflow:
  - Create test layer via `create_test_layer`
  - Create test case with valid test_layer_id
  - Create test case with valid test_layer_name
  - Attempt to create test case with invalid test layer (verify warning)
  - Verify test case has correct test layer assignment in TestOps

**AC #12: Backward Compatibility**
**Given** existing code using `create_test_case` without test_layer parameters
**When** those tools are executed
**Then** they continue to work without modification
**And** no breaking changes are introduced

## Tasks / Subtasks

- [x] Task 1: Extend `create_test_case` tool signature
  - [x] 1.1: Add `test_layer_id: int | None` parameter to tool
  - [x] 1.2: Add `test_layer_name: str | None` parameter to tool
  - [x] 1.3: Add parameter descriptions optimized for LLM understanding
  - [x] 1.4: Ensure parameters are optional (default=None) for backward compatibility

- [x] Task 2: Implement validation logic in TestCaseService
  - [x] 2.1: Add `_validate_test_layer()` method to `TestCaseService`
  - [x] 2.2: Integrate `TestLayerService` as a dependency in `TestCaseService.__init__()`
  - [x] 2.3: Implement test layer ID validation (check existence via `get_test_layer()`)
  - [x] 2.4: Implement test layer name resolution (list + filter + match)
  - [x] 2.5: Handle ambiguous name matches with clear error
  - [x] 2.6: Generate actionable warning/error messages with available options

- [x] Task 3: Update `create_test_case` method
  - [x] 3.1: Call `_validate_test_layer()` in `TestCaseService.create_test_case()`
  - [x] 3.2: Pass validated `test_layer_id` to `TestCaseCreateV2Dto`
  - [x] 3.3: Ensure validation happens before test case creation (early exit on error)
  - [x] 3.4: Update method signature to accept `test_layer_id` or `test_layer_name`

- [x] Task 4: Tests
  - [x] 4.1: Unit tests for `TestCaseService._validate_test_layer()` (all validation scenarios)
  - [x] 4.2: Unit tests for `TestCaseService.create_test_case()` with test layer parameters
  - [x] 4.3: Integration tests for `create_test_case` tool output formatting
  - [x] 4.4: E2E tests covering full workflow (create layer + create case + verify assignment)

## Dev Notes

### Existing Capabilities

**From Story 3.7 (CRUD Test Layers - COMPLETED):**
- `TestLayerService` with full CRUD operations for test layers and schemas
- Tools: `list_test_layers`, `create_test_layer`, `get_test_layer` (if exists)
- Test layers have ID and name fields
- Comprehensive test coverage for test layer management

**Current `create_test_case` Implementation:**
- Located at: [`src/tools/create_test_case.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/create_test_case.py)
- Service layer: [`src/services/test_case_service.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/test_case_service.py)
- Accepts: name, description, steps, tags, attachments, custom_fields
- **Does NOT currently accept test_layer_id or test_layer_name**

### Generated Models

From Allure TestOps OpenAPI spec:
- `TestLayerDto` - has `id: int` and `name: str` fields
- `TestCaseCreateV2Dto` - supports `test_layer_id: int | None` field
- `TestCasePatchV2Dto` - supports `test_layer_id: int | None` field for updates

### Implementation Constraints

1. **Thin Tool / Fat Service Pattern:**
   - Tool (`create_test_case`) should only parse parameters and call service
   - All validation logic goes in `TestCaseService._validate_test_layer()`
   - No business logic in tools

2. **Error Handling:**
   - **NO try/except in tools** (per project-context.md)
   - Let exceptions bubble to global error handler
   - Service layer raises `AllureValidationError` for validation failures

3. **Test Layer Service Integration:**
   - Import and use `TestLayerService` in `TestCaseService`
   - Pass `AllureClient` instance to `TestLayerService` constructor
   - Reuse existing `list_test_layers()` and `get_test_layer()` methods

4. **Parameter Resolution Priority:**
   - If both `test_layer_id` and `test_layer_name` provided → error (mutually exclusive)
   - If `test_layer_id` provided → validate ID exists
   - If `test_layer_name` provided → resolve to ID, handle ambiguity
   - If neither provided → skip validation (backward compatible)

5. **Warning vs Error:**
   - Invalid test layer = **ERROR** (raise AllureValidationError)
   - Do NOT create test case if test layer validation fails
   - Agent Hint should guide user to fix the issue

### References

**Code Review Source:**
- Original issue: Code Review Story 3.7, Issue #1 (HIGH - CRITICAL)
- Issue #6 also addressed: E2E test for AC #12

**Related Files:**
- [`src/services/test_layer_service.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/test_layer_service.py) - Test layer CRUD service
- [`src/tools/create_test_case.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/create_test_case.py) - Tool to modify
- [`src/services/test_case_service.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/test_case_service.py) - Service to extend
- [`specs/project-context.md`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-context.md) - Project coding standards

**Previous Story Intelligence:**
- Story 3.7 implemented all test layer CRUD operations
- 28 tests passing for test layer functionality
- Idempotent update and delete patterns established
- Error messages provide actionable guidance

## Senior Developer Review (AI)

- **Outcome**: Changes Requested
- **Notes**:
  - **High**: AC #2 requires warning messaging prior to proceeding; validation currently raises errors and blocks creation. Adjusted error copy to explicitly warn and to state creation was not performed.
  - **High**: AC #10 lacked integration validation of formatted output messages; added message-focused integration coverage.
  - **Medium**: AC #11 warning verification updated to assert warning message content for invalid layer name.
  - **Medium (Deferred)**: `list_test_layers` only checks the first 100 results when validating names/IDs; pagination is not handled and could yield false negatives.

## Dev Agent Record

### Agent Model Used

gpt-5.2-codex

### Debug Log References

- Updated validation messages for invalid test layers to include warning context and non-creation notice.

### Completion Notes List

- Updated test layer validation messages to include warning context, list available layers, and clarify that creation is blocked.
- Added integration coverage for test layer validation message formatting.
- Updated E2E expectation to validate warning message content for invalid test layer names.

### File List

- [src/services/test_case_service.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/test_case_service.py)
- [tests/unit/test_test_case_service.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/tests/unit/test_test_case_service.py)
- [tests/integration/test_tool_hints.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/tests/integration/test_tool_hints.py)
- [tests/e2e/test_create_test_case.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/tests/e2e/test_create_test_case.py)
- [specs/implementation-artifacts/3-9-test-layer-validation-in-create-test-case.md](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/specs/implementation-artifacts/3-9-test-layer-validation-in-create-test-case.md)

### Change Log

#### 2026-02-03: Senior Developer Review (AI)
- Updated test layer validation messages to surface warnings and clarify non-creation behavior.
- Added integration test coverage for validation message formatting.
- Updated E2E invalid-name expectation to verify warning content.
- Deferred pagination handling for test layer lookup beyond first 100.
