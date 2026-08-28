# Story 12.4: Extend Get Launch Info with Complete Execution Results

Status: in-progress

<!-- Note: This story was validated against the create-story checklist, current source, generated client, full/filtered OpenAPI, Stories 10.3 and 12.1-12.3, and the user's clarified execution-result contract. -->

## Story

As an **AI Agent**,
I want to **opt into complete launch execution information through `get_launch`**,
so that **I can understand the launch, identify exact Test Result IDs, and navigate to result details and evidence without reconstructing TestOps API calls**.

## Acceptance Criteria

1. **Keep launch inspection backward compatible and opt-in**
   - **Given** the existing `get_launch(launch_id, project_id, output_format)` tool and `lucius launch get` route.
   - **When** this story is implemented.
   - **Then** the public signature adds `include_execution_results: bool = False` and `tree_id: int | None = None` without adding a new tool, route, or business path.
   - **And** the existing positional order `launch_id, project_id, output_format` remains unchanged; the new options are appended after those parameters or made keyword-only if supported by the repository's FastMCP schema path.
   - **And** when `include_execution_results` is false or omitted, existing exact-ID launch fields, plain/JSON behavior, output defaults, CLI behavior, and lifecycle consumers remain backward compatible.
   - **And** every 12.4-only output key—including execution collections, tree views, snapshot, `partial`, and `unavailable_sections`—is omitted when execution inclusion is false; it is not emitted as null, false, or an empty placeholder.
   - **And** `list_launches` remains compact, performs no detail/enrichment request per item, and keeps its distinct output schema.
   - **And** supplying `tree_id` while `include_execution_results=false` returns a typed validation hint rather than silently ignoring the tree selection.

2. **Return every stable launch-scoped read section when requested**
   - **Given** a valid Launch ID.
   - **When** I call `get_launch(include_execution_results=true)`.
   - **Then** the stable application-owned response retains all current launch fields: identity, project, name, open/closed state, timing, autoclose/external flags, creator/modifier, status statistics, known/new defect counts, environment, jobs, tags, issues, links, manual-execution guidance, and URL.
   - **And** it adds all distinct stable launch-scoped execution read views present in the checked-in TestOps OpenAPI 25.4.1:
     - duration distribution;
     - progress/readiness;
     - assignees and testers;
     - launch variables;
     - launch defect rows and counts;
     - member statistics;
     - muted result rows;
     - retry rows and previous-retry references;
     - unresolved result rows;
     - complete compact flat test-result rows;
     - the launch-scoped core test-result index;
     - result timeline and result-defect tree views;
     - resolved project-tree metadata, tree statistics widgets, and hierarchical result trees.
   - **And** collection/result-tree surfaces are curated into compact non-recursive references as required by AC 3; “all available” means all distinct read views, not a raw dump or duplicate publication of every field on the richer `TestResultDto` index.
   - **And** launch mutations, diff-between-launches, export, suggest, and matcher-application operations are out of scope.
   - **And** valid `0`, `false`, empty strings, empty lists, and empty pages are preserved and never converted to missing values.

3. **Expose complete compact execution rows with authoritative follow-up IDs**
   - **Given** TestOps returns flat/core launch result rows, muted rows, unresolved rows, retry rows, or any result-bearing tree leaf.
   - **When** Lucius maps those rows.
   - **Then** each application-owned row deliberately projects every stable field available on its upstream DTO rather than dumping generated models or raw dictionaries.
   - **And** the upstream result `id` is retained as `id`; its schema/help describes it as the exact Test Result ID (TestOps run ID) to pass to `get_test_result(test_result_id=<id>)` for complete details and later artifact preparation.
   - **And** Lucius does not invent a duplicate `run_id` field because the relevant TestOps DTOs expose `id`, not `run_id`.
   - **And** job-run IDs remain clearly identified as job-run IDs and are never presented as Test Result IDs.
   - **And** `failed`, `broken`, `skipped`, `passed`, and `unknown` remain distinct according to the generated TestOps status DTO/enum; Lucius does not merge `failed` with `broken` or relabel skipped results.
   - **And** `StatisticDto.in_progress` remains an aggregate statistic only and is never fabricated as a `TestStatus` row value.
   - **And** plain output visibly surfaces results and their statuses/IDs instead of rendering only counts, while JSON and plain remain semantically equivalent.
   - **And** collection rows remain compact references: `get_launch` never calls `get_test_result` per row and never embeds execution steps, fixtures, attachment metadata, or attachment bytes.

