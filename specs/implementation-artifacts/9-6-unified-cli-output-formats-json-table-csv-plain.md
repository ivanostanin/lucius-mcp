# Story 9.6: Tool-to-CLI Output Contract (Tools JSON Default, CLI Table/CSV Rendering)

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer or QA Engineer,
I want the CLI to ingest and display the data returned by tools through a consistent output contract,
so that automation and human-readable workflows are both supported without ambiguity.

This story defines a breaking output-contract change:
- Tools must support `plain` and `json` outputs.
- Tool default output format becomes `json` (breaking change from current plain-text default behavior).
- `table` and `csv` are CLI-only renderers and must not be introduced as tool-level output formats.

## Acceptance Criteria

1. **Tool output contract and defaults (breaking change)**
   - **Given** any tool that returns result payloads
   - **When** output format is not explicitly requested
   - **Then** tool output defaults to `json`
   - **And** tools support exactly `plain|json` output modes
   - **And** this default change is treated as a breaking change.

2. **CLI renderer scope**
   - **Given** CLI command execution (`lucius <entity> <action>`)
   - **When** output is rendered
   - **Then** CLI supports `plain|json|table|csv`
   - **And** `table` and `csv` exist only in CLI rendering layer
   - **And** tools do not expose `table` or `csv` output modes.

3. **Tool-to-CLI data flow contract**
   - **Given** CLI calls a mapped tool
   - **When** tool returns `json` (default) or `plain`
   - **Then** CLI ingests tool output and renders requested CLI format deterministically
   - **And** no traceback/internal logs are printed for normal format handling.

4. **Plain text newline handling**
   - **Given** plain text payloads containing escaped newline markers (`\\n`)
   - **When** plain output is displayed
   - **Then** `\\n` is rendered as an actual line break (not literal backslash+n text).

5. **Integration test coverage for ACs and data flow**
   - **Given** automated test suites
   - **When** tests run in CI
   - **Then** integration tests verify:
     - tool default `json` output behavior
     - tool `plain` output behavior
     - CLI ingestion of tool outputs and rendering across `plain|json|table|csv`
     - newline normalization in plain output
     - deterministic table/csv column behavior for multi-record results.

6. **Documentation requirements (PRD + Architecture)**
   - **Given** this story implementation
   - **When** documentation is updated
   - **Then** `specs/prd.md` and `specs/architecture.md` explicitly document:
     - tool output contract (`plain|json`, default `json`)
     - CLI-only renderer contract (`table|csv`)
     - end-to-end data flow from tools to CLI renderers.

7. **Breaking-change commit convention requirement**
   - **Given** this story introduces a breaking output-contract change
   - **When** changes are committed
   - **Then** commit message uses Conventional Commits with a breaking marker `!` (example: `feat(cli)!: ...`)
   - **And** commit body includes a `BREAKING CHANGE:` note describing impact and migration expectations.

8. **Every-tool compliance and passthrough guarantee**
   - **Given** the complete set of exposed tools/routes
   - **When** output is produced and consumed by CLI
   - **Then** every tool follows the `plain|json` output contract with default `json`
   - **And** CLI returns tool `plain` and `json` outputs to users without content changes
   - **And** CLI performs rendering transformations only for `table` and `csv` formats.

## Tasks / Subtasks

- [ ] **Task 1: Define tool output contract** (AC: 1)
  - [ ] 1.1 Add/confirm tool-level output mode support: `plain|json`.
  - [ ] 1.2 Set tool default output format to `json`.
  - [ ] 1.3 Document migration impact as breaking change.

- [ ] **Task 2: Enforce CLI-only table/csv renderers** (AC: 2, 3)
  - [ ] 2.1 Keep `table|csv` implementation in CLI layer only.
  - [ ] 2.2 Ensure CLI renderer behavior is deterministic for multi-record payloads.
  - [ ] 2.3 Ensure non-tabular payload handling is deterministic and user-friendly.

- [ ] **Task 3: Implement plain newline normalization** (AC: 4)
  - [ ] 3.1 Normalize escaped `\\n` markers in plain output rendering.
  - [ ] 3.2 Verify behavior for both direct tool plain output and CLI plain rendering.

- [ ] **Task 4: Add integration tests for AC and data flow** (AC: 5)
  - [ ] 4.1 Add/extend integration tests for tool default `json` output.
  - [ ] 4.2 Add/extend integration tests for tool `plain` output.
  - [ ] 4.3 Add/extend integration tests for CLI ingestion and rendering (`plain|json|table|csv`).
  - [ ] 4.4 Add tests for newline normalization and deterministic table/csv output.

- [ ] **Task 5: Update docs and traceability artifacts** (AC: 6)
  - [ ] 5.1 Update `specs/prd.md` output contracts and tool->CLI flow.
  - [ ] 5.2 Update `specs/architecture.md` output contracts and tool->CLI flow.
  - [ ] 5.3 Update Epic 9 story listing and sprint status tracking for this revised scope.

- [ ] **Task 6: Commit metadata for breaking behavior changes** (AC: 7)
  - [ ] 6.1 Use Conventional Commit with `!` marker for implementation commit.
  - [ ] 6.2 Add `BREAKING CHANGE:` footer describing tool default and renderer-scope changes.

- [ ] **Task 7: Enforce every-tool contract and passthrough behavior** (AC: 8)
  - [ ] 7.1 Audit all exposed tools/routes to verify `plain|json` support and default `json`.
  - [ ] 7.2 Add integration tests asserting CLI passthrough parity for tool `plain` and `json` outputs.
  - [ ] 7.3 Add tests asserting that only `table|csv` apply CLI-specific rendering transformations.

## Dev Notes

### Scope Clarification

- This story is about output contracts across both layers:
  - tools (producer): `plain|json`, default `json`
  - CLI (renderer): `plain|json|table|csv` with `table|csv` CLI-only.
- The key intent is robust tool->CLI data ingestion and rendering.

### References

- [Source: specs/project-planning-artifacts/epics.md]
- [Source: specs/prd.md]
- [Source: specs/architecture.md]
- [Source: specs/implementation-artifacts/9-3-service-first-cli-entity-action.md]

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Completion Notes List

- Story was re-scoped to clarify tool output defaults/contracts and CLI-only table/csv rendering.
- Status reset to `ready-for-dev` to reflect revised acceptance criteria and pending implementation alignment.

### File List

- specs/implementation-artifacts/9-6-unified-cli-output-formats-json-table-csv-plain.md
