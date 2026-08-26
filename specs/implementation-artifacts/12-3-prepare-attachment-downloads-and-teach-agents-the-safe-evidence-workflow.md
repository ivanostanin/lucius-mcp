# Story 12.3: Prepare Attachment Downloads and Teach Agents the Safe Evidence Workflow

Status: ready-for-dev

## Story

As an **AI Agent**,
I want **a discoverable `prepare_attachment_download` tool and attachment-producing tool descriptions that teach the prepare-then-GET workflow**,
so that **I can download evidence safely without trying to read base64 into context or call an unauthenticated TestOps URL**.

## Acceptance Criteria

1. **Expose one clear preparation tool**
   - **Given** Story 12.2's broker implementation is available but has not been initialized.
   - **When** an agent calls `prepare_attachment_download`.
   - **Then** the public input requires `attachment_id`, `attachment_kind` (`test_result`, `fixture_result`, or `test_case`), and the relevant verified owner context (`test_result_id` or `test_case_id`), plus optional `project_id` and repository-standard `output_format`.
   - **And** mutually incompatible/missing owner inputs, non-positive IDs, unsupported kinds, cross-owner IDs, and expired/unavailable delivery contexts return typed actionable errors.
   - **And** the thin tool resolves authenticated context, verifies ownership, delegates to the broker service, and renders its typed result; it contains no direct HTTP, cache, token, or gateway choreography.
   - **And** it is the public trigger for lazy broker initialization only after public input and ownership validation succeed; invalid calls must not initialize the broker.
   - **And** the public result contains only attachment metadata, `download_url`, and `expires_at`; it never contains attachment bytes, base64, TestOps authorization headers, API tokens, raw TestOps content URLs, or filesystem cache paths.

2. **Make the returned URL an explicit prepare-then-GET contract**
   - **Given** preparation succeeds.
   - **When** the result is rendered in default structured output, explicit JSON, or plain output.
   - **Then** it tells the agent: first call `prepare_attachment_download`; then use an HTTP `GET` on the returned `download_url` before `expires_at`; the URL needs no Allure bearer header.
   - **And** it identifies the URL as one-time/short-lived and explains that a new preparation is required after expiry or successful retrieval.
   - **And** the tool description and parameter descriptions are concise enough for natural model selection, including the terms “prepare”, “download”, “attachment”, and “GET”.

3. **Replace unsafe attachment guidance in all attachment-producing read tools**
   - **Given** `get_test_result` returns result-, step-, or fixture-level attachment metadata.
   - **When** an MCP client, CLI user, or agent inspects its tool description/help/result.
   - **Then** every attachment provides stable metadata needed to prepare it: attachment ID, name, content type, content length when available, verified kind, and required owner context.
   - **And** the tool description, `Returns` documentation, plain renderer, JSON schema descriptions, `docs/tools.md`, generated tool schemas, and MCP manifest state: “Call `prepare_attachment_download` with the attachment reference, then HTTP GET the returned Lucius URL.”
   - **And** it does not expose or recommend a bearer-authenticated TestOps `download_url`.
   - **Given** `get_test_case_details` returns test-case attachment IDs.
   - **When** its documentation/help/result is inspected.
   - **Then** it gives the same `test_case` preparation guidance and includes the owner context needed by the preparation tool.
   - **And** no tool that only accepts attachment uploads is misleadingly described as a download mechanism.

4. **Keep existing output and discovery contracts correct**
   - **Given** `get_test_result` and `get_test_case_details` already publish concrete output schemas.
   - **When** raw upstream download URLs are removed/replaced.
   - **Then** their strict output models, top-level `@output_fields`, structured content, and plain/JSON parity are updated together.
   - **And** an attachment record's kind/owner contract is typed and validates against its published schema.
   - **And** `list_launch_test_results` remains compact; it may direct agents to `get_test_result` to discover attachment metadata but must not add rich attachment payloads to every list row.
   - **And** existing normal outputs retain their unrelated fields and partial-diagnostic semantics.

5. **Register MCP, CLI, generated metadata, and documentation**
   - **Given** the new tool is implemented.
   - **When** MCP registry, manifest, CLI help, and route discovery are generated.
   - **Then** `prepare_attachment_download` is imported/exported/registered in `src/tools/__init__.py`, has a concrete object-root output schema, and is annotated read-only/idempotent with attachment/test-result/test-case tags.
   - **And** the canonical CLI route is unambiguous and uses the same tool/service behavior (recommended: `lucius attachment prepare-download`; aliases may be added only through the canonical route matrix).
   - **And** CLI maintains its no-FastMCP-runtime-import boundary and default JSON behavior; `table|csv` remain CLI-only formatting choices.
   - **And** `src/cli/data/tool_schemas.json`, `docs/mcp_manifest.json`, MCPB manifests, shell completions, `docs/tools.md`, and any route/registry documentation are regenerated with repository scripts rather than hand-edited derived files.

