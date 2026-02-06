# Story 3.13: Integration Filtering for Issue Links

Status: ready-for-dev

<!-- Note: This story addresses the warning "Multiple integrations found" by adding integration selection support -->

## User Story

As an AI Agent,
I want to discover available integrations and specify which integration to use for issue linking,
So that when multiple integrations exist (e.g., Jira, GitHub), I can reliably link issues to the correct tracker.

## Background

When creating or updating test cases with issue links in Allure TestOps projects that have multiple integrations configured, the service currently defaults to the first integration and logs a warning:

```
WARNING  Multiple integrations found (Github Integration, Noxtua Jira Integration, TestOps, TestOps TMS). 
         Defaulting to 'Github Integration' for issue linking.
```

This creates uncertainty for agents and may result in issues being linked to the wrong tracker.

## Acceptance Criteria

**AC #1: List Integrations Tool**
**Given** a project with one or more integrations configured
**When** I call `list_integrations()`
**Then** the tool returns a list of available integrations with:
  - ID
  - Name
  - Type/Info (if available)
**And** if `project_id` is not provided, it is inherited from runtime settings
**And** the list is filterable by project_id if provided explicitly

**AC #2: Integration ID Parameter for Create Test Case**
**Given** a test case creation request with issues to link
**When** I specify `integration_id` or `integration_name` parameter
**Then** the tool uses the specified integration for all issue links
**And** validates the integration exists before linking

**AC #3: Integration ID Parameter for Update Test Case**
**Given** a test case update request with issues to add
**When** I specify `integration_id` or `integration_name` parameter
**Then** the tool uses the specified integration for the new issue links

**AC #4: Mutually Exclusive Integration Parameters**
**Given** a request with both `integration_id` and `integration_name`
**When** the tool processes the request
**Then** it returns a validation error indicating mutual exclusivity

**AC #5: Integration Resolution by Name**
**Given** an `integration_name` parameter
**When** linking issues
**Then** the tool resolves the name to an ID (case-sensitive match)
**And** returns an error with available integrations if not found

**AC #6: Default to Single Integration**
**Given** a project with exactly one integration
**When** linking issues without specifying integration_id/name
**Then** the tool uses that integration automatically (current behavior)

**AC #7: Error When Multiple Integrations and No Selection**
**Given** a project with multiple integrations
**When** linking issues without specifying integration_id/name
**Then** the tool returns an error listing available integrations
**And** prompts the agent to specify which integration to use
**And** does NOT default to the first integration

**AC #8: Unit Tests**
**Given** the integration listing and filtering logic
**When** running unit tests
**Then** tests cover:
  - List integrations with mocked responses
  - Integration ID resolution by name
  - Validation of integration existence
  - Error handling for multiple integrations without selection
  - Mutual exclusivity of id/name parameters

**AC #9: Integration Tests**
**Given** the integration tools
**When** running integration tests
**Then** tests verify formatted output messages for listing

**AC #10: E2E Tests**
**Given** a sandbox Allure TestOps instance with integrations
**When** running E2E tests
**Then** tests cover:
  - List available integrations
  - Create test case with explicit integration_id
  - Update test case with issues using integration_name

**AC #11: Agentic Tool Tests Update**
**Given** the changes to issue linking and new `list_integrations` tool
**When** the implementation is complete
**Then** the agentic tool tests (`tests/agentic/agentic-tool-calls-tests.md`) are updated to:
  - Add `list_integrations` to the tool inventory
  - Add a new scenario step to discover integrations before linking issues
  - Update existing Issue Linking scenario (§9) to include integration selection
  - Add integration-related expectations to the coverage matrix

## Tasks / Subtasks