4. **Return both tree views and resolve omitted tree IDs through TestOps**
   - **Given** `include_execution_results=true` and a positive `tree_id` is supplied.
   - **When** Lucius resolves tree data.
   - **Then** it verifies/resolves that tree through the project tree API and retrieves both:
     - the launch tree statistics widget from `GET /api/launch/{id}/widget/tree`;
     - the hierarchical result tree from `GET /api/v2/launch/{launchId}/test-result/tree/entity`.
   - **And** only the selected tree is expanded.
   - **Given** `include_execution_results=true` and `tree_id` is omitted.
   - **When** Lucius resolves tree context automatically.
   - **Then** it exhausts the project tree catalog through the existing V2 tree API and retrieves both representations for every resolved project tree rather than guessing a default tree.
   - **And** automatic resolution requests active trees (`with_archived=false`); archived trees are not silently added to every launch response.
   - **And** a verified-empty tree catalog yields an empty tree collection, not an unavailable section.
   - **And** an explicitly supplied tree may be resolved with archived lookup enabled, but its `TreeDtoV2.project_id` must match the authoritative launch/resolved project before expansion; a cross-project tree returns a typed validation error.
   - **And** group/leaf discrimination uses the upstream `type` discriminator; ambiguous generated `oneOf` parsing must not cause Lucius to guess a node type.
   - **And** leaf `id` is retained as the Test Result ID/run ID for `get_test_result`, while group IDs remain typed as hierarchy group IDs.
   - **And** no tree leaf triggers a recursive rich-result fetch.

5. **Exhaust all pages and hierarchy branches safely**
   - **Given** flat/core result indexes, variables, defects, member statistics, muted results, retries, unresolved results, tree catalogs, tree widgets, or hierarchy nodes span multiple pages.
   - **When** execution enrichment runs.
   - **Then** Lucius requests the largest verified supported page size and follows pagination until every page is collected.
   - **And** successful earlier pages remain in the response if a later page fails.
   - **Given** a hierarchy group is returned.
   - **When** the complete result tree is assembled.
   - **Then** Lucius recursively requests that group's path, preserves parent/child structure and deterministic upstream ordering, and visits every branch.
   - **And** reusable pagination/tree collectors detect repeated pages, non-progressing metadata, duplicate/cyclic paths, malformed totals, and excessive upstream work.
   - **And** defensive page/request/node/depth guards exist only to prevent infinite or pathological upstream behavior; hitting a guard preserves collected data and reports the affected section incomplete rather than claiming full completion.
   - **And** there are no caller-facing page/size inputs for this complete aggregate: `include_execution_results=true` means collect all available data.

6. **Return best-effort data with exact completeness diagnostics**
   - **Given** the authoritative `GET /api/launch/{id}` base read fails.
   - **When** TestOps reports validation, authorization, not-found, or another failure.
   - **Then** existing typed launch errors and Agent Hints remain authoritative and no partial launch is fabricated.
   - **Given** `include_execution_results=true`, the base launch succeeds, but any optional section fails, is forbidden, is unsupported, cannot be safely parsed, or becomes incomplete after one or more successful pages/branches.
   - **When** `get_launch` returns.
   - **Then** it preserves every successful base/enrichment value, sets `partial=true`, and lists every affected section in `unavailable_sections`.
   - **And** each diagnostic contains a stable section path, safe reason, optional HTTP status, sanitized message, and retrieved item count where applicable.
   - **And** per-tree diagnostics identify the tree and representation/branch that is incomplete rather than marking unrelated tree data unavailable.
   - **And** verified-empty values remain typed empty values and are not listed as unavailable.
   - **And** credentials, authorization headers, response bodies, raw upstream URLs, and user/business payload data are never copied into diagnostics, logs, or telemetry.
   - **And** optional calls run concurrently only where independence and bounded work make that safe, using Python 3.10-compatible async primitives.
   - **And** the opt-in implementation obtains an authoritative base/raw launch response before any optional statistic/environment/job or execution request; it must not call the current all-in-one `AllureClient.get_launch` path if that path can propagate an optional-enrichment failure and erase the base.
   - **And** the opt-out path retains the pre-story `AllureClient.get_launch` behavior, including its existing output and error semantics.

7. **Identify open-launch data as a mutable point-in-time snapshot**
   - **Given** execution enrichment is requested.
   - **When** the response is composed.
   - **Then** it includes a typed `execution_snapshot` with a UTC capture timestamp, authoritative launch closed/open state, and a flag/message explaining whether the data can still change.
   - **And** an open/running launch is explicitly described as a point-in-time mutable snapshot in plain and JSON output.
   - **And** an open launch is not marked `partial` merely because TestOps may receive later results; `partial` is reserved for unavailable, unsafe, truncated, or failed reads.
   - **And** a closed launch may still be marked partial if one of its requested sections could not be collected.

8. **Generate only the missing client surface and reuse existing operations**
   - **Given** `launch-controller`, `test-result-flat-controller`, and `tree-controller-v-2` are already retained and generated.
   - **When** client work is implemented.
   - **Then** existing generated methods/models are reused for launch statistics, duration, environment, jobs, progress, assignees, testers, variables, defects, member statistics, muted rows, retries, unresolved rows, flat results, and project-tree discovery.
   - **And** `scripts/filter_openapi.py` additionally retains `test-result-tree-controller-v-2` for the real hierarchy endpoint.
   - **And** `./scripts/generate_testops_api_client.sh` regenerates `filtered-report-service.json` and `src/client/generated/`; generated files are never edited manually.
   - **And** the generated result-tree `oneOf` ambiguity is handled behind `src/client/`, preferably through the generated raw-response method plus explicit discriminator mapping, without leaking raw dictionaries above the client boundary.
   - **And** the implementation reviews generated diffs for unrelated upstream churn.

