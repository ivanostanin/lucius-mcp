# Story 9.6: Tool-to-CLI Output Contract (Tools Plain Default, CLI JSON-by-Default Calls + Table/CSV Rendering)

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer or QA Engineer,
I want the CLI to ingest and display the data returned by tools through a consistent output contract,
so that automation and human-readable workflows are both supported without ambiguity.

This story defines output-contract behavior across tools and CLI:
- Tools must support `plain` and `json` outputs.
- Tool default output format is `plain`.
- CLI must call tools with explicit `output_format=json` by default, and `output_format=plain` only when plain output is requested.
- `table` and `csv` are CLI-only renderers and must not be introduced as tool-level output formats.

## Acceptance Criteria

1. **Tool output contract and defaults**
   - **Given** any tool that returns result payloads
   - **When** output format is not explicitly requested
   - **Then** tool output defaults to `plain`
   - **And** tools support exactly `plain|json` output modes
   - **And** each tool applies output-format rendering in-function (not via runtime wrappers).

2. **CLI renderer scope**
   - **Given** CLI command execution (`lucius <entity> <action>`)
   - **When** output is rendered
   - **Then** CLI supports `plain|json|table|csv`
   - **And** `table` and `csv` exist only in CLI rendering layer
   - **And** tools do not expose `table` or `csv` output modes.

3. **Tool-to-CLI data flow contract**
   - **Given** CLI calls a mapped tool
   - **When** tool returns `plain` (default) or `json`
   - **Then** CLI ingests tool output and renders requested CLI format deterministically
   - **And** CLI requests tool output with `output_format=json` by default and `output_format=plain` only for plain mode
   - **And** no traceback/internal logs are printed for normal format handling.

4. **Plain text newline handling**
   - **Given** plain text payloads containing escaped newline markers (`\\n`)
   - **When** plain output is displayed
   - **Then** `\\n` is rendered as an actual line break (not literal backslash+n text).

5. **Integration test coverage for ACs and data flow**
   - **Given** automated test suites
   - **When** tests run in CI
   - **Then** integration tests verify:
     - tool default `plain` output behavior
     - tool `plain` output behavior
     - CLI ingestion of tool outputs and rendering across `plain|json|table|csv`
     - newline normalization in plain output
     - deterministic table/csv column behavior for multi-record results.
     - CLI process e2e checks executed in `uv run` mode for requested output formats.

6. **Documentation requirements (PRD + Architecture)**
   - **Given** this story implementation
   - **When** documentation is updated
   - **Then** `specs/prd.md` and `specs/architecture.md` explicitly document:
     - tool output contract (`plain|json`, default `plain`)
     - CLI-only renderer contract (`table|csv`)
     - end-to-end data flow from tools to CLI renderers including CLI default `json` tool-call behavior.

7. **Breaking-change commit convention requirement**
   - **Given** this story introduces a breaking output-contract change
   - **When** changes are committed
   - **Then** commit message uses Conventional Commits with a breaking marker `!` (example: `feat(cli)!: ...`)
   - **And** commit body includes a `BREAKING CHANGE:` note describing impact and migration expectations.

8. **Every-tool compliance and passthrough guarantee**
   - **Given** the complete set of exposed tools/routes
   - **When** output is produced and consumed by CLI
   - **Then** every tool follows the `plain|json` output contract with default `plain`
   - **And** CLI returns tool `plain` and `json` outputs to users without content changes
   - **And** CLI performs rendering transformations only for `table` and `csv` formats.

## Tasks / Subtasks

- [x] **Task 1: Define tool output contract** (AC: 1)
  - [x] 1.1 Add/confirm tool-level output mode support: `plain|json`.
  - [x] 1.2 Set tool default output format to `plain`.
  - [x] 1.3 Ensure output rendering is implemented in each tool function body.

- [x] **Task 2: Enforce CLI-only table/csv renderers** (AC: 2, 3)
  - [x] 2.1 Keep `table|csv` implementation in CLI layer only.
  - [x] 2.2 Ensure CLI renderer behavior is deterministic for multi-record payloads.
  - [x] 2.3 Ensure non-tabular payload handling is deterministic and user-friendly.

