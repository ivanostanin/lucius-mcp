# Story 3.9: Test Layer Validation in create_test_case

Status: ready-for-dev

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

- [ ] Task 1: Extend `create_test_case` tool signature
  - [ ] 1.1: Add `test_layer_id: int | None` parameter to tool
  - [ ] 1.2: Add `test_layer_name: str | None` parameter to tool
  - [ ] 1.3: Add parameter descriptions optimized for LLM understanding
  - [ ] 1.4: Ensure parameters are optional (default=None) for backward compatibility

- [ ] Task 2: Implement validation logic in TestCaseService
  - [ ] 2.1: Add `_validate_test_layer()` method to `TestCaseService`
  - [ ] 2.2: Integrate `TestLayerService` as a dependency in `TestCaseService.__init__()`
  - [ ] 2.3: Implement test layer ID validation (check existence via `get_test_layer()`)
  - [ ] 2.4: Implement test layer name resolution (list + filter + match)
  - [ ] 2.5: Handle ambiguous name matches with clear error
  - [ ] 2.6: Generate actionable warning/error messages with available options

- [ ] Task 3: Update `create_test_case` method
  - [ ] 3.1: Call `_validate_test_layer()` in `TestCaseService.create_test_case()`
  - [ ] 3.2: Pass validated `test_layer_id` to `TestCaseCreateV2Dto`
  - [ ] 3.3: Ensure validation happens before test case creation (early exit on error)
  - [ ] 3.4: Update method signature to accept `test_layer_id` or `test_layer_name`

- [ ] Task 4: Tests
  - [ ] 4.1: Unit tests for `TestCaseService._validate_test_layer()` (all validation scenarios)
  - [ ] 4.2: Unit tests for `TestCaseService.create_test_case()` with test layer parameters
  - [ ] 4.3: Integration tests for `create_test_case` tool output formatting
  - [ ] 4.4: E2E tests covering full workflow (create layer + create case + verify assignment)

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

## Dev Agent Record

### Agent Model Used

(To be filled by dev agent)

### Debug Log References

(To be filled by dev agent)

### Completion Notes List

(To be filled by dev agent)

### File List

(To be filled by dev agent)
