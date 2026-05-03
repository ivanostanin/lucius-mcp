# Story 9.11: CLI Human-Readable Table Dates with Local Timezone Fallback

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer or QA Engineer,
I want `lucius <entity> <action> --format table` to render date/time fields in a human-readable format using local timezone when available,
so that I can read operational timestamps quickly without manual epoch or ISO conversion.

## Acceptance Criteria

1. **Human-readable table datetime rendering**
  - **Given** table rendering receives JSON payload data from tools
  - **When** date/time-like values are present (for example epoch seconds/milliseconds or ISO-8601 strings)
  - **Then** table output shows those values as human-readable datetimes
  - **And** non-date values remain unchanged
  - **And** unparseable date-like values do not crash rendering.

2. **Local timezone conversion when available**
  - **Given** local timezone can be determined at runtime
  - **When** date/time values are rendered in table format
  - **Then** values are converted to local timezone consistently within the command output
  - **And** the table explicitly states which timezone was used.

3. **UTC fallback with explicit label**
  - **Given** local timezone cannot be resolved or conversion fails
  - **When** table output includes date/time values
  - **Then** values are rendered in UTC
  - **And** timezone is explicitly labeled as `UTC`
  - **And** command execution succeeds without traceback/internal logs.

4. **Output-contract boundaries stay intact**
  - **Given** the CLI output-contract from Story 9.6
  - **When** output format is `json`, `plain`, or `csv`
  - **Then** behavior remains unchanged
  - **And** tool output contract (`plain|json`) remains unchanged.

5. **Deterministic formatting**
  - **Given** repeated CLI invocations on the same input payload and timezone context
  - **When** table output is rendered
  - **Then** datetime formatting is deterministic
  - **And** table column ordering remains deterministic.

6. **Automated coverage**
  - **Given** test suites run
  - **Then** tests cover:
    - epoch seconds and epoch milliseconds date conversion in table mode
    - ISO-8601 parsing (including `Z` and offset variants)
    - explicit local-timezone label
    - explicit UTC fallback label when timezone resolution fails
    - no behavior change for non-table formats.
  - **And** process-level CLI E2E tests validate table datetime rendering through `uv run lucius ...`, not via a built binary.

## Tasks / Subtasks

- [ ] **Task 1: Add timezone/date rendering helpers in CLI formatter path** (AC: 1, 2, 3, 5)
  - [ ] 1.1 Add helper(s) in `src/cli/cli_entry.py` to resolve display timezone from local environment with deterministic fallback to UTC.
  - [ ] 1.2 Add datetime parsing helper(s) for both numeric epoch values and ISO-8601 strings.
  - [ ] 1.3 Add table-cell renderer helper(s) that apply human-readable datetime formatting only when parsing succeeds.

- [ ] **Task 2: Integrate datetime rendering into table mode only** (AC: 1, 2, 3, 4, 5)
  - [ ] 2.1 Update `format_as_table()` to use datetime-aware rendering for date/time-like columns/fields.
  - [ ] 2.2 Ensure rendered table explicitly communicates timezone used (local zone label or UTC fallback).
  - [ ] 2.3 Keep `format_as_plain()`, `format_as_csv()`, and JSON passthrough behavior unchanged.

- [ ] **Task 3: Add and extend tests for formatter behavior** (AC: 1, 2, 3, 5, 6)
  - [ ] 3.1 Extend `tests/cli/test_e2e_mocked.py` with table-format assertions for datetime conversion and timezone labeling.
  - [ ] 3.2 Extend `tests/cli/test_cli_coverage_helpers.py` with branch tests for datetime parsing success/failure and fallback behavior.
  - [ ] 3.3 Add tests ensuring invalid date-like values remain render-safe and do not produce tracebacks.
  - [ ] 3.4 Extend the shared `uv run lucius` CLI E2E suite with representative table-rendering process tests for timezone resolution and UTC fallback.

- [ ] **Task 4: Document user-facing behavior** (AC: 2, 3, 4)
  - [ ] 4.1 Update `docs/CLI.md` output-format documentation to describe table datetime localization behavior.
  - [ ] 4.2 Document UTC fallback behavior and explicit timezone labeling in table output examples.

## Dev Notes

### Current Implementation Snapshot

- Table formatting is centralized in `src/cli/cli_entry.py` (`format_as_table`, `_format_table_value`).
- Table/csv rendering operates on parsed JSON payloads after tool call completion.
- Tool output contract remains `plain|json` at tool layer (`src/tools/output_contract.py`), while `table|csv` remain CLI-only renderers.

### Implementation Guardrails

- Use Python standard library datetime/timezone handling only; do not add third-party timezone dependencies.
- Keep this as a CLI rendering concern; do not change service-layer or tool-layer payload contracts.
- Avoid locale-specific formatting that could create unstable test output.
- Preserve existing deterministic column ordering and non-date rendering behavior.

### File Structure Requirements

- Primary code file:
  - `src/cli/cli_entry.py`
- Primary test files:
  - `tests/cli/test_e2e_mocked.py`
  - `tests/cli/test_cli_coverage_helpers.py`
- Docs:
  - `docs/CLI.md`

### Previous Story Intelligence

- Story 9.6 defined current output-contract boundaries (`plain|json` tool contract; CLI-only `table|csv` renderers); this story must not violate those boundaries.
- Story 9.9 introduced JSON pretty-printing behavior; table datetime formatting must stay independent from `--pretty`.
- Story 9.10 focuses on completions and local CLI setup; no overlap with action-result table rendering, but keep command UX consistency.

### Git Intelligence Summary

- Recent commits are release/dependency maintenance oriented, so this story should prefer minimal, scoped CLI formatter changes with explicit tests to prevent regressions in stable CLI behavior.

### Testing Requirements

- Targeted validation commands after implementation:
  - `uv run --python 3.13 --extra dev pytest tests/cli/test_e2e_mocked.py tests/cli/test_cli_coverage_helpers.py -q`
  - `uv run ruff check src/cli tests/cli`
  - `uv run mypy src/cli`

### References

- [Source: specs/project-planning-artifacts/epics.md#Epic 9]
- [Source: specs/prd.md#CLI Interaction Model]
- [Source: specs/prd.md#CLI Output Data Flow & Format Contracts]
- [Source: specs/architecture.md#CLI Output Format Data Flow]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: src/cli/cli_entry.py]
- [Source: src/tools/output_contract.py]
- [Source: src/tools/launches.py]
- [Source: tests/cli/test_e2e_mocked.py]
- [Source: tests/cli/test_cli_coverage_helpers.py]

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

Ultimate context engine analysis completed - comprehensive developer guide created.

### File List
