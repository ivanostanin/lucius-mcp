# Story 12.5: Remove Upstream `storage_key` from Test-Result Attachment Outputs

Status: ready-for-dev

## Story

As an **AI Agent**,
I want **test-result attachment metadata to omit upstream storage implementation identifiers**,
so that **I can prepare and download evidence through Lucius's verified owner-context workflow without receiving unnecessary internal storage data**.

## Acceptance Criteria

1. **Remove `storage_key` from every public test-result attachment projection**
   - **Given** `get_test_result` returns result-level, execution-step, or fixture attachment metadata.
   - **When** Lucius renders default structured output, explicit JSON, or plain output.
   - **Then** no attachment object or rendered text contains `storage_key`, including when TestOps supplied a non-null `storageKey`.
   - **And** result attachments remain on the result, step attachments remain on their owning step, and fixture attachments remain on their verified fixture.
   - **And** all other published attachment fields remain unchanged: `attachment_id`, `attachment_kind`, exactly one valid owner context, `name`, `entity`, `content_type`, `content_length`, `missed`, and `from_test_case`.
   - **And** existing partial-result and unavailable-section behavior remains unchanged.

2. **Discard upstream storage data at the application boundary**
   - **Given** an upstream attachment DTO includes `storageKey`.
   - **When** `TestResultService` creates the application-owned attachment model.
   - **Then** it does not retain or propagate the value to an output serializer, diagnostic, or log.
   - **And** the filtered OpenAPI specification, generated client DTOs, and generated-client documentation remain untouched; they model TestOps input, not Lucius's public contract.

3. **Preserve the safe prepare-then-GET workflow**
   - **Given** an attachment reference returned from `get_test_result`.
   - **When** an agent calls `prepare_attachment_download` and HTTP GETs the returned Lucius capability URL.
   - **Then** owner verification, capability URL behavior, cache lifecycle, and all preparation metadata are unchanged.
   - **And** this change does not restore a raw TestOps `download_url` or introduce credentials, cache paths, bytes, base64, or upstream storage data into public output.

4. **Regenerate and verify public contracts**
   - **Given** strict output schemas and generated MCP metadata are inspected.
   - **When** the change is complete.
   - **Then** `TestResultAttachmentOutput` and `docs/mcp_manifest.json` omit `storage_key` at every attachment nesting level.
   - **And** strict validation rejects the removed field rather than silently accepting it.
   - **And** focused unit tests prove a non-null upstream `storageKey` cannot appear in result-, step-, or fixture-level structured or plain output.

## Tasks / Subtasks

- [ ] **Task 1: Remove the public projection field at the service boundary** (AC: 1, 2)
  - [ ] Remove `storage_key` from `AttachmentDetail` and stop reading it in `TestResultService._attachment`.
  - [ ] Preserve the existing typed attachment ID/kind/owner mapping, fixture reconciliation, and partial-diagnostic paths exactly.
  - [ ] Do not modify `src/client/generated/` or either OpenAPI specification.

- [ ] **Task 2: Tighten the public output schema and derived manifest** (AC: 1, 4)
  - [ ] Remove `storage_key` from `TestResultAttachmentOutput`; its reuse by result, step, and fixture projections must cover all public nesting levels.
  - [ ] Regenerate `docs/mcp_manifest.json` with `uv run fastmcp inspect src/main.py --format mcp -o docs/mcp_manifest.json`; never hand-edit the manifest.
  - [ ] Keep `src/cli/data/tool_schemas.json`, MCPB manifests, shell completions, tool descriptions, and route metadata unchanged unless validation proves a generated public reference exists. CLI tool schemas cover inputs and currently do not contain this field.

- [ ] **Task 3: Add regression coverage for output redaction and contract parity** (AC: 1, 3, 4)
  - [ ] Update `tests/unit/test_test_result_tools.py` fixtures and expected payloads for the removed model field.
  - [ ] Add service-level coverage with a non-null upstream `storage_key` for result, step, and fixture attachment sources; assert the mapped public attachment data has no such attribute/value.
  - [ ] Assert JSON/structured and plain outputs contain no `storage_key`, while required preparation metadata and attachment placement remain intact.
  - [ ] Extend output-schema/manifest assertions so the removed field is rejected and absent from generated metadata.

- [ ] **Task 4: Record the intentional public-contract tightening** (AC: 1, 4)
  - [ ] Treat removal of `get_test_result.*.storage_key` as an intentional breaking public-output change; follow the repository release-note convention if this branch is prepared for release.
  - [ ] Supersede only Story 12.1's historical promise of attachment storage metadata. Do not rewrite its implementation history or broaden this story to other upstream `storage_key` fields (for example export/import DTOs).

## Dev Notes

### Existing implementation and safe change boundary

