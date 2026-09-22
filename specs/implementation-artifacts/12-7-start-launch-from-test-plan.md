---
title: 'Story 12.7: Start a launch from a test plan'
type: 'feature'
created: '2026-09-22'
status: 'review'
baseline_commit: '90f22b6'
context:
  - '../project-planning-artifacts/epics.md'
  - 'epic-12-context.md'
  - '../../docs/development.md'
  - '../../src/services/plan_service.py'
  - '../../src/services/launch_service.py'
  - '../../src/tools/plans.py'
  - '../../src/tools/launches.py'
  - '../../src/tools/output_schemas.py'
  - '../../openapi/allure-testops-service/filtered-report-service.json'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Agents can curate test plans (`create_test_plan`, `manage_test_plan_content`, `list_test_plans`) and manage launches (`create_launch`, `close_launch`, `reopen_launch`), but they cannot start a launch from a test plan. Executing a plan today requires the Allure TestOps UI or hand-built API calls outside Lucius.

**Approach:** Add a `run_test_plan` tool backed by a new `PlanService.run_plan` method that calls the already-generated `TestPlanControllerApi.run3` operation (`POST /api/testplan/{id}/run`, "Run test plan by given id") with a `TestPlanRunRequestDto`, then map the returned `LaunchDto` into the existing curated launch mutation-summary contract with the source plan context. Expose the same behavior through the canonical CLI route `lucius test_plan run`.

## Boundaries & Constraints

**Always:** Validate `launch_name` locally (non-empty, at most 255 characters — the upstream request requires it) before any upstream call. Accept optional `tags`, `links`, and `issues` through the same simplified input conventions as `create_launch`. Map the upstream `LaunchDto` response into an application-owned curated summary (source plan ID, launch ID, name, project, launch URL, operation) and publish a concrete object-root output schema for it. Keep plain/JSON output parity with plain as the human-readable rendering. Follow the thin-tool/service-first layering and the agent-hints error contract (no silent failures). Let telemetry flow through the existing tool-usage events without adding a new telemetry surface.

**Ask First:** The upstream `TestPlanRunRequestDto` also accepts `envVarValueSets` (environment variable value sets). This story deliberately does not expose them; confirm the deferral or specify the desired simplified input shape before extending the tool.

**Never:** Do not edit `src/client/generated/` by hand, and do not change `scripts/filter_openapi.py` or regenerate the client for this story — the run endpoint is already retained in the filtered spec and the generated client. Do not add a destructive-operation confirmation gate (starting a launch is reversible via `delete_launch`, consistent with `create_launch`). Do not recursively fetch execution results or hydrate launch details after the run — return the compact mutation summary only. Do not leak generated upstream DTOs or raw API dictionaries as public output. Do not alter `create_launch` or any existing tool's behavior or schema.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Happy path | Existing `plan_id`, valid `launch_name` | Launch started from the plan; curated summary: `plan_id`, launch `id`, `name`, `project_id`, `url`, `operation` plus compact launch fields | N/A |
| Missing/empty name | `launch_name` omitted, empty, or whitespace | Request rejected locally | `AllureValidationError` with schema hint; no upstream call |
| Over-long name | `launch_name` longer than 255 characters | Request rejected locally | Same as above |
| Unknown plan | `plan_id` does not exist or is not runnable | No launch created | Upstream 4xx mapped to actionable agent hints |
| Invalid enrichment | Malformed `tags`/`links`/`issues` shapes | Request rejected locally | Validation error identifying the offending field |
| Output parity | `output_format` plain vs JSON | Equivalent structured data; plain renders launch ID, name, and URL | N/A |

</frozen-after-approval>

## Code Map

- `src/services/plan_service.py` -- add `run_plan` that validates inputs, builds `TestPlanRunRequestDto`, awaits `TestPlanControllerApi.run3`, and returns the created `LaunchDto`.
- `src/tools/plans.py` -- add the `run_test_plan` tool following the thin-tool pattern used by the other plan tools.
- `src/tools/__init__.py` -- import `run_test_plan` and add it to `__all__`; registration is automatic.
- `src/tools/output_schemas.py` -- publish the curated run-result output schema (extend `LaunchMutationSummary` with an optional `plan_id` or add a dedicated model, see Design Notes).
- `src/cli/route_matrix.py` -- add `"run": "run_test_plan"` to the `test_plan` entity.
- `docs/tools.md` -- add the `run_test_plan` row to the Test Plan Management table.
- `tests/unit/test_plan_service.py` -- service-level coverage.
- `tests/integration/test_plan_tools.py` -- tool-level coverage.
- `tests/e2e/` -- optional sandbox coverage following the existing launch e2e patterns (e.g. `test_launch_manual_execution.py`).
- Explicitly out of scope: `src/client/generated/**`, `openapi/**`, `scripts/filter_openapi.py`, `scripts/generate_testops_api_client.sh`.

## Tasks & Acceptance