9. **Publish one stable output contract across MCP, CLI, and docs**
   - **Given** the expanded `get_launch` response.
   - **When** MCP schemas, structured content, CLI help, or documentation are inspected.
   - **Then** `LaunchDetailOutput` (or its replacement) is a concrete strict object-root model covering existing fields, optional execution sections, `execution_snapshot`, `partial`, and `unavailable_sections`.
   - **And** top-level `@output_fields`, nested output models, JSON serialization, plain rendering, generated CLI schemas, and MCP manifests are updated together.
   - **And** `lucius launch get` routes to the same tool/service behavior and documents `include_execution_results` and optional `tree_id`.
   - **And** MCP output remains `plain|json`; `table|csv` remain CLI-only and may render deterministic nested fallbacks without changing the tool payload.
   - **And** docs tell agents to take a result row's `id` and call `get_test_result(test_result_id=<id>)`; attachment discovery/download remains the responsibility of Stories 12.1-12.3 rather than this aggregate.

10. **Prove complete, partial, and non-recursive behavior end to end**
   - **Given** focused automated verification runs.
   - **When** unit, integration, schema, CLI, generated-artifact, agentic, and sandbox E2E tests execute.
   - **Then** they cover opt-in/off behavior, all read sections, every TestOps status without conflation, falsey values, automatic and explicit tree resolution, both tree representations, recursive branch/page exhaustion, exact result IDs, deterministic ordering, and no recursive result-detail calls.
   - **And** a controlled process-level E2E scenario uses a stub TestOps upstream where the authoritative launch succeeds and at least one optional endpoint/later page fails, then verifies successful tool output with `partial=true`, the correct incomplete section and retrieved-item count, preserved successful data, and no unsafe upstream details.
   - **And** the controlled failure E2E exercises the real tool/service/client and serialization path rather than only a service mock.
   - **And** sandbox E2E verifies a real launch's expanded snapshot, follows at least one returned result `id` through `get_test_result`, and verifies explicit/automatic tree behavior where the sandbox project provides tree data.
   - **And** the sandbox test does not deliberately corrupt or disable TestOps to test failure semantics; deterministic failure injection remains in the controlled local E2E.
   - **And** existing launch create/list/get/close/reopen/delete/upload/manual-result and test-result-detail suites remain green.

## Tasks / Subtasks

- [ ] **Task 0: Verify live launch/widget/tree payloads before mapping** (AC: 2-8)
  - [ ] Capture sanitized sandbox shapes for every direct launch read, flat/core result indexes, result timeline/defect trees, project tree catalog, tree widget, root hierarchy page, and nested group page.
  - [ ] Confirm page-size limits, sorting defaults, pagination metadata, tree path semantics, status serialization, and the exact `type` discriminator values for group and leaf nodes.
  - [ ] Confirm that `TestResultFlatDto.id`, muted/unresolved row `id`, retry row `id`/`previousRetry.id`, and hierarchy leaf `id` are Test Result IDs accepted by `get_test_result`.
  - [ ] Record upstream schema drift in typed fixtures/tests without committing tokens, raw response bodies containing business data, or evidence bytes.

- [ ] **Task 1: Retain and regenerate the V2 result-tree client** (AC: 4, 8)
  - [ ] Add `test-result-tree-controller-v-2` to `KEEP_TAGS` in `scripts/filter_openapi.py`.
  - [ ] Run `./scripts/generate_testops_api_client.sh`; inspect the filtered-spec/generated diff and never patch generated files by hand.
  - [ ] Verify the generated controller exposes `get_tree_entities` with `launchId`, `treeId`, `path`, search/filter, pagination, and sorting inputs.
  - [ ] Add/update generated-facade coverage so accidental filter removal fails tests.

- [ ] **Task 2: Add typed client-facade reads for every section** (AC: 2, 4-8)
  - [ ] Extend `src/client/client.py` controller imports/lifecycle and `_get_api` overloads only for the newly generated result-tree controller.
  - [ ] Add a core/raw exact-launch read that parses authoritative base and preview fields but performs no optional enrichment; keep the existing all-in-one `get_launch` path for opt-out compatibility.
  - [ ] Add typed facade wrappers for the currently unused launch-controller reads: duration, progress, assignees, testers, variables, defects, member stats, muted rows, retries, unresolved rows, and tree widget pages.
  - [ ] Add typed wrappers/projections for the already generated launch-scoped core test-result index, result-defect tree, and result timeline operations on `TestResultControllerApi`.
  - [ ] Reuse the existing statistic/environment/jobs enrichment, `list_launch_test_results`, `list_trees`, and `get_tree` behavior instead of duplicating HTTP calls.
  - [ ] Add a V2 result-tree facade that uses raw generated response handling plus explicit `type` discrimination if the generated `oneOf` cannot deserialize reliably.
  - [ ] Keep all TestOps network traffic and generated DTO/raw parsing inside `src/client/`; services must not call `httpx` or generated controllers directly.
  - [ ] Preserve typed `AllureValidationError`, `AllureAuthError`, `AllureNotFoundError`, and `AllureAPIError` translation.