6. **Prove natural agent use and cache cleanup end to end**
   - **Given** a sandbox result with result, step, fixture, and a test case with attachment metadata.
   - **When** an agent follows documented discovery.
   - **Then** it calls the read tool, selects a typed attachment reference, calls `prepare_attachment_download`, and performs `GET` on the returned Lucius URL without an Allure bearer token.
   - **And** the downloaded content matches expected bytes, MIME type, filename, and size where available.
   - **And** a second GET of the same one-time URL fails safely, cache cleanup occurs, and a newly prepared URL works until its expiry.
   - **And** agentic documentation records this exact sequence and compares the observed output with its expectation.

## Tasks / Subtasks

- [ ] **Task 1: Define public prepare-tool contract and typed outputs** (AC: 1, 2, 4)
  - [ ] Add strict input validation and an application-owned result model (for example `PreparedAttachmentDownloadOutput`) in the appropriate tool output schema module.
  - [ ] Use one public `attachment_kind` enum and owner-context contract across result, fixture, and test-case attachments; do not create separate near-duplicate public tools.
  - [ ] Decide exact canonical route naming once, update `src/cli/route_matrix.py`, and add the matching entity/action aliases only where route-matrix conventions permit.
  - [ ] Ensure the public result does not disclose cache keys, private paths, raw upstream URLs, credentials, or content.
  - [ ] Ensure invalid input fails before the broker lazy initializer is requested.

- [ ] **Task 2: Add the thin MCP/CLI façade** (AC: 1, 5)
  - [ ] Add `prepare_attachment_download` to a feature-appropriate tool module, using the existing client context/auth-resolution helpers and the Story 12.2 broker service.
  - [ ] Add it to `src/tools/__init__.py` imports, `__all__`, and `all_tools`; update `src/tools/annotations.py` read-only policy/tags and output-schema coverage.
  - [ ] Keep tool errors global/typed; do not catch transport/client errors in the tool.
  - [ ] Trigger the broker only after the tool's validation and ownership checks; do not initialize it during tool registration or adapter startup.
  - [ ] Regenerate CLI schema data using `scripts/build_tool_schema.py` and validate direct CLI routing through the existing service-first command runner.

- [ ] **Task 3: Migrate result and test-case attachment contracts/guidance** (AC: 2-4)
  - [ ] Update `src/tools/launches.py:get_test_result` docstring, parameter/return descriptions, plain renderer, output models, and serialized attachment payloads.
  - [ ] Update `src/tools/search.py:get_test_case_details` docstring, plain renderer, output model/schema descriptions, and serialized attachment payloads.
  - [ ] Replace each raw TestOps `download_url` with typed preparation fields (`attachment_id`, `attachment_kind`, owner ID/context) and a concise `prepare_attachment_download` instruction.
  - [ ] Preserve all 12.1 attachment hierarchy/ownership rules: result attachments stay on the result, step attachments stay on steps, and fixture attachments remain on verified fixtures.
  - [ ] Update `docs/tools.md` descriptions for `get_test_result`, `get_test_case_details`, and `prepare_attachment_download` so an agent sees the same workflow outside the tool call.

- [ ] **Task 4: Regenerate all derived metadata and package surfaces** (AC: 3, 5)
  - [ ] Regenerate `docs/mcp_manifest.json`, CLI schemas, MCPB manifests, and shell completions using established scripts; do not hand-edit generated files.
  - [ ] Update tool-registry, output-schema, route-matrix, completion, manifest, and package tests for the new registered tool and the changed attachment output models.
  - [ ] Update agentic inventory/expectations in `tests/agentic/agentic-tool-calls-tests.md`.

- [ ] **Task 5: Add focused and sandbox workflow tests** (AC: 1-6)
  - [ ] Add unit tests for tool argument forwarding, public output redaction, plain/JSON parity, schema validation, annotations, tags, and tool registration.
  - [ ] Update existing `tests/unit/test_test_result_service.py`, `tests/unit/test_test_result_tools.py`, and `tests/e2e/test_test_result_detail.py` expectations from raw bearer-authenticated URLs to preparation fields and broker URLs.
  - [ ] Add/extend test-case detail coverage for typed attachment preparation references.
  - [ ] Add CLI source/invocation tests for route discovery, help wording, default JSON, aliases, and no-FastMCP-runtime imports.
  - [ ] In sandbox E2E and manual agentic validation, prove `read → prepare → GET → cleanup` without passing TestOps credentials to the second GET.

## Dev Notes

### User-facing workflow to encode verbatim where practical

```text
1. Call get_test_result or get_test_case_details to discover attachment metadata.
2. Select the attachment's ID, kind, and owner context.
3. Call prepare_attachment_download.
4. HTTP GET the returned download_url before expires_at; do not send an Allure bearer token.
5. The URL is one-time/short-lived. Prepare again if it expires or has already been fetched.
```

