# Manual MCP tool-call validation (full tool coverage, stdio + HTTP)

## Goal
Validate **manual tool calls for every MCP tool** using scenarios derived from `tests/e2e`. All checks are manual (no pytest runs in scope).

## Inputs (confirmed)
- MCP is installed and running with the name 'testops-mcp'.
- Validate only transport that is available for installed MCP server.
- Manual tool calls only; automated E2E tests are out of scope.

## Agentic Execution Protocol
To ensure robust end-to-end validation, any AI agent executing this plan MUST follow these rules:

1.  **Strict QA Persona**: Adopt a persona of a meticulous QA Engineer. Do not assume success; verify it explicitly.
2.  **Explicit Verification**: After every "Write" operation (create/update/delete), you MUST perform a "Read" operation (list/get) to verify the state change, even if the tool reports success.
3.  **Data Isolation**: Use unique identifiers for test data (e.g., prefixes like `[Agent-QA]`) to avoid collisions with production or other test data.
4.  **State Management**: Capture IDs returned by tools into variables (e.g., `TC_ID`, `LAUNCH_ID`) and reuse them in subsequent steps.
5.  **Output Parsing**: Compare actual tool outputs against the "Expectation" strings provided in scenarios. Report any semantic or structural deviations.
6.  **Cleanup**: You are responsible for cleaning up all created entities (tests, layers, shared steps, launches) at the end of the session, even if some steps fail.
7.  **Deterministic Reports**: Produce a final markdown table summarizing Pass/Fail status for every scenario.
8.  **Transparency & Suspicion**: You MUST explicitly record and report all tool failures, retry attempts, and "suspicions" (behavior that is technically successful but appears inconsistent or unusual). Do not hide troubleshooting steps; document them as learning points for the server's robustness.

## References (repo)
- Tool registry (canonical list): `src/tools/__init__.py:3-79`
- Server entry & transports: `src/main.py:81-90`
- E2E scenarios (manual equivalents below):
  - MCP lifecycle: `tests/e2e/test_mcp_server_lifecycle.py:112-166`
  - Tool output formats: `tests/e2e/test_tool_outputs.py:14-92`
  - Test case CRUD/updates: `tests/e2e/test_case_crud.py:20-136`, `tests/e2e/test_update_test_case.py:8-108`, `tests/e2e/test_update_test_case_extended.py:8-267`, `tests/e2e/test_delete_test_case.py:8-44`
  - List/search: `tests/e2e/test_list_test_cases.py:8-70`, `tests/e2e/test_search_test_cases.py:8-170`, `tests/e2e/test_search_test_cases_aql.py:12-88`
  - Custom fields: `tests/e2e/test_get_custom_fields.py:15-235`, `tests/e2e/test_custom_field_validation_e2e.py:15-196`
  - Shared steps + link/unlink: `tests/e2e/test_shared_steps.py:14-210`, `tests/e2e/test_link_shared_step.py:13-108`, `tests/e2e/test_link_shared_steps.py:12-86`
  - Test layers + schemas: `tests/e2e/test_test_layer_crud.py:20-352`
  - Auth override (optional negatives): `tests/e2e/test_runtime_auth_override.py:12-83`
- Tool outputs (source of expected strings):
  - `create_test_case`: `src/tools/create_test_case.py:83-95`
  - `update_test_case`: `src/tools/update_test_case.py:96-150`
  - `delete_test_case`: `src/tools/delete_test_case.py:36-53`
  - `search/list/details`: `src/tools/search.py:9-251`
  - `get_custom_fields`: `src/tools/get_custom_fields.py:9-49`
  - `get_test_case_custom_fields`: `src/tools/get_test_case_custom_fields.py:9-34`
  - `shared_steps` tools: `src/tools/shared_steps.py:9-170`
  - `link/unlink`: `src/tools/link_shared_step.py:38-93`, `src/tools/unlink_shared_step.py:29-68`
  - `test_layers` tools: `src/tools/create_test_layer.py:11-33`, `src/tools/list_test_layers.py:11-38`, `src/tools/update_test_layer.py:11-33`, `src/tools/delete_test_layer.py:11-31`
  - `test_layer_schema` tools: `src/tools/create_test_layer_schema.py:11-39`, `src/tools/list_test_layer_schemas.py:11-43`, `src/tools/update_test_layer_schema.py:11-40`, `src/tools/delete_test_layer_schema.py:11-31`
  - `launches`: `src/tools/launches.py:11-112`