- [ ] **Task 3: Build reusable complete pagination and hierarchy collectors** (AC: 4-6)
  - [ ] Reuse/generalize Story 12.1's collected-page/incomplete-section pattern where practical; do not create near-duplicate unbounded loops.
  - [ ] Implement page exhaustion that preserves earlier items on later failure and detects non-progress/cycles/malformed metadata.
  - [ ] Implement project-tree catalog exhaustion and result-tree recursion with visited-path tracking, parent-child preservation, and defensive request/depth/node limits.
  - [ ] Keep upstream ordering deterministic and define stable section paths for page/branch diagnostics.
  - [ ] Use bounded concurrency for independent sections/trees without spawning one task per unbounded result row.

- [ ] **Task 4: Extend the launch service's application-owned aggregate** (AC: 1-7)
  - [ ] Extend `LaunchService.get_launch` with `include_execution_results` and `tree_id`, keeping the authoritative base read fatal and optional reads best-effort.
  - [ ] Preserve the current client/service path byte-for-byte where practical when the option is false; for the opt-in path, call the new core/raw launch read first and only then start optional statistic/environment/job/execution work.
  - [ ] Organize enrichment orchestration so client methods perform API reads while the service owns completeness policy, page/tree collection, stable DTO mapping, and snapshot semantics.
  - [ ] Add typed service models for duration, progress, variables, defects, member stats, compact flat/core result indexes, result timeline/defect trees, muted/unresolved rows, retry references, tree descriptors/widgets/nodes, execution snapshot, and unavailable sections.
  - [ ] Deliberately map all stable upstream DTO fields and preserve falsey values; do not return generated models or raw dictionaries as the public service contract.
  - [ ] Keep status values exactly aligned with TestOps DTOs and retain upstream result `id` as the documented follow-up identifier.
  - [ ] When `tree_id` is omitted, resolve and expand every active project tree; when supplied, resolve active/archived exact tree metadata, require matching project ownership, and expand only that tree.
  - [ ] Never call `get_test_result` from launch aggregation and never fetch attachments here.

- [ ] **Task 5: Expand the strict launch output and renderer** (AC: 1-3, 6, 7, 9)
  - [ ] Add strict nested Pydantic models in `src/tools/output_schemas.py` for every execution section and diagnostic; keep `extra="forbid"` and an object-root schema.
  - [ ] Update `src/tools/launches.py:get_launch` arguments/docstring, `@output_fields`, serializer, and plain renderer together.
  - [ ] Keep the tool thin: validate/resolve context, call `LaunchService`, and render; no endpoint choreography, pagination, tree traversal, or try/except in the tool.
  - [ ] Make plain output expose actual compact result rows/tree data and explicit partial/snapshot state, not only aggregate counts.
  - [ ] Normalize immutable/tuple-backed service collections before strict output validation, following the Story 12.1 review fix.
  - [ ] Preserve the existing `get_launch` fields and manual-execution guidance when execution inclusion is off or on.
  - [ ] Omit every execution-only field, including snapshot and completeness diagnostics, when inclusion is off; add regression assertions against the pre-story JSON keys and plain text.

- [ ] **Task 6: Update CLI, schemas, docs, and agent guidance** (AC: 1, 3, 9)
  - [ ] Keep the existing canonical `launch/get` route and aliases; regenerate `src/cli/data/tool_schemas.json` after the signature/schema change.
  - [ ] Update `docs/tools.md`, `docs/mcp_manifest.json`, MCPB manifests, shell completions, and any generated tool inventory using repository scripts rather than hand-editing derived artifacts.
  - [ ] Document the opt-in cost, automatic tree resolution, all-pages behavior, snapshot semantics, and the exact follow-up call `get_test_result(test_result_id=<row.id>)`.
  - [ ] Update `tests/agentic/agentic-tool-calls-tests.md` with launch inspection followed by exact failed/broken/skipped result selection without status conflation.

- [ ] **Task 7: Add focused unit and integration coverage** (AC: 1-10)
  - [ ] Extend `tests/integration/test_launch_client.py` for every facade operation, the no-enrichment core read, exact path/query inputs, pagination, raw tree discrimination, result index/timeline/defect views, and typed error translation.
  - [ ] Extend `tests/unit/test_launch_service.py` for flag validation, exact opt-out key/output compatibility, every opt-in section, all row statuses plus aggregate-only `in_progress`, falsey values, automatic active-tree resolution, explicit archived/cross-project tree handling, all-page/branch collection, later-page preservation, cycle/guard handling, and deterministic diagnostics.
  - [ ] Extend `tests/unit/test_launch_tools.py`, `tests/unit/test_output_schemas.py`, and `tests/unit/test_tool_structured_outputs.py` for strict schema, plain/JSON parity, tuple normalization, snapshot state, and partial output.
  - [ ] Update `tests/unit/test_client_facade_coverage.py`, registry/annotation/manifest checks, CLI schema tests, and deterministic table/CSV fallback tests as applicable.
  - [ ] Assert no code path performs one rich result read per compact row or one launch detail read per `list_launches` item.

