# Story 9.11: CLI Human-Readable Table Dates with Local Timezone Fallback

Status: done

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

- [x] **Task 1: Add timezone/date rendering helpers in CLI formatter path** (AC: 1, 2, 3, 5)
  - [x] 1.1 Add helper(s) in `src/cli/cli_entry.py` to resolve display timezone from local environment with deterministic fallback to UTC.
  - [x] 1.2 Add datetime parsing helper(s) for both numeric epoch values and ISO-8601 strings.
  - [x] 1.3 Add table-cell renderer helper(s) that apply human-readable datetime formatting only when parsing succeeds.

- [x] **Task 2: Integrate datetime rendering into table mode only** (AC: 1, 2, 3, 4, 5)
  - [x] 2.1 Update `format_as_table()` to use datetime-aware rendering for date/time-like columns/fields.
  - [x] 2.2 Ensure rendered table explicitly communicates timezone used (local zone label or UTC fallback).
  - [x] 2.3 Keep `format_as_plain()`, `format_as_csv()`, and JSON passthrough behavior unchanged.

- [x] **Task 3: Add and extend tests for formatter behavior** (AC: 1, 2, 3, 5, 6)
  - [x] 3.1 Extend `tests/cli/test_e2e_mocked.py` with table-format assertions for datetime conversion and timezone labeling.
  - [x] 3.2 Extend `tests/cli/test_cli_coverage_helpers.py` with branch tests for datetime parsing success/failure and fallback behavior.
  - [x] 3.3 Add tests ensuring invalid date-like values remain render-safe and do not produce tracebacks.
  - [x] 3.4 Extend the shared `uv run lucius` CLI E2E suite with representative table-rendering process tests for timezone resolution and UTC fallback.

- [x] **Task 4: Document user-facing behavior** (AC: 2, 3, 4)
  - [x] 4.1 Update `docs/CLI.md` output-format documentation to describe table datetime localization behavior.
  - [x] 4.2 Document UTC fallback behavior and explicit timezone labeling in table output examples.

### Review Findings

- [x] [Review][Patch] Absolute `TZ` values can crash table rendering [src/cli/formatting.py:42]
- [x] [Review][Patch] Local timezone fallback uses the current fixed offset for historical/future timestamps [src/cli/formatting.py:47]
- [x] [Review][Patch] UTC conversion fallback can still label the table with the failed timezone [src/cli/formatting.py:106]
- [x] [Review][Patch] Naive ISO strings are silently treated as UTC despite the offset-aware contract [src/cli/formatting.py:90]
- [x] [Review][Patch] Duration-like fields ending in `time` can be converted as wall-clock datetimes [src/cli/formatting.py:64]

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

GPT-5 Codex

### Debug Log References

- `uv run --python 3.13 --extra dev pytest tests/cli/test_e2e_mocked.py tests/cli/test_cli_coverage_helpers.py tests/cli/test_cli_basics.py -q` - red run failed on missing datetime helpers, then passed after implementation (103 passed).
- `uv run --python 3.13 --extra dev pytest tests/cli/test_e2e_mocked.py tests/cli/test_cli_coverage_helpers.py -q` - passed (76 passed).
- `uv run --python 3.13 --extra dev ruff check src/cli tests/cli` - passed.
- `uv run --python 3.13 --extra dev mypy src/cli` - passed.
- `uv run --python 3.13 --extra dev pytest -q` - passed (776 passed, 100 skipped).
- Code review fix validation: `uv run --python 3.13 --extra dev pytest tests/cli/test_e2e_mocked.py tests/cli/test_cli_coverage_helpers.py tests/cli/test_cli_basics.py -q` - passed (108 passed).
- Code review fix validation: `uv run --python 3.13 --extra dev ruff check src/cli tests/cli` - passed.
- Code review fix validation: `uv run --python 3.13 --extra dev mypy src/cli` - passed.

### Completion Notes List

Ultimate context engine analysis completed - comprehensive developer guide created.
- Implemented table-only datetime rendering in the actual CLI formatter module, `src/cli/formatting.py`, where `format_as_table()` and `_format_table_value()` now live in the current codebase.
- Added standard-library timezone resolution with `TZ`/local-zone support and deterministic UTC fallback.
- Added guarded datetime parsing for epoch seconds, epoch milliseconds, and ISO-8601 strings with `Z` or explicit offsets; invalid date-like values remain unchanged.
- Added timezone captions to tables only when datetime values are rendered.
- Preserved `json`, `plain`, and `csv` output behavior and the tool-layer `plain|json` contract.
- Added direct formatter branch coverage and a process-level `uv run lucius ... --format table` regression test with a mocked tool result.
- Addressed code review findings for absolute `TZ` handling, local timezone fallback, UTC fallback labeling, naive ISO handling, and duration-like `*time` fields.

### File List

- docs/CLI.md
- specs/implementation-artifacts/9-11-cli-table-human-readable-dates-local-timezone-fallback.md
- specs/implementation-artifacts/sprint-status.yaml
- src/cli/formatting.py
- tests/cli/subprocess_helpers.py
- tests/cli/test_cli_basics.py
- tests/cli/test_cli_coverage_helpers.py
- tests/cli/test_e2e_mocked.py

### Change Log

- 2026-05-03: Implemented CLI table datetime localization with UTC fallback, coverage, docs, and story tracking updates.
- 2026-05-03: Resolved code review findings and marked story done.