## Reusable test data & conventions (for future reuse)
- **Run prefix**: use a unique prefix like `[manual-<date>-<rand>]` in names to avoid collisions.
- **Attachment payload** (1x1 pixel, from `tests/e2e/conftest.py:88-90`):
  - `pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgANjd8qAAAAAElFTkSuQmCC"`
- **Track IDs** as you go: `TEST_CASE_ID`, `SHARED_STEP_ID`, `LAYER_ID`, `SCHEMA_ID`, `LAUNCH_ID`.
- **Cleanup policy**: use delete tools for cases/steps/layers/schemas. Launches have no delete tool; use a unique name and clean in UI if needed.

## Tool inventory (must be covered)
From `src/tools/__init__.py:24-79`:
- `create_test_case`, `get_test_case_details`, `update_test_case`, `delete_test_case`, `list_test_cases`, `search_test_cases`
- `get_custom_fields`, `get_test_case_custom_fields`
- `create_custom_field_value`, `list_custom_field_values`, `update_custom_field_value`, `delete_custom_field_value`
- `create_launch`, `list_launches`, `get_launch`
- `create_shared_step`, `list_shared_steps`, `update_shared_step`, `delete_shared_step`
- `link_shared_step`, `unlink_shared_step`
- `list_test_layers`, `create_test_layer`, `update_test_layer`, `delete_test_layer`
- `list_test_layer_schemas`, `create_test_layer_schema`, `update_test_layer_schema`, `delete_test_layer_schema`
- `list_integrations`

## Execution plan

### 1) Manual tool-call checklist — derived from E2E scenarios
> The steps below translate E2E tests to **manual tool calls**. Record IDs and outputs.
> **Sub-agent guidance:** spawn sub-agents when it does not interrupt the test flow. Each scenario should use a sub-agent, 
> and parallel updates of different fields shoud use a sub-agent per update. 
> Any **update → read/verify** sequence must run **sequentially** (no parallelization). 
> Deletion calls MUST be run in parallel.
> Strictly execute all calls, and verify the expected output explicitly. Document any deviation from the expected result in the report.

#### 1. Test case core CRUD + output formatting
- **Goal**: Verify basic test case lifecycle and response formatting.
- **Steps**:
  1. **Create**: `create_test_case(name="[Agent] Core CRUD", description="Initial description", steps=[{"action":"Step 1","expected":"Result 1"}])`
     - Expectation: Output contains `"Created Test Case ID"`.
     - Action: Capture `id` as `TC_CORE_ID`.
  2. **Read Details**: `get_test_case_details(test_case_id=TC_CORE_ID)`
     - Expectation: Output contains `"Step 1"` and `"Result 1"`.
  3. **Update Description**: `update_test_case(test_case_id=TC_CORE_ID, description="Updated via tool")`
     - Expectation: Output contains `"Changes: description"`.
  4. **Verify Update**: `get_test_case_details(test_case_id=TC_CORE_ID)`
     - Expectation: Description is `"Updated via tool"`.
  5. **Delete (No Confirm)**: `delete_test_case(test_case_id=TC_CORE_ID, confirm=false)`
     - Expectation: Output contains a confirmation prompt or warning.
  6. **Delete (Confirm)**: `delete_test_case(test_case_id=TC_CORE_ID, confirm=true)`
     - Expectation: Output contains `"successfully archived"`.
  7. **Delete (Idempotent)**: `delete_test_case(test_case_id=TC_CORE_ID, confirm=true)`
     - Expectation: Output contains `"already archived"`.

