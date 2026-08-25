# Story 12.1: Retrieve Complete Individual Test Result Details

Status: in-progress

<!-- Note: This story was validated against the create-story checklist, current source, generated client, full/filtered OpenAPI, prior launch stories, and sprint artifacts. -->

## Story

As an **AI Agent**,
I want to **retrieve a complete, stable view of one test result using its Test Result ID, including execution details and authenticated direct attachment download links**,
so that **I can diagnose failures and download or analyze evidence without navigating TestOps manually or recursively loading related runs**.

## Acceptance Criteria

1. **Resolve the exact Test Result ID with launch URL context**
   - **Given** a TestOps link such as `/launch/89067/tree/1498142?treeId=172`.
   - **When** I call `get_test_result(test_result_id=1498142)`.
   - **Then** Lucius treats `1498142` as the Test Result ID and ignores `treeId`.
   - **And** the public tool has no `tree_id` input and does not parse or emit the `treeId` query parameter.
   - **And** the authoritative core read uses `GET /api/testresult/{id}` for the exact Test Result ID.
   - **And** the Test Result ID is validated as a positive integer.
   - **And** Lucius does not scan the launch or perform a separate client-side launch/result membership check.
   - **And** the response discloses the result's actual upstream `launch_id` when available.
   - **And** the result browser URL is `{base_url}/launch/{actual_launch_id}/tree/{test_result_id}` with no `treeId` query, using the authoritative result's upstream Launch ID.
   - **And** `result_url` is omitted and the relevant section is marked unavailable when the upstream result does not provide a verified Launch ID.

2. **Return a stable, curated, complete Lucius result DTO**
   - **Given** the authoritative Test Result exists.
   - **When** the response is composed.
   - **Then** application-owned strict DTOs expose all available verified fields grouped into stable sections rather than leaking generated DTO dumps or raw API dictionaries.
   - **And** the contract includes, where available:
     - identity and context: actual Launch ID, Test Result ID, Project ID, Test Case ID, result URL, launch URL, and Test Case URL;
     - name, full name, status, manual/external/hidden/flaky/muted/known flags;
     - start, stop, duration, creation, and modification metadata;
     - assignee, tester, creator, modifier, host, thread, scenario key, and history key;
     - description, precondition, expected result, their HTML forms, message, and trace;
     - category, layer, parameters, tags, and external links;
     - job/executor/source metadata;
     - custom fields, environment values, members, test keys, issues, and defects;
     - execution steps, fixtures, result/step/fixture attachments, and related-result references.
   - **And** valid `0`, `false`, empty string, and empty collection values are preserved rather than treated as missing.
   - **And** the published output schema has an object root and matches the actual structured payload.

3. **Preserve execution hierarchy and attachment ownership**
   - **Given** execution steps, fixtures, or attachments exist.
   - **When** Lucius builds the result detail.
   - **Then** it explicitly calls the verified V2 execution path with `v2=true` because resolved manual results may have an empty non-V2 execution.
   - **And** step hierarchy and supported step variants preserve status, timing, action/body, expected result, message, trace, parameters, and child steps.
   - **And** attachment child steps materialized by V2 execution remain attached to their owning step.
   - **And** result-level attachments remain on the result model.
   - **And** fixture scenario attachments remain on their fixture model.
   - **And** fixture attachment rows are reconciled with fixture-scoped scenario attachment steps by attachment ID and deduplicated at their owning fixture.
   - **And** when fixture ownership cannot be established, the fixture-attachment section is marked incomplete/unavailable rather than guessing ownership, duplicating evidence, flattening it into result attachments, or publishing an orphan attachment bucket.
   - **And** every attachment exposes its available ID, name, content type, content length, entity/discriminator, missed/from-test-case flags, storage metadata, and direct download URL.

4. **Provide stable bearer-authenticated attachment download URLs**
   - **Given** attachment metadata is returned.
   - **When** an agent follows `download_url`.
   - **Then** the URL contains no bearer token, signature, temporary credential, or expiry value.
   - **And** the agent can download it using the same TestOps bearer authentication used by Lucius.
   - **And** result attachments use `{base_url}/api/testresult/attachment/{attachment_id}/content?inline=false`.
   - **And** fixture attachments use `{base_url}/api/testfixtureresult/attachment/{attachment_id}/content?inline=false`.
   - **And** test-case-origin attachments use `{base_url}/api/testcase/attachment/{attachment_id}/content?inline=false` when the attachment discriminator requires that endpoint.
   - **And** endpoint selection is based on verified attachment entity/ownership; IDs are never routed through an unrelated content endpoint.
   - **And** the links are stable API paths, not presigned or time-limited links.