**Execution:**
- [x] `src/services/plan_service.py` -- add `run_plan(plan_id, launch_name, issues=None, links=None, tags=None)` that validates `launch_name` (non-empty, ≤255) and the simplified enrichment inputs, builds `TestPlanRunRequestDto` (with `generate_schema_hint(TestPlanRunRequestDto)` surfaced on DTO validation failure), awaits `run3(id=plan_id, ...)`, and returns the created `LaunchDto` -- (AC: #1, #2, #3)
- [x] `src/tools/plans.py` -- add the `run_test_plan` tool (`plan_id`, `launch_name`, optional `tags`/`links`/`issues`, `output_format`) decorated with `@output_fields(..., model=...)`, building the curated payload with the launch URL from the returned `LaunchDto` (prefer `launch.project_id` when present) and the source plan context -- (AC: #1, #4)
- [x] `src/tools/__init__.py` -- register `run_test_plan` -- (AC: #5)
- [x] `src/tools/output_schemas.py` -- publish the concrete object-root output schema for the curated run result -- (AC: #1, #5)
- [x] `src/cli/route_matrix.py` plus regenerated completions (`python3 deployment/scripts/generate_completions.py`) -- add the `test_plan run` action -- (AC: #5)
- [x] `docs/tools.md` -- document the tool, its parameters, and the plan-to-launch workflow -- (AC: #5)
- [x] `tests/unit/test_plan_service.py` -- cover local validation failures and the successful `run3` invocation -- (AC: #2, #3)
- [x] `tests/integration/test_plan_tools.py` -- cover plain/JSON parity, payload fields, URL construction, and upstream error mapping -- (AC: #1, #2, #3)
- [x] Optional: sandbox e2e coverage when the e2e harness supports plan execution -- (AC: #6)

**Acceptance Criteria:**
1. Given an existing test plan and a valid launch name, when `run_test_plan` is called, then a launch is started from the plan via `POST /api/testplan/{id}/run` and a curated summary with the source plan ID, launch ID, name, project, launch URL, and operation is returned in both output formats.
2. Given a missing, empty, or over-long launch name, the request is rejected locally with an actionable validation error and no upstream call is made.
3. Given an unknown or non-runnable plan, or an upstream rejection, the failure surfaces as actionable agent hints and no launch is reported created.
4. Given optional tags, links, or issues, they are mapped to the upstream request through the same simplified conventions used by `create_launch`.
5. Given MCP and CLI inspection, `run_test_plan` publishes a concrete object-root output schema, `lucius test_plan run` routes to the same service behavior, and documentation and shell completions include the new tool.
6. Given the automated suite, focused unit and integration tests pass and existing launch and test-plan tools remain unchanged.

## Spec Change Log

## Design Notes

- Upstream contract (checked-in filtered spec): operation `run_3` on tag `test-plan-controller`, `POST /api/testplan/{id}/run`; request `TestPlanRunRequestDto` — `launchName` required (1–255 chars), optional `envVarValueSets: EnvironmentSetDto[]`, `issues: IssueDto[]`, `links: ExternalLinkDto[]` (`name`, `type`, `url`), `tags: LaunchTagDto[]` (`id`, `name`); response `LaunchDto` (`id`, `name`, `projectId`, `closed`, `external`, `autoclose`, `createdDate`, `lastModifiedDate`, `issues`, `links`, `tags`). The generated client already exposes this as `TestPlanControllerApi.run3` in `src/client/generated/api/test_plan_controller_api.py` — no client regeneration is needed.
- Naming: `run_test_plan` matches the upstream "Run test plan" semantics and the repo's verb-noun tool naming; `lucius test_plan run` matches the entity-action CLI grammar (`lucius <entity> <action> --args '{...}'`).
- Output contract: reuse `LaunchMutationSummary` ("Stable compact launch fields emitted by create and lifecycle tools", `src/tools/output_schemas.py`). Extending it with an optional `plan_id: int | None = Field(default=None)` keeps every existing field optional, so `create_launch`, `close_launch`, and `reopen_launch` are unaffected; a dedicated `TestPlanRunOutput` model is an acceptable alternative if the `output_fields` schema builder requires exact field/model alignment. Either way, keep `create_launch` behavior and schema identical.
- URL construction: build the launch URL from the returned `LaunchDto.project_id` when present — the plan may belong to a project other than the configured default — and fall back to the client's configured project otherwise. `launch_url` lives in `src/utils/links.py`.
- Input mapping: mirror `create_launch`'s simplified inputs — `tags: list[str]` → `LaunchTagDto`, `links: list[dict[str, str]]` → `ExternalLinkDto`, `issues: list[dict]` → `IssueDto`. The `_build_*_dtos` and `_validate_*` helpers currently live on `LaunchService` (`src/services/launch_service.py`); reuse or extract them into a shared location rather than duplicating mapping logic in `PlanService`.
- No confirmation gate: starting a launch is a non-destructive, reversible operation (deletion stays gated in `delete_launch`/`delete_test_plan`), consistent with `create_launch`.
- Telemetry: tool-usage events are emitted automatically from the tool name (`TelemetryService.emit_tool_usage_event`); add no new telemetry surface and preserve the privacy constraints documented in `docs/development.md`.
- Error handling: follow the repo's agent-hints pattern — wrap upstream 4xx/5xx as informative text responses (no silent failures), surface DTO validation problems as `AllureValidationError` with `generate_schema_hint` suggestions.

## Verification

**Commands:**
- `uv run pytest tests/unit/test_plan_service.py tests/integration/test_plan_tools.py -q` -- expected: all focused plan tests pass.
- `uv run pytest tests/unit/test_launch_tools.py tests/unit/test_launch_service.py -q` -- expected: no launch regressions.
- `uv run ruff format . && uv run ruff check .` -- expected: clean.
- `uv run mypy --strict src` -- expected: type checking succeeds.

## Open Questions

- Should `env_var_value_sets` (upstream `envVarValueSets`) be exposed in a follow-up story, and if so with what simplified input shape?
- Is sandbox e2e coverage for plan execution feasible with the current e2e harness, or should this stay unit/integration-only for now?

## Dev Agent Record

### Agent Model Used

nox/noxtua-ai-4.3

### Debug Log References

- RED/GREEN cycle: new service and tool tests were written first and confirmed failing, then the implementation made them pass.
- Validated: focused plan suite (38 passed: 22 unit + 16 integration), launch regression suites (`test_launch_tools.py` + `test_launch_service.py`, 127 passed), full unit/integration/docs suite (1,186 passed), CLI suite (257 passed); `ruff format .` and `ruff check .` clean; `mypy --strict src` clean (99 files).
- Sandbox e2e coverage follows the existing `test_plan_management.py` lifecycle pattern; it skips locally without sandbox credentials and executes only in the credential-backed e2e workflow.

### Completion Notes List

- `PlanService.run_plan` validates `launch_name` (non-empty, ≤255) plus the simplified `tags`/`links`/`issues` inputs locally, builds `TestPlanRunRequestDto` with `generate_schema_hint(TestPlanRunRequestDto)` surfaced on DTO validation failure, awaits `TestPlanControllerApi.run3` (`POST /api/testplan/{id}/run`), and maps upstream 404s to an actionable "Test plan ID {id} not found or is not runnable" error. `envVarValueSets` is deliberately not exposed (Ask-First boundary).
- The simplified input validators and DTO builders were extracted into `src/services/launch_inputs.py` (Design Notes: reuse or extract, never duplicate in `PlanService`); `LaunchService` delegates to them, so `create_launch`/`close_launch`/`reopen_launch` behavior and published schemas are unchanged (127 launch regression tests and the output-schema suites pass untouched).
- `run_test_plan` publishes a concrete object-root schema via `TestPlanRunOutput` (a `LaunchMutationSummary` subclass adding optional `plan_id`), reuses `_launch_mutation_payload` for exact mutation-summary parity with `create_launch`, sets `operation: "started"`, and builds the launch URL preferring `launch.project_id` with fallback to the client's configured project.
- CLI: `lucius test_plan run` routes to the same tool via `route_matrix.py`; `src/cli/data/tool_schemas.json`, `deployment/shell-completions/*`, and `docs/mcp_manifest.json` were regenerated via `scripts/build_tool_schema.py`, `deployment/scripts/generate_completions.py`, and `fastmcp inspect`.
- Files touched beyond the Code Map (`src/tools/annotations.py`, `src/cli/data/tool_schemas.json`, `docs/mcp_manifest.json`) are required by repo-enforced registration coverage: annotations/tags policy is validated at import time, the CLI registry is built from the checked-in tool schemas, and `tests/docs/test_mcp_manifest.py` fails when the manifest drifts from `src.tools.all_tools`.
- Open questions resolved: sandbox e2e coverage is feasible and was added (`test_run_test_plan_starts_launch`); `envVarValueSets` stays deferred to a follow-up story pending a simplified input shape.

### Change Log

- 2026-09-22: Story created and marked ready-for-dev.
- 2026-09-22: Implemented `run_test_plan` (service `run_plan`, tool, output schema, CLI route, regenerated schemas/completions/manifest, docs, unit/integration/e2e tests); all quality gates green; marked ready for review.

### File List

- src/services/launch_inputs.py
- src/services/launch_service.py
- src/services/plan_service.py
- src/tools/output_schemas.py
- src/tools/plans.py
- src/tools/__init__.py
- src/tools/annotations.py
- src/cli/route_matrix.py
- src/cli/data/tool_schemas.json
- deployment/shell-completions/lucius.bash
- deployment/shell-completions/lucius.fish
- deployment/shell-completions/lucius.ps1
- deployment/shell-completions/lucius.zsh
- docs/mcp_manifest.json
- docs/tools.md
- tests/unit/test_plan_service.py
- tests/integration/test_plan_tools.py
- tests/e2e/test_plan_management.py
- specs/implementation-artifacts/12-7-start-launch-from-test-plan.md
- specs/implementation-artifacts/sprint-status.yaml
