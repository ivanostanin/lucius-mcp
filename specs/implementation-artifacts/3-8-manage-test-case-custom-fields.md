# Story 3.8: Manage Test Case Custom Fields

Status: ready-for-dev

<!-- Note: This story builds on Story 3.6 (get_custom_fields) to provide full custom field lifecycle management -->

## User Story

As an AI Agent,
I want to update and clear custom field values on existing test cases using the dedicated custom field endpoints,
So that I can maintain accurate metadata without rewriting entire test cases and can explicitly remove outdated custom field values.

## Acceptance Criteria

**AC #1: Custom Field Update via Dedicated Endpoint**
**Given** a valid test case ID and a custom field map
**When** I call `update_test_case(custom_fields={...})`
**Then** the tool updates those custom fields using the dedicated custom-field-values endpoint (`PATCH /api/testcase/{testCaseId}/cfv`)
**And** other test case fields remain unchanged

**AC #2: Clear Custom Field Values**
**Given** a test case with existing custom field values
**When** I call `update_test_case` with a custom field set to an empty list per API contract
**Then** the tool clears that custom field value completely
**And** the custom field is removed from the test case

**AC #3: Get Test Case Custom Field Values**
**Given** a valid test case ID
**When** I call `get_test_case_custom_fields`
**Then** the tool returns the test case's current custom field values using `GET /api/testcase/{testCaseId}/cfv`
**And** the output is formatted as LLM-friendly plain text

**AC #4: Custom Field Validation**
**Given** invalid custom field names or values
**When** the tool validates input before update
**Then** it returns an LLM-friendly error via the global Agent Hint flow
**And** the error lists ALL invalid fields or values (aggregated validation)
**And** suggests valid custom fields from `get_custom_fields`

**AC #5: Custom Field Name Resolution**
**Given** a custom field name (string) in the update request
**When** validating the custom field
**Then** the tool resolves the name to the corresponding custom field ID
**And** validates the value against allowed values (if restricted)

**AC #6: Multi-Value Custom Field Support**
**Given** a custom field that allows multiple values
**When** I provide a list of values
**Then** all values are validated and applied correctly
**And** invalid values in the list trigger aggregated validation errors

**AC #7: Required Custom Field Enforcement**
**Given** a project with required custom fields
**When** I attempt to clear a required custom field
**Then** the tool returns a clear error indicating the field is required
**And** suggests valid values for that field

**AC #8: Idempotent Updates**
**Given** I call `update_test_case` with the same custom field values twice
**When** both requests complete
**Then** the second request succeeds without error
**And** no unnecessary API calls are made

**AC #9: Integration with Story 3.6**
**Given** the `get_custom_fields` tool from Story 3.6
**When** validating custom fields in `update_test_case`
**Then** the same cached custom field metadata is reused
**And** no duplicate API calls to `/api/testcase/cfv` occur

**AC #10: Tool Output Formatting**
**Given** any custom field operation (update, clear, get)
**When** the operation completes
**Then** the tool returns concise, actionable LLM-friendly text
**And** includes what changed (for updates) or current state (for get)

**AC #11: Unit Tests**
**Given** the new custom field management logic
**When** running unit tests
**Then** tests cover:
  - Update custom field values with valid inputs
  - Clear custom field values (empty list)
  - Get custom field values for test case
  - Invalid custom field name error
  - Invalid custom field value error (against allowed values)
  - Required field validation
  - Multi-value field validation
  - Idempotent update verification

**AC #12: Integration Tests**
**Given** the custom field management tools
**When** running integration tests
**Then** tests verify the formatted output messages for all operations

**AC #13: E2E Tests**
**Given** a sandbox Allure TestOps instance with configured custom fields
**When** running E2E tests
**Then** tests cover the full workflow:
  - Get available custom fields via `get_custom_fields`
  - Create test case with custom fields
  - Update custom field values via dedicated endpoint
  - Get custom field values and verify update
  - Clear custom field value
  - Verify cleared field no longer appears
  - Attempt invalid custom field (verify error)

**AC #14: Backward Compatibility**
**Given** existing code using `create_test_case` with custom_fields parameter
**When** those tools are executed
**Then** they continue to work without modification
**And** the resolution and validation logic is shared

## Tasks / Subtasks