5. **Represent related results, retries, history, and runs as links only**
   - **Given** history entries, retries, `retried_by`, nested results, or related job/run references exist.
   - **When** Lucius includes them.
   - **Then** each related execution is projected to a compact typed reference containing the available relation, ID, identifying label/status, launch context, and stable URL.
   - **And** Lucius may page through history/retry indexes to discover all references.
   - **But** it never calls `get_test_result` recursively and never fetches full detail/enrichment for any referenced result or run.
   - **And** a URL is omitted rather than invented when the related launch/result context cannot be verified.

6. **Return best-effort partial results with explicit completeness diagnostics**
   - **Given** the authoritative base result read fails.
   - **When** the upstream API reports validation, authorization, not-found, or another failure.
   - **Then** the existing typed Lucius error and Agent Hint behavior remains authoritative and no partial result is fabricated.
   - **Given** the base result succeeds but an optional enrichment fails, is forbidden, is unsupported, cannot be fully paged, or cannot be safely associated.
   - **When** the response is returned.
   - **Then** all successful core and enrichment data is preserved.
   - **And** `partial` is `true` and `unavailable_sections` names every failed or incomplete section with a stable reason, optional HTTP status, sanitized message, and fetched item count where relevant.
   - **And** a verified-empty section is represented by its empty typed value and is not listed as unavailable.
   - **And** successful earlier pages are preserved if a later page fails, with the section explicitly marked incomplete.
   - **And** diagnostics never expose response bodies, authorization headers, tokens, attachment bytes, or unsafe upstream URLs.
   - **And** independent enrichments run concurrently where safe with bounded work and Python 3.10-compatible async primitives.

7. **Retrieve all pages without recursive expansion**
   - **Given** attachments, fixture attachments, history, retries, defects, or another enrichment is paginated.
   - **When** the tool requests complete details.
   - **Then** the service follows pagination, using the largest supported page size where appropriate, until the section is complete.
   - **And** pagination cannot silently stop at an existing default such as ten rows.
   - **And** malformed pagination or a safety bound produces collected data plus an explicit incomplete-section diagnostic rather than silent truncation or an infinite loop.

8. **Generate and use the required API client surfaces**
   - **Given** the checked-in full OpenAPI includes detail endpoints omitted by the current filtered client.
   - **When** this story is implemented.
   - **Then** `scripts/filter_openapi.py` retains these required controller tags:
     - `test-result-custom-field-controller`;
     - `test-result-defect-controller`;
     - `test-result-env-var-controller`;
     - `test-result-issue-controller`;
     - `test-result-members-controller`;
     - `test-result-test-key-controller`;
     - `test-fixture-result-attachment-controller`.
   - **And** `./scripts/generate_testops_api_client.sh` regenerates the filtered spec and `src/client/generated/`.
   - **And** developers never hand-edit generated files.
   - **And** the facade reuses existing core result, raw execution with explicit `v2=true`, fixture, result-attachment, history, and retry operations and adds only the missing typed wrappers.

9. **Expose the workflow consistently through MCP, CLI, documentation, and tests**
   - **Given** the new read-only tool is registered.
   - **When** MCP metadata or CLI help is inspected.
   - **Then** `get_test_result` has LLM-optimized argument documentation, read-only/idempotent annotations, and a `test-result` tag.
   - **And** the canonical CLI route is `lucius test-result get` (alias `tr`) and invokes the same tool/service behavior.
   - **And** MCP tool output remains `plain|json` with plain as the tool default, while the CLI keeps its existing JSON default and CLI-only table/CSV rendering behavior.
   - **And** plain and JSON output expose equivalent detail and clearly report partial/unavailable sections.
   - **And** `list_launch_test_results` remains compact and backward compatible as the discovery step before this exact rich read.
   - **And** docs show how `test_result_id=1498142` is extracted from the example URL while `treeId` is ignored.
   - **And** unit, integration, output-schema, registry, CLI, agentic, and sandbox E2E tests cover the complete contract.
   - **And** sandbox E2E tests download representative result-, step-, and fixture-level evidence through returned URLs using the same bearer token and verify bytes/content metadata.

## Tasks / Subtasks

