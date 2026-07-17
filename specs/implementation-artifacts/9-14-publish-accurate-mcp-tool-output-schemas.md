# Story 9.14: Publish Accurate MCP Tool Output Schemas

Status: review

## Story

As an MCP client or AI agent,
I want every Lucius tool to publish an accurate structured-output schema,
so that I can reliably understand and validate the JSON payload returned by each tool.

## Acceptance Criteria

1. **Every registered tool publishes a concrete schema**
   - **Given** FastMCP lists Lucius tools or `docs/mcp_manifest.json` is regenerated
   - **When** a client inspects any of the registered tools
   - **Then** its `outputSchema` is a non-null JSON Schema object with an object root
   - **And** schemas are generated from an explicit Pydantic v2 output model using serialization mode and aliases (`model_json_schema(mode="serialization", by_alias=True)`)
   - **And** every tool name in `src.tools.all_tools` has exactly one schema registration and no stale/unknown registration exists.

2. **Schemas describe the actual structured JSON contract, not a generic wrapper**
   - **Given** the structured response for a tool's omitted `output_format` or explicit `output_format="json"`
   - **When** the tool returns success, empty-collection, confirmation-required, or another normal documented response branch
   - **Then** `structuredContent` validates against that tool's registered Pydantic model/schema
   - **And** field names, nesting, scalar types, nullable fields, arrays, pagination envelopes, URLs, and discriminator/status fields match the actual JSON payload
   - **And** schemas must not be the former generic `{"result": "string"}` wrapper or an unconstrained `dict[str, Any]` substitute.

3. **FastMCP registration preserves the existing output-format behavior**
   - **Given** FastMCP 3.4.4 receives a tool registered with an explicit output schema
   - **When** Lucius returns a default or `json` response
   - **Then** FastMCP publishes the existing flat payload as `structuredContent` without an `x-fastmcp-wrap-result` envelope
   - **And** a tool called with `output_format="plain"` continues to provide its existing text output to direct callers and the CLI
   - **And** the MCP registration/wrapper converts the plain path to a text-only `ToolResult` when necessary, so FastMCP never attempts to publish a scalar as structured content.

4. **Schema metadata and runtime payloads cannot silently drift**
   - **Given** FastMCP passes through an already-created `ToolResult` without validating it against `output_schema`
   - **When** Lucius constructs structured output
   - **Then** the central output-contract/registration boundary validates and serializes the payload with the matching output model before it is placed in `ToolResult.structured_content`
   - **And** Pydantic validation failures are surfaced as normal server errors; they must not be hidden, coerced to strings, or cause a schema/payload mismatch.

5. **Generated documentation and regression checks enforce the contract**
   - **Given** the manifest generation command runs (`uv run --locked fastmcp inspect src/main.py --format mcp -o docs/mcp_manifest.json`)
   - **When** documentation tests execute
   - **Then** all 64 current tools have non-null schemas and every schema has an object root with meaningful declared properties/constraints
   - **And** `tests/docs/test_mcp_manifest.py` fails for null, generic, malformed, missing, or stale schemas
   - **And** the pre-commit manifest-sync hook runs when changes affect either tool output definitions/contracts or `src/main.py` registration.

6. **No unrelated output-contract regression is introduced**
   - **Given** direct MCP calls and `lucius <entity> <action>` calls use `plain`, `json`, `table`, or `csv` as they do today
   - **When** the schema feature is enabled
   - **Then** tool-level modes remain limited to `plain|json`, CLI-only table/csv rendering remains unchanged, and existing CLI decoupling from `src.main` remains intact
   - **And** no generated Allure client model is modified or regenerated solely for this feature.

## Tasks / Subtasks

- [x] **Task 1: Establish the output-schema registry and model conventions** (AC: 1, 2, 4)
  - [x] 1.1 Create a focused output-model module/package under `src/tools/` (for example `src/tools/output_schemas.py`); do not reuse generated API DTOs as tool response schemas.
  - [x] 1.2 Define composable Pydantic v2 response models for shared concepts (confirmation, pagination, entity summaries, links, attachments, steps) and one concrete object-root model per registered tool.
  - [x] 1.3 Use `BaseModel`, `ConfigDict`, `Field` descriptions, concrete nested models, `Literal`/enums, and typed maps where the response contract intentionally permits variable keys. Prefer `extra="forbid"`; document and narrowly justify any allowed additional properties.
  - [x] 1.4 Build one authoritative registry keyed by `tool.__name__`; add an import-time/test-time coverage check comparing the registry keys to `all_tools`.
  - [x] 1.5 Generate registration schemas with `model_json_schema(mode="serialization", by_alias=True)`. Do not register a root list, scalar, or root-union schema because FastMCP requires object-root output schemas.