- [ ] Task 1: Implement dedicated custom field value endpoint support
  - [ ] 1.1: Add `get_test_case_custom_fields()` method to `TestCaseService`
  - [ ] 1.2: Add `update_test_case_custom_fields()` method to `TestCaseService`
  - [ ] 1.3: Integrate `get_custom_fields_with_values3` API (GET test case cfv)
  - [ ] 1.4: Integrate `update_cfvs_of_test_case` API (PATCH test case cfv)
  - [ ] 1.5: Build `CustomFieldWithValuesDto` payloads for updates
  - [ ] 1.6: Support explicit empty values for clearing custom fields

- [ ] Task 2: Enhanced custom field validation
  - [ ] 2.1: Extract/enhance `_validate_and_resolve_custom_fields()` method
  - [ ] 2.2: Validate custom field names against project metadata
  - [ ] 2.3: Validate custom field values against allowed values
  - [ ] 2.4: Aggregate validation errors (collect all issues before failing)
  - [ ] 2.5: Enforce required custom field rules
  - [ ] 2.6: Generate actionable error messages with suggestions

- [ ] Task 3: Update `update_test_case` tool
  - [ ] 3.1: Route custom-field-only updates through `update_test_case_custom_fields()`
  - [ ] 3.2: Use dedicated `/cfv` endpoint instead of full PATCH for custom fields
  - [ ] 3.3: Maintain backward compatibility with mixed updates
  - [ ] 3.4: Update tool signature if needed (ensure custom_fields parameter exists)

- [ ] Task 4: Create `get_test_case_custom_fields` tool
  - [ ] 4.1: Create new tool in `src/tools/get_test_case_custom_fields.py`
  - [ ] 4.2: Accept `test_case_id` parameter with validation
  - [ ] 4.3: Format output as LLM-friendly plain text
  - [ ] 4.4: Register tool in `src/tools/__init__.py`

- [ ] Task 5: Tests
  - [ ] 5.1: Unit tests for `get_test_case_custom_fields()` service method
  - [ ] 5.2: Unit tests for `update_test_case_custom_fields()` service method
  - [ ] 5.3: Unit tests for validation logic (all scenarios)
  - [ ] 5.4: Integration tests for tool output formatting
  - [ ] 5.5: E2E tests covering full custom field lifecycle

## Dev Notes

### Existing Capabilities

**From Story 3.6 (get_custom_fields - COMPLETED):**
- `TestCaseService.get_custom_fields()` - Lists project custom fields with allowed values
- `TestCaseService._get_resolved_custom_fields()` - Resolves CF names → IDs with caching
- Custom field cache (`_cf_cache`) shared across operations for performance
- LLM-friendly text output format established

