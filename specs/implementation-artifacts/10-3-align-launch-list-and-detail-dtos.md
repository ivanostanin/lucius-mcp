# Story 10.3: Align Launch List and Detail DTOs

Status: ready-for-dev

<!-- Note: Ultimate context engine analysis completed - comprehensive developer guide created. -->

## Story

As an **AI Agent**,
I want **launch collection results to stay compact while a single-launch lookup returns rich execution context**,
so that **I can scan many launches efficiently and inspect one launch without losing statistics or metadata**.

## Acceptance Criteria

1. **Compact collection contract**
   - **Given** a project with multiple launches.
   - **When** I call `list_launches` in `json` or `plain` mode.
   - **Then** every item follows basic `LaunchDto` semantics and includes only stable collection fields such as `id`, `name`, open/closed state, created/modified timestamps, project/external/autoclose metadata when available, and `url`.
   - **And** pagination, `search`, `filter_id`, `sort`, runtime project override, and the existing AQL search fallback continue to work.
   - **And** collection retrieval does not perform one detail request per launch or expose preview-only statistics, defect counts, environment, or jobs.
   - **And** removing the currently published `known_defects_count`, `new_defects_count`, and `manual_execution_guidance` fields from `list_launches.items` is an intentional breaking output-contract change.
   - **And** the implementation updates `CHANGELOG.md` and uses a Conventional Commit `!` marker with a `BREAKING CHANGE:` footer; tool names, inputs, pagination, and lifecycle behavior remain unchanged.

2. **Rich exact-launch contract**
   - **Given** a valid Launch ID.
   - **When** I call `get_launch` in `json` or `plain` mode.
   - **Then** the result is for the exact requested ID and follows rich `LaunchPreviewDto` semantics.
   - **And** it includes all available common metadata plus `created_by`, `last_modified_by`, `statistic`, `known_defects_count`, `new_defects_count`, `environment`, `jobs`, `tags`, `issues`, and `links`.
   - **And** it retains the TestOps launch `url` and the manual-execution guidance introduced by Story 10.2.
   - **And** base by-ID metadata that is not present in `LaunchPreviewDto`, such as `autoclose`, remains available when the upstream API supplies it.
   - **And** `statistic`, `environment`, and `jobs` are populated from verified exact-ID launch endpoints when the raw by-ID payload omits them.
   - **And** defect counts and creator/modifier fields are populated only from a documented, tested upstream source with matching semantics; otherwise their optional schema fields remain unavailable rather than being fabricated.

3. **Exact-ID-safe rich resolution**
   - **Given** the checked-in OpenAPI 25.4.1 contract declares `GET /api/launch/{id}` as sparse `LaunchDto` while `GET /api/launch` may return rich `PageLaunchPreviewDto`.
   - **When** the rich lookup is implemented.
   - **Then** the developer first verifies the live raw by-ID response against the sandbox.
   - **And** if the raw response is rich, the client preserves those fields instead of allowing generated `LaunchDto` deserialization to discard them.
   - **And** if the raw response is genuinely sparse, the client/service composes the required launch-specific by-ID endpoints into one rich detail result.
   - **And** the implementation never relies on a fuzzy/partial name match, never returns the first same-name candidate, and never performs an unbounded scan of all launches.
   - **And** every declared optional detail field remains in the output schema, but it has a value only when it comes from the verified raw response or is truthfully derived from a documented endpoint.

4. **Stable serialization and error semantics**
   - **Given** legitimate zero counts, empty collections, or absent optional fields.
   - **When** launch output is serialized.
   - **Then** numeric zero is preserved and is not replaced by `None` through truthiness-based fallback.
   - **And** present empty collections remain empty collections while unavailable optional values remain schema-valid and consistent between plain and JSON output.
   - **And** a non-positive ID still raises `AllureValidationError`, while an upstream missing launch still maps to `LaunchNotFoundError` and an actionable Agent Hint.
   - **And** only a 404 from the authoritative base by-ID read maps to `LaunchNotFoundError`.
   - **And** unsupported or forbidden optional enrichment is represented as unavailable according to the documented field policy, while unexpected enrichment failures propagate as typed `AllureAPIError` with endpoint context instead of being silently discarded or misreported as launch-not-found.

5. **Distinct published output schemas**
   - **Given** MCP clients or generated documentation inspect `list_launches` and `get_launch`.
   - **When** their output schemas are published.
   - **Then** `list_launches.items` uses a dedicated compact launch-list item model.
   - **And** `get_launch` uses a dedicated rich launch-detail model with typed nested statistics, environment, jobs, tags, issues, and links.
   - **And** create/close/reopen output contracts are not accidentally widened or changed by reusing the rich detail schema.

