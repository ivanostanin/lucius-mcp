# Story 9.8: CLI List Command Tool Table

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer or QA Engineer,
I want `lucius list` to display the same available-tools discovery table as running `lucius` without arguments,
so that I can explicitly list supported CLI capabilities without relying on an empty invocation.

## Acceptance Criteria

1. **Top-level list command works**
   - **Given** I run `lucius list`
   - **When** the CLI starts
   - **Then** it exits with code `0`
   - **And** it prints the same discovery table content as running `lucius` with no arguments.

2. **No-argument output remains the source of truth**
   - **Given** both `lucius` and `lucius list` are executed
   - **When** their stdout is compared after normal CLI rendering
   - **Then** they contain the same usage section and the same discovery table rows for all canonical entities/actions.

3. **List help is local and explicit**
   - **Given** I run `lucius list --help` or `lucius list -h`
   - **When** help is requested
   - **Then** it exits with code `0`
   - **And** it describes `list` as a local discovery command
   - **And** it makes clear that `list` does not require `--args`, credentials, or network access.

4. **No MCP/runtime imports for list**
   - **Given** `lucius list` is used
   - **When** the output is generated
   - **Then** it uses build-time static metadata loaded through `load_tool_schemas()` and `build_command_registry()`
   - **And** it does not import `src.tools`, `src.main`, `fastmcp`, `starlette`, `uvicorn`, or any HTTP server/runtime components.

5. **Legacy command behavior remains correct**
   - **Given** users run removed legacy commands
   - **When** `lucius call ...` is invoked
   - **Then** it still fails with the existing legacy-command guidance
   - **And** only top-level `list` is restored as an accepted local command.

6. **Route/schema integrity is preserved**
   - **Given** the canonical route matrix and generated static schemas
   - **When** `lucius list` is implemented
   - **Then** `list` is not added to `CANONICAL_ROUTE_MATRIX` as a fake TestOps entity or action
   - **And** `src/cli/data/tool_schemas.json` is not modified unless the schema generator output is legitimately stale.

7. **Tests cover the CLI contract**
   - **Given** automated tests run
   - **Then** they verify `lucius list`, `lucius list --help`, output parity with no-argument invocation, shell completion exposure, `lucius call` rejection, no traceback/internal logs, and no import-boundary regressions.
   - **And** process-level CLI E2E tests invoke `uv run lucius list ...` from source, not via a built binary.

8. **Shell completions expose the new top-level command**
   - **Given** shell completions are generated
   - **When** users request top-level command completion for `lucius`
   - **Then** `list` is offered alongside `help`, `version`, and entity tokens
   - **And** bash, zsh, fish, and PowerShell completion scripts include `list`
   - **And** generated completion scripts stay derived from `deployment/scripts/generate_completions.py`, not hand-edited only.

## Tasks / Subtasks

- [x] **Task 1: Add top-level `list` routing** (AC: 1, 2, 4, 5, 6)
  - [x] 1.1 Update `src/cli/cli_entry.py` so `argv[0] == "list"` is handled before entity resolution.
  - [x] 1.2 Reuse the same code path as no-argument/global help output: load static schemas, build the registry, and call the existing global discovery renderer.
  - [x] 1.3 Keep `argv[0] == "call"` rejected with the existing legacy-command `CLIError` and migration hint.
  - [x] 1.4 Do not add `list` to `src/cli/route_matrix.py`; it is CLI-local discovery, not a TestOps tool route.

- [x] **Task 2: Add explicit help for `lucius list`** (AC: 3, 4)
  - [x] 2.1 Support `lucius list --help` and `lucius list -h` without entering entity/action option parsing.
  - [x] 2.2 Document that `list` prints local static discovery metadata and requires no credentials/network.
  - [x] 2.3 Reject unexpected options to `lucius list` with a clean `CLIError` and no traceback.

- [x] **Task 3: Preserve static import boundary** (AC: 4, 6)
  - [x] 3.1 Ensure the `list` implementation imports only CLI-local modules already used by no-argument help.
  - [x] 3.2 Do not call `call_tool_function()`, `_load_tool_function()`, `resolve_tool_function()`, or anything under `src.tools` for `list`.
  - [x] 3.3 Keep `src/cli/data/tool_schemas.json` as the static metadata source; do not introspect live MCP tools at runtime.