- [x] **Task 2: Make structured output schema-aware without changing direct-call semantics** (AC: 2, 3, 4, 6)
  - [x] 2.1 Extend the central output contract and/or MCP wrapper so the active tool's model validates and serializes every structured payload before constructing `ToolResult`.
  - [x] 2.2 Preserve direct tool invocation behavior: `output_format="plain"` remains a string and default/`json` remain the existing structured result shape expected by callers and CLI adapters.
  - [x] 2.3 At the FastMCP-only boundary, adapt a plain string to a text-only `ToolResult` when an explicit output schema is registered. Do not attach scalar `structured_content` and do not change the CLI's service-first execution path.
  - [x] 2.4 Preserve the flat structured payload. Do not introduce FastMCP's generic wrapped-result extension or make clients unwrap a new `result` property.
  - [x] 2.5 Model and validate each normal output branch produced by the existing helpers: `render_output`, `render_message_output`, `render_confirmation_required`, and `render_collection_output`, including tool-specific conditional branches.

- [x] **Task 3: Register Pydantic-generated schemas with FastMCP** (AC: 1, 3)
  - [x] 3.1 Replace the blanket `output_schema=None` in `src/main.py` with lookup of the registered schema for each tool.
  - [x] 3.2 Keep existing tags, annotations, telemetry events, tool names, and input schemas unchanged.
  - [x] 3.3 Add a focused regression test proving a representative nested model is accepted by the pinned FastMCP 3.4.4 registration API and appears without `x-fastmcp-wrap-result`.

- [x] **Task 4: Regenerate and harden the published manifest workflow** (AC: 5)
  - [x] 4.1 Regenerate `docs/mcp_manifest.json` using the locked FastMCP command after implementation; commit the generated artifact.
  - [x] 4.2 Extend `tests/docs/test_mcp_manifest.py` to assert one-to-one schema coverage, non-null object roots, meaningful constraints, and absence of the obsolete generic string wrapper.
  - [x] 4.3 Add tests that validate representative success, empty, confirmation, and complex nested payloads for every registry entry against the matching Pydantic model/schema. Use focused fixtures/mocks rather than live TestOps dependencies.
  - [x] 4.4 Update `scripts/pre_commit_sync_mcp_manifest.sh` trigger detection to include schema registration changes in `src/main.py` as well as output definitions under `src/tools/`.
  - [x] 4.5 Retain the release workflow in `scripts/prepare-release.md`; its locked regeneration and manifest test command is the release-level verification path.

- [x] **Task 5: Validate behavior across MCP and CLI boundaries** (AC: 2, 3, 4, 6)
  - [x] 5.1 Extend `tests/unit/test_tool_structured_outputs.py` to execute registered FastMCP tools with explicit schemas and assert valid structured content for omitted and `json` output formats.
  - [x] 5.2 Add tests for the plain FastMCP path to ensure it produces text content with no scalar structured content, while direct tool tests continue to receive the expected string.
  - [x] 5.3 Retain/extend CLI mocked and source-invoked checks proving JSON passthrough and `plain|table|csv` behavior remain unchanged and the CLI does not import `src.main`.
  - [x] 5.4 Run focused checks first: `uv run --locked pytest tests/docs/test_mcp_manifest.py tests/unit/test_tool_structured_outputs.py tests/cli -q`, then applicable integration and source-invoked CLI E2E coverage; run `uv run --locked ruff check` and `uv run --locked mypy src` on touched areas.

## Dev Notes

### Confirmed implementation facts

- `docs/mcp_manifest.json` currently exposes 64 tools and all 64 `outputSchema` values are `null`.
- The cause is explicit: `src/main.py` passes `output_schema=None` for every registered tool. That was introduced in commit `c44684a` to suppress FastMCP's earlier incorrect generic `{"result": "string"}` output schema.
- `src/tools/output_contract.py` currently aliases `ToolOutput` to `Any` and builds `ToolResult(content=[], structured_content=dict)` dynamically. This cannot provide FastMCP with a precise inferred return type.
- The pinned runtime supports the proposed approach: FastMCP 3.4.4 accepts an explicit JSON-schema dict in `mcp.tool(..., output_schema=...)`; Pydantic 2.13.4's concrete `BaseModel.model_json_schema(mode="serialization", by_alias=True)` produces compatible object-root schemas with nested `$defs`.
- FastMCP does **not** validate a preconstructed `ToolResult` against the registered schema. `Tool.convert_result()` returns it unchanged. Validation must therefore occur in Lucius before the result is constructed or at the registration wrapper boundary.
- An explicit output schema changes FastMCP's handling of a raw string return. This is why the MCP-only wrapper must preserve plain output as text-only `ToolResult`; changing all direct tool callers to receive `ToolResult` would regress the CLI and existing tests.

