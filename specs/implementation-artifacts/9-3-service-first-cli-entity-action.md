# Story 9.3: Service-First CLI Entity/Action Command Model

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer or QA Engineer,
I want the CLI to use `lucius <entity> <action>` commands wired directly to existing service methods,
so that CLI usage is more intuitive and no longer depends on FastMCP runtime wiring.

## Acceptance Criteria

1. **New command grammar**
   - **Given** the CLI entry point `lucius`
   - **When** I invoke a command
   - **Then** command structure is `lucius <testops_entity_type> <action> [--args <json>] [--format json|table|plain]`
   - **And** `lucius call <tool_name>` is removed from primary UX.

2. **Entity discovery**
   - **Given** a valid entity
   - **When** I run `lucius <entity>`
   - **Then** CLI prints all supported actions for that entity
   - **And** each action line includes a short description.

3. **Action help**
   - **Given** any valid `lucius <entity> <action>`
   - **When** I run `--help`
   - **Then** CLI prints:
     - action description
     - parameter names and types
     - required vs optional
     - at least one usage example.

4. **Service-first execution (no FastMCP in CLI path)**
   - **Given** any `lucius <entity> <action>` command
   - **When** it executes
   - **Then** it is routed to an existing service method (via existing tool behavior contract)
   - **And** CLI execution path does not import `src.main` or `fastmcp`.

5. **Behavior parity**
   - **Given** a command mapped from an existing tool
   - **When** invoked with equivalent parameters
   - **Then** output semantics match current tool behavior:
     - success message shape
     - validation/confirmation behavior
     - idempotency semantics
     - user-facing error hints.

6. **No new tools, no new business layer**
   - **Given** this story scope
   - **Then** no new TestOps tools are introduced
   - **And** no new domain/service abstraction layer is introduced
   - **And** CLI remains a thin adapter over existing service methods and response formatting.

7. **Output formats preserved**
   - **Given** `--format json|table|plain`
   - **When** used on any action command
   - **Then** output is rendered consistently with existing CLI formatter behavior
   - **And** `json` remains default.

8. **Dependency boundary**
   - **Given** CLI module and CLI binary
   - **Then** FastMCP is not a runtime dependency for CLI command execution
   - **And** CLI schema/help generation does not require `mcp.list_tools()`.

9. **Route coverage**
   - **Given** current implemented tool/service capabilities
   - **Then** every supported `entity/action` route is explicitly mapped to existing service methods (see routing matrix below).

10. **Test coverage**
    - **Given** the revised CLI
    - **Then** tests cover:
      - parsing/routing for `entity/action`
      - entity-only action listing
      - help rendering
      - parity checks for representative CRUD/link/search/close/reopen commands
      - absence of FastMCP imports in CLI execution path
      - 100% canonical route representation (at least one automated test per canonical `entity/action`)
      - >=90% line coverage for `src/cli/`.

## Tasks / Subtasks

- [x] **Task 1: Replace command model in CLI entrypoint** (AC: 1, 2, 3)
  - [x] 1.1 Replace top-level `call` UX with `entity action` routing.
  - [x] 1.2 Add entity-only command behavior (`lucius <entity>` -> list actions).
  - [x] 1.3 Keep `--format` and `--args` behavior for action commands.

- [x] **Task 2: Implement static route table (thin CLI adapter)** (AC: 4, 5, 6, 9)
  - [x] 2.1 Define canonical entity/action keys and aliases in CLI module.
  - [x] 2.2 Map each route to existing service method invocation pattern.
  - [x] 2.3 Preserve current confirm-flag safety semantics for destructive operations.
  - [x] 2.4 Preserve current tool-style output messages for parity.

- [x] **Task 3: Remove FastMCP coupling from CLI path** (AC: 4, 8)
  - [x] 3.1 Remove lazy `from src.main import mcp` usage from CLI execution flow.
  - [x] 3.2 Ensure CLI help/list/schema generation no longer depends on FastMCP tool registry.
  - [x] 3.3 Keep server runtime (`src/main.py`) untouched for MCP mode.

