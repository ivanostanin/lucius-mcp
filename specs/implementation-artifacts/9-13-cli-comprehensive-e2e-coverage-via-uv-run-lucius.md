# Story 9.13: CLI Comprehensive E2E Coverage via uv run lucius

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer or QA Engineer,
I want comprehensive CLI command E2E coverage executed from source with `uv run lucius`,
so that CLI behavior is verified end-to-end without depending on built binaries and regressions in local commands or high-priority entity flows are caught early.

## Acceptance Criteria

1. **Source-invoked E2E execution**
   - **Given** the CLI E2E suite is executed
   - **When** command processes are launched
   - **Then** commands run from source via `uv run lucius ...`
   - **And** the suite does not require building a Nuitka or wheel binary to validate CLI behavior.

2. **All non-tool-call commands are covered**
   - **Given** CLI paths that do not directly execute a TestOps tool
   - **When** process-level E2E tests run
   - **Then** coverage includes `lucius`, `lucius --help`, `lucius --version`, `lucius <entity>`, and `lucius <entity> <action> --help`
   - **And** it also covers every CLI-local command introduced in Epic 9, including `list`, `auth`, `auth status`, and `install-completions`
   - **And** tests verify clean exit codes, expected discovery/help text, and no Python tracebacks/internal logs.

3. **High-priority test-case flows are covered**
   - **Given** high-priority `test_case` command flows
   - **When** source-invoked CLI E2E tests run
   - **Then** they cover representative discovery, help, and execution paths for `test_case`
   - **And** they verify default JSON routing plus CLI rendering for `plain`, `table`, and `csv`
   - **And** escaped-newline normalization in plain output remains covered end-to-end.

4. **High-priority launch flows are covered**
   - **Given** high-priority `launch` command flows
   - **When** source-invoked CLI E2E tests run
   - **Then** they cover representative discovery, help, and execution paths for `launch`
   - **And** they validate at least one list/read flow and at least one lifecycle state-transition flow such as `close` or `reopen`.

5. **High-priority custom-field flows are covered**
   - **Given** high-priority custom-field command flows
   - **When** source-invoked CLI E2E tests run
   - **Then** they cover representative discovery, help, and execution paths for `custom_field` and `custom_field_value`
   - **And** they validate both entity-level operations and value-level CRUD-style flows.

6. **CLI-only feature regressions are exercised through the process boundary**
   - **Given** staged CLI-only behaviors such as pretty JSON, local-timezone table rendering, and short aliases
   - **When** the corresponding stories are implemented
   - **Then** the shared `uv run lucius` CLI E2E suite includes representative process-level tests for those behaviors
   - **And** aliases such as `tc`, `ln`, `cf`, or `cfv` are covered where the corresponding feature is available.

7. **Future command stories are forced to extend the shared suite**
   - **Given** future CLI-local commands or CLI-only rendering features are added
   - **When** a story is prepared for development
   - **Then** its acceptance criteria explicitly require extending the shared `uv run lucius` CLI E2E suite
   - **And** its tasks identify the concrete test file(s) to update.

## Tasks / Subtasks

- [ ] **Task 1: Consolidate reusable `uv run lucius` CLI process helpers** (AC: 1, 2, 3, 4, 5, 6)
  - [ ] 1.1 Review and extend `tests/cli/subprocess_helpers.py` so source-invoked CLI execution is centralized and reused consistently.
  - [ ] 1.2 Keep helper coverage explicit for both direct CLI invocation through `uv run lucius` and patched/stubbed tool execution through equivalent source-invoked wrappers.
  - [ ] 1.3 Avoid introducing binary-build assumptions into the helper layer.

- [ ] **Task 2: Add non-tool-call command coverage** (AC: 2)
  - [ ] 2.1 Extend or create a focused file such as `tests/e2e/test_cli_local_commands_uv_run.py`.
  - [ ] 2.2 Cover `lucius`, `lucius --help`, and `lucius --version`.
  - [ ] 2.3 Cover `lucius <entity>` discovery and `lucius <entity> <action> --help` through real subprocess execution.
  - [ ] 2.4 Cover CLI-local commands added by Epic 9 stories, including `list`, `auth`, `auth status`, and `install-completions`.
  - [ ] 2.5 Assert clean exit codes, stable help/discovery text markers, and absence of tracebacks/internal logs.

- [ ] **Task 3: Expand high-priority entity command coverage** (AC: 3, 4, 5, 6)
  - [ ] 3.1 Extend `tests/e2e/test_cli_output_formats_uv_run.py` or add a sibling file such as `tests/e2e/test_cli_entity_commands_uv_run.py`.
  - [ ] 3.2 Add representative `test_case` process tests for default JSON, plain output, and CLI table/csv rendering.
  - [ ] 3.3 Add representative `launch` process tests for discovery/help plus at least one list/read flow and one lifecycle flow.
  - [ ] 3.4 Add representative `custom_field` and `custom_field_value` process tests for discovery/help and value-management flows.
  - [ ] 3.5 Reuse mocked tool injection where appropriate so routing/output behavior is tested without introducing live-network dependence.