- [ ] **Task 0: Verify live result and attachment contracts before mapping** (AC: 1-8)
  - [ ] Capture sanitized sandbox payload shapes for the exact result, V2 execution, fixtures, all optional enrichment endpoints, history, retries, and attachment lists.
  - [ ] Verify that the result browser URL uses the authoritative upstream Launch ID, omits `treeId`, and is absent when that context is unavailable; verify the three attachment content URL families against the sandbox.
  - [ ] Confirm which paginated APIs expose total/last metadata and establish a defensive termination rule.
  - [ ] Confirm how aggregate fixture attachment rows map to fixture-scoped scenario attachment steps; if ownership cannot be established, report the section incomplete without publishing orphan rows.
  - [ ] Record any upstream schema drift in tests/fixtures or story completion notes without committing secrets or attachment bytes.

- [ ] **Task 1: Expand the filtered OpenAPI and regenerate the client** (AC: 4, 8)
  - [ ] Add the seven required read-controller tags to `scripts/filter_openapi.py`.
  - [ ] Run `./scripts/generate_testops_api_client.sh` rather than modifying `src/client/generated/` manually.
  - [ ] Verify generated APIs/models expose custom fields, defects, environment values, issues, members, test keys, and fixture attachment content.
  - [ ] Review the generated diff for unrelated upstream churn and keep the checked-in filtered spec consistent.

- [ ] **Task 2: Add typed client-facade wrappers** (AC: 2-8)
  - [ ] Extend `src/client/client.py` controller imports, optional members, initialization, `_get_api` overloads, and typed wrappers using existing client lifecycle patterns.
  - [ ] Add facade wrappers for already-generated history and retry reads.
  - [ ] Add wrappers for every newly generated result enrichment read and fixture attachment content endpoint.
  - [ ] Reuse the core result, fixture, fixture-attachment, result-attachment, and result attachment content wrappers.
  - [ ] For execution, call `get_test_result_execution_raw(test_result_id, v2=True)` and map its curated shape, or introduce a new typed `get_test_result_execution_v2()` wrapper that explicitly sends `v2=true`; do not treat the existing non-V2 typed helper as a V2 request.
  - [ ] Keep all I/O asynchronous and route calls through existing `_call_api` / `_call_api_raw` error translation.

- [ ] **Task 3: Implement the curated result service and best-effort orchestration** (AC: 1-7)
  - [ ] Add `src/services/test_result_service.py` with application-owned frozen dataclasses (or the repository-equivalent immutable typed models) for the stable service contract.
  - [ ] Fetch the authoritative base result first; only after it succeeds, run independent optional enrichments concurrently with Python 3.10-compatible `asyncio.gather` patterns.
  - [ ] Implement reusable paginated collectors that preserve completed pages, detect non-progress/cycles, and report incomplete sections safely.
  - [ ] Map all core fields without truthiness loss, including zero/false/empty values.
  - [ ] Preserve step/fixture hierarchy, reconcile and deduplicate fixture attachments by ID, and never guess fixture association or expose orphan fixture evidence.
  - [ ] Project history/retries/related runs to link-only references and prohibit recursive detail calls.
  - [ ] Build deterministic `partial` and `unavailable_sections` state with sanitized diagnostics.
  - [ ] Do not scan launch results for membership; use only the authoritative result's upstream Launch ID for navigation URLs.

- [ ] **Task 4: Add verified URL helpers** (AC: 1, 4, 5)
  - [ ] Extend `src/utils/links.py` with a test-result browser URL helper that requires the authoritative upstream Launch ID and omits `treeId`.
  - [ ] Add entity-specific attachment download URL helpers for result, fixture-result, and test-case attachment content.
  - [ ] Normalize `base_url` consistently and never embed credentials or tokens.
  - [ ] Add direct unit coverage for every URL family and discriminator decision.

- [ ] **Task 5: Add the thin MCP tool and stable output schema** (AC: 2, 6, 9)
  - [ ] Add strict nested Pydantic output models in `src/tools/output_schemas.py` using `extra="forbid"` and the repository's schema conventions.
  - [ ] Add `get_test_result` to `src/tools/launches.py`; limit the tool to resolving context, calling `TestResultService`, and rendering the result.
  - [ ] Use `test_result_id` consistently in the public signature and documentation.
  - [ ] Add `@output_fields(...)` with the concrete top-level output model.
  - [ ] Implement complete JSON serialization and an LLM-readable plain renderer with explicit partial/unavailable reporting.
  - [ ] Keep try/except and endpoint choreography out of the tool.

- [ ] **Task 6: Register MCP/CLI/package metadata** (AC: 9)
  - [ ] Import, export, and register `get_test_result` in `src/tools/__init__.py` in the same change as its output schema.
  - [ ] Add read-only/idempotent annotations and the `test-result` tag in `src/tools/annotations.py`.
  - [ ] Add `"get": "get_test_result"` to the canonical `test_result` route in `src/cli/route_matrix.py` and alias it as `tr`.
  - [ ] Regenerate `src/cli/data/tool_schemas.json`, MCP documentation/manifest metadata, MCPB manifests, and shell completions using repository scripts.
  - [ ] Do not add a second CLI business path or import FastMCP runtime wiring into CLI execution.

