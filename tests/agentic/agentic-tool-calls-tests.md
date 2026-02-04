# Manual MCP tool-call validation (full tool coverage, stdio + HTTP)

## Goal
Validate **manual tool calls for every MCP tool** using scenarios derived from `tests/e2e`. All checks are manual (no pytest runs in scope).

## Inputs (confirmed)
- MCP is installed and running with the name 'testops-mcp'.
- Validate only transport that is available for installed MCP server.
- Manual tool calls only; automated E2E tests are out of scope.

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
- `create_launch`, `list_launches`
- `create_shared_step`, `list_shared_steps`, `update_shared_step`, `delete_shared_step`
- `link_shared_step`, `unlink_shared_step`
- `list_test_layers`, `create_test_layer`, `update_test_layer`, `delete_test_layer`
- `list_test_layer_schemas`, `create_test_layer_schema`, `update_test_layer_schema`, `delete_test_layer_schema`

## Execution plan

### 1) Manual tool-call checklist — derived from E2E scenarios
> The steps below translate E2E tests to **manual tool calls**. Record IDs and outputs.
> **Sub-agent guidance:** spawn sub-agents when it does not interrupt the test flow. Each scenario should use a sub-agent, 
> and parallel updates of different fields shoud use a sub-agent per update. 
> Any **update → read/verify** sequence must run **sequentially** (no parallelization). 
> Deletion calls MUST be run in parallel.
> Strictly execute all calls, and verify the expected output explicitly. Document any deviation from the expected result in the report.

#### A. Test case core CRUD + output formatting
- **Scenario sources**: `test_tool_outputs.py:14-92`, `test_case_crud.py:20-83`, `test_delete_test_case.py:8-44`
- Calls:
  1. `create_test_case` with `name`, `description`, `steps=[{"action":"Step 1","expected":"Result 1"}]`.
     - Expect: `Created Test Case ID: <id> Name: <name>` (`create_test_case.py:83-95`).
  2. `get_test_case_details(TEST_CASE_ID)` → expect formatted details, including steps and tags if present (`search.py:162-235`).
  3. `update_test_case(TEST_CASE_ID, description="Updated description")`.
     - Expect: `Test Case <id> updated successfully. Changes: description` (`update_test_case.py:96-150`).
  4. `delete_test_case(TEST_CASE_ID, confirm=False)` → expect confirmation prompt (`delete_test_case.py:36-41`).
  5. `delete_test_case(TEST_CASE_ID, confirm=True)` → expect archived message (`delete_test_case.py:50-53`).
  6. Call delete again (idempotent) → expect “already archived” message (`delete_test_case.py:50-52`).

#### B. Test case update scenarios (fields, tags, steps, attachments, links)
- **Scenario sources**: `test_update_test_case.py:8-108`, `test_update_test_case_extended.py:109-266`
- Calls:
  - **Core fields**: `update_test_case` with `name`, `description`, `precondition`, `expected_result`.
  - **Tags**: set `tags=["tag1","tag2"]`, then `tags=[]` to clear.
  - **Steps**: `steps=[{"action":"New Step 1","expected":"Result 1"}, {"action":"New Step 2"}]`.
  - **Nested steps**: `steps=[{"action":"Parent","steps":[{"action":"Child 1"},{"action":"Child 2","steps":[{"action":"Grandchild"}]}]}]`.
  - **Global attachments**: `attachments=[{"name":"a1.png","content":pixel_b64,"content_type":"image/png"}]`.
  - **Links**: `links=[{"name":"JIRA-123","url":"https://jira.example.com/JIRA-123","type":"issue"}]`.
  - **Custom fields**: `custom_fields={"<FieldName>":"<AllowedValue>"}` (use `get_custom_fields` first).
  - **Test layer**: `test_layer_id=<ID>` (use `list_test_layers` first).
  - **Automated flag**: `automated=true` or `false`.
- Verify changes via `get_test_case_details` and `list_test_cases` output where possible.

#### C. List & search test cases
- **Scenario sources**: `test_list_test_cases.py:8-70`, `test_search_test_cases.py:8-170`, `test_search_test_cases_aql.py:12-88`
- Calls:
  - `list_test_cases(page=0,size=1)` → expect “Found … (page 1 of …)” + `status` + `tags` (`search.py:192-207`).
  - `list_test_cases(name_filter="login", tags=["smoke"], status="Draft")` → expect valid output (even if empty).
  - `search_test_cases(query="login")` → expect “Found …” or “No test cases found” with tags.
  - `search_test_cases(query="tag:smoke tag:regression")` → same pattern.
  - `search_test_cases(aql='name ~= "test"')` → expect valid output.
  - `search_test_cases(aql='name ~= "login" or name ~= "test"')` → expect valid output.
  - **Invalid AQL**: `search_test_cases(aql="this is not valid aql %%% syntax")` → expect validation error.
  - **No query**: `search_test_cases()` → expect validation error (`search.py:133-147`).