- [x] **Task 4: Regenerate CLI metadata from tool/service source, not MCP runtime** (AC: 3, 8)
  - [x] 4.1 Update `scripts/build_tool_schema.py` to introspect existing tool functions/signatures directly.
  - [x] 4.2 Persist metadata needed for `entity`, `action`, description, params, and examples.
  - [x] 4.3 Validate metadata completeness against route table.

- [x] **Task 5: Help and discoverability UX** (AC: 2, 3)
  - [x] 5.1 `lucius` root help lists entities.
  - [x] 5.2 `lucius <entity>` prints actions with one-line descriptions.
  - [x] 5.3 `lucius <entity> <action> --help` prints description, parameters, and examples.

- [x] **Task 6: Tests** (AC: 5, 7, 10)
  - [x] 6.1 Update CLI unit tests for new grammar and routing.
  - [x] 6.2 Add parity tests for representative routes across entities.
  - [x] 6.3 Add guard test that CLI execution path does not import `fastmcp`/`src.main`.
  - [x] 6.4 Retain existing output format tests for json/table/plain.
  - [x] 6.5 Add route-matrix coverage test to assert every canonical `entity/action` is represented by at least one automated test.
  - [x] 6.6 Enforce CLI coverage gate (>=90% for `src/cli/`) in test/CI configuration.

- [x] **Task 7: Documentation updates** (AC: 1, 2, 3, 7)
  - [x] 7.1 Update README CLI examples to `entity/action`.
  - [x] 7.2 Update `docs/CLI.md` command reference and migration notes.
  - [x] 7.3 Document accepted entity aliases and canonical names.

### Review Follow-ups (AI)

- [x] [AI-Review][HIGH] Restore type/shape validation parity for CLI action calls (not only required/unknown keys); current validation does not enforce schema types and can pass invalid payloads to service/tool layer. [/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/src/cli/cli_entry.py:453]
- [x] [AI-Review][HIGH] Update CLI binary workflow steps still invoking legacy `list` syntax; current CI calls `lucius ... list --format json`, which is intentionally rejected by the new grammar and will break the pipeline. [/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/.github/workflows/cli-build.yml:220]
- [x] [AI-Review][MEDIUM] Enforce CLI coverage gate in CI/test commands (`--cov=src/cli`) instead of relying only on coverage config defaults; current configured test commands do not activate coverage measurement. [/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/.github/workflows/cli-build.yml:228]
- [x] [AI-Review][MEDIUM] Improve unknown-entity guidance by listing canonical entities too; current hint builder filters out underscore/dash tokens, hiding valid commands like `test_case` and `custom_field_value`. [/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/src/cli/cli_entry.py:253]
- [ ] [AI-Review][MEDIUM] Reconcile story File List with git reality; current working set includes modified `.gitignore` and `src/cli/__init__.py` that are not documented in this story's File List. [/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/specs/implementation-artifacts/9-3-service-first-cli-entity-action.md:346]

## Dev Notes

### Architecture Patterns and Constraints

- Keep **Thick Service -> Thin CLI**:
  - service layer keeps domain logic and API interactions
  - CLI only parses input, routes commands, validates args, and formats output.
- No new tool modules and no new business layer:
  - only rewire CLI routing and metadata extraction
  - reuse existing service classes and methods.
- Preserve current user-visible behavior from tool modules:
  - keep same confirmation semantics (`confirm=True` gates)
  - keep same error guidance style.
- CLI path must not depend on FastMCP internals.

### Canonical Command Shape

- Canonical:
  - `lucius <entity>`
  - `lucius <entity> <action> --args '<json>' [--format json|table|plain]`
  - `lucius <entity> <action> --help`
- Examples:
  - `lucius test_case list`
  - `lucius test_case create --args '{"name":"Smoke login"}'`
  - `lucius launch close --args '{"launch_id":123}'`
  - `lucius integrations` (alias of `lucius integration`)

### Entity Aliases

