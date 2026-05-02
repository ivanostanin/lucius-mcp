# Story 9.9: CLI Pretty JSON Output Flag

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer or QA Engineer,
I want an optional `--pretty` flag for CLI commands that use JSON output,
so that I can read structured responses with line breaks and indentation while preserving existing compact JSON behavior by default.

## Acceptance Criteria

1. **Pretty-print for default JSON action output**
   - **Given** I run an entity/action command without `--format` and with `--pretty`
   - **When** the tool returns valid JSON text
   - **Then** the CLI still requests tool `output_format=json`
   - **And** the CLI prints pretty JSON (multi-line with deterministic indentation).

2. **Pretty-print for explicit JSON format**
   - **Given** I run `lucius <entity> <action> --format json --pretty`
   - **When** the command succeeds
   - **Then** output is pretty JSON
   - **And** no extra transformation is applied beyond JSON reformatting.

3. **No behavior change without `--pretty`**
   - **Given** I run action commands without `--pretty`
   - **When** output is `json|plain|table|csv`
   - **Then** current behavior remains unchanged, including passthrough contracts and table/csv rendering rules.

4. **Validation for invalid `--pretty` combinations**
   - **Given** I pass `--pretty` with `--format plain`, `--format table`, or `--format csv`
   - **When** arguments are validated
   - **Then** the CLI exits with a clear `CLIError`
   - **And** the hint explains that `--pretty` is valid only for JSON output.

5. **Non-action command safety**
   - **Given** I run non-action flows (`lucius`, `lucius <entity>`, `lucius --help`, `lucius --version`)
   - **When** `--pretty` is supplied where unsupported
   - **Then** CLI returns a clean, guided error and does not introduce traceback/internal logs.

6. **Help, documentation, and completions**
   - **Given** this feature is implemented
   - **When** users inspect help/docs/completions
   - **Then** action usage includes `--pretty`
   - **And** docs explain that `--pretty` applies only to JSON output
   - **And** completion generation includes `--pretty` in action options for bash, zsh, fish, and PowerShell.

7. **Automated coverage**
   - **Given** test suites run
   - **Then** tests verify:
     - JSON default + `--pretty` output formatting
     - explicit `--format json --pretty` formatting
     - rejection for non-JSON combinations
     - preservation of existing non-pretty output behavior
     - no traceback/internal logs in error paths.
   - **And** process-level CLI E2E coverage exercises `--pretty` via `uv run lucius ...`, not via a built binary.

## Tasks / Subtasks

- [ ] **Task 1: Extend CLI action option parsing for `--pretty`** (AC: 1, 2, 4, 5)
  - [ ] 1.1 Add `pretty_json: bool = False` to `ActionOptions` in `src/cli/cli_entry.py`.
  - [ ] 1.2 Extend `parse_action_options()` to recognize `--pretty`.
  - [ ] 1.3 Update option validation and error hints so `--pretty` is accepted only for JSON action output.

- [ ] **Task 2: Implement pretty JSON rendering path** (AC: 1, 2, 3)
  - [ ] 2.1 In action execution path, keep tool request contract unchanged (`output_format=json` for default/json/table/csv and `plain` only for plain).
  - [ ] 2.2 When effective output mode is JSON and `--pretty` is enabled, parse tool JSON and re-render with stable indentation.
  - [ ] 2.3 If tool JSON is invalid while pretty-print is requested, return actionable `CLIError` without traceback.

- [ ] **Task 3: Preserve existing contracts and boundaries** (AC: 3)
  - [ ] 3.1 Keep tool output contract unchanged in `src/tools/output_contract.py` (`plain|json`, default `plain`).
  - [ ] 3.2 Keep `table|csv` rendering logic unchanged and CLI-local.
  - [ ] 3.3 Avoid introducing FastMCP/runtime imports in help/discovery paths.

- [ ] **Task 4: Update help text, docs, and completion generation** (AC: 6)
  - [ ] 4.1 Update usage/help strings in `src/cli/cli_entry.py` to include `--pretty`.
  - [ ] 4.2 Update `docs/CLI.md` with `--pretty` examples and JSON-only applicability.
  - [ ] 4.3 Add `--pretty` to action option completions via `deployment/scripts/generate_completions.py`.
  - [ ] 4.4 Regenerate completion artifacts under `deployment/shell-completions/`.

- [ ] **Task 5: Add/extend tests** (AC: 7)
  - [ ] 5.1 Extend `tests/cli/test_cli_basics.py` for process-level pretty JSON behavior and invalid flag combinations.
  - [ ] 5.2 Extend `tests/cli/test_e2e_mocked.py` for argument parsing and mocked action-output pretty rendering.
  - [ ] 5.3 Extend `tests/e2e/test_cli_output_formats_uv_run.py` for uv-run pretty JSON checks.
  - [ ] 5.4 Extend `tests/cli/test_cli_coverage_helpers.py` for option parser branches (`--pretty`) and error-path assertions.

## Dev Notes

### Current Behavior Snapshot

- `src/cli/cli_entry.py` currently defaults action output to JSON and forwards JSON/plain text directly for passthrough modes.
- `parse_action_options()` currently supports only `--args/-a`, `--format/-f`, and `--help/-h`.
- `format_json()` already exists and can be reused for deterministic pretty JSON rendering.
- Completion option lists in `deployment/scripts/generate_completions.py` currently do not include `--pretty`.

### Implementation Guardrails

- This is a CLI-layer feature; do not change service logic or tool signatures for this story.
- Do not change `CANONICAL_ROUTE_MATRIX` for this flag.
- Do not alter existing default compact JSON behavior when `--pretty` is not requested.
- Keep output behavior deterministic and testable for CI.

### Project Structure Notes

- Primary change targets:
  - `src/cli/cli_entry.py`
  - `deployment/scripts/generate_completions.py`
  - `deployment/shell-completions/lucius.bash`
  - `deployment/shell-completions/lucius.zsh`
  - `deployment/shell-completions/lucius.fish`
  - `deployment/shell-completions/lucius.ps1`
  - `docs/CLI.md`
  - `tests/cli/test_cli_basics.py`
  - `tests/cli/test_e2e_mocked.py`
  - `tests/cli/test_cli_coverage_helpers.py`
  - `tests/e2e/test_cli_output_formats_uv_run.py`

### Previous Story Intelligence

- Story 9.6 established CLI output format/data-flow contracts and passthrough guarantees.
- Story 9.8 established local `list` command behavior and completion update workflow.
- This story should layer on top of those contracts without changing route semantics or tool-level output defaults.

### References

- [Source: specs/project-planning-artifacts/epics.md#Epic 9]
- [Source: specs/prd.md#CLI Interaction Model]
- [Source: specs/prd.md#CLI Output Data Flow & Format Contracts]
- [Source: specs/architecture.md#CLI Architecture (Service-First Course Correction)]
- [Source: specs/architecture.md#CLI Output Format Data Flow]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: src/cli/cli_entry.py]
- [Source: deployment/scripts/generate_completions.py]
- [Source: docs/CLI.md]
- [Source: tests/cli/test_cli_basics.py]
- [Source: tests/cli/test_e2e_mocked.py]
- [Source: tests/e2e/test_cli_output_formats_uv_run.py]

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

Ultimate context engine analysis completed - comprehensive developer guide created.

### File List
