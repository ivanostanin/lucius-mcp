# Story 9.12: CLI Short Entity Aliases

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer or QA Engineer,
I want short aliases for common CLI entities such as `tc` for `test_case`,
so that frequent `lucius <entity> <action>` commands are faster to type while preserving the canonical entity/action model.

## Acceptance Criteria

1. **Short aliases resolve through the canonical alias source**
  - **Given** the CLI route matrix defines canonical entities and existing aliases
  - **When** short aliases are added
  - **Then** each alias resolves to exactly one canonical entity
  - **And** aliases are defined in `src/cli/route_matrix.py` `ENTITY_ALIASES`
  - **And** no duplicate canonical entities, fake tools, or parallel parser mappings are introduced.

2. **`tc` works for `test_case`**
  - **Given** the user types `tc` as the entity token
  - **When** they run `lucius tc`, `lucius tc list --help`, or `lucius tc list --args '{}'`
  - **Then** the CLI behaves exactly as if the user typed `test_case`
  - **And** errors, validation, output formats, and tool resolution remain unchanged.

3. **Useful short aliases are available for all current canonical entities**
  - **Given** the current canonical entities in `CANONICAL_ROUTE_MATRIX`
  - **When** short aliases are configured
  - **Then** the following mappings are supported unless implementation finds a concrete collision:
    - `tc` -> `test_case`
    - `cf` -> `custom_field`
    - `cfv` -> `custom_field_value`
    - `ln` -> `launch`
    - `int` -> `integration`
    - `ss` -> `shared_step`
    - `tl` -> `test_layer`
    - `tls` -> `test_layer_schema`
    - `ts` -> `test_suite`
    - `tp` -> `test_plan`
    - `df` -> `defect`
    - `dm` -> `defect_matcher`
  - **And** any rejected alias has a documented collision reason in code comments or tests.

4. **Help and completion discovery include short aliases**
  - **Given** aliases are added
  - **When** root help is rendered
  - **Then** short aliases are visible alongside existing entity aliases where aliases are currently displayed.
  - **Given** completion scripts are regenerated
  - **When** bash, zsh, fish, and PowerShell completion content is inspected
  - **Then** short aliases are offered at the entity position
  - **And** each short alias offers the same action completions as its canonical entity.

5. **Normalization and error behavior remain clean**
  - **Given** alias tokens are normalized by the existing `normalize_token()` path
  - **When** users provide uppercase aliases or dash/underscore variants where applicable
  - **Then** resolution remains consistent with existing alias behavior
  - **And** invalid aliases still produce clean `CLIError` messages with no Python traceback/internal logs.

6. **Automated coverage protects alias behavior**
  - **Given** CLI tests run
  - **Then** tests verify:
    - representative short aliases resolve in entity discovery and action help
    - `tc` can execute the same mocked action path as `test_case`
    - alias map has no duplicate alias keys with conflicting canonical targets
    - root help exposes short aliases
    - generated completions include short aliases and preserve existing aliases
    - canonical, plural, and dash-form aliases continue to work.
  - **And** source-invoked CLI E2E tests exercise representative alias flows via `uv run lucius ...`, without requiring a built binary.

## Tasks / Subtasks

- [x] **Task 1: Add short aliases to the canonical alias map** (AC: 1, 2, 3, 5)
  - [x] 1.1 Update `src/cli/route_matrix.py` `ENTITY_ALIASES` with the short alias mappings.
  - [x] 1.2 Keep all canonical entity/action entries in `CANONICAL_ROUTE_MATRIX` unchanged.
  - [x] 1.3 Validate aliases through `all_entities_with_aliases()` and existing `normalize_token()` behavior instead of adding parser-specific special cases.
  - [x] 1.4 Add collision assertions so no alias can silently map to two canonical entities.

- [x] **Task 2: Preserve and improve alias discoverability** (AC: 4)
  - [x] 2.1 Ensure `print_global_help()` displays short aliases in the entity table.
  - [x] 2.2 Keep entity-specific help output canonical (`Actions for test_case`) after resolving short aliases.
  - [x] 2.3 Update `docs/CLI.md` to document short aliases and examples, including `lucius tc list --args '{}'`.

- [x] **Task 3: Regenerate and validate shell completions** (AC: 4, 6)
  - [x] 3.1 Regenerate completions using `deployment/scripts/generate_completions.py`.
  - [x] 3.2 Verify generated bash, zsh, fish, and PowerShell completions include short aliases at the entity position.
  - [x] 3.3 Verify actions offered for short aliases match their canonical entity action sets.