**Current Custom Field Implementation:**
- Located at: [`src/services/test_case_service.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/test_case_service.py)
- `create_test_case()` validates and resolves custom fields (lines 117-171)
- `update_test_case()` patches custom fields via `TestCasePatchV2Dto` (lines 419-490)
- `_validate_custom_fields()` performs basic type checking (lines 718-735)
- `_get_resolved_custom_fields()` provides name→ID mapping with caching (lines 757-778)
- `_build_custom_field_dtos()` constructs CF DTOs for API calls (lines 783-807)

### API Endpoints

**Custom Field Value Endpoints (TestCaseCustomFieldControllerApi):**
- `get_custom_fields_with_values2` - POST `/api/testcase/cfv` - Project-level custom field metadata
  - Used by Story 3.6 for discovery
  - Returns `CustomFieldProjectWithValuesDto[]` with field definitions and allowed values
  
- `get_custom_fields_with_values3` - GET `/api/testcase/{testCaseId}/cfv` - Test case custom field values
  - **NEW for this story** - Get current CF values for specific test case
  - Returns `CustomFieldWithValuesDto[]` with field + values
  
- `update_cfvs_of_test_case` - PATCH `/api/testcase/{testCaseId}/cfv` - Update test case custom fields
  - **NEW for this story** - Dedicated endpoint for CF updates
  - Accepts `CustomFieldWithValuesDto[]` (customField + values)
  - Supports explicit empty values to clear fields

**Reference:** [`src/client/generated/docs/TestCaseCustomFieldControllerApi.md`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/docs/TestCaseCustomFieldControllerApi.md)

### Generated Models

From Allure TestOps OpenAPI spec:
- `CustomFieldWithValuesDto` - CF ID + values list (for PATCH requests)
- `CustomFieldProjectWithValuesDto` - Project CF with allowed values
- `CustomFieldProjectDto` - CF definition (id, name, required, singleSelect, etc.)
- `CustomFieldValueDto` - Single CF value
- `TestCaseTreeSelectionDto` - Project ID wrapper for POST requests

### Current Gaps & Issues

**Gap #1: Dedicated Endpoint Not Used**
- `update_test_case()` uses `TestCasePatchV2Dto` which patches entire test case
- Should use `PATCH /api/testcase/{testCaseId}/cfv` for custom-field-only updates
- Avoids unintended side effects on other fields

**Gap #2: Cannot Clear Custom Fields**
- Current implementation doesn't support explicit empty values
- No way to remove custom field value from test case
- API requires empty `values` array to clear

**Gap #3: No Get Custom Field Values Tool**
- Can get project custom fields (Story 3.6) but not test case values
- Agents need to see current state before updating

**Gap #4: Validation Not Comprehensive**
- Current validation only checks dict type and key/value types
- Doesn't validate against allowed values
- Doesn't aggregate multiple validation errors
- Required field enforcement missing

### Implementation Constraints

1. **Thin Tool / Fat Service Pattern:**
   - Tools (`update_test_case`, `get_test_case_custom_fields`) should only parse parameters
   - All business logic in `TestCaseService` methods
   - No try/except in tools (per project-context.md)

2. **Error Handling:**
   - Let exceptions bubble to global error handler
   - Service layer raises `AllureValidationError` for validation failures
   - Aggregate all validation errors before raising

3. **Cache Reuse from Story 3.6:**
   - Share `_cf_cache` between `get_custom_fields` and custom field operations
   - Reuse `_get_resolved_custom_fields()` for name→ID resolution
   - Avoid duplicate API calls to `/api/testcase/cfv` (project-level)

4. **Endpoint Selection Logic:**
   - If **only** custom_fields provided → Use `PATCH /api/testcase/{testCaseId}/cfv`
   - If custom_fields + other fields → Use `PATCH /api/testcase/{testCaseId}` (current behavior)
   - Maintain backward compatibility

5. **Custom Field Value Format:**
   - Single-select fields: `values: ["value"]` (array with one item)
   - Multi-select fields: `values: ["value1", "value2", ...]`
   - Clear field: `values: []` (empty array)
   - Build `CustomFieldWithValuesDto(customField=CustomFieldDto(id=...), values=[...])`

### Validation Rules

1. **Custom Field Name Validation:**
   - Name must exist in project custom fields
   - Case-sensitive match against `CustomFieldProjectDto.name`
   - Error message includes available custom field names

2. **Custom Field Value Validation:**
   - If field has `values` list (restricted) → value must be in allowed list
   - If field is `singleSelect=true` → only one value allowed
   - If field is `required=true` → cannot clear (empty values array)
   - Error message includes allowed values for that field

3. **Aggregated Validation:**
   - Collect ALL validation errors before raising exception
   - Return structured error: "Invalid custom fields: [Layer: value 'X' not allowed (allowed: A, B, C), Component: required field cannot be cleared]"

### References

**Related Stories:**
- Story 3.6: get_custom_fields (COMPLETED) - Provides discovery and cache foundation
- Story 1.3: create_test_case (COMPLETED) - Established custom field resolution pattern

**Related Files:**
- [`src/services/test_case_service.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/test_case_service.py) - Service to extend (lines 52-807)
- [`src/tools/update_test_case.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/update_test_case.py) - Tool to modify
- [`src/tools/get_custom_fields.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/get_custom_fields.py) - Reference for output format
- [`src/client/client.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/client.py) - Client wrapper for CF endpoints
- [`src/client/generated/docs/TestCaseCustomFieldControllerApi.md`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/docs/TestCaseCustomFieldControllerApi.md) - API documentation
- [`src/client/generated/models/custom_field_with_values_dto.py`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/models/custom_field_with_values_dto.py) - DTO for PATCH
- [`specs/project-context.md`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/specs/project-context.md) - Project coding standards

**Previous Story Intelligence:**
- Story 3.6 established LLM-friendly output format for custom fields
- Caching pattern proven effective for performance
- `_get_resolved_custom_fields()` method is reusable and tested

## Change Log

- 2026-02-02: Documented senior review exception for Issue #2 (POST vs PATCH for CFV endpoint is as-designed).

## Senior Developer Review (AI)

- Issue #2 (POST vs PATCH for CFV endpoint): As-designed. The endpoint is intentionally POST per API contract; no change required.

## Dev Agent Record

### Agent Model Used

(To be filled by dev agent)

### Debug Log References

(To be filled by dev agent)

### Completion Notes List

(To be filled by dev agent)

### File List

(To be filled by dev agent)
