# Story 3.11: CRUD for Custom Field Values

Status: ready-for-dev

<!-- Note: This story manages custom field VALUE options at the project level (e.g., adding "Smoke", "Regression" as allowed values for a "Test Type" field), independent of test case assignments. -->

## Story

As an AI Agent,
I want to create, list, update, and delete custom field value options for a project,
so that I can manage the allowed values that can be assigned to test cases without manually configuring them in the Allure TestOps UI.

## Acceptance Criteria

**AC #1: List Custom Field Values**
**Given** a valid project ID and custom field ID
**When** I call `list_custom_field_values`
**Then** the tool returns all allowed values for that custom field in the project
**And** the output includes value ID, name, and test case count
**And** results support pagination via `page` and `size` parameters
**And** results can be filtered via `query` parameter

**AC #2: Create Custom Field Value**
**Given** a valid project ID and custom field ID
**When** I call `create_custom_field_value` with a name
**Then** a new value option is created for that custom field in the project
**And** the response includes the new value's ID and name
**And** duplicate names result in an error with a clear hint

**AC #3: Update Custom Field Value**
**Given** a valid custom field value ID
**When** I call `update_custom_field_value` with new properties
**Then** the value is updated (e.g., renamed)
**And** test results are NOT affected by the rename (per API contract)
**And** the tool returns a success message

**AC #4: Delete Custom Field Value**
**Given** a valid custom field value ID
**When** I call `delete_custom_field_value`
**Then** the value is removed from the project
**And** test cases that had this value will no longer have it assigned
**And** the tool returns a confirmation message

**AC #5: Custom Field Resolution**
**Given** a custom field name (string) instead of ID
**When** calling any of the CRUD tools
**Then** the tool resolves the name to the corresponding custom field ID
**And** invalid names result in an error suggesting valid custom fields

**AC #6: Tool Output Formatting**
**Given** any custom field value operation
**When** the operation completes
**Then** the tool returns concise, actionable LLM-friendly text
**And** list operations show values in a scannable format
**And** errors include hints for correction

**AC #7: Unit Tests**
**Given** the new `CustomFieldValueService`
**When** running unit tests
**Then** tests cover:
  - List custom field values with pagination
  - Create custom field value with valid input
  - Create with duplicate name error
  - Update custom field value
  - Delete custom field value
  - Custom field name resolution
  - Invalid custom field ID error

**AC #8: Integration Tests**
**Given** the custom field value tools
**When** running integration tests
**Then** tests verify the formatted output messages for all operations

**AC #9: E2E Tests**
**Given** a sandbox Allure TestOps instance with configured custom fields
**When** running E2E tests
**Then** tests cover the full workflow:
  - List existing custom field values
  - Create a new custom field value
  - Verify created value appears in list
  - Update the value (rename)
  - Delete the value
  - Verify deleted value no longer appears

## Tasks / Subtasks

- [ ] Task 1: Create CustomFieldValueService
  - [ ] 1.1: Create `src/services/custom_field_value_service.py`
  - [ ] 1.2: Implement `list_custom_field_values()` using `CustomFieldValueProjectControllerApi.find_all22`
  - [ ] 1.3: Implement `create_custom_field_value()` using `CustomFieldValueProjectControllerApi.create26`
  - [ ] 1.4: Implement `update_custom_field_value()` using `CustomFieldValueProjectControllerApi.patch23`
  - [ ] 1.5: Implement `delete_custom_field_value()` using `CustomFieldValueProjectControllerApi.delete47`
  - [ ] 1.6: Implement custom field name → ID resolution using shared `_get_resolved_custom_fields()` pattern

- [ ] Task 2: Extend AllureClient
  - [ ] 2.1: Add wrapper methods for `CustomFieldValueProjectControllerApi` endpoints
  - [ ] 2.2: Handle 404 responses as `AllureNotFoundError`
  - [ ] 2.3: Handle duplicate name conflicts as `AllureValidationError`

- [ ] Task 3: Create MCP Tools
  - [ ] 3.1: Create `src/tools/list_custom_field_values.py`
  - [ ] 3.2: Create `src/tools/create_custom_field_value.py`
  - [ ] 3.3: Create `src/tools/update_custom_field_value.py`
  - [ ] 3.4: Create `src/tools/delete_custom_field_value.py`
  - [ ] 3.5: Register all tools in `src/tools/__init__.py`
  - [ ] 3.6: Add LLM-optimized docstrings with detailed parameter descriptions

- [ ] Task 4: Tests
  - [ ] 4.1: Unit tests for `CustomFieldValueService` methods
  - [ ] 4.2: Unit tests for custom field name resolution
  - [ ] 4.3: Integration tests for tool output formatting
  - [ ] 4.4: E2E tests covering full CRUD lifecycle

## Dev Notes

### Developer Context (Guardrails)