#### 2. Test case update scenarios (fields, tags, steps, attachments, links)
- **Goal**: Verify bulk and nested updates across various fields.
- **Prerequisite**: Create a test case and capture as `TC_UPDATE_ID`.
- **Steps**:
  1. **Core Fields**: `update_test_case(test_case_id=TC_UPDATE_ID, name="[Agent] Renamed", precondition="Pre-data", expected_result="Final data", confirm=true)`
     - Expectation: Changes reported for `name`, `precondition`, `expected_result`.
  2. **Tags**: `update_test_case(test_case_id=TC_UPDATE_ID, tags=["agent-qa", "smoke"], confirm=true)`
     - Expectation: Changes reported for `tags`.
  3. **Nested Steps**: `update_test_case(test_case_id=TC_UPDATE_ID, steps=[{"action":"Parent","steps":[{"action":"Child"}]}], confirm=true)`
     - Expectation: Steps updated successfully.
  4. **Attachment**: `update_test_case(test_case_id=TC_UPDATE_ID, attachments=[{"name":"pixel.png","content":pixel_b64,"content_type":"image/png"}], confirm=true)`
     - Expectation: Attachment reported in changes.
  5. **Custom Fields**: Use `get_custom_fields` to find a valid field/value, then: `update_test_case(test_case_id=TC_UPDATE_ID, custom_fields={"Priority":"High"}, confirm=true)`
     - Expectation: Custom field update confirmed.
  6. **Automated Flag**: `update_test_case(test_case_id=TC_UPDATE_ID, automated=true, confirm=true)`
     - Expectation: `automated` updated.
  7. **Verify All**: `get_test_case_details(test_case_id=TC_UPDATE_ID)`
     - Expectation: Inspect output to ensure all above fields match.

#### 3. List & search test cases
- **Goal**: Verify discovery and filtering logic.
- **Steps**:
  1. **List Pagination**: `list_test_cases(page=0, size=5)`
     - Expectation: Output contains `"Found X test cases (page 1 of Y)"`.
  2. **Search Name**: `search_test_cases(query="[Agent]")`
     - Expectation: List contains test cases created in prior steps.
  3. **Search Tag**: `search_test_cases(query="tag:agent-qa")`
     - Expectation: List contains test cases with that tag.
  4. **AQL Search**: `search_test_cases(aql='status="Draft" and automated=true')`
     - Expectation: Returns filtered list.
  5. **Invalid AQL**: `search_test_cases(aql="not valid syntax!!!")`
     - Expectation: Output contains a clear syntax error message.
  6. **Empty Query**: `search_test_cases(query="")`
     - Expectation: Output contains validation error for empty search.

#### 4. Custom fields discovery + validation errors
- **Goal**: Verify custom field enumeration and error aggregation.
- **Steps**:
  1. **Enumerate All**: `get_custom_fields()`
     - Expectation: Returns bulleted list of all project custom fields with allowed values.
  2. **Filter Fields**: `get_custom_fields(name="Prior")`
     - Expectation: Returns only fields matching the string.
  3. **Invalid Field Error**: `create_test_case(name="Invalid CF TC", custom_fields={"NonExistentField":"SomeValue"})`
     - Expectation: Error message lists `"NonExistentField"` and suggests existing fields.
  4. **Invalid Value Error**: `create_test_case(name="Invalid Val TC", custom_fields={"Priority":"Extra-High"})`
     - Expectation: Error message lists `"Extra-High"` as invalid and shows allowed values.
  5. **Mixed Error**: Call `create_test_case` with one invalid field AND one valid field with an invalid value.
     - Expectation: Error output aggregates BOTH issues.

#### 5. Shared steps lifecycle + link/unlink
- **Goal**: Verify shared steps management and their association with test cases.
- **Steps**:
  1. **Create Shared**: `create_shared_step(name="[Agent] Shared Auth", steps=[{"action":"Login","expected":"Dashboard"}])`
     - Expectation: Output contains `"Created Shared Step ID"`.
     - Action: Capture `id` as `SS_ID`.
  2. **Verify Shared**: `list_shared_steps(search="[Agent]")`
     - Expectation: List contains `SS_ID`.
  3. **Update Shared**: `update_shared_step(step_id=SS_ID, name="[Agent] Shared Auth Updated", confirm=true)`
     - Expectation: Confirmation of name change.
  4. **Link to TC**: `link_shared_step(test_case_id=TC_CORE_ID, shared_step_id=SS_ID, confirm=true)`
     - Expectation: Success message with updated steps preview.
  5. **Verify Link**: `get_test_case_details(test_case_id=TC_CORE_ID)`
     - Expectation: Details show the shared step reference.
  6. **Unlink**: `unlink_shared_step(test_case_id=TC_CORE_ID, shared_step_id=SS_ID, confirm=true)`
     - Expectation: Confirmation of removal.
  7. **Delete Shared**: `delete_shared_step(step_id=SS_ID, confirm=true)`
     - Expectation: Success message.