- [x] **Task 4: Add CLI tests** (AC: 1, 2, 3, 5, 7)
  - [x] 4.1 Extend `tests/cli/test_cli_basics.py` with `lucius list` success assertions.
  - [x] 4.2 Add a parity assertion comparing no-argument stdout and `list` stdout for shared usage/table markers such as `Available Entities`, canonical entity names, and action names.
  - [x] 4.3 Add `lucius list --help` assertions for local discovery language and no credential requirement.
  - [x] 4.4 Keep or adjust the legacy test so `lucius call ...` remains rejected while `lucius list` is accepted.
  - [x] 4.5 Assert `Traceback` and Python file frames are absent from `list` error cases.

- [x] **Task 5: Add import-boundary regression coverage** (AC: 4, 7)
  - [x] 5.1 Add or extend a subprocess/snippet test that blocks or detects imports of `src.tools`, `src.main`, `fastmcp`, and HTTP server modules during `run_cli(["list"])`.
  - [x] 5.2 Mirror the existing help/version import-boundary intent; `list` must be as lightweight as no-argument help.
  - [x] 5.3 If a packaging-level binary smoke test is cheap, update it to call `list` as the explicit discovery command; otherwise keep packaging coverage focused on source tests.
  - [x] 5.4 Extend the shared `uv run lucius` CLI E2E suite with `lucius list`, `lucius`, and `lucius list --help` parity checks.

- [x] **Task 6: Update user-facing docs if needed** (AC: 3)
  - [x] 6.1 Update `docs/CLI.md` command model/examples to include `lucius list` as explicit discovery.
  - [x] 6.2 Update README CLI snippets only if the README already documents no-argument CLI discovery.

- [x] **Task 7: Update shell completions** (AC: 8)
  - [x] 7.1 Update `deployment/scripts/generate_completions.py` so top-level completion tokens include `list`.
  - [x] 7.2 Regenerate `deployment/shell-completions/lucius.bash`, `deployment/shell-completions/lucius.zsh`, `deployment/shell-completions/lucius.fish`, and `deployment/shell-completions/lucius.ps1`.
  - [x] 7.3 Add or extend tests/assertions so generated completion output includes `list` as a top-level command for every supported shell.
  - [x] 7.4 Keep `call` out of completion suggestions unless the project intentionally wants to expose rejected legacy commands.

## Dev Notes

### Current Behavior and Required Change

- Active CLI entry point: `src/cli/cli_entry.py`.
- Current no-argument path is `run_cli([])` at `src/cli/cli_entry.py:602-608`; it loads static schemas, builds the command registry, and calls `print_global_help(registry)`.
- Current legacy rejection is `if argv[0] in {"list", "call"}` at `src/cli/cli_entry.py:614-621`; this must be split so only `call` remains rejected and `list` becomes a supported local command.
- `print_global_help()` currently renders the discovery table titled `Available Entities`. The user requirement is parity with this no-argument table, so do not invent a different output unless the no-argument renderer is intentionally changed in the same implementation.

### Implementation Guardrails

- `lucius list` is a CLI-local discovery command. It is not an MCP tool and not a TestOps entity/action.
- Do not add `list` to `CANONICAL_ROUTE_MATRIX`; doing so would make `build_command_registry()` expect a nonexistent tool schema and would blur the TestOps route contract.
- Do not generate a fake `list` entry in `src/cli/data/tool_schemas.json`.
- Do not import `src.tools`, `src.main`, FastMCP, Starlette, uvicorn, or HTTP components for `list`; this command must stay fast and offline.
- If `lucius list --format ...` is considered, keep it out of scope unless the implementation can preserve parity with no-argument output. The requested behavior is the same table as no args, not a new formatter contract.

### Output Contract Context

- Story 9.6 established action output behavior: action commands default to requesting tool `json`; `plain/json` are passthrough; `table/csv` are CLI-only renderers.
- `lucius list` does not execute a tool, so the tool output contract does not apply directly.
- It should use the CLI's existing Rich-rendered discovery UI, like `lucius` with no args.

### Existing Static Metadata Path

- `src/cli/data/tool_schemas.json` currently contains static metadata for 56 canonical tool routes.
- `scripts/build_tool_schema.py` generates this file from the canonical route matrix and tool signatures at build time.
- `load_tool_schemas()` already handles source and packaged fallback locations; reuse it.
- `build_command_registry()` already enforces every schema is represented by the route matrix, so `list` should benefit from that existing validation.

### Shell Completion Requirements

- Completion generation is centralized in `deployment/scripts/generate_completions.py`.
- The current top-level completion source is `GLOBAL_TOKENS`; add `list` there or introduce an equivalent local-command token collection used by all shell generators.
- Generated files live under `deployment/shell-completions/`:
  - `lucius.bash`
  - `lucius.zsh`
  - `lucius.fish`
  - `lucius.ps1`