- The only relevant public path is `TestResultAttachmentRowDto.storageKey` → `TestResultService._attachment` → `AttachmentDetail` → `dataclasses.asdict()` in `get_test_result` → `TestResultAttachmentOutput` → generated MCP manifest. `AttachmentDetail` is reused by result, step, and fixture attachment projections.
- Remove the service dataclass field and its mapping in the same change as the strict output-schema field. Removing only the schema field first makes `extra="forbid"` reject payloads that the service still emits.
- Plain output is JSON-rendered from the same normalized payload as structured output. Do not add per-attachment guidance or a second formatter; absence from the shared payload preserves JSON/plain parity.
- `prepare_attachment_download` needs only attachment ID, verified kind, and verified owner context. Do not change the broker, capability URLs, cache/lifecycle, direct-CLI handling, or the preparation tool's output contract.

### Scope boundaries

- This intentionally supersedes the attachment `storage metadata`/`storage_key` statements in Story 12.1. The safe evidence workflow introduced by Stories 12.2 and 12.3 remains authoritative.
- Do not reintroduce a bearer-authenticated TestOps `download_url`; do not expose upstream URLs, authorization headers, API tokens, cache paths, attachment bytes, or base64.
- Do not remove `storage_key` from generated TestOps DTOs, OpenAPI documents, or unrelated export/import models. Lucius must still deserialize upstream responses; only its curated public projection changes.
- Do not change `get_test_case_details`; its attachment output has no `storage_key` field. Do not add attachment payloads to `list_launch_test_results`.

### Project Structure Notes

| Area | Files | Direction |
| --- | --- | --- |
| Service projection | `src/services/test_result_service.py` | Remove the application-owned field and its upstream mapping; retain attachment hierarchy and ownership logic. |
| Public contract | `src/tools/output_schemas.py` | Remove the field from `TestResultAttachmentOutput`; strict schema reuse updates every result attachment nesting level. |
| Tool serialization | `src/tools/launches.py` | Reuse the existing `asdict`/normalization path; no new tool logic should be necessary. |
| Generated metadata | `docs/mcp_manifest.json` | Regenerate with FastMCP after the output model changes. |
| Tests | `tests/unit/test_test_result_service.py`, `tests/unit/test_test_result_tools.py`, `tests/unit/test_output_schemas.py`, `tests/docs/test_mcp_manifest.py` | Prove non-null upstream values cannot leak and the strict public contract is consistent. |

### Validation

- Run focused checks first:
  - `uv run pytest tests/unit/test_test_result_service.py tests/unit/test_test_result_tools.py tests/unit/test_output_schemas.py tests/docs/test_mcp_manifest.py -q`
  - `uv run ruff check src/services/test_result_service.py src/tools/output_schemas.py tests/unit/test_test_result_service.py tests/unit/test_test_result_tools.py`
  - `uv run mypy --strict src`
- Sandbox E2E is optional for this projection-only change; run it if a modified workflow test needs live verification. Do not expose TestOps tokens or evidence contents in assertions or reports.

### References

- [Source: `specs/implementation-artifacts/deferred-work.md` — deferred review finding that initiated this story]
- [Source: `specs/implementation-artifacts/12-3-prepare-attachment-downloads-and-teach-agents-the-safe-evidence-workflow.md` — safe evidence and public-redaction contract]
- [Source: `specs/implementation-artifacts/12-2-broker-authenticated-attachment-downloads-through-short-lived-capability-links.md` — broker and capability-link boundaries]
- [Source: `specs/implementation-artifacts/12-1-retrieve-complete-individual-test-result-details.md` — original curated attachment DTO and superseded storage-metadata promise]
- [Source: `src/services/test_result_service.py:AttachmentDetail`, `src/services/test_result_service.py:_attachment` — current public projection boundary]
- [Source: `src/tools/output_schemas.py:TestResultAttachmentOutput` and `src/tools/launches.py:get_test_result` — strict schema and shared serialization path]
- [Source: `scripts/pre_commit_sync_mcp_manifest.sh` — generated manifest command]
- [Source: `docs/development.md` and `specs/project-context.md` — uv validation, thin-tool, strict-Pydantic, and privacy rules]

## Dev Agent Record

### Agent Model Used

GPT-5

### Debug Log References

- Deferred from the Story 12.3 adversarial review after confirming `storage_key` predates the safe preparation workflow and is not needed by it.
- Planning research found no PRD, architecture, or UX artifact beyond Epic 12 relevant to this narrow public-contract change.
- Source analysis confirmed the generated client and OpenAPI documents must retain the upstream field while Lucius's application-owned output discards it.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Story 12.5 is independent of Story 12.4 and may be implemented in parallel; it depends on the completed 12.1/12.2/12.3 attachment contracts.

### File List

- `specs/project-planning-artifacts/epics.md`
- `specs/implementation-artifacts/sprint-status.yaml`
- `specs/implementation-artifacts/deferred-work.md`
- `specs/implementation-artifacts/12-5-remove-upstream-storage-key-from-test-result-attachment-outputs.md`