- [x] **Task 4: Add targeted CLI regression tests** (AC: 2, 5, 6)
  - [x] 4.1 Extend `tests/cli/test_cli_basics.py` with process-level checks for `tc` entity discovery, action help, and mocked action execution.
  - [x] 4.2 Extend `tests/cli/test_cli_coverage_helpers.py` or `tests/cli/test_route_matrix.py` with alias-map uniqueness and representative short-alias resolution tests.
  - [x] 4.3 Add completion content assertions for `tc`, `cf`, `cfv`, and at least one multi-word entity alias such as `tls`.
  - [x] 4.4 Confirm existing tests for `integrations`, `test-cases`, and canonical entity names still pass unchanged.
  - [x] 4.5 Extend the shared `uv run lucius` CLI E2E suite with representative alias commands such as `tc`, `ln`, `cf`, and `cfv`.

## Dev Notes

### Current Implementation Snapshot

- CLI command parsing is centralized in `src/cli/cli_entry.py`.
- Canonical entity/action routing is centralized in `src/cli/route_matrix.py`.
- `ENTITY_ALIASES` currently contains plural aliases such as `test_cases` -> `test_case`.
- `all_entities_with_aliases()` automatically adds dash-form variants for each canonical entity and configured alias.
- `resolve_entity_name()` builds its accepted alias map from `all_entities_with_aliases()`.
- Shell completions are generated from the same route-matrix helpers by `deployment/scripts/generate_completions.py`.

### Implementation Guardrails

- Do not add short aliases to `CANONICAL_ROUTE_MATRIX`; they are aliases, not canonical entities.
- Do not add fake tools or duplicate route entries for aliases.
- Do not special-case `tc` in `run_cli()` or `resolve_entity_name()` unless a reusable alias collision guard requires a small helper.
- Preserve existing legacy command behavior around `list`/`call`; short aliases must not turn top-level command names into entities.
- Keep CLI runtime independent from FastMCP, `src.main`, Starlette, uvicorn, and HTTP server imports.
- Keep all errors user-facing through `CLIError`; no tracebacks or internal logs for invalid aliases.

### Proposed Alias Set

- `tc` -> `test_case`
- `cf` -> `custom_field`
- `cfv` -> `custom_field_value`
- `ln` -> `launch`
- `int` -> `integration`
- `ss` -> `shared_step`
- `tl` -> `test_layer`
- `tls` -> `test_layer_schema`
- `ts` -> `test_suite`
- `tp` -> `test_plan`
- `df` -> `defect`
- `dm` -> `defect_matcher`

Rationale: these are short, mnemonic, and avoid using `l` for `launch`, which could be confused with top-level `list` behavior from adjacent CLI stories.

### File Structure Requirements

- Primary code:
  - `src/cli/route_matrix.py`
  - `src/cli/cli_entry.py` only if root-help alias display needs adjustment
- Generated artifacts:
  - `deployment/shell-completions/lucius.bash`
  - `deployment/shell-completions/lucius.zsh`
  - `deployment/shell-completions/lucius.fish`
  - `deployment/shell-completions/lucius.ps1`
- Tests:
  - `tests/cli/test_cli_basics.py`
  - `tests/cli/test_cli_coverage_helpers.py`
  - `tests/cli/test_route_matrix.py`
- Docs:
  - `docs/CLI.md`

### Previous Story Intelligence

- Story 9.3 established the service-first `lucius <entity> <action>` grammar. This story must preserve that grammar and only add shorter entity tokens.
- Story 9.6 established output-contract boundaries. Aliases must resolve to the same action path and must not alter output-format behavior.
- Story 9.8 adds local discovery behavior and completion exposure for top-level commands. Alias changes must not represent discovery commands as TestOps entities.
- Story 9.9 adds JSON-only `--pretty` handling. Alias parsing must happen before action-option parsing and must not affect option validation.
- Story 9.10 embeds/generated completions. Regenerate completion scripts after route alias changes rather than editing generated outputs by hand.
- Story 9.11 is table-rendering scoped and should not be touched for this alias story.

### Git Intelligence Summary

- Recent commits are release/dependency maintenance oriented. Keep implementation minimal and test-focused.
- Current worktree already contains ready-for-dev Epic 9 story files for 9.7 through 9.11; do not overwrite or reformat those unrelated story artifacts.

### Testing Requirements