- [ ] **Task 7: Add focused unit and integration coverage** (AC: 1-9)
  - [ ] Add `tests/unit/test_test_result_service.py` for complete mapping, all falsey values, verified-empty versus unavailable, each optional failure, later-page failure, pagination termination, hierarchy preservation, and non-recursion.
  - [ ] Add `tests/integration/test_test_result_client.py` for every wrapper, endpoint, query, response mapping, and typed error translation, including an exact assertion that execution sends `v2=true`.
  - [ ] Add `tests/unit/test_test_result_tools.py` for argument forwarding, JSON/plain parity, partial diagnostics, and attachment links.
  - [ ] Extend link, output-schema, structured-output, annotation, registry, facade-coverage, manifest, route-matrix, and completion tests.
  - [ ] Assert that only `test_result_id` is forwarded, the actual upstream Launch ID remains visible, and `result_url` uses only that authoritative ID.

- [ ] **Task 8: Add CLI, agentic, and sandbox E2E coverage** (AC: 1-9)
  - [ ] Extend the shared `uv run lucius` E2E suite for launch discovery, action help, route execution, default JSON, and representative plain rendering.
  - [ ] Update `tests/agentic/agentic-tool-calls-tests.md` with the example-link extraction workflow and attachment-analysis follow-up.
  - [ ] Add `tests/e2e/test_test_result_detail.py`, separate from manual-launch execution coverage, to obtain a real result with result, step, and fixture evidence.
  - [ ] Verify rich fields, attachment placement, related link-only output, result URL without `treeId`, and no recursive result calls.
  - [ ] Download returned evidence URLs with the same bearer auth and verify status, bytes, content type, and content length where available.
  - [ ] Keep deterministic partial-failure permutations in unit/integration tests rather than inducing sandbox failures.

- [ ] **Task 9: Update documentation and validate** (AC: 8, 9)
  - [ ] Update `docs/tools.md`, tool inventory/schema metadata, and any README launch workflow that enumerates supported actions.
  - [ ] Run focused unit/integration/schema/CLI checks first, then the sandbox E2E scenario with `.env.test`.
  - [ ] Run `uv run ruff check` on touched paths and `uv run mypy --strict src/`.
  - [ ] Run the relevant documentation, MCP manifest, MCPB manifest, registry, route, and generated-artifact consistency tests.
  - [ ] Do not mark the story done unless the returned links are proven downloadable in the sandbox or the story is explicitly blocked by a documented upstream capability.

## Dev Notes

### Developer Context

This is a rich exact-result read, not a replacement for compact discovery:

| Surface | Purpose | Contract |
|:--|:--|:--|
| `list_launch_test_results` | Discover result IDs inside a launch | Keep existing compact paginated items unchanged |
| `get_test_result` | Inspect one exact result and its evidence | New curated comprehensive DTO with partial diagnostics |
| Related history/retry/run references | Navigate to adjacent executions | Link-only; never recursively enrich |

The public signature should follow existing runtime-context and output conventions:

```text
get_test_result(
    test_result_id: int,
    project_id: int | None = None,
    output_format: plain | json = plain,
)
```

The example TestOps URL supplies the Test Result ID and upstream navigation context:

```text
https://noxtua.testops.cloud/launch/89067/tree/1498142?treeId=172
                                      ^^^^^             upstream launch context only
                                                 ^^^^^^^ test_result_id
```

`treeId=172` is UI tree state. It is intentionally ignored and is not part of the public contract.

`GET /api/testresult/{id}` is not launch-scoped. Lucius therefore accepts only the Test Result ID, does not add a launch scan, and exposes the actual upstream Launch ID only when TestOps returns it. The launch path segment in a copied UI URL is navigation context, not a tool argument.

### Stable Response Contract

Use strict, application-owned nested models. The exact class names may follow existing conventions, but the semantic shape must remain stable:

```text
TestRunResultDetail
├── actual_launch_id, test_result_id, project_id
├── url, launch_url, test_case
├── core metadata/status/timing/content/source
├── parameters, tags, links, custom_fields, environment
├── members, test_keys, issues, defects
├── execution.steps[]
│   └── attachments[] / child steps[]
├── fixtures[]
│   ├── scenario.steps[]
│   └── attachments[]  # reconciled/deduplicated by ID
├── result_attachments[]
├── related_results[]  # link references only
├── partial
└── unavailable_sections[]
```