- `deployment/scripts/build_all_cli.sh` already regenerates completions during CLI builds, but this story must still update and commit regenerated completion artifacts so installed scripts expose `list`.
- If adding `list --help` support changes local-command options, reflect that in completions only if the existing completion architecture supports command-specific options cleanly. Minimum required behavior is top-level `lucius <TAB>` includes `list`.

### Relevant Files

- `src/cli/cli_entry.py` - top-level routing, global help/list rendering, CLI errors.
- `src/cli/route_matrix.py` - canonical TestOps entity/action routes; should not receive a fake `list` command.
- `src/cli/data/tool_schemas.json` - static metadata source; normally unchanged for this story.
- `tests/cli/test_cli_basics.py` - best location for process-level CLI behavior tests.
- `tests/cli/subprocess_helpers.py` - existing helpers for subprocess CLI tests.
- `tests/packaging/test_cli_binaries.py` - optional binary discovery smoke coverage if packaging tests are already being touched.
- `deployment/scripts/generate_completions.py` - completion token generator; must include top-level `list`.
- `deployment/shell-completions/lucius.bash` - regenerated bash completion.
- `deployment/shell-completions/lucius.zsh` - regenerated zsh completion.
- `deployment/shell-completions/lucius.fish` - regenerated fish completion.
- `deployment/shell-completions/lucius.ps1` - regenerated PowerShell completion.
- `docs/CLI.md` - command model docs.

### Previous Story Intelligence

- Story 9.3 established the service-first CLI and import boundary: discovery/help commands must not import FastMCP or `src.main`.
- Story 9.6 established output-format rules and added `table|csv` as CLI-only renderers for action results. Do not route `lucius list` through action rendering.
- Story 9.7 is ready-for-dev and may add `auth` as another CLI-local command. Implement `list` in a way that remains compatible with future top-level local commands by keeping local-command branching clear and small.

### Testing Requirements

- Run targeted checks:
  - `uv run --python 3.13 --extra dev pytest tests/cli -q`
  - `uv run ruff check src/cli tests/cli`
  - `uv run mypy src/cli`
  - `uv run --python 3.13 python deployment/scripts/generate_completions.py`
- If packaging code is touched, also run relevant packaging CLI tests; otherwise do not expand scope.

### References

- [Source: specs/project-planning-artifacts/epics.md#Epic 9]
- [Source: specs/prd.md#CLI Interaction Model]
- [Source: specs/architecture.md#CLI Architecture]
- [Source: specs/architecture.md#CLI Output Format Data Flow]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: specs/implementation-artifacts/9-6-unified-cli-output-formats-json-table-csv-plain.md]
- [Source: specs/implementation-artifacts/9-7-cli-auth-command-persistent-configuration.md]
- [Source: src/cli/cli_entry.py]
- [Source: src/cli/route_matrix.py]
- [Source: tests/cli/test_cli_basics.py]
- [Source: scripts/build_tool_schema.py]
- [Source: deployment/scripts/generate_completions.py]
- [Source: deployment/shell-completions/lucius.bash]
- [Source: deployment/shell-completions/lucius.zsh]
- [Source: deployment/shell-completions/lucius.fish]
- [Source: deployment/shell-completions/lucius.ps1]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `uv run --python 3.13 python deployment/scripts/generate_completions.py`
- `uv run --python 3.13 --extra dev pytest tests/cli -q`
- `uv run ruff check src/cli tests/cli`
- `uv run mypy src/cli`

### Completion Notes List

- Added a dedicated CLI-local `list` handler that reuses the same static-schema discovery renderer as bare `lucius` and never enters entity/action execution.
- Added explicit `lucius list --help` output and clean unsupported-option errors for the local command.
- Made auth command loading lazy in `src/cli/cli_entry.py` so `lucius list` does not import auth/client modules that transitively pull `starlette`.
- Extended subprocess and `uv run lucius` tests to verify output parity, help text, legacy `call` rejection, clean errors, and import-boundary enforcement.
- Regenerated bash, zsh, fish, and PowerShell completion scripts so top-level completion includes `list`.

### File List

- deployment/shell-completions/lucius.bash
- deployment/shell-completions/lucius.zsh
- deployment/shell-completions/lucius.fish
- deployment/shell-completions/lucius.ps1
- docs/CLI.md
- src/cli/cli_entry.py
- src/cli/command_runner.py
- src/cli/help_output.py
- src/cli/list_command.py
- src/cli/local_commands.py
- tests/cli/test_cli_auth.py
- tests/cli/test_cli_basics.py
- specs/implementation-artifacts/9-8-cli-list-command-tool-table.md
- specs/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-04-29: Implemented CLI-local `lucius list`, added help/import-boundary regression coverage, updated docs, and regenerated shell completions.