- Targeted validation commands after implementation:
  - `uv run --python 3.13 --extra dev pytest tests/cli/test_cli_basics.py tests/cli/test_cli_coverage_helpers.py tests/cli/test_route_matrix.py -q`
  - `uv run ruff check src/cli tests/cli deployment/scripts/generate_completions.py`
  - `uv run mypy src/cli`
- Completion generation command:
  - `uv run --python 3.13 --extra dev python deployment/scripts/generate_completions.py`

### References

- [Source: specs/project-planning-artifacts/epics.md#Epic 9]
- [Source: specs/prd.md#Product Scope]
- [Source: specs/architecture.md#Technical Constraints & Dependencies]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: src/cli/route_matrix.py]
- [Source: src/cli/cli_entry.py]
- [Source: deployment/scripts/generate_completions.py]
- [Source: docs/CLI.md]
- [Source: tests/cli/test_cli_basics.py]
- [Source: tests/cli/test_cli_coverage_helpers.py]
- [Source: tests/cli/test_route_matrix.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-05-04: Added failing CLI alias regression coverage, then implemented short aliases in `ENTITY_ALIASES`.
- 2026-05-04: Ran `uv run --python 3.13 --extra dev pytest tests/cli/test_cli_basics.py tests/cli/test_cli_coverage_helpers.py tests/cli/test_route_matrix.py -q` - passed, 126 tests.
- 2026-05-04: Ran `uv run ruff check src/cli tests/cli deployment/scripts/generate_completions.py` - passed after import ordering fix.
- 2026-05-04: Ran `uv run mypy src/cli` - passed.
- 2026-05-04: Regenerated shell completions with `uv run --python 3.13 --extra dev python deployment/scripts/generate_completions.py`.
- 2026-05-04: Inspected generated bash, zsh, fish, and PowerShell completion scripts for `tc`, `cf`, `cfv`, and `tls` entity tokens and matching action blocks.
- 2026-05-04: Ran `uv run --python 3.13 --extra dev pytest tests/cli/test_completion_installer.py tests/cli/test_cli_basics.py tests/cli/test_cli_coverage_helpers.py tests/cli/test_route_matrix.py -q` - passed, 156 tests.
- 2026-05-04: Ran `bash scripts/full-test-suite.sh` - unit, integration, docs, and CLI phases passed; live `tests/e2e` phase failed with external Allure TestOps `httpx.ConnectError`, `RemoteProtocolError`, and `ReadTimeout` during token/API calls, so story was not moved to review.
- 2026-05-04: Ran `uv run --extra dev pytest tests/packaging -q` separately after full-suite E2E halt - passed, 34 tests.
- 2026-05-04: Reran `uv run --extra dev --env-file .env.test pytest tests/e2e -n auto -rs` with escalated filesystem/network access after sandbox uv-cache denial - passed, 113 passed and 1 skipped.

### Completion Notes List

Ultimate context engine analysis completed - comprehensive developer guide created.
- Implemented all short entity aliases through `src/cli/route_matrix.py` `ENTITY_ALIASES`; no parser-specific alias handling or canonical route duplication was introduced.
- Added normalized alias collision validation in `all_entities_with_aliases()` so aliases cannot silently target two canonical entities or an unknown entity.
- Preserved canonical entity/action help after short alias resolution; `lucius tc` renders `Actions for test_case` and `lucius tc list --help` renders canonical `lucius test_case list` help.
- Updated `docs/CLI.md` with short alias mappings and `lucius tc list --args '{}'` usage.
- Regenerated checked-in bash, zsh, fish, and PowerShell completion scripts from the completion generator.
- Added CLI regression coverage for short alias resolution, root help display, mocked `tc list` execution, completion generation, `uv run lucius` alias flows, and completion installer output.
- Cleared the earlier live E2E connectivity blocker with a successful E2E rerun and moved the story to review.

### File List

- `src/cli/route_matrix.py`
- `docs/CLI.md`
- `deployment/shell-completions/lucius.bash`
- `deployment/shell-completions/lucius.zsh`
- `deployment/shell-completions/lucius.fish`
- `deployment/shell-completions/lucius.ps1`
- `tests/cli/test_cli_basics.py`
- `tests/cli/test_cli_coverage_helpers.py`
- `tests/cli/test_completion_installer.py`
- `tests/cli/test_route_matrix.py`
- `specs/implementation-artifacts/9-12-cli-short-entity-aliases.md`
- `specs/implementation-artifacts/sprint-status.yaml`