`unavailable_sections` entries should use a bounded, sanitized model such as:

```json
{
  "section": "fixtures",
  "reason": "upstream_error",
  "status_code": 503,
  "message": "Fixture details are temporarily unavailable",
  "items_retrieved": 0
}
```

Do not place raw exceptions, HTTP bodies, headers, tokens, or arbitrary upstream URLs in this model.

The nested public DTOs must deliberately project these verified fields; regenerated or future upstream fields are excluded until they are intentionally added to the stable contract:

| Curated model | Stable fields |
|:--|:--|
| Test case reference | `id`, `name`, `url` |
| Category / layer | `id`, `name` and other verified identity/status fields required to distinguish the upstream category or layer |
| Parameter | `name`, `value`, `excluded`, `hidden` |
| Tag | `id`, `name` |
| External link | `name`, `type`, `url` |
| Job run / source | `id`, `name`, `status`, `stage`, `url`, `error_message`, `external_id`, nested job `id`, `name`, `type`, `url` |
| Custom field with values | nested custom field `id`, `name`, `required`, `single_select`, `locked`, `archived`, `default_custom_field_value_id`; values `id`, `name` |
| Environment value | `id`, `name`, nested variable `id`, `name` |
| Member | `id`, `name`, nested role `id`, `name` where provided |
| Test key | `id`, `integration_id`, `name`, `url` |
| Issue | `id`, `integration_id`, `integration_type`, `name`, `display_name`, `status`, `summary`, `url`, `closed` |
| Defect | `id`, `name`, `closed`, nested issue fields available on `DefectRowDto` |
| Fixture | `id`, `name`, `type`, `status`, `start`, `stop`, `duration`, `message`, `trace`, scenario, reconciled attachments |
| Execution step | discriminator/type, action/name/body/body JSON/expected result, keyword, status, start, stop, duration, message, trace, parameters, child steps, owned attachments |
| Attachment | `id`, `name`, `entity`, `content_type`, `content_length`, `missed`, `from_test_case`, `storage_key`, `download_url` where applicable |
| Related execution reference | `relation`, `test_result_id`, `launch_id`, `name`, `status`, `url` |
| Unavailable section | `section`, stable `reason`, optional `status_code`, sanitized `message`, `items_retrieved` |

### Existing Client Capabilities to Reuse

The current facade already exposes:

- exact result read: `AllureClient.get_test_result`;
- a typed non-V2 execution read plus raw execution reads;
- fixture reads and aggregate fixture-attachment listing;
- result-attachment listing and result attachment content reads.

The existing `get_test_result_execution()` helper does **not** send `v2=true` despite returning a V2-named generated model. Use `get_test_result_execution_raw(test_result_id, v2=True)` or add a dedicated typed V2 facade and assert the query parameter. The generated `TestResultControllerApi` already contains `find_history` and `find_retries`; add facade wrappers rather than regenerating duplicate operations.

The base `TestResultDto` already carries most core detail: audit fields, descriptions, duration, flags, names/keys, job run, layer/category, links, message/trace, parameters, IDs, retry pointer, timing/status, tags, and ownership fields. Map every field deliberately; do not use raw `model_dump()` as the agent contract.

### Required Generated Client Expansion

The full checked-in OpenAPI 25.4.1 contains these read endpoints, but `scripts/filter_openapi.py` currently removes their controller tags:

| Section | Endpoint | Required tag |
|:--|:--|:--|
| Custom fields | `GET /api/testresult/{testResultId}/cfv` | `test-result-custom-field-controller` |
| Defects | `GET /api/testresult/{testResultId}/defect` | `test-result-defect-controller` |
| Environment | `GET /api/testresult/{testResultId}/evv` | `test-result-env-var-controller` |
| Issues | `GET /api/testresult/{testResultId}/issue` | `test-result-issue-controller` |
| Members | `GET /api/testresult/{testResultId}/members` | `test-result-members-controller` |
| Test keys | `GET /api/testresult/{testResultId}/testkey` | `test-result-test-key-controller` |
| Fixture evidence content | `GET /api/testfixtureresult/attachment/{id}/content` | `test-fixture-result-attachment-controller` |

Regenerate through `./scripts/generate_testops_api_client.sh`; never hand-edit `src/client/generated/`. Inspect the generated diff because the script replaces the generated directory and the upstream full spec may introduce unrelated churn.

### Best-Effort and Performance Guardrails