- `integrations` -> `integration`
- `test_cases` -> `test_case`
- `launches` -> `launch`
- `shared_steps` -> `shared_step`
- `test_layers` -> `test_layer`
- `test_layer_schemas` -> `test_layer_schema`
- `test_suites` -> `test_suite`
- `test_plans` -> `test_plan`
- `defects` -> `defect`
- `defect_matchers` -> `defect_matcher`
- `custom_fields` -> `custom_field`
- `custom_field_values` -> `custom_field_value`

### Route-to-Service Mapping Matrix

#### test_case

| Action | Existing tool behavior | Service method(s) |
|---|---|---|
| create | `create_test_case` | `TestCaseService.create_test_case` (+ `add_issues_to_test_case` when `issues` present) |
| get | `get_test_case_details` | `SearchService.get_test_case_details` |
| update | `update_test_case` | `TestCaseService.get_test_case`, `TestCaseService.update_test_case` |
| delete | `delete_test_case` | `TestCaseService.delete_test_case` |
| delete_archived | `delete_archived_test_cases` | `TestCaseService.cleanup_archived` |
| list | `list_test_cases` | `SearchService.list_test_cases` |
| search | `search_test_cases` | `SearchService.search_test_cases` |
| get_custom_fields | `get_test_case_custom_fields` | `TestCaseService.get_test_case_custom_fields_values` |

#### custom_field

| Action | Existing tool behavior | Service method(s) |
|---|---|---|
| get | `get_custom_fields` | `TestCaseService.get_custom_fields` |
| delete_unused | `delete_unused_custom_fields` | `CustomFieldService.cleanup_unused` |

#### custom_field_value

| Action | Existing tool behavior | Service method(s) |
|---|---|---|
| list | `list_custom_field_values` | `CustomFieldValueService.list_custom_field_values` |
| create | `create_custom_field_value` | `CustomFieldValueService.create_custom_field_value` |
| update | `update_custom_field_value` | `CustomFieldValueService.update_custom_field_value` |
| delete | `delete_custom_field_value` | `CustomFieldValueService.delete_custom_field_value` |

#### launch

| Action | Existing tool behavior | Service method(s) |
|---|---|---|
| create | `create_launch` | `LaunchService.create_launch` |
| list | `list_launches` | `LaunchService.list_launches` |
| get | `get_launch` | `LaunchService.get_launch` |
| delete | `delete_launch` | `LaunchService.delete_launch` |
| close | `close_launch` | `LaunchService.close_launch` |
| reopen | `reopen_launch` | `LaunchService.reopen_launch` |

#### integration

| Action | Existing tool behavior | Service method(s) |
|---|---|---|
| list | `list_integrations` | `IntegrationService.list_integrations` |

#### shared_step

| Action | Existing tool behavior | Service method(s) |
|---|---|---|
| create | `create_shared_step` | `SharedStepService.create_shared_step` |
| list | `list_shared_steps` | `SharedStepService.list_shared_steps` |
| update | `update_shared_step` | `SharedStepService.update_shared_step` |
| delete | `delete_shared_step` | `SharedStepService.delete_shared_step` |
| delete_archived | `delete_archived_shared_steps` | `SharedStepService.cleanup_archived` |
| link_test_case | `link_shared_step` | `TestCaseService.add_shared_step_to_case` |
| unlink_test_case | `unlink_shared_step` | `TestCaseService.remove_shared_step_from_case` |

#### test_layer

| Action | Existing tool behavior | Service method(s) |
|---|---|---|
| list | `list_test_layers` | `TestLayerService.list_test_layers` |
| create | `create_test_layer` | `TestLayerService.create_test_layer` |
| update | `update_test_layer` | `TestLayerService.update_test_layer` |
| delete | `delete_test_layer` | `TestLayerService.delete_test_layer` |

#### test_layer_schema