- [ ] **Task 4: Wire staged CLI-only features into the shared suite** (AC: 6, 7)
  - [ ] 4.1 Ensure Story 9.9 coverage extends the shared `uv run lucius` suite for `--pretty`.
  - [ ] 4.2 Ensure Story 9.11 coverage extends the shared `uv run lucius` suite for table datetime localization/fallback.
  - [ ] 4.3 Ensure Story 9.12 coverage extends the shared `uv run lucius` suite for short aliases such as `tc`, `ln`, `cf`, and `cfv`.
  - [ ] 4.4 Reference the shared suite from adjacent CLI stories so future developers know exactly where command-level E2E coverage belongs.

- [ ] **Task 5: Document and validate the CLI E2E strategy** (AC: 1, 2, 7)
  - [ ] 5.1 Update CLI testing notes in story docs and, if needed, in `docs/development.md` or equivalent contributor guidance.
  - [ ] 5.2 Add or update a small coverage inventory comment/assertion so new CLI-local commands are less likely to ship without source-invoked E2E tests.
  - [ ] 5.3 Define the targeted validation command(s) for developers, centered on `uv run --python 3.13 --extra dev pytest tests/e2e/test_cli_* -q` or the equivalent focused files.

## Dev Notes

### Current CLI Test Surface

- Existing source-invoked coverage already lives in `tests/e2e/test_cli_output_formats_uv_run.py`.
- Reusable subprocess utilities live in `tests/cli/subprocess_helpers.py`.
- Current process-level CLI basics also exist in `tests/cli/test_cli_basics.py`, but this story is specifically about E2E-style command invocation through `uv run lucius`.
- Keep a clear distinction:
  - `tests/cli/`: unit and mocked integration around CLI internals
  - `tests/e2e/`: source-invoked subprocess command coverage

### Scope Boundaries

- This story is about CLI execution coverage, not adding new CLI features by itself.
- Run the CLI from source with `uv run lucius`; do not build Nuitka binaries just to exercise command behavior.
- Mock or stub tool functions where needed so the suite validates command parsing, routing, output-format selection, and renderer behavior without depending on live TestOps access.
- Do not duplicate lower-level unit assertions already covered in `tests/cli/` unless the subprocess boundary adds value.

### High-Priority Areas to Cover

- Non-tool-call commands:
  - `lucius`
  - `lucius --help`
  - `lucius --version`
  - `lucius <entity>`
  - `lucius <entity> <action> --help`
  - Epic 9 local commands such as `list`, `auth`, `auth status`, and `install-completions`
- High-priority entities:
  - `test_case`
  - `launch`
  - `custom_field`
  - `custom_field_value`
- CLI-only features that should attach to this suite as they land:
  - `--pretty`
  - local-timezone table rendering
  - short entity aliases

### Relevant Files

- `tests/cli/subprocess_helpers.py`
- `tests/cli/test_cli_basics.py`
- `tests/e2e/test_cli_output_formats_uv_run.py`
- `src/cli/cli_entry.py`
- `src/cli/route_matrix.py`
- `specs/implementation-artifacts/9-7-cli-auth-command-persistent-configuration.md`
- `specs/implementation-artifacts/9-8-cli-list-command-tool-table.md`
- `specs/implementation-artifacts/9-9-cli-pretty-json-output-flag.md`
- `specs/implementation-artifacts/9-10-cli-install-completions-command.md`
- `specs/implementation-artifacts/9-11-cli-table-human-readable-dates-local-timezone-fallback.md`
- `specs/implementation-artifacts/9-12-cli-short-entity-aliases.md`

### Previous Story Intelligence

- Story 9.8 introduces `lucius list` as a CLI-local command and should extend source-invoked command tests.
- Story 9.9 already points at `tests/e2e/test_cli_output_formats_uv_run.py`; use that as an anchor instead of inventing a parallel E2E style.
- Story 9.10 adds another CLI-local command (`install-completions`) that must be covered without depending on repository completion files at runtime.
- Story 9.11 affects CLI-only rendering logic and should be verified through the process boundary, not only formatter helpers.
- Story 9.12 adds short aliases that should be verified through real CLI token parsing in subprocess tests.

### Testing Requirements

- Targeted validation commands after implementation:
  - `uv run --python 3.13 --extra dev pytest tests/e2e/test_cli_output_formats_uv_run.py -q`
  - `uv run --python 3.13 --extra dev pytest tests/e2e/test_cli_*uv_run*.py -q`
  - `uv run --python 3.13 --extra dev pytest tests/cli/test_cli_basics.py tests/cli/test_e2e_mocked.py tests/cli/test_cli_coverage_helpers.py -q`

### References

- [Source: specs/prd.md#CLI Interaction Model]
- [Source: specs/prd.md#CLI Output Data Flow & Format Contracts]
- [Source: specs/prd.md#CLI Functional Requirements]
- [Source: specs/architecture.md#CLI Architecture (Service-First Course Correction)]
- [Source: specs/architecture.md#CLI Output Format Data Flow]
- [Source: specs/architecture.md#Automated Test Coverage Strategy]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: tests/cli/subprocess_helpers.py]
- [Source: tests/e2e/test_cli_output_formats_uv_run.py]
- [Source: src/cli/cli_entry.py]
- [Source: src/cli/route_matrix.py]

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

Ultimate context engine analysis completed - comprehensive developer guide created.

### File List