- [ ] Task 1: Implement list_integrations tool (AC: #1)
  - [ ] 1.1: Add `list_integrations()` method to `AllureClient` (extend existing)
  - [ ] 1.2: Create `list_integrations` tool in `src/tools/`
  - [ ] 1.3: Format output as LLM-friendly list (ID, name, type)

- [ ] Task 2: Add integration service layer (AC: #2, #3, #4, #5, #6, #7)
  - [ ] 2.1: Create `IntegrationService` class in `src/services/`
  - [ ] 2.2: Implement `get_integration_by_id()` method
  - [ ] 2.3: Implement `get_integration_by_name()` method
  - [ ] 2.4: Implement `resolve_integration()` method with mutual exclusivity check

- [ ] Task 3: Update TestCaseService issue linking (AC: #2, #3, #6, #7)
  - [ ] 3.1: Add `integration_id` and `integration_name` parameters to `_build_issue_dtos()`
  - [ ] 3.2: Change behavior: error when multiple integrations and no selection
  - [ ] 3.3: Integrate with new `IntegrationService.resolve_integration()` method

- [ ] Task 4: Update create_test_case tool (AC: #2, #4)
  - [ ] 4.1: Add `integration_id` parameter to tool signature
  - [ ] 4.2: Add `integration_name` parameter to tool signature
  - [ ] 4.3: Update tool docstring
  - [ ] 4.4: Pass parameters to service layer

- [ ] Task 5: Update update_test_case tool (AC: #3, #4)
  - [ ] 5.1: Add `integration_id` parameter to tool signature
  - [ ] 5.2: Add `integration_name` parameter to tool signature
  - [ ] 5.3: Update tool docstring
  - [ ] 5.4: Pass parameters to service layer

- [ ] Task 6: Tests (AC: #8, #9, #10)
  - [ ] 6.1: Unit tests for `IntegrationService` methods
  - [ ] 6.2: Unit tests for `_build_issue_dtos()` with integration resolution
  - [ ] 6.3: Update existing issue linking unit tests for new behavior
  - [ ] 6.4: Integration tests for `list_integrations` tool output
  - [ ] 6.5: E2E tests for integration discovery and issue linking

- [ ] Task 7: Update Agentic Tool Tests (AC: #11)
  - [ ] 7.1: Add `list_integrations` to tool inventory in `tests/agentic/agentic-tool-calls-tests.md`
  - [ ] 7.2: Create new scenario step for integration discovery before issue linking
  - [ ] 7.3: Update existing Issue Linking scenario (§9) to use `integration_id` or `integration_name`
  - [ ] 7.4: Update coverage matrix to reflect new tool

## Dev Notes

### API Endpoints

**Integration Controller (already in filtered OpenAPI):**
- `GET /api/integration` - List all integrations (paginated)
- `GET /api/integration/{id}` - Get integration by ID

**Existing Client Method:**
```python
# src/client/client.py:422-435
async def get_integrations(self) -> list[IntegrationDto]:
    """Fetch all integrations."""
    page = await self._integration_api.get_integrations(page=0, size=100)
    return page.content or []
```

### Current Warning Location

```python
# src/services/test_case_service.py:726-734
# Multiple integrations found
# We default to the first one but log a warning
target_integration_id = integrations[0].id
integration_names = [i.name for i in integrations if i.name]
logger.warning(
    f"Multiple integrations found ({', '.join(integration_names)}). "
    f"Defaulting to '{integrations[0].name}' for issue linking."
)
```

### IntegrationDto Model

```python
# src/client/generated/models/integration_dto.py
class IntegrationDto(BaseModel):
    created_date: Optional[StrictInt]
    id: Optional[StrictInt]
    info: Optional[IntegrationInfoDto]  # Contains type info
    last_modified_date: Optional[StrictInt]
    name: Optional[StrictStr]
    projects_count: Optional[StrictInt]
```

### Implementation Approach

1. **IntegrationService Pattern:**
   - Follow existing service patterns (TestLayerService, CustomFieldValueService)
   - Inject AllureClient, provide resolution methods
   - Cache integrations list for efficiency within request

2. **Tool Parameter Pattern:**
   - Follow test_layer_id/test_layer_name pattern from create_test_case
   - Mutually exclusive parameters with validation

3. **Breaking Change Handling:**
   - AC #7 changes default behavior from "pick first" to "error out"
   - This is a BREAKING CHANGE but improves reliability
   - Document in changelog

### Filter Script Already Includes Integration Controller

```python
# scripts/filter_openapi.py:38
"integration-controller",  # Already in KEEP_TAGS
```

No changes needed to OpenAPI filter or client regeneration.

### Project Structure Notes

- New file: `src/services/integration_service.py`
- New file: `src/tools/list_integrations.py`
- Modified: `src/services/test_case_service.py`
- Modified: `src/tools/create_test_case.py`
- Modified: `src/tools/update_test_case.py`
- New test files for unit/integration/e2e

### Testing Commands

```bash
# Unit + Integration tests
uv run --env-file .env.test pytest tests/unit/ tests/integration/

# E2E tests (requires sandbox instance)
uv run --env-file .env.test pytest tests/e2e/

# Packaging tests
uv run pytest tests/packaging/
```

### References

**Related Stories:**
- Story 3.12: Issue Links (original implementation)
- Story 3.7: Test Layers (pattern for ID/name parameters)

**Related Files:**
- [test_case_service.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/test_case_service.py) - Issue linking logic
- [client.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/client.py) - get_integrations() method
- [filter_openapi.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/scripts/filter_openapi.py) - OpenAPI filter config
- [integration_dto.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/client/generated/models/integration_dto.py) - Integration model
- [agentic-tool-calls-tests.md](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/tests/agentic/agentic-tool-calls-tests.md) - Agentic tests to update

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