The words **prepare**, **attachment**, **download**, and **GET** must appear in the public tool descriptions for `prepare_attachment_download`, `get_test_result`, and `get_test_case_details`. This is prompt-engineering behavior, not optional prose. It allows an agent that sees attachment metadata to select the preparation tool naturally rather than attempting to fetch the old TestOps endpoint.

### Do not preserve the old raw download contract

Story 12.1 intentionally exposed stable TestOps content URLs that required the same bearer authentication as Lucius. This story supersedes that surface. Remove/replace the public raw `download_url` fields and their old claims in descriptions, manifests, and tests in the same change. The new Lucius `download_url` exists only in the output of `prepare_attachment_download` and is an opaque short-lived broker URL.

Do not return attachment content as text, base64, an embedded MCP resource, or a direct upstream URL. The caller must retrieve the prepared URL out-of-band with HTTP GET. A capability URL is a secret for its short lifetime; descriptions and logs must not encourage copying it into public text or telemetry.

### Existing source patterns

| Area | Files | Direction |
| --- | --- | --- |
| Result tool/format | `src/tools/launches.py`, `src/tools/output_schemas.py` | Update concise public guidance and strict attachment fields while preserving 12.1 hierarchy/partial DTO behavior. |
| Test-case detail | `src/tools/search.py`, `src/services/search_service.py` | Add typed `test_case` preparation references and matching help wording. |
| Tool registration | `src/tools/__init__.py`, `src/tools/annotations.py` | Add import/export/registry, output coverage, read-only hints, and tags together. |
| CLI parity | `src/cli/route_matrix.py`, `src/cli/command_runner.py`, `src/cli/data/tool_schemas.json` | Add route schema and help without a second business path or runtime imports. |
| Derived docs | `docs/tools.md`, `docs/mcp_manifest.json` | Regenerate/update descriptions so every agent-facing surface says prepare then GET. |
| Existing tests | `tests/unit/test_test_result_tools.py`, `tests/unit/test_output_schemas.py`, `tests/e2e/test_test_result_detail.py` | Migrate old raw bearer URL assertions to the broker workflow. |

### Scope boundaries

- Depends on Story 12.2. Do not duplicate cache, token, server-route, cleanup, or lazy-initializer implementation in this story.
- `prepare_attachment_download` is the only new public tool that triggers the broker, and only after validation and ownership verification; it must not be initialized at registration or startup.
- `list_launch_test_results` is discovery-only; do not add attachment payloads or N+1 result reads to its collection response.
- Keep `plain|json` as the MCP tool output contract. CLI table/CSV behavior remains adapter-only.
- Do not change upload tools (`add_test_result_attachment`, `add_test_step_attachment`) into download tools. Their descriptions may link to the safe evidence workflow only if they return a readable attachment reference.
- Do not hand-edit generated OpenAPI client output, CLI schema data, manifests, MCPB artifacts, or completions.

### Testing requirements

Run focused unit/integration/CLI/schema checks first with `uv run`, then `uv run ruff check <touched paths>` and `uv run mypy --strict src`. Run sandbox E2E with `.env.test` and preserve the existing cleanup tracker. Manual agentic validation must report cache deletion/expiry behavior and must not expose test tokens or evidence content in the report.

### References

- [Source: `specs/implementation-artifacts/12-2-broker-authenticated-attachment-downloads-through-short-lived-capability-links.md` — prerequisite broker and transport contract]
- [Source: `specs/implementation-artifacts/12-1-retrieve-complete-individual-test-result-details.md` — current exact-result attachment DTO and tests]
- [Source: `src/tools/launches.py:get_test_result`; `src/tools/search.py:get_test_case_details` — attachment-producing public tools]
- [Source: `src/tools/output_contract.py`; `src/tools/output_schemas.py`; `src/tools/annotations.py` — output/schema/registry conventions]
- [Source: `src/cli/route_matrix.py`; `src/cli/command_runner.py`; `specs/implementation-artifacts/9-3-service-first-cli-entity-action.md` — CLI parity and runtime boundary]
- [Source: `docs/development.md` — validation and telemetry privacy requirements]

## Dev Agent Record

### Agent Model Used

GPT-5

### Debug Log References

- Story-context research confirmed 12.1 currently returns direct URLs that require bearer authentication and cannot be used by an unauthenticated agent GET.
- Story-context research identified `get_test_result` and `get_test_case_details` as the existing attachment-producing read tools requiring explicit prepare-then-GET guidance.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- This story deliberately makes the safe attachment workflow part of tool descriptions, schema descriptions, generated CLI help, documentation, and agentic validation.

### File List

- `specs/project-planning-artifacts/epics.md`
- `specs/implementation-artifacts/sprint-status.yaml`
- `specs/implementation-artifacts/12-3-prepare-attachment-downloads-and-teach-agents-the-safe-evidence-workflow.md`