6. **Lifecycle and CLI compatibility**
   - **Given** existing create, close, reopen, delete, upload, launch-result discovery, rerun, manual session, submission, and attachment workflows.
   - **When** list/detail DTO usage changes.
   - **Then** those workflows retain their current behavior and typed state checks.
   - **And** close/reopen verification continues to use an authoritative exact-ID read rather than an eventually consistent collection preview.
   - **And** `lucius launch list|get` still supports `plain|json|table|csv` at the CLI boundary with deterministic list columns and no traceback/internal logs.

7. **Automated and sandbox verification**
   - **Given** focused automated checks run.
   - **When** client, service, tool, output-schema, CLI, documentation, and E2E suites execute.
   - **Then** they prove basic list normalization, rich detail preservation, exact-ID selection, duplicate/similar-name safety, zero-count preservation, nested-field serialization, 404 mapping, and lifecycle compatibility.
   - **And** a sandbox E2E scenario creates or reuses a launch, adds results when needed, verifies compact collection output, verifies rich single-launch statistics/metadata for the same ID, and exercises close/reopen without regression.

## Tasks / Subtasks

- [ ] **1. Make client DTO contracts deterministic** (AC: 1-4, 6)
  - [ ] In `src/client/client.py`, change collection handling so `list_launches` yields a basic `PageLaunchDto`/`LaunchDto` contract rather than leaking the generated ambiguous oneOf into services.
  - [ ] Preserve pagination, search/filter/sort parameters and existing error translation.
  - [ ] Prevent the current oneOf fallback from silently downcasting a rich response merely because `PageLaunchDto` ignores extra keys; normalize intentionally and test the field policy.
  - [ ] Establish an exact-ID rich read path for `get_launch`:
    - [ ] inspect the raw `find_one23_without_preload_content` sandbox payload;
    - [ ] parse it with `LaunchPreviewDto` semantics only if the live payload actually contains the rich fields;
    - [ ] otherwise compose verified launch-specific endpoints for statistic, environment, jobs, and defect/related metadata behind the client facade.
  - [ ] Keep a sparse authoritative by-ID helper for mutation/existence checks if separating it avoids lifecycle regressions.
  - [ ] Do not hand-edit `src/client/generated/`; if a generated contract must change, patch the filter/overlay source and regenerate.

- [ ] **2. Separate service collection and detail models** (AC: 1-4, 6)
  - [ ] In `src/services/launch_service.py`, narrow `LaunchListResult.items` to the compact collection type.
  - [ ] Introduce an application-owned typed `LaunchDetail` (name may follow local convention) aligned with `LaunchPreviewDto` fields and merged authoritative base metadata; do not mutate generated DTO instances or attach dynamic attributes.
  - [ ] Encapsulate any multi-endpoint enrichment in the client/service layer; tools must not coordinate API calls.
  - [ ] Bound enrichment work to the requested launch and run independent async calls concurrently where safe.
  - [ ] Make the base by-ID read authoritative for existence and implement the enrichment failure policy from AC 4 without silently returning accidental partial data.
  - [ ] Update internal consumers of `get_launch` deliberately: `close_launch`, `reopen_launch`, result upload existence checks, manual execution, and `_determine_close_report_status` must retain correct typing and state behavior.
  - [ ] Preserve the `list_launches` search-to-AQL fallback and `search_launches_aql` basic result contract.

- [ ] **3. Split tool payloads and published schemas** (AC: 1, 2, 4, 5)
  - [ ] In `src/tools/output_schemas.py`, replace the shared list/detail use of `LaunchSummary` with separate compact list-item and rich detail output models; leave mutation summaries stable.
  - [ ] Define strict agent-facing nested output models (`extra="forbid"`) rather than publishing raw generated-model dumps, with stable projections at minimum:
    - [ ] statistic: `{status, count}`;
    - [ ] environment value: `{id, name, variable: {id, name}}`;
    - [ ] job run: `{id, name, status, stage, url, error_message, external_id, job: {id, name, type, url}}`;
    - [ ] tag: `{id, name}`;
    - [ ] issue: `{id, name, display_name, status, summary, url, closed}`;
    - [ ] link: `{name, type, url}`.
  - [ ] In `src/tools/launches.py`, use separate serializers for collection items and single-launch detail.
  - [ ] Expand JSON and plain detail rendering to expose the same rich information, while keeping the list terse.
  - [ ] Replace `value_a or value_b` numeric alias selection with explicit `None` coalescing so `0` survives.
  - [ ] Keep `url` generation and `manual_execution_guidance` unchanged in meaning.