- [ ] **Task 8: Add controlled and sandbox E2E coverage** (AC: 3-7, 9, 10)
  - [ ] Add a controlled TestOps stub E2E that exercises the real `get_launch` tool path, fails an optional first or later page after base success, and asserts preserved data plus safe `partial`/`unavailable_sections` output.
  - [ ] Extend `tests/e2e/test_cli_entity_commands_uv_run.py` and/or `tests/e2e/test_cli_output_formats_uv_run.py` for `include_execution_results`, optional `tree_id`, default JSON, explicit plain, and clean validation hints.
  - [ ] Extend `tests/e2e/test_launches.py` with a real opt-in snapshot, all available sections supported by the sandbox, complete pagination assertions where test data can span pages, and bounded polling only for documented eventual consistency.
  - [ ] Follow one returned result `id` with `get_test_result` in sandbox E2E; do not duplicate its detail/evidence assertions in the launch aggregate test.
  - [ ] Cover automatic all-tree resolution and explicit tree selection when the sandbox exposes trees; otherwise record the environment limitation without weakening deterministic client/service/tree tests.
  - [ ] Preserve cleanup and all existing launch lifecycle/manual execution/result-detail scenarios.

- [ ] **Task 9: Validate generated artifacts and the implementation** (AC: 1-10)
  - [ ] Run the smallest touched unit/integration/schema suites first, then relevant source-invoked CLI and controlled E2E tests with `uv run`.
  - [ ] Run sandbox E2E with `uv run --env-file .env.test pytest ...` and report any unavailable live tree/section coverage precisely.
  - [ ] Run `uv run ruff check` on touched paths and `uv run mypy --strict src/`.
  - [ ] Run documentation, MCP manifest, MCPB manifest, generated-client/facade, tool registry, route, completion, and packaging consistency tests affected by regenerated artifacts.
  - [ ] Do not mark implementation complete if any section silently truncates, statuses are conflated, result IDs cannot drive `get_test_result`, or optional failures erase otherwise valid launch data.

## Dev Notes

### Confirmed public contract

```text
get_launch(
    launch_id: int,
    project_id: int | None = None,
    output_format: plain | json = <repository default>,
    include_execution_results: bool = False,
    tree_id: int | None = None,
)
```

- `include_execution_results=false` preserves the current launch-detail behavior and cost.
- `include_execution_results=true` requests the complete execution aggregate.
- `tree_id=None` means resolve every available project tree through TestOps and expand both tree representations.
- A supplied `tree_id` limits tree expansion to that verified tree.
- A supplied `tree_id` with execution inclusion disabled is invalid rather than ignored.

### Stable aggregate shape

Exact class names may follow repository conventions, but the semantic structure must remain explicit and strict:

```text
LaunchDetailOutput
├── existing launch identity/metadata/statistic/environment/jobs/tags/issues/links/guidance/url
├── duration
├── progress
├── assignees
├── testers
├── variables
├── defects
├── member_stats
├── muted_results
├── retries
├── unresolved_results
├── flat_test_results
├── core_test_result_index
├── result_timeline
├── result_defect_tree
├── trees[]
│   ├── tree metadata
│   ├── statistic_widget
│   └── hierarchy nodes[] (group | leaf, recursively nested)
├── execution_snapshot
├── partial
└── unavailable_sections[]
```

`flat_test_results` is the complete compact flat-result collection. `core_test_result_index`, `result_timeline`, and `result_defect_tree` preserve the distinct launch-scoped read views without recursively enriching rows or publishing an uncurated `TestResultDto` dump. Result collections contain every upstream status without merging categories. Failed tests are therefore actual rows with `status=failed`, broken tests have `status=broken`, and skipped tests have `status=skipped`; the same rule applies to other result-bearing sections. `in_progress` may appear in aggregate `StatisticDto` projections but is not a `TestStatus` row value.

### Authoritative identifier contract

The relevant TestOps execution DTOs expose the exact result/run identifier as `id`:

| Source DTO | Identifier meaning | Follow-up |
| --- | --- | --- |
| `TestResultFlatDto.id` | Test Result ID / TestOps run ID | `get_test_result(test_result_id=id)` |
| `TestResultRowDto.id` | Test Result ID for muted/unresolved row | `get_test_result(test_result_id=id)` |
| `TestResultRetriesRowDto.id` | Current retry Test Result ID | `get_test_result(test_result_id=id)` |
| `Retry.id` | Previous retry Test Result ID | `get_test_result(test_result_id=id)` |
| `TestResultTreeLeafDtoV2.id` | Hierarchy leaf Test Result ID | `get_test_result(test_result_id=id)` |
| `JobRunDto.id` | Job-run ID, not a Test Result ID | Do not pass as `test_result_id` |

