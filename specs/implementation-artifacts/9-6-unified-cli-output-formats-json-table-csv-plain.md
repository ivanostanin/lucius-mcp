# Story 9.6: Unified CLI Output Formats (JSON Default + Table/CSV/Plain)

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer or QA Engineer,
I want CLI tool results to support `plain`, `json`, `table`, and `csv` output formats with `json` as the default,
so that both machine consumers and human reviewers can use the same commands effectively.

This story extends Epic 9 CLI output behavior by adding first-class `csv` support and formalizing rendering rules for multi-record responses (for example `test_case list`).

## Acceptance Criteria

1. **Format matrix and defaults**
   - **Given** any supported `lucius <entity> <action>` command
   - **When** `--format` is omitted
   - **Then** output defaults to `json`
   - **And** this default applies to all CLI action calls unless `--format` is explicitly provided
   - **And** explicit `--format plain|json|table|csv` is accepted.

2. **Plain format compatibility**
   - **Given** existing command behavior that currently returns plain text summaries
   - **When** I run with `--format plain`
   - **Then** output remains human-readable and backward-compatible with current plain semantics.
   - **And** escaped newline sequences (`\\n`) in plain text payloads are rendered as actual line breaks in terminal output (not as literal backslash+n text).

3. **Table format for multi-record responses**
   - **Given** a command that returns multiple records (for example `lucius test_case list`)
   - **When** I run with `--format table`
   - **Then** output is a printable tabular view with headers and rows
   - **And** column order is deterministic across runs.

4. **CSV format for multi-record responses**
   - **Given** a command that returns multiple records (for example `lucius test_case list`)
   - **When** I run with `--format csv`
   - **Then** output is a valid CSV table with a header row
   - **And** CSV columns match the table-format columns for the same command
   - **And** CSV escaping/quoting is RFC-4180-compatible.

5. **Single-record/non-tabular behavior**
   - **Given** commands returning single objects or plain messages
   - **When** I request `table` or `csv`
   - **Then** output follows a documented, deterministic fallback behavior (single-row projection or actionable format guidance)
   - **And** no traceback or internal logs are printed.

6. **E2E coverage for format behavior**
   - **Given** CLI test suites
   - **When** tests run in CI
   - **Then** E2E tests verify `plain`, `json`, `table`, and `csv` rendering for representative commands
   - **And** at minimum include one multi-record flow (`test_case list`) and one single-record flow
   - **And** validate deterministic headers/column ordering for `table` and `csv`
   - **And** include explicit tests validating `plain` newline rendering (`\\n` -> newline).

7. **Architecture and PRD documentation requirements**
   - **Given** this story implementation
   - **When** documentation is updated
   - **Then** `specs/architecture.md` includes an explicit data-flow section for output format rendering
   - **And** `specs/prd.md` includes the canonical format contract (`plain`, `json` default, `table`, `csv`) and data-flow expectations
   - **And** both docs stay consistent with CLI behavior and tests.

8. **Breaking-change commit convention requirement**
   - **Given** Story 9.6 introduces CLI output behavior changes
   - **When** changes are committed
   - **Then** commit message uses Conventional Commits with a breaking marker `!` (example: `feat(cli)!: ...`)
   - **And** commit body includes a `BREAKING CHANGE:` note describing the behavior change.

## Tasks / Subtasks

- [ ] **Task 1: Extend format enum and defaults** (AC: 1, 2)
  - [ ] 1.1 Add `csv` to accepted output format values.
  - [ ] 1.2 Enforce `json` as the default for all CLI action calls whenever `--format` is omitted.
  - [ ] 1.3 Preserve backward-compatible `plain` summaries.
  - [ ] 1.4 Render escaped newline markers (`\\n`) as real line breaks in `plain` output.

- [ ] **Task 2: Implement rendering contracts** (AC: 3, 4, 5)
  - [ ] 2.1 Implement deterministic table rendering for multi-record outputs.
  - [ ] 2.2 Implement CSV rendering using the same column selection/order as table.
  - [ ] 2.3 Implement and document single-record fallback behavior for table/csv requests.
  - [ ] 2.4 Ensure formatter failures return user-facing hints only.

- [ ] **Task 3: Add comprehensive tests** (AC: 6)
  - [ ] 3.1 Add unit tests for format parsing/default behavior.
  - [ ] 3.2 Add mocked integration tests for formatter output shapes and deterministic headers.
  - [ ] 3.3 Add E2E CLI tests for `plain|json|table|csv` on representative commands.
  - [ ] 3.4 Add regression tests for CSV quoting/escaping edge cases.
  - [ ] 3.5 Add unit + E2E regression tests for `plain` newline rendering (`\\n` is printed as newline, not literal text).

- [ ] **Task 4: Update docs and traceability artifacts** (AC: 7)
  - [ ] 4.1 Update `specs/prd.md` format contract and data-flow section.
  - [ ] 4.2 Update `specs/architecture.md` CLI format rendering data-flow section.
  - [ ] 4.3 Update Epic 9 story listing and sprint status tracking for Story 9.6.

- [ ] **Task 5: Commit metadata for breaking behavior changes** (AC: 8)
  - [ ] 5.1 Use Conventional Commit with `!` marker for Story 9.6 implementation commit.
  - [ ] 5.2 Add `BREAKING CHANGE:` footer describing JSON default and plain newline rendering behavior changes.

## Dev Notes

### Scope Clarification

- Story focuses on output formatting contracts at the CLI layer.
- Existing domain/service behavior remains unchanged.
- No new business logic layer is introduced.

### Format Intent

- `json`: machine-consumable default for automation.
- `plain`: concise human-readable summaries (current behavior baseline).
- `table`: readable terminal table for multi-record result sets.
- `csv`: export-friendly tabular output for multi-record result sets.

### Suggested Touchpoints

- `src/cli/cli_entry.py`
- `src/cli/formatter` module (or equivalent formatter functions)
- `tests/cli/test_cli_basics.py`
- `tests/cli/test_e2e_mocked.py`
- CLI E2E process-invocation tests
- `specs/prd.md`
- `specs/architecture.md`

### References

- [Source: specs/project-planning-artifacts/epics.md]
- [Source: specs/prd.md]
- [Source: specs/architecture.md]
- [Source: specs/implementation-artifacts/9-3-service-first-cli-entity-action.md]
- [Source: specs/implementation-artifacts/9-5-nuitka-onefile-caching-for-cli-startup.md]

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Completion Notes List

- Story created in Epic 9 as ready-for-dev.
- Acceptance criteria explicitly include E2E test coverage and data-flow documentation updates in PRD/Architecture.
- Output format contract expanded to include `csv` while keeping `plain` and `json` default behavior explicit.

### File List

- specs/implementation-artifacts/9-6-unified-cli-output-formats-json-table-csv-plain.md