- [ ] **4. Update documentation and generated metadata** (AC: 5, 6)
  - [ ] Update `docs/tools.md` and `tests/agentic/agentic-tool-calls-tests.md` to state “basic many, rich one” and list the observable rich fields.
  - [ ] Regenerate and verify `docs/mcp_manifest.json` after output schema or tool documentation changes.
  - [ ] Regenerate `src/cli/data/tool_schemas.json` only if tool docstrings or input schemas change.
  - [ ] Do not regenerate shell completions or MCPB featured-tool manifests unless names, routes, aliases, inputs, or featured descriptions actually change.
  - [ ] Document the intentional removal of `known_defects_count`, `new_defects_count`, and `manual_execution_guidance` from list items in `CHANGELOG.md`; use the repository's required breaking Conventional Commit notation and footer.

- [ ] **5. Add focused unit and integration coverage** (AC: 1-6)
  - [ ] Update `tests/integration/test_launch_client.py` for deterministic basic list parsing and exact rich get parsing/enrichment, including raw response mocks.
  - [ ] Cover a rich collection payload that would validate as both generated page DTOs and prove normalization does not accidentally drive the detail contract.
  - [ ] Update `tests/unit/test_launch_service.py` to assert basic list items, rich get fields, typed invalid/not-found errors, and unchanged close/reopen/upload behavior.
  - [ ] Cover authoritative base 404 separately from enrichment 403/404 and enrichment 5xx behavior so only a missing base launch becomes `LaunchNotFoundError`.
  - [ ] Update `tests/unit/test_launch_tools.py` and `tests/integration/test_launch_tools.py` using real generated DTO-shaped fixtures; assert JSON/plain parity, nested values, empty collections, and zero counts.
  - [ ] Update `tests/unit/test_output_schemas.py` and `tests/unit/test_tool_structured_outputs.py` for distinct list/detail schemas.
  - [ ] Update `tests/unit/test_client_facade_coverage.py` if the facade switches to raw generated methods.
  - [ ] Add duplicate/similar launch names and multi-page conditions to ensure exact-ID lookup cannot return the wrong preview.

- [ ] **6. Extend CLI and E2E regression coverage** (AC: 6, 7)
  - [ ] Extend the shared source-invoked CLI E2E suite in `tests/e2e/test_cli_entity_commands_uv_run.py` and/or `tests/e2e/test_cli_output_formats_uv_run.py` for launch list/get JSON plus deterministic list table/csv rendering.
  - [ ] Extend `tests/e2e/test_launches.py` and, where useful, `tests/e2e/test_launch_manual_execution.py` to verify the same launch ID through compact list and rich get flows.
  - [ ] Poll only where the sandbox is demonstrably eventually consistent, with a bounded timeout and a diagnostic failure.
  - [ ] Verify close/reopen after rich detail resolution so lifecycle checks remain authoritative.

- [ ] **7. Validate the implementation** (AC: 1-7)
  - [ ] Run focused tests first:
    - [ ] `uv run pytest tests/unit/test_launch_service.py tests/unit/test_launch_tools.py tests/unit/test_output_schemas.py tests/unit/test_tool_structured_outputs.py tests/unit/test_client_facade_coverage.py tests/integration/test_launch_client.py tests/integration/test_launch_tools.py -q`
    - [ ] `uv run --python 3.13 --extra dev pytest tests/e2e/test_cli_entity_commands_uv_run.py tests/e2e/test_cli_output_formats_uv_run.py -q`
    - [ ] `uv run --env-file .env.test pytest tests/e2e/test_launches.py tests/e2e/test_launch_manual_execution.py -q`
  - [ ] Run documentation/schema verification, including `tests/docs/test_mcp_manifest.py`.
  - [ ] Run `uv run ruff check` on touched paths and `uv run mypy --strict src/`.

## Dev Notes

### Developer Context

The DTO names are counterintuitive in the checked-in Allure TestOps OpenAPI client:

| Surface | Current generated contract | Actual richness | Intended Lucius contract |
|:--|:--|:--|:--|
| `GET /api/launch` / `list_launches` | `PageLaunchPreviewDto | PageLaunchDto` | Can contain rich preview data | Normalize to compact basic items for many-launch discovery |
| `GET /api/launch/{id}` / `get_launch` | `LaunchDto` | OpenAPI declares only sparse metadata | Return an exact-ID rich detail view aligned with `LaunchPreviewDto` semantics |
| `GET /api/launch/__search` | `PageLaunchDto` | Sparse/basic | Keep basic for AQL collection results |