Keep `id` to follow TestOps DTOs. Do not rename it to or duplicate it as `run_id`; make its meaning unambiguous through model names and descriptions.

### API surfaces and generation decision

| Section | Operation | Current state | Direction |
| --- | --- | --- | --- |
| Base | `GET /api/launch/{id}` | Generated/used | Authoritative fatal read |
| Statistics | `GET /api/launch/{id}/statistic` | Generated/used | Reuse |
| Environment | `GET /api/launch/{id}/env` | Generated/used | Reuse |
| Jobs | `GET /api/launch/{id}/job` | Generated/used | Reuse |
| Duration | `GET /api/launch/{id}/duration` | Generated/unused | Add facade projection |
| Progress | `GET /api/launch/{id}/progress` | Generated/unused | Add facade projection |
| Assignees/testers | `GET /api/launch/{id}/assignees`, `/tester` | Generated/unused | Add facade projections |
| Variables | `GET /api/launch/{id}/variables` | Generated/unused/paged | Exhaust pages |
| Defects | `GET /api/launch/{id}/defect` | Generated/unused/paged | Exhaust pages |
| Member stats | `GET /api/launch/{id}/memberstats` | Generated/unused/paged | Exhaust pages |
| Muted results | `GET /api/launch/{id}/muted` | Generated/unused/paged | Exhaust pages |
| Retries | `GET /api/launch/{id}/retries` | Generated/unused/paged | Exhaust pages |
| Unresolved results | `GET /api/launch/{id}/unresolved` | Generated/unused/paged | Exhaust pages |
| Flat results | `GET /api/v2/launch/{launchId}/test-result/flat` | Generated/wrapped | Reuse and exhaust pages |
| Core result index | `GET /api/testresult?launchId={id}` | Generated/unused/paged | Add compact projection and exhaust pages |
| Result defect tree | `GET /api/testresult/defects?launchId={id}` | Generated/unused | Add distinct tree projection |
| Result timeline | `GET /api/testresult/timeline?launchId={id}` | Generated/unused | Add distinct tree projection |
| Project trees | `GET /api/v2/tree` and exact tree read | Generated/wrapped | Reuse for automatic resolution |
| Tree widget | `GET /api/launch/{id}/widget/tree` | Generated/unused/paged | Fetch per resolved tree |
| Result hierarchy | `GET /api/v2/launch/{launchId}/test-result/tree/entity` | Full spec only | Retain tag and regenerate |

Only `test-result-tree-controller-v-2` requires generator expansion. The launch widgets and flat-result/project-tree clients already exist. Do not regenerate duplicate APIs or hand-edit `src/client/generated/`.

The result-tree response uses an ambiguous generated `oneOf` between group and leaf because both DTOs have optional fields and the discriminator lacks a mapping. Treat `type` as authoritative behind the client facade and add fixtures for both node kinds. Do not allow a generated deserialization ambiguity to escape as a raw `ValueError` or tempt the service/tool to parse upstream dictionaries.

### Completeness, snapshot, and performance rules

- The exact launch base read is authoritative. Do not use fuzzy name search, collection scanning, or a preview as existence authority.
- The opt-in service path must receive the base/raw launch result before optional statistic/environment/job/execution work begins. Add a client core-read split if needed; do not reuse an all-in-one method whose optional 5xx discards the base.
- Optional failures never erase the base or other successful sections.
- Exhaust every valid page/branch. Safety guards exist to stop malformed/cyclic upstream behavior, not to implement a silent product page limit.
- Preserve collected pages/branches on later failure and report precise `items_retrieved`.
- A verified empty section is `[]`/empty typed data, not unavailable.
- Automatic tree resolution means all active project trees, not an inferred default. Explicit archived-tree selection is allowed only after project ownership is verified.
- Do not perform one detail call per result or one detail call per launch-list item.
- Open-launch execution data is a mutable snapshot. This does not itself mean incomplete.
- Build capture timestamps with Python 3.10-compatible UTC APIs used elsewhere in the repository.
- Keep diagnostic ordering deterministic so schemas, plain output, CLI rendering, and tests remain stable.

### Existing code to reuse

| Need | Existing source | Required direction |
| --- | --- | --- |
| Exact rich launch read | `src/client/client.py:get_launch`; `src/services/launch_service.py:get_launch` | Preserve opt-out behavior; add a no-optional-enrichment core read for opt-in orchestration |
| Current rich merge | `LaunchDetailResponse`; `LaunchDetail`; `_launch_detail` | Evolve into stable aggregate rather than returning generated DTOs |
| Statistics/environment/jobs | `AllureClient._enrich_sparse_launch_preview` | Reuse reads; move completeness policy to service as needed |
| Flat result discovery | `AllureClient.list_launch_test_results`; `LaunchService.list_launch_test_results` | Reuse DTO mapping/statuses, but collect all without recursive detail |
| Core result/timeline/defect views | generated `TestResultControllerApi` | Add facade wrappers and compact non-recursive projections |
| Project trees | `AllureClient.list_trees`; `AllureClient.get_tree` | Reuse for automatic/explicit resolution |
| Complete pagination diagnostics | `src/services/test_result_service.py` | Reuse/generalize Story 12.1 collector semantics |
| Output schema/rendering | `src/tools/output_schemas.py:LaunchDetailOutput`; `src/tools/launches.py:_launch_detail_payload` | Extend strict projections and preserve plain/JSON parity |
| CLI route | `src/cli/route_matrix.py` existing launch/get mapping | Keep route; regenerate schema/help only |