- Keep tools thin; all validation and API logic belongs in `CustomFieldValueService`. [Source: specs/project-context.md#The-"Thin-Tool-/-Fat-Service"-Pattern]
- No try/except in tools; let exceptions bubble to the global handler. [Source: specs/project-context.md#Error-Handling-Strategy]
- Avoid `Any` in new code and tests; use precise types like `dict[str, object]` or dedicated DTOs. [Source: GEMINI.md]
- Do not mute lint checks or exclude tests. [Source: GEMINI.md]

### Technical Requirements

**API Endpoints (CustomFieldValueProjectControllerApi):**
- `find_all22` - GET `/api/project/{projectId}/cfv` - List CF values for project
  - Required: `project_id`, `custom_field_id`
  - Optional: `query`, `var_global`, `test_case_search`, `page`, `size`, `sort`
  - Returns: `PageCustomFieldValueWithTcCountDto`
  
- `create26` - POST `/api/project/{projectId}/cfv` - Create new CF value
  - Required: `project_id`, `custom_field_value_project_create_dto`
  - Returns: `CustomFieldValueWithCfDto`
  
- `patch23` - PATCH `/api/project/{projectId}/cfv/{cfvId}` - Update CF value
  - Required: `project_id`, `cfv_id`, `custom_field_value_project_patch_dto`
  - Note: Test results won't be affected
  - Returns: void
  
- `delete47` - DELETE `/api/project/{projectId}/cfv/{id}` - Delete CF value
  - Required: `project_id`, `id`
  - Returns: void (204 No Content)

**Reference:** [`src/client/generated/docs/CustomFieldValueProjectControllerApi.md`](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/docs/CustomFieldValueProjectControllerApi.md)

### Generated Models

From Allure TestOps OpenAPI spec:
- `CustomFieldValueProjectCreateDto` - For creating new CF values (name, customFieldId)
- `CustomFieldValueProjectPatchDto` - For patching CF values
- `CustomFieldValueWithCfDto` - Response with CF value + parent CF info
- `PageCustomFieldValueWithTcCountDto` - Paginated list with test case count
- `CustomFieldValueWithTcCountDto` - Single value with test case usage count

### Architecture Compliance

- Follow "Thin Tool / Fat Service" pattern established in project. [Source: specs/project-context.md#The-"Thin-Tool-/-Fat-Service"-Pattern]
- Reuse custom field resolution pattern from `TestCaseService._get_resolved_custom_fields()`. [Source: src/services/test_case_service.py:757-778]
- Use global exception handler for error responses. [Source: specs/project-context.md#Error-Handling-Strategy]
- All HTTP via async `httpx` client. [Source: specs/project-context.md#Technology-Stack-&-Versions]

### Library/Framework Requirements

- Python 3.14, Pydantic v2 strict mode, async `httpx`, pytest, respx. [Source: specs/project-context.md#Technology-Stack-&-Versions]
- Use existing generated client models and DTOs; no new dependencies.

### File Structure Requirements

New files:
- `src/services/custom_field_value_service.py` - Service with CRUD operations
- `src/tools/list_custom_field_values.py` - List tool
- `src/tools/create_custom_field_value.py` - Create tool
- `src/tools/update_custom_field_value.py` - Update tool
- `src/tools/delete_custom_field_value.py` - Delete tool

Modified files:
- `src/client/client.py` - Add wrapper methods for new API endpoints
- `src/tools/__init__.py` - Register new tools

Test files:
- `tests/unit/test_custom_field_value_service.py`
- `tests/integration/test_custom_field_value_tools.py`
- `tests/e2e/test_manage_custom_field_values.py`

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

### Previous Story Intelligence

- Story 3.6 established `get_custom_fields` tool for listing project custom fields with allowed values; reuse the same output formatting patterns. [Source: specs/implementation-artifacts/3-6-get-custom-fields-with-values.md]
- Story 3.8 established custom field resolution and validation patterns in `TestCaseService`; reuse the caching and resolution logic. [Source: specs/implementation-artifacts/3-8-manage-test-case-custom-fields.md]
- Story 3.7 demonstrated CRUD pattern for test layers; follow similar service/tool structure. [Source: specs/implementation-artifacts/3-7-crud-test-layers.md]

### Relationship to Other Stories

- Story 3.6 (`get_custom_fields`) - Lists custom fields with their existing values; this story enables MANAGING those values
- Story 3.8 (`update_test_case` custom fields) - Assigns CF values to test cases; this story manages the VALUES themselves
- This story is independent of test cases; it manages the OPTIONS available for assignment

### Project Context Reference

- Project rules and patterns are in `specs/project-context.md` and must be followed for all updates.
- Tool outputs must be LLM-friendly text, not raw JSON. [Source: specs/project-context.md#Tool-Outputs]
- Tool names in `snake_case`. [Source: specs/project-context.md#Tool-Names-&-Args]

### References

- Custom field value project API: src/client/generated/docs/CustomFieldValueProjectControllerApi.md
- Custom field resolution pattern: src/services/test_case_service.py:757-778
- Get custom fields tool (output format reference): src/tools/get_custom_fields.py
- Test layer CRUD pattern (structure reference): src/services/test_layer_service.py
- Project context rules: specs/project-context.md

## Story Completion Status

- Status: ready-for-dev
- Completion note: Ultimate context engine analysis completed - comprehensive developer guide created

## Dev Agent Record

### Agent Model Used

(To be filled by dev agent)

### Debug Log References

(To be filled by dev agent)

### Completion Notes List

(To be filled by dev agent)

### File List

(To be filled by dev agent)