`LaunchDto` contains basic metadata (`autoclose`, `closed`, dates, `external`, `id`, `issues`, `links`, `name`, `project_id`, `tags`). `LaunchPreviewDto` adds creator/modifier metadata, environment, jobs, known/new defect counts, and status statistics, but it omits `autoclose`; a truly rich Lucius detail result may therefore need a typed merge rather than simply changing one annotation.

### Current Failure Mode

- `AllureClient.list_launches` exposes the generated oneOf. On ambiguity it raw-parses `PageLaunchDto` first. Because generated models accept optional fields and ignore extras, a rich preview payload can be accepted as basic and lose its extra fields silently.
- `AllureClient.get_launch` uses generated `find_one23`, so any fields not declared on `LaunchDto` can be discarded during deserialization.
- `LaunchService` currently allows both DTOs in `LaunchListResult`, while `get_launch` is typed only as `LaunchDto`.
- `list_launches` and `get_launch` share `_launch_payload` and `LaunchSummary`, so the published MCP schemas cannot express their different purposes.
- The plain detail formatter already attempts defect counts/statistics, but its real service DTO cannot provide them. JSON serialization omits most preview-only fields entirely.
- `_launch_payload` uses truthiness fallback for numeric aliases; valid zero defect counts can become missing values.

### Architecture and Implementation Guardrails

- **Thin Tool / Fat Service:** API coordination and DTO mapping belong in `src/client/` and `src/services/`; tools only delegate and render.
- **Exact-ID correctness:** Do not implement rich get through fuzzy name search. Duplicate names, partial matches, bracketed names, and pagination make that unsafe.
- **Bounded performance:** Do not scan an unbounded launch collection and do not make N detail calls from `list_launches`. Prefer verified by-ID payloads or fixed launch-specific endpoint aggregation.
- **Lifecycle authority:** Collection previews may be eventually consistent. Preserve a direct exact-ID metadata read for close/reopen and existence checks.
- **Generated boundary:** Never edit `src/client/generated/` manually. Use `scripts/filter_openapi.py` plus `./scripts/generate_testops_api_client.sh` only when a truthful, durable schema overlay is justified.
- **Stable agent contract:** Serialize explicit application-owned field shapes. Avoid leaking upstream DTO objects or unstable model dumps directly into MCP output.
- **Tool outputs:** Keep tool modes `plain|json`; `table|csv` remain CLI-only.
- **Errors:** Keep try/except out of tools. Services/client map validation and not-found failures to typed Allure exceptions for global Agent Hints.
- **Compatibility:** Adding rich `get_launch` fields is additive. Removing an already published list field or changing deterministic CLI columns may be breaking and must follow the repository's Conventional Commit breaking-change rule.

### Library and Framework Requirements

- Python `>=3.13` as declared in `pyproject.toml`; use `uv` for all project commands.
- FastMCP `>=3.0.0`, Pydantic `>=2.12.5`, async `httpx >=0.28.1`, pytest, ruff, and strict mypy.
- Checked-in generated client: Allure TestOps OpenAPI `25.4.1`, upstream service commit `623f6ed302ba4b651cf9040faca4635af2d93b7c`.
- No dependency upgrade or external library is required for this story; the local OpenAPI, generated client, and sandbox response are the technical sources of truth.

### Source Tree Impact

| Component | Path | Expected action |
|:--|:--|:--|
| Client facade | `src/client/client.py`, possibly `src/client/__init__.py` | Modify DTO parsing/rich exact-ID retrieval |
| Generated client | `src/client/generated/` | Do not hand-edit; regenerate only through the documented pipeline if required |
| Launch service | `src/services/launch_service.py` | Separate compact list and rich detail contracts; protect lifecycle consumers |
| Launch tools | `src/tools/launches.py` | Split serializers/formatters and preserve zero values |
| Output models | `src/tools/output_schemas.py` | Add distinct compact list and rich detail schemas |
| Tool metadata | `docs/mcp_manifest.json`, possibly `src/cli/data/tool_schemas.json` | Regenerate as applicable |
| Documentation | `docs/tools.md`, `tests/agentic/agentic-tool-calls-tests.md` | Clarify observable contract |
| Tests | `tests/unit/`, `tests/integration/`, `tests/e2e/`, `tests/docs/` | Add contract and regression coverage |