#### 6. Test layers + schemas
- **Goal**: Verify taxonomy management via layers and custom field mapping.
- **Steps**:
  1. **List Initial**: `list_test_layers()`
     - Expectation: List of layers provided.
  2. **Create Layer**: `create_test_layer(name="[Agent] Layer")`
     - Expectation: Confirmation message with ID.
     - Action: Capture `id` as `LAYER_ID`.
  3. **Update Layer**: `update_test_layer(layer_id=LAYER_ID, name="[Agent] Layer Renamed", confirm=true)`
     - Expectation: Confirmation of update.
  4. **Create Schema**: `create_test_layer_schema(key="agent_key", test_layer_id=LAYER_ID, project_id=<PROJECT_ID>)`
     - Expectation: Confirmation message with ID.
     - Action: Capture `id` as `SCHEMA_ID`.
  5. **Verify Schema**: `list_test_layer_schemas(project_id=<PROJECT_ID>)`
     - Expectation: List contains `SCHEMA_ID` mapping to `LAYER_ID`.
  6. **Delete Schema**: `delete_test_layer_schema(schema_id=SCHEMA_ID, confirm=true)`
     - Expectation: Success message.
  7. **Delete Layer**: `delete_test_layer(layer_id=LAYER_ID, confirm=true)`
     - Expectation: Success message.

#### 7. Launches
- **Scenario source**: tool coverage
- **Goal**: Validate launch creation, listing, and detail retrieval.
- **Steps**:
  1. **Create**: `create_launch(name="[Agent] Launch", tags=["agent-test"], external=false)`
     - Expectation: Output contains `Created Launch ID`.
     - Action: Capture `id` as `LAUNCH_ID`.
  2. **List**: `list_launches(search="[Agent]")`
     - Expectation: List contains launch with `id: LAUNCH_ID` and `name: "[Agent] Launch"`.
  3. **Get Details**: `get_launch(launch_id=LAUNCH_ID)`
     - Expectation: Output contains strict keys: `id`, `name`, `status`, `created_date`.
     - Verification: `id` matches `LAUNCH_ID`.

#### 8. Custom Field Values Lifecycle
- **Scenario source**: `specs/implementation-artifacts/3-11-crud-custom-field-values.md`
- **Goal**: Verify project-level custom field value management.
- **Prerequisite**: Use `get_custom_fields` to find a valid `CF_ID` (or create a temporary custom field if none exist).
- **Steps**:
  1. **List Initial**: `list_custom_field_values(project_id=<PROJECT_ID>, custom_field_id=<CF_ID>)`
     - Expectation: Returns a list (empty or populated).
  2. **Create**: `create_custom_field_value(project_id=<PROJECT_ID>, custom_field_id=<CF_ID>, name="[Agent] Value")`
     - Expectation: Output contains `"Created Custom Field Value"`.
     - Action: Capture `id` as `VALUE_ID`.
  3. **Verify Creation**: `list_custom_field_values(project_id=<PROJECT_ID>, custom_field_id=<CF_ID>)`
     - Expectation: List contains an item with `id: VALUE_ID` and `name: "[Agent] Value"`.
  4. **Update**: `update_custom_field_value(cfv_id=VALUE_ID, name="[Agent] Value Updated", confirm=true)`
     - Expectation: Output contains `"updated successfully"`.
  5. **Verify Update**: `list_custom_field_values(project_id=<PROJECT_ID>, custom_field_id=<CF_ID>)`
     - Expectation: List item with `id: VALUE_ID` has `name: "[Agent] Value Updated"`.
  6. **Delete**: `delete_custom_field_value(project_id=<PROJECT_ID>, cfv_id=VALUE_ID, confirm=true)`
     - Expectation: Output contains `"deleted successfully"`.
  7. **Verify Deletion**: `list_custom_field_values(project_id=<PROJECT_ID>, custom_field_id=<CF_ID>)`
     - Expectation: List DOES NOT contain `id: VALUE_ID`.