### Scope and design boundaries

- The published schema describes MCP `structuredContent`, not human-readable text content. It applies to omitted/structured and explicit `json` output paths; plain mode remains text.
- Do not use the Allure OpenAPI-generated request/response DTOs as public MCP output models. They expose upstream/API-centric fields and do not match Lucius's deliberate, agent-oriented JSON envelopes.
- Do not add a FastMCP, Pydantic, or MCP dependency: the locked versions already support this work.
- Do not change tool names, input schemas, annotations/tags, `output_format` accepted values, CLI route metadata, or any Allure API call/service behavior.
- Resolve the current documentation ambiguity while implementing: planning documents describe plain as the tool default, whereas omitted `output_format` currently returns a structured `ToolResult`. Document precisely that output schemas cover MCP structured content and keep CLI behavior unchanged; do not make an unrelated output-default change in this story.
- Preserve telemetry privacy guarantees: output-schema validation/model failures must not log tokens, headers, or request/business payloads.

### Expected files

- `src/tools/output_schemas.py` (new; or a small `src/tools/output_schemas/` package if grouping is necessary)
- `src/tools/output_contract.py`
- `src/main.py`
- `src/utils/telemetry.py` only if it is the narrowest FastMCP-only adaptation boundary
- `tests/docs/test_mcp_manifest.py`
- `tests/unit/test_tool_structured_outputs.py`
- a focused new schema-registry/unit test module under `tests/unit/`
- selected `tests/cli/` and `tests/e2e/test_cli_*uv_run.py` tests only where behavior needs regression coverage
- `scripts/pre_commit_sync_mcp_manifest.sh`
- `docs/mcp_manifest.json` (generated)
- `scripts/prepare-release.md` only if its instructions need a clarification; do not remove the locked command

### Project Structure Notes

- Keep response-schema ownership in `src/tools/`, alongside the output contract it describes. `src/client/generated/` remains generated upstream-client code and is out of scope.
- Keep the FastMCP wiring change in `src/main.py`; do not import it from the CLI. The only permitted cross-cutting adaptation is the existing telemetry wrapper if it is the narrowest way to preserve text-only MCP results.
- Treat `docs/mcp_manifest.json` as generated release/documentation metadata. Never hand-edit individual schemas in that file.

### References

- [Source: src/main.py:35-41]
- [Source: src/tools/output_contract.py:10-99]
- [Source: src/utils/telemetry.py:21-47]
- [Source: tests/unit/test_tool_structured_outputs.py:90-139]
- [Source: tests/docs/test_mcp_manifest.py]
- [Source: scripts/pre_commit_sync_mcp_manifest.sh:1-17]
- [Source: scripts/prepare-release.md:34-39]
- [Source: docs/mcp_manifest.json]
- [Source: specs/project-planning-artifacts/epics.md#Story-9.6-Tool-to-CLI-Output-Contract-Tools-JSON-Default-CLI-TableCSV-Rendering]
- [Source: specs/implementation-artifacts/9-6-unified-cli-output-formats-json-table-csv-plain.md]
- [Source: specs/implementation-artifacts/spec-sync-mcp-manifest-release.md]
- [Source: specs/architecture.md#Data-Architecture]
- [Source: specs/project-context.md#Pydantic--Data]
- [Source: pyproject.toml:10-18; uv.lock:541-566, 1283-1295]

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Confirmed by local proof: a Pydantic output model generated nested object JSON Schema and FastMCP 3.4.4 accepted it as an explicit `output_schema`.
- Added an authoritative 64-tool Pydantic output-schema registry with closed object-root models and reusable nested response concepts.
- Registered serialization schemas with FastMCP and validated MCP structured results in the telemetry registration boundary; plain MCP responses are now explicitly text-only `ToolResult`s without changing direct or CLI calls.
- Regenerated the manifest: all 64 tools publish object-root output schemas with no wrapper extension.
- Verified with focused docs/unit/CLI tests, source-invoked CLI E2E coverage, `ruff`, `mypy`, and the full non-live regression suite.

### File List

- docs/mcp_manifest.json
- scripts/pre_commit_sync_mcp_manifest.sh
- specs/project-planning-artifacts/epics.md
- specs/implementation-artifacts/9-14-publish-accurate-mcp-tool-output-schemas.md
- specs/implementation-artifacts/sprint-status.yaml
- src/main.py
- src/tools/output_schemas.py
- src/utils/telemetry.py
- tests/docs/test_mcp_manifest.py
- tests/unit/test_output_schemas.py
- tests/unit/test_tool_structured_outputs.py

## Change Log

- 2026-07-17: Added validated, per-tool MCP output schemas, regenerated the manifest, and hardened schema/CLI regression coverage.