- Core result read is authoritative and fatal on failure. Optional enrichment begins only after core success.
- Use bounded independent enrichment calls and Python 3.10-compatible async orchestration (`asyncio.gather`, not `asyncio.TaskGroup`).
- Preserve successful data when another section fails.
- Exhaust paginated sections; existing attachment helpers default to ten rows and cannot be called once for a complete response.
- Add cycle/non-progress protection to pagination. Never silently truncate.
- Do not recursively fetch history, retry, `retried_by`, nested-result, or job-run targets.
- Keep attachment bytes out of the detail response. Return metadata and authenticated URLs only.
- Do not log response bodies or evidence content. Existing telemetry privacy constraints remain unchanged.

### Architecture Compliance

- **Thin Tool / Fat Service:** endpoint choreography, best-effort policy, pagination, DTO mapping, and URL association belong below the tool layer.
- **Generated boundary:** generated APIs/models are replaced only by the documented filter/generator workflow.
- **Client boundary:** all TestOps network access remains in `src/client/`; services do not perform direct `httpx` requests.
- **CLI boundary:** CLI routes to existing tool/service behavior and must not import `src.main` or FastMCP runtime wiring.
- **Errors:** tools contain no try/except. Core errors bubble through typed Allure exceptions; optional errors become sanitized service diagnostics.
- **Output contracts:** register the concrete output model beside the tool; preserve tool `plain|json` and CLI `plain|json|table|csv` responsibilities.

### Library and Runtime Requirements

- Python `>=3.10,<3.15`; do not introduce syntax or asyncio APIs unavailable on Python 3.10.
- Use `uv` for all project commands.
- FastMCP `>=3.0.0`, Pydantic `>=2.12.5`, async `httpx >=0.28.1`, pytest, Ruff, and strict mypy.
- Generated client baseline: Allure TestOps OpenAPI `25.4.1`, upstream commit `623f6ed302ba4b651cf9040faca4635af2d93b7c`.
- No new dependency is required.

### Source Tree Impact

| Component | Path | Expected action |
|:--|:--|:--|
| OpenAPI filter/spec | `scripts/filter_openapi.py`, `openapi/allure-testops-service/filtered-report-service.json` | Add required tags and regenerate |
| Generated client | `src/client/generated/` | Regenerate; never hand-edit |
| Client facade | `src/client/client.py` | Add controller lifecycle and detail wrappers |
| Result service | `src/services/test_result_service.py`, `src/services/__init__.py` | New curated DTO/orchestration service |
| URL helpers | `src/utils/links.py` | Add verified result and attachment URL helpers |
| Test-result tool | `src/tools/launches.py` | Add thin `get_test_result` wrapper/renderers |
| Output schemas | `src/tools/output_schemas.py` | Add strict stable nested models |
| Tool registry/metadata | `src/tools/__init__.py`, `src/tools/annotations.py` | Register and classify the tool |
| CLI | `src/cli/route_matrix.py`, `src/cli/data/tool_schemas.json` | Add route and regenerate metadata |
| Package/docs metadata | `deployment/mcpb/manifest.*.json`, `deployment/shell-completions/`, `docs/mcp_manifest.json`, `docs/tools.md` | Regenerate/update as required |
| Tests | `tests/unit/`, `tests/integration/`, `tests/e2e/`, `tests/agentic/`, `tests/docs/`, `tests/packaging/` | Add contract and regression coverage |

### Testing Requirements

- Unit tests must cover every core field category, falsey-value preservation, every optional section failure, empty versus unavailable semantics, later-page failure, pagination non-progress, attachment ownership, URL selection, and non-recursion.
- Client integration tests must assert the exact generated controller operation, path/query inputs, pagination, response mapping, and existing typed error translation.
- Output tests must validate strict schemas, object-root publication, structured payload conformance, plain/JSON parity, registration, annotations, and manifest consistency.
- CLI tests must cover discovery, help, routing, default JSON, plain output, and clean errors through source invocation with `uv run lucius`.
- Sandbox E2E must read an actual result and download representative evidence through returned URLs with the same bearer token. It must verify bytes/content metadata and parent-level placement.
- Do not use live failure injection to prove best-effort behavior; keep those permutations deterministic in unit/integration tests.

### Previous Story Intelligence

- Story 10.1 established URL construction from the resolved client base/project context and prohibits inventing unverified links.
- Story 10.2 established result discovery, exact result/execution/fixture/attachment client surfaces, resolved-manual-result V2 execution semantics, and nested attachment child steps.
- Story 10.3 established stable application-owned rich DTOs, bounded optional enrichment, exact-ID authority, and verified-empty versus unavailable semantics for launches.
- Story 9.14 requires every new tool to publish a concrete output schema and keep generated manifests aligned.
- `list_launch_test_results` is intentionally compact. Do not expand or replace it as part of this story.