#### 9. Issue Linking
- **Scenario source**: `specs/implementation-artifacts/3-12-support-issue-links-in-test-cases.md`, `specs/implementation-artifacts/3-13-integration-filtering-for-issue-links.md`
- **Goal**: Verify adding, removing, clearing, and validating issue links with integration filtering.
- **Steps**:
  1. **Discover Integrations**: `list_integrations()`
     - Expectation: List of available integrations with `id` and `name`.
     - Action: Capture a valid `id` as `INT_ID` or `name` as `INT_NAME`.
  2. **Create with Issue**: `create_test_case(name="[Agent] TC with Issue", issues=["PROJ-123"], integration_id=INT_ID)`
     - Expectation: Output contains `"Linked 1 issues"`.
     - Action: Capture `id` as `TC_ISSUE_ID`.
  3. **Verify Link**: `get_test_case_details(test_case_id=TC_ISSUE_ID)`
     - Expectation: `issues` list contains `PROJ-123`.
  4. **Add Issue (by name)**: `update_test_case(test_case_id=TC_ISSUE_ID, issues=["PROJ-456"], integration_name=INT_NAME, confirm=true)`
     - Expectation: Output contains `"Added 1 issues"`.
  4. **Verify Addition**: `get_test_case_details(test_case_id=TC_ISSUE_ID)`
     - Expectation: `issues` list contains BOTH `PROJ-123` and `PROJ-456`.
  5. **Remove Issue**: `update_test_case(test_case_id=TC_ISSUE_ID, remove_issues=["PROJ-123"], confirm=true)`
     - Expectation: Output contains `"Removed 1 issues"`.
  6. **Verify Removal**: `get_test_case_details(test_case_id=TC_ISSUE_ID)`
     - Expectation: `issues` list contains `PROJ-456` but NOT `PROJ-123`.
  7. **Clear Issues**: `update_test_case(test_case_id=TC_ISSUE_ID, clear_issues=True, confirm=true)`
     - Expectation: Output contains `"Cleared all issues"`.
  8. **Verify Clear**: `get_test_case_details(test_case_id=TC_ISSUE_ID)`
     - Expectation: `issues` list is empty.
  9. **Negative Test**: `create_test_case(name="Invalid Issue", issues=["INVALID_FORMAT"])`
     - Expectation: Error message containing `"Invalid issue key format"`.

#### 10. Test Plan Management
- **Scenario source**: `specs/implementation-artifacts/7-1-test-plan-management.md`
- **Goal**: Verify Test Plan lifecycle (creation, update, content management, listing).
- **Steps**:
  1. **Create Manual Plan**: `create_test_plan(name="[Agent] Manual Plan", test_case_ids=[TC_CORE_ID])`
     - Expectation: Output contains `"Created Test Plan <PLAN_ID>: '[Agent] Manual Plan'"`.
     - Action: Capture `id` as `MANUAL_PLAN_ID`.
  2. **Verify Creation**: `list_test_plans(page=0, size=10)`
     - Expectation: List contains `[<MANUAL_PLAN_ID>] [Agent] Manual Plan`.
  3. **Create AQL Plan**: `create_test_plan(name="[Agent] AQL Plan", aql_filter="tag:smoke")`
     - Expectation: Output contains `"Created Test Plan <AQL_PLAN_ID>: '[Agent] AQL Plan'"`.
     - Action: Capture `id` as `AQL_PLAN_ID`.
  4. **Update Plan Metadata**: `update_test_plan(plan_id=MANUAL_PLAN_ID, name="[Agent] Manual Plan Renamed")`
     - Expectation: Output contains `"Updated Test Plan <MANUAL_PLAN_ID>: '[Agent] Manual Plan Renamed'"`.
  5. **Manage Content (Add)**: `manage_test_plan_content(plan_id=MANUAL_PLAN_ID, add_test_case_ids=[TC_UPDATE_ID])`
     - Expectation: Output contains `"Updated content for Test Plan <MANUAL_PLAN_ID>"`.
  6. **Manage Content (Remove)**: `manage_test_plan_content(plan_id=MANUAL_PLAN_ID, remove_test_case_ids=[TC_CORE_ID])`
     - Expectation: Output contains `"Updated content for Test Plan <MANUAL_PLAN_ID>"`.
  7. **Update AQL Filter**: `manage_test_plan_content(plan_id=AQL_PLAN_ID, update_aql_filter="tag:regression")`
     - Expectation: Output contains `"Updated content for Test Plan <AQL_PLAN_ID>"`.
  8. **List Plans**: `list_test_plans()`
     - Expectation: Output lists both plans with updated names and potentially updated case counts.