#### D. Custom fields discovery + validation errors
- **Scenario sources**: `test_get_custom_fields.py:15-235`, `test_custom_field_validation_e2e.py:15-196`
- Calls:
  1. `get_custom_fields()` → list fields with required/allowed values.
  2. `get_custom_fields(name="<partial>")` → filtered list or “No custom fields found”.
  3. **Invalid field names**: `create_test_case(name="Invalid CF", custom_fields={"MissingField1":"Value1","MissingField2":"Value2"})` → expect aggregated missing-field error.
  4. **Invalid values**: use `get_custom_fields` to find fields with allowed values, then call `create_test_case` with invalid values → expect error mentioning allowed values.
  5. **Mixed missing + invalid**: include both missing field names and invalid values in one call; expect aggregated guidance.
  6. `get_test_case_custom_fields(TEST_CASE_ID)` → verify set custom fields (or “none”).

#### E. Shared steps lifecycle + link/unlink
- **Scenario sources**: `test_shared_steps.py:14-210`, `test_link_shared_step.py:13-108`, `test_link_shared_steps.py:12-86`
- Calls:
  1. `create_shared_step(name, steps=[{"action":"Do something","expected":"Something happens"}])` → capture `SHARED_STEP_ID`.
  2. `list_shared_steps(search=<name>)` → verify `[ID: SHARED_STEP_ID]` appears.
  3. `update_shared_step(step_id=SHARED_STEP_ID, name="Updated Name")` → expect updated message.
  4. `update_shared_step(step_id=SHARED_STEP_ID, name="Updated Name")` again → expect “No changes needed”.
  5. `delete_shared_step(step_id=SHARED_STEP_ID, confirm=False)` → expect confirmation warning.
  6. `delete_shared_step(step_id=SHARED_STEP_ID, confirm=True)` → expect archived confirmation.
  7. **Attachment**: create a shared step with `steps=[{"action":"Check image","attachments":[{"name":"pixel.png","content":pixel_b64}]}]`.
  8. **Link/unlink**:
     - Create a test case → `TEST_CASE_ID`.
     - `link_shared_step(test_case_id=TEST_CASE_ID, shared_step_id=SHARED_STEP_ID)` → expect success and updated steps preview.
     - `unlink_shared_step(test_case_id=TEST_CASE_ID, shared_step_id=SHARED_STEP_ID)` → expect remaining steps preview without shared step.

#### F. Test layers + schemas
- **Scenario source**: `test_test_layer_crud.py:20-352`
- Calls:
  1. `list_test_layers()` → expect list or “No test layers found”.
  2. `create_test_layer(name="E2E-Tool-Layer")` → capture `LAYER_ID`.
  3. `update_test_layer(layer_id=LAYER_ID, name="E2E-Tool-Layer-Updated")` → expect updated or info message.
  4. `delete_test_layer(layer_id=LAYER_ID)` → expect deletion message; call again for idempotent check.
  5. `create_test_layer_schema(key="e2e_schema", test_layer_id=<LAYER_ID>, project_id=<PROJECT_ID>)` → capture `SCHEMA_ID`.
  6. `list_test_layer_schemas(project_id=<PROJECT_ID>)` → expect `SCHEMA_ID` present.
  7. `update_test_layer_schema(schema_id=SCHEMA_ID, key="e2e_schema_updated")` → expect updated or info message.
  8. `delete_test_layer_schema(schema_id=SCHEMA_ID)` → expect deletion message; call again for idempotent check.
  9. **Multiple schemas**: create two layers + two schemas, list to confirm both, then delete both schemas and layers.

#### G. Launches
- **Scenario source**: tool coverage (no E2E file)
- Calls:
  1. `create_launch(name="[manual-...] Launch", tags=["manual"], external=false)` → capture `LAUNCH_ID`.
  2. `list_launches(search="[manual-...]")` → verify launch appears.

## Report
- After all checks are complete, produce a final test report.
- The report must list **every performed check** with a strict result: **Pass / Fail / Skipped**.
- For each check include the key output (message text or IDs) that justifies the result.
- Explicitly call out any deviations from expected output and link them to the failing check.
- Show the report to the user **after all checks** are finished.
- List all failed checks at the end of the report.

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
- **Test cases**: A–E cover `create_test_case`, `get_test_case_details`, `update_test_case`, `delete_test_case`, `list_test_cases`, `search_test_cases`, `get_test_case_custom_fields`.
- **Custom fields**: E covers `get_custom_fields`.
- **Shared steps**: F covers `create_shared_step`, `list_shared_steps`, `update_shared_step`, `delete_shared_step`, `link_shared_step`, `unlink_shared_step`.
- **Test layers**: G covers `list_test_layers`, `create_test_layer`, `update_test_layer`, `delete_test_layer`, `list_test_layer_schemas`, `create_test_layer_schema`, `update_test_layer_schema`, `delete_test_layer_schema`.
- **Launches**: H covers `create_launch`, `list_launches`.

## Notes / constraints
- Some E2E checks use service-level assertions (scenario DTOs). Manual validation relies on tool outputs + `get_test_case_details` as the closest proxy.
- No repo code changes required; this is a runtime validation plan only.