### Git Intelligence Summary

- Current branch at story creation: `main`, release commit `834050b` (`v0.14.4`), with no pre-existing worktree changes.
- Recent release/dependency commits do not change the result-detail design.
- Commit `63ddb0b` is the primary precedent for curated exact-ID detail, bounded enrichment, schema separation, and launch tool tests.
- Earlier manual-result work established the current launch result and attachment client/service layout; reuse it rather than adding parallel HTTP code.

### Latest Technical Information

- The checked-in full OpenAPI and generated client are the repository-specific sources of truth. External browsing was unavailable at story creation because the configured browser harness required Chrome remote-debugging approval.
- The filtered client already includes the core Test Result controller; client generation is still required because seven requested read surfaces are currently filtered out.
- Fixture attachment content has its own verified OpenAPI path and must not be routed through the result attachment endpoint.
- The exact result API accepts only Test Result ID. The story intentionally does not add a Lucius membership scan; the launch segment in a copied UI URL is navigation context only.

### References

- [Source: specs/project-planning-artifacts/epics.md#Epic 12: Enhanced Launch and Test Result Management]
- [Source: specs/project-planning-artifacts/epics.md#Epic 5: Execution Management]
- [Source: specs/project-planning-artifacts/epics.md#Epic 10: Quality of Life and API Coverage]
- [Source: specs/implementation-artifacts/10-2-manual-test-execution-inside-launches.md#Observed Sandbox Semantics]
- [Source: specs/implementation-artifacts/10-3-align-launch-list-and-detail-dtos.md#Architecture and Implementation Guardrails]
- [Source: specs/implementation-artifacts/5-2-get-launch-details.md#Dev Notes]
- [Source: specs/prd.md#Data Schemas & Formatting]
- [Source: specs/prd.md#Non-Functional Requirements]
- [Source: specs/architecture.md#Data Architecture]
- [Source: specs/architecture.md#API & Communication Patterns]
- [Source: specs/architecture.md#Implementation Patterns & Consistency Rules]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: specs/project-context.md#Tool Names & Args]
- [Source: docs/development.md#Adding a New Tool]
- [Source: docs/development.md#Regenerating the API Client]
- [Source: scripts/filter_openapi.py#Tags to keep]
- [Source: openapi/allure-testops-service/report-service.json]
- [Source: src/client/client.py#Launch operations]
- [Source: src/client/generated/models/test_result_dto.py]
- [Source: src/client/generated/api/test_result_controller_api.py]
- [Source: src/client/generated/api/test_result_attachment_controller_api.py]
- [Source: src/client/generated/api/test_result_fixture_controller_api.py]
- [Source: src/services/launch_service.py]
- [Source: src/tools/launches.py]
- [Source: src/tools/output_schemas.py]
- [Source: src/utils/links.py]
- [Source: tests/integration/test_launch_client.py]
- [Source: tests/unit/test_launch_service.py]
- [Source: tests/unit/test_launch_tools.py]
- [Source: tests/e2e/test_launch_manual_execution.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story-context analysis only; no implementation or runtime tests were executed.
- External browser research was attempted but blocked by Chrome remote-debugging approval; local OpenAPI 25.4.1, generated client, current source, and completed sandbox-informed stories were used as technical authority.
- Regenerated the filtered OpenAPI client with all seven requested read-controller tags, then ran focused lint, strict typing, registry, CLI, documentation, unit, integration, and sandbox checks.
- Sandbox E2E verified the exact curated read and authenticated result/step evidence paths. A read-only scan found no fixture attachment sample in the accessible sandbox launch data, so fixture download remains unverified live.
- Renamed the public tool to `get_test_result` and moved its CLI surface from launch management to `lucius test-result get` (alias `lucius tr get`), matching TestOps' `/testresult/{id}` resource.
- Split coverage into dedicated result-service/tool unit tests, client integration tests, CLI route tests, and `test_test_result_detail.py` sandbox E2E rather than extending the manual-launch submission test.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Created new Epic 12, **Enhanced Launch and Test Result Management**, and Story 12.1.
- Defined `test_result_id` extraction from TestOps result links and explicitly ignored `treeId`.
- Required a stable curated Lucius DTO, non-recursive related-result links, entity-level attachment placement, permanent bearer-authenticated evidence URLs, and explicit best-effort completeness diagnostics.
- Confirmed generated client regeneration is necessary for seven read-controller families present in the full OpenAPI but absent from the filtered client.
- Implemented the in-progress exact-result service, facade wrappers, URL helpers, MCP/CLI registration, generated metadata, docs, and deterministic unit coverage.
- Focused validation passed: Ruff formatting/linting, strict mypy, dedicated unit/integration/CLI/metadata checks, and 5 sandbox E2E tests (the separate result-detail test plus manual-launch workflow).
- Blocker: fixture-level attachment download could not be exercised because the configured sandbox returned no fixture attachment evidence during a read-only scan. Keep this story in progress until a fixture-evidence sample is available or the environment is explicitly waived.

### File List

- specs/project-planning-artifacts/epics.md
- specs/implementation-artifacts/12-1-retrieve-complete-individual-test-result-details.md
- specs/implementation-artifacts/sprint-status.yaml
- scripts/filter_openapi.py
- openapi/allure-testops-service/filtered-report-service.json
- src/client/client.py
- src/client/generated/
- src/services/test_result_service.py
- src/services/__init__.py
- src/utils/links.py
- src/tools/launches.py
- src/tools/output_schemas.py
- src/tools/__init__.py
- src/tools/annotations.py
- src/cli/route_matrix.py
- src/cli/data/tool_schemas.json
- docs/mcp_manifest.json
- docs/tools.md
- deployment/mcpb/manifest.uv.json
- deployment/mcpb/manifest.python.json
- deployment/shell-completions/
- tests/unit/test_test_result_service.py
- tests/unit/test_test_result_tools.py
- tests/unit/test_launch_tools.py
- tests/unit/test_links.py
- tests/integration/test_test_result_client.py
- tests/e2e/test_launch_manual_execution.py
- tests/e2e/test_test_result_detail.py
- tests/e2e/test_cli_entity_commands_uv_run.py
- tests/agentic/agentic-tool-calls-tests.md
- README.md

### Change Log

- 2026-08-25: Created Epic 12 and Story 12.1; marked the story ready for development.
- 2026-08-25: Began implementation; regenerated required client surfaces and added the curated exact-result read. Story remains in progress pending live fixture-evidence download validation.
- 2026-08-25: Renamed the tool to `get_test_result`, added `test-result`/`tr` CLI routing, updated documentation and generated metadata, and separated result-detail unit, integration, and E2E coverage.

### Review Findings

- [x] [Review][Patch] [P0] Normalize tuple-backed detail collections before strict MCP output validation; the default structured path rejects them as non-lists. [src/tools/launches.py:402]
- [x] [Review][Patch] [P1] Preserve previously collected paginated items and report the later-page failure as incomplete instead of discarding the entire section. [src/services/test_result_service.py:256]
- [x] [Review][Patch] [P1] Omit related-result URLs when the related item does not provide a verified launch ID. [src/services/test_result_service.py:430]
- [x] [Review][Patch] [P1] Reconcile fixture attachment rows with their scenario-step owners and select download endpoints from the verified attachment discriminator. [src/services/test_result_service.py:328]
- [x] [Review][Patch] [P1] Replace open-ended result-detail dictionaries with strict application-owned nested output models and projections. [src/tools/output_schemas.py:361]
- [x] [Review][Patch] [P1] Render the actual rich result data in plain output, rather than only collection counts, to preserve plain/JSON parity. [src/tools/launches.py:1022]
- [x] [Review][Patch] [P2] Deduplicate repeated fixture attachment IDs at their owning fixture. [src/services/test_result_service.py:393]

### Review Findings — Pass 1 (2026-08-25)

- [x] [Review][Patch] [P1] Return plain text by default from the MCP tool, as required by the story contract. [src/tools/launches.py:386]
- [x] [Review][Patch] [P1] Unwrap generated fixture scenario one-of step values before mapping their fields and attachments. [src/services/test_result_service.py:387]
- [x] [Review][Patch] [P1] Preserve attachment steps that provide only `attachmentId`, so evidence remains on its owning step or fixture. [src/services/test_result_service.py:388]
- [x] [Review][Patch] [P2] Preserve upstream `project_id=0` instead of replacing it with the configured project. [src/services/test_result_service.py:145]
- [x] [Review][Patch] [P2] Mark contradictory or non-progressing pagination metadata as incomplete instead of silently accepting the collected subset. [src/services/test_result_service.py:283]
- [x] [Review][Patch] [P2] Reject boolean values for Test Result IDs. [src/services/test_result_service.py:508]
- [x] [Review][Patch] [P2] Mark a non-positive upstream launch ID as unverified context. [src/services/test_result_service.py:183]
- [x] [Review][Patch] [P2] Do not label a test-case reference with the test-result name. [src/services/test_result_service.py:353]