- [x] **Task 3: Implement plain newline normalization** (AC: 4)
  - [x] 3.1 Normalize escaped `\\n` markers in plain output rendering.
  - [x] 3.2 Verify behavior for both direct tool plain output and CLI plain rendering.

- [x] **Task 4: Add integration tests for AC and data flow** (AC: 5)
  - [x] 4.1 Add/extend integration tests for tool default `plain` output.
  - [x] 4.2 Add/extend integration tests for tool `plain` output.
  - [x] 4.3 Add/extend integration tests for CLI ingestion and rendering (`plain|json|table|csv`).
  - [x] 4.4 Add tests for newline normalization and deterministic table/csv output.
  - [x] 4.5 Add e2e CLI tests in `uv run` mode to assert requested format behavior.

- [x] **Task 5: Update docs and traceability artifacts** (AC: 6)
  - [x] 5.1 Update `specs/prd.md` output contracts and tool->CLI flow.
  - [x] 5.2 Update `specs/architecture.md` output contracts and tool->CLI flow.
  - [x] 5.3 Update Epic 9 story listing and sprint status tracking for this revised scope.

- [ ] **Task 6: Commit metadata for breaking behavior changes** (AC: 7)
  - [ ] 6.1 Use Conventional Commit with `!` marker for implementation commit.
  - [ ] 6.2 Add `BREAKING CHANGE:` footer describing tool default and renderer-scope changes.

- [x] **Task 7: Enforce every-tool contract and passthrough behavior** (AC: 8)
  - [x] 7.1 Audit all exposed tools/routes to verify `plain|json` support and default `plain`.
  - [x] 7.2 Add integration tests asserting CLI passthrough parity for tool `plain` and `json` outputs.
  - [x] 7.3 Add tests asserting that only `table|csv` apply CLI-specific rendering transformations.

## Dev Notes

### Scope Clarification

- This story is about output contracts across both layers:
  - tools (producer): `plain|json`, default `plain`
  - CLI (renderer): `plain|json|table|csv` with `table|csv` CLI-only.
  - CLI call behavior: explicit `output_format=json` by default; explicit `output_format=plain` only for plain mode.
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

- Implemented explicit output contract in EVERY async tool in `src/tools`: each function now declares `output_format` with default `plain` and applies the format in-function.
- Removed resolver/wrapper fallback behavior so tool formatting is owned by each tool implementation.
- Updated CLI runtime flow to always pass explicit `output_format` to tools (`json` default, `plain` when requested) and to pass through tool `plain/json` output unchanged.
- Limited CLI rendering transformations to `table|csv` by parsing tool JSON output only for these modes.
- Added integration/coverage tests for:
  - every-tool signature contract (`src/tools`)
  - tool default `plain` + CLI default tool-call `json` behavior
  - CLI-only rendering transformation behavior for `table|csv`.
- Added e2e CLI format tests executed through `uv run` mode.
- Regenerated `src/cli/data/tool_schemas.json` to include tool output-contract parameter.
- Validation results:
  - `uv run --python 3.13 --extra dev pytest tests/cli tests/integration/test_tool_hints.py tests/e2e/test_cli_output_formats_uv_run.py -q` -> 147 passed
  - `uv run ruff check src/tools/output_contract.py src/cli/cli_entry.py tests/cli/test_cli_basics.py tests/cli/test_cli_coverage_helpers.py tests/e2e/test_cli_output_formats_uv_run.py tests/integration/test_tool_hints.py` -> passed
  - `uv run mypy src/tools/output_contract.py src/cli/cli_entry.py` -> passed
- Commit metadata task remains pending until an actual commit is created.

### File List

- src/tools/output_contract.py
- src/tools/__init__.py
- src/cli/tool_resolver.py
- src/cli/cli_entry.py
- src/cli/data/tool_schemas.json
- tests/cli/test_cli_basics.py
- tests/cli/test_cli_coverage_helpers.py
- tests/cli/test_e2e_mocked.py
- tests/e2e/test_cli_output_formats_uv_run.py
- tests/integration/test_tool_hints.py
- specs/implementation-artifacts/9-6-unified-cli-output-formats-json-table-csv-plain.md
- specs/implementation-artifacts/sprint-status.yaml