| Action | Existing tool behavior | Service method(s) |
|---|---|---|
| list | `list_test_layer_schemas` | `TestLayerService.list_test_layer_schemas` |
| create | `create_test_layer_schema` | `TestLayerService.create_test_layer_schema` |
| update | `update_test_layer_schema` | `TestLayerService.update_test_layer_schema` |
| delete | `delete_test_layer_schema` | `TestLayerService.delete_test_layer_schema` |

#### test_suite

| Action | Existing tool behavior | Service method(s) |
|---|---|---|
| create | `create_test_suite` | `TestHierarchyService.create_test_suite` |
| list | `list_test_suites` | `TestHierarchyService.list_test_suites` |
| assign_test_cases | `assign_test_cases_to_suite` | `TestHierarchyService.assign_test_cases_to_suite` |
| delete | `delete_test_suite` | `TestHierarchyService.delete_suite` |

#### test_plan

| Action | Existing tool behavior | Service method(s) |
|---|---|---|
| create | `create_test_plan` | `PlanService.create_plan` |
| update | `update_test_plan` | `PlanService.update_plan` |
| manage_content | `manage_test_plan_content` | `PlanService.update_plan_content` |
| list | `list_test_plans` | `PlanService.list_plans` |
| delete | `delete_test_plan` | `PlanService.delete_plan` |

#### defect

| Action | Existing tool behavior | Service method(s) |
|---|---|---|
| create | `create_defect` | `DefectService.create_defect` |
| get | `get_defect` | `DefectService.get_defect` |
| update | `update_defect` | `DefectService.update_defect` |
| delete | `delete_defect` | `DefectService.delete_defect` |
| list | `list_defects` | `DefectService.list_defects` |
| link_test_case | `link_defect_to_test_case` | `DefectService.link_defect_to_test_case` |
| list_test_cases | `list_defect_test_cases` | `DefectService.list_defect_test_cases` |

#### defect_matcher

| Action | Existing tool behavior | Service method(s) |
|---|---|---|
| create | `create_defect_matcher` | `DefectService.create_defect_matcher` |
| update | `update_defect_matcher` | `DefectService.update_defect_matcher` |
| delete | `delete_defect_matcher` | `DefectService.delete_defect_matcher` |
| list | `list_defect_matchers` | `DefectService.list_defect_matchers` |

### File Structure Requirements

- Update:
  - `src/cli/cli_entry.py`
  - `scripts/build_tool_schema.py`
  - `src/cli/data/tool_schemas.json`
  - `tests/cli/test_cli_basics.py`
  - `tests/cli/test_e2e_mocked.py`
  - `docs/CLI.md`
  - `README.md`
- No changes to:
  - `src/tools/*` business behavior
  - `src/services/*` domain logic signatures (unless required for strict parity bug fixes).

### Testing Requirements

- Command parsing and discovery:
  - root help lists entities
  - `lucius <entity>` lists available actions
  - invalid entity/action returns guided error.
- Help rendering:
  - each action supports `--help` with params and examples.
- Behavior parity:
  - representative routes from each entity return expected output semantics.
- Dependency boundary:
  - CLI command execution path has no `fastmcp` or `src.main` import requirement.
- Regression:
  - existing output format tests (json/table/plain) remain green.
- Coverage thresholds:
  - `src/cli/` line coverage must be >=90%
  - canonical route coverage must be 100% (at least one test per canonical command).
- CI gating:
  - coverage and route-matrix checks must fail CI when below thresholds.

### References