### Architecture and regression guardrails

- **Thin Tool / Fat Service:** endpoint orchestration, completeness, tree traversal, DTO mapping, snapshot semantics, and pagination belong below `src/tools/`.
- **Client boundary:** all TestOps requests and raw/generated response parsing stay in `src/client/`.
- **Generated boundary:** change the filter and run the generator; never edit generated files manually.
- **Output boundary:** publish strict application-owned models; do not expose generated DTO dumps or open dictionaries.
- **Error boundary:** tools have no try/except. Base errors bubble as typed Agent Hints; optional errors become sanitized unavailable-section records.
- **CLI boundary:** keep the existing service/tool path and no-FastMCP-runtime-import rule.
- **Discovery/detail boundary:** `list_launches` stays compact; `get_launch` aggregate rows stay compact; `get_test_result` owns exact execution/attachment detail.
- **Attachment boundary:** Stories 12.2/12.3 own preparation/download. This story returns no attachment metadata, URLs, bytes, broker data, or base64.
- **Lifecycle regression:** create, list, close, reopen, delete, upload, manual execution, and exact result detail must retain their existing contracts.
- **Telemetry privacy:** never include raw upstream response bodies, result names, variables, issue content, credentials, or tree paths in telemetry; log only safe operation/outcome/count metadata.

### Library and runtime requirements

- Python `>=3.10,<3.15`; do not use `asyncio.TaskGroup` or syntax unavailable on Python 3.10.
- Use `uv` for all project commands.
- FastMCP `>=3.0.0`, Pydantic `>=2.12.5`, async `httpx >=0.28.1`, pytest, Ruff, and strict mypy.
- Generated client baseline: checked-in Allure TestOps OpenAPI `25.4.1`, upstream service commit `623f6ed302ba4b651cf9040faca4635af2d93b7c`.
- No new dependency is required.

### Source tree impact

| Component | Path | Expected action |
| --- | --- | --- |
| OpenAPI filter/spec | `scripts/filter_openapi.py`, `openapi/allure-testops-service/filtered-report-service.json` | Retain V2 result-tree controller and regenerate |
| Generated client | `src/client/generated/` | Regenerate only; never hand-edit |
| Client facade | `src/client/client.py`, possibly `src/client/__init__.py` | Add typed launch reads/result-tree parsing |
| Launch service | `src/services/launch_service.py` | Add opt-in aggregate, all-page/tree collection, partial and snapshot models |
| Launch tool/schema | `src/tools/launches.py`, `src/tools/output_schemas.py` | Add arguments, strict nested outputs, serializers, plain renderer |
| CLI/generated metadata | `src/cli/data/tool_schemas.json`, `docs/mcp_manifest.json`, `deployment/mcpb/manifest.*.json`, `deployment/shell-completions/` | Regenerate affected artifacts |
| Documentation | `docs/tools.md`, `tests/agentic/agentic-tool-calls-tests.md` | Document aggregate and follow-up workflow |
| Tests | `tests/unit/`, `tests/integration/`, `tests/e2e/`, `tests/docs/`, `tests/packaging/` | Add contract, controlled failure, sandbox, and regression coverage |

### Previous story intelligence

- Story 12.3 keeps `list_launch_test_results` compact and directs agents from compact discovery to `get_test_result`; preserve the same boundary here.
- Story 12.2/12.3 own authenticated evidence delivery. Story 12.4 must only expose the result ID needed to enter that workflow later.
- Story 12.1 established authoritative-base-first reads, full pagination, preserved earlier pages, explicit `partial`/`unavailable_sections`, strict application-owned DTOs, tuple normalization before output validation, plain/JSON parity, and non-recursive related references. Reuse those reviewed patterns.
- Story 10.3 established exact-ID launch authority, compact `list_launches`, current statistic/environment/job enrichment, zero preservation, and separate list/detail output schemas.
- Story 10.2 established `FAILED` plus `BROKEN` filtering only for the separate `failed_only` convenience flag. This story must not reuse that conflation in its complete raw-status result collection.
- Story 9.14 requires every changed tool output to retain a concrete object-root schema and regenerated manifest metadata.

### Git intelligence summary

- Story creation branch: `main` at `4946a64` (`feat(test-result): add complete result details (#353)`).
- That latest commit is the strongest implementation precedent for generated controller expansion, exact-result DTOs, bounded best-effort enrichment, full pagination, schemas, and sandbox follow-up.
- Existing uncommitted Story 12.2/12.3 epic, sprint, and story artifacts belong to the user and must be preserved; Story 12.4 is additive.
- Recent release/dependency commits do not require library upgrades or architecture changes for this story.