### Previous Story Intelligence

- Story 10.2 added manual launch execution and requires `get_launch` to retain concise guidance pointing to `list_launch_test_results`; rich detail must not absorb result-level workflow logic.
- Story 5.1 established pagination, the search-to-AQL fallback, project override handling, and a workaround for launch-list oneOf conflicts. Preserve those behaviors while making DTO normalization intentional.
- Story 5.2 promised full launch details, but its formatter tests use ad-hoc objects with rich fields even though production returns `LaunchDto`; replace these mocks with realistic generated or application-owned detail fixtures.
- Story 5.5 expects uploaded results to update launch statistics and uses get/close in its E2E flow, making upload-to-rich-get and lifecycle behavior useful regression coverage.

### Git Intelligence Summary

- Recent release/dependency commits do not alter this design.
- Commit `77b727c` only reorders a launch-result status union for schema generation; it is not a DTO-selection precedent.
- Output-schema work in `97cf13e`/`0243e93` established concrete `@output_fields(...)` models and manifest verification; this story must preserve that discipline.
- Manual launch work in `975cf24` established the current launch service/tool/test layout and the Story 10.2 guidance contract.

### Latest Technical Information

- Local generated artifacts are based on Allure TestOps OpenAPI 25.4.1 and are the appropriate baseline for this repository.
- The OpenAPI itself does not promise rich `LaunchPreviewDto` from the by-ID endpoint. Do not “fix” this only by changing a return annotation or lying in a schema overlay.
- The implementation decision must be based on a captured sandbox by-ID response. If it is sparse, use verified launch-specific endpoints and document the composition; if it is rich, preserve the raw fields in the client facade and cover the upstream contract drift with tests.

### Project Structure Notes

- Keep changes in the existing launch feature files; no new tool, route, or alias is required.
- Use an application-owned typed detail model to avoid conflating generated DTOs and to provide a stable superset for tool output; do not mutate generated DTO instances.
- No database, deployment, authentication, or telemetry changes are in scope.

### References

- [Source: specs/project-planning-artifacts/epics.md#Epic 5: Execution Management]
- [Source: specs/project-planning-artifacts/epics.md#Epic 10: Quality of Life and API Coverage]
- [Source: specs/implementation-artifacts/5-1-create-and-list-launches.md]
- [Source: specs/implementation-artifacts/5-2-get-launch-details.md]
- [Source: specs/implementation-artifacts/5-5-expose-upload-results-to-launch.md]
- [Source: specs/implementation-artifacts/10-2-manual-test-execution-inside-launches.md]
- [Source: specs/prd.md#Data Schemas & Formatting]
- [Source: specs/prd.md#Non-Functional Requirements]
- [Source: specs/architecture.md#Data Architecture]
- [Source: specs/architecture.md#API & Communication Patterns]
- [Source: specs/architecture.md#Implementation Patterns & Consistency Rules]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: docs/development.md#Adding a New Tool]
- [Source: docs/development.md#Regenerating the API Client]
- [Source: docs/tools.md#Launch Management]
- [Source: src/client/generated/models/launch_dto.py]
- [Source: src/client/generated/models/launch_preview_dto.py]
- [Source: src/client/client.py#Launch operations]
- [Source: src/services/launch_service.py]
- [Source: src/tools/launches.py]
- [Source: src/tools/output_schemas.py]
- [Source: tests/integration/test_launch_client.py]
- [Source: tests/unit/test_launch_service.py]
- [Source: tests/unit/test_launch_tools.py]

## Dev Agent Record

### Agent Model Used

GPT-5

### Debug Log References

- Story-context analysis only; no implementation or runtime tests were executed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added this user-requested launch DTO alignment as Story 10.3 under active Epic 10 because it is an API-coverage/usability correction rather than new launch CRUD scope.
- Defined the intended “basic many, rich one” contract and the exact-ID/performance guardrails required by the asymmetric upstream OpenAPI.
- Identified the existing generated oneOf downcast risk, shared output-schema mismatch, zero-value serialization bug, and lifecycle consumers that require regression protection.
- External web research was not needed: the checked-in OpenAPI/client and sandbox verification requirement are the authoritative technical sources for this repository-specific contract.

### File List

- specs/project-planning-artifacts/epics.md
- specs/implementation-artifacts/10-3-align-launch-list-and-detail-dtos.md
- specs/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-07-29: Created Story 10.3 and marked it ready for development. 