- `specs/project-planning-artifacts/epics.md` (Epic 9 / Story 9.2 context)
- `specs/implementation-artifacts/9-2-fastmcp-cli-integration.md`
- `src/cli/cli_entry.py`
- `scripts/build_tool_schema.py`
- `src/tools/__init__.py`
- `src/tools/*.py`
- `src/services/*.py`
- `.codex/prompts/bmad-bmm-create-story.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Story 9.3 spec drafted from committed code state (HEAD) to avoid uncommitted local changes.
- Scope now includes completed source code implementation aligned to this story's architecture and UX contract.
- Implemented canonical static route matrix in CLI and removed dynamic FastMCP-based command mapping.
- Reworked schema generation to introspect existing tool functions/signatures directly (no `mcp.list_tools()` usage).
- Updated CLI tests for canonical entity/action routing, route-matrix coverage, import-boundary guardrails, and >=90% CLI coverage gate.
- Updated CLI documentation and README examples to canonical `lucius <entity> <action>` syntax.

### File List

- specs/implementation-artifacts/9-3-service-first-cli-entity-action.md
- .gitignore
- src/cli/cli_entry.py
- src/cli/__init__.py
- src/cli/route_matrix.py
- scripts/build_tool_schema.py
- src/cli/data/tool_schemas.json
- tests/cli/test_cli_basics.py
- tests/cli/test_e2e_mocked.py
- tests/cli/test_route_matrix.py
- tests/cli/test_cli_coverage_helpers.py
- pyproject.toml
- docs/CLI.md
- README.md

## Change Log

- 2026-03-13: Senior Developer Review (AI) completed; status moved to in-progress and review follow-up tasks added.
- 2026-03-13: Addressed AI review findings 1-4 (validation parity, CI command grammar, CI coverage gating, and entity hint quality); finding 5 intentionally deferred.

## Senior Developer Review (AI)

### Reviewer

Ivan Ostanin (AI)

### Date

2026-03-13

### Outcome

Changes Requested

### Findings Summary

- High: 2
- Medium: 3
- Low: 0

### Key Findings

1. **[HIGH] CLI argument validation no longer enforces schema types/constraints**
   - `validate_args_against_schema()` checks only required fields and unknown keys; type and constraint mismatches are not rejected before invocation, which breaks validation parity expectations for tool calls.
   - Evidence: `/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/src/cli/cli_entry.py:453`

2. **[HIGH] CI still executes legacy CLI grammar that this story deprecates**
   - The CLI build workflow still runs `list --format json`, but `run_cli()` now treats `list`/`call` as legacy and exits with error.
   - Evidence: `/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/.github/workflows/cli-build.yml:220`, `/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/src/cli/cli_entry.py:541`

3. **[MEDIUM] Coverage gate is configured but not enforced by current CI test command**
   - `fail_under = 90` is set, but workflow test command does not enable coverage collection (`--cov=src/cli`), so the threshold is not actively gating those runs.
   - Evidence: `/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/pyproject.toml:143`, `/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/.github/workflows/cli-build.yml:228`

4. **[MEDIUM] Unknown-entity hint omits many valid canonical entities**
   - Hint generation filters out aliases containing `_` or `-`, removing canonical forms like `test_case`, `shared_step`, and `custom_field_value` from guidance.
   - Evidence: `/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/src/cli/cli_entry.py:253`

5. **[MEDIUM] Story traceability drift vs repository working set**
   - The story File List did not include modified `.gitignore` and `src/cli/__init__.py`, reducing review traceability for this implementation slice.
   - Evidence: `/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/specs/implementation-artifacts/9-3-service-first-cli-entity-action.md:346`

### Validation Performed by Reviewer

- `uv run pytest tests/cli -q` -> 113 passed
- `uv run pytest tests/cli --cov=src/cli --cov-report=term-missing -q` -> 113 passed, 91.67% coverage for `src/cli`
- `.venv/bin/python scripts/build_tool_schema.py` -> schema generation successful (56 tools)

### Sprint Status Sync

- Story file updated to `in-progress`.
- Sprint sync warning: `9-3-service-first-cli-entity-action` key is not present under `development_status` in `/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/specs/implementation-artifacts/sprint-status.yaml`.

### Remediation Update (AI)

- Resolved findings:
  - #1 Type/constraint validation parity restored in CLI argument validation path.
  - #2 Binary CI check updated to use entity/action grammar instead of legacy `list`.
  - #3 CLI test step now explicitly runs with `--cov=src/cli` to enforce `fail_under` coverage gate.
  - #4 Unknown entity hint now includes canonical entity names.
- Deferred by request:
  - #5 Story traceability reconciliation.