## Report
- After all checks are complete, produce a final test report.
- The report must list **every performed check** with a strict result: **Pass / Fail / Skipped**.
- **Failures & Retries**: Every tool failure MUST be logged with the exact error message. If you attempted a retry (e.g., corrected AQL syntax), document the initial failure and the successful retry explicitly.
- **Suspicions**: Document any behavior that was successful but suspicious (e.g., a "negative test" that should have failed but passed due to loose pattern matching).
- For each check include the key output (message text or IDs) that justifies the result.
- Explicitly call out any deviations from expected output and link them to the failing check.
- Show the report to the user **after all checks** are finished.
- List all failed checks and unresolved suspicions at the end of the report.

## Cleanup
- Delete all test entities created during the test run. This is mandatory. Spawn sub-agents to make the process faster.

## Verification / Expected outputs
- `create_test_case` → `Created Test Case ID: <id> Name: <name>`.
- `update_test_case` → `Test Case <id> updated successfully. Changes: ...`.
- `delete_test_case` without confirm → warning text; with confirm → archived message; repeated delete → “already archived” message.
- `list_test_cases` → “Found <n> test cases (page ...)” with `status:` and `tags:`.
- `search_test_cases` → “Found … matching ...” or “No test cases found matching ...”.
- `get_custom_fields` → “Found <n> custom fields:” + bullet list (or not-found message).
- `get_test_case_custom_fields` → “Custom Fields for Test Case …” or “no custom field values set.”
- Shared steps: create/list/update/delete messages as in `shared_steps.py`.
- Link/unlink: confirmation plus updated steps preview (`link_shared_step.py:91-93`, `unlink_shared_step.py:65-68`).
- Test layers/schemas: success or info messages as defined in tool files.
- Launches: formatted list with pagination (`launches.py:91-112`).

## Coverage matrix (tool → scenario module)
- **Test cases**: 1-3 cover `create_test_case`, `get_test_case_details`, `update_test_case`, `delete_test_case`, `list_test_cases`, `search_test_cases`, `get_test_case_custom_fields`.
- **Custom fields**: 4 covers `get_custom_fields`.
- **Shared steps**: 5 covers `create_shared_step`, `list_shared_steps`, `update_shared_step`, `delete_shared_step`, `link_shared_step`, `unlink_shared_step`.
- **Test layers**: 6 covers `list_test_layers`, `create_test_layer`, `update_test_layer`, `delete_test_layer`, `list_test_layer_schemas`, `create_test_layer_schema`, `update_test_layer_schema`, `delete_test_layer_schema`.
- **Launches**: 7 covers `create_launch`, `list_launches`, `get_launch`.
- **Custom Field Values**: 8 covers `create_custom_field_value`, `list_custom_field_values`, `update_custom_field_value`, `delete_custom_field_value`.
- **Issue Linking & Integrations**: 9 covers `list_integrations` and `issues` parameter in `create_test_case` and `update_test_case` (add, remove, clear, explicit integration selection).
- **Test Plans**: 10 covers `create_test_plan`, `update_test_plan`, `manage_test_plan_content`, `list_test_plans`.

## Notes / constraints
- Some E2E checks use service-level assertions (scenario DTOs). Manual validation relies on tool outputs + `get_test_case_details` as the closest proxy.
- No repo code changes required; this is a runtime validation plan only.