### Latest technical information

- The checked-in full OpenAPI and generated client are the repository-specific technical authority. No external library/version research changes the implementation decision.
- All requested launch read operations except the real V2 result hierarchy are already present in the filtered/generated client.
- The real hierarchy endpoint requires `treeId` and pages one `path` at a time; complete hierarchy retrieval therefore requires project-tree resolution plus recursive branch collection.
- The TestOps DTOs call the result/run identifier `id`; `run_id` is not an upstream field.

### References

- [Source: `specs/project-planning-artifacts/epics.md#Epic 12: Enhanced Launch and Test Result Management`]
- [Source: `specs/implementation-artifacts/12-1-retrieve-complete-individual-test-result-details.md`]
- [Source: `specs/implementation-artifacts/12-2-broker-authenticated-attachment-downloads-through-short-lived-capability-links.md`]
- [Source: `specs/implementation-artifacts/12-3-prepare-attachment-downloads-and-teach-agents-the-safe-evidence-workflow.md`]
- [Source: `specs/implementation-artifacts/10-3-align-launch-list-and-detail-dtos.md`]
- [Source: `specs/implementation-artifacts/10-2-manual-test-execution-inside-launches.md`]
- [Source: `specs/prd.md#Data Schemas & Formatting`; `specs/prd.md#Non-Functional Requirements`]
- [Source: `specs/architecture.md#Data Architecture`; `specs/architecture.md#API & Communication Patterns`; `specs/architecture.md#Implementation Patterns & Consistency Rules`]
- [Source: `specs/project-context.md#Critical Implementation Patterns`; `specs/project-context.md#Tool Names & Args`]
- [Source: `docs/development.md#Regenerating the API Client`; `docs/development.md#Testing`; `docs/development.md#Telemetry Privacy Note`]
- [Source: `scripts/filter_openapi.py`; `openapi/allure-testops-service/report-service.json`]
- [Source: `src/client/client.py:get_launch`; `src/client/client.py:list_launch_test_results`; `src/client/client.py:list_trees`; `src/client/client.py:get_tree`]
- [Source: `src/client/generated/api/launch_controller_api.py`; `src/client/generated/api/test_result_controller_api.py`; `src/client/generated/api/test_result_flat_controller_api.py`]
- [Source: `src/services/launch_service.py`; `src/services/test_result_service.py`]
- [Source: `src/tools/launches.py`; `src/tools/output_schemas.py`; `src/cli/route_matrix.py`]
- [Source: `tests/integration/test_launch_client.py`; `tests/unit/test_launch_service.py`; `tests/unit/test_launch_tools.py`; `tests/e2e/test_launches.py`]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story-context analysis only; no implementation or runtime tests were executed.
- Read-only analysis verified the full/filtered OpenAPI, current generated client, launch/result services and tools, output schemas, adjacent stories, tests, and git history.
- Regenerated the client from the checked-in OpenAPI after retaining `test-result-tree-controller-v-2`; inspected the resulting controller and generated diff.
- Read-only sandbox verification used launch `90358` and confirmed compact result IDs, active-tree metadata/hierarchy views, status fidelity, and an open-launch snapshot. No credentials or raw upstream response bodies were recorded.
- Focused launch/client/CLI tests pass (184 tests); project-wide Ruff and strict mypy checks pass. The combined unit/integration/docs suite exceeded this environment's 30-second command window and was not treated as passing.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added an opt-in complete launch execution aggregate while preserving compact launch discovery and existing exact-ID behavior.
- Defined automatic all-tree resolution, both tree representations, complete page/branch collection, exact result-ID follow-up, status fidelity, open-launch snapshots, and best-effort diagnostics.
- Required a controlled E2E failure scenario that proves partial responses through the real tool/service/client/serialization path.
- Confirmed only the V2 result-tree controller requires generated-client expansion.

### File List

- `docs/mcp_manifest.json`
- `docs/tools.md`
- `openapi/allure-testops-service/filtered-report-service.json`
- `scripts/filter_openapi.py`
- `src/cli/data/tool_schemas.json`
- `src/client/client.py`
- `src/client/generated/README.md`
- `src/client/generated/__init__.py`
- `src/client/generated/api/__init__.py`
- `src/client/generated/api/test_result_tree_controller_v2_api.py`
- `src/client/generated/docs/TestResultTreeControllerV2Api.md`
- `src/services/launch_service.py`
- `src/tools/launches.py`
- `src/tools/output_schemas.py`
- `tests/unit/test_launch_tools.py`
- `specs/project-planning-artifacts/epics.md`
- `specs/implementation-artifacts/sprint-status.yaml`
- `specs/implementation-artifacts/12-4-extend-get-launch-info-with-complete-execution-results.md`

### Change Log

- 2026-08-27: Added the opt-in launch execution aggregate, V2 result-tree client surface, CLI/MCP schemas, and focused regression coverage; story remains in progress pending the remaining exhaustive contract/E2E work.
