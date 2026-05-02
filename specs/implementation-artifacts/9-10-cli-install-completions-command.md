# Story 9.10: CLI Install Completions Command

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer or QA Engineer,
I want `lucius install-completions` to detect my shell and install the matching completion script from the binary,
so that standalone CLI users can enable tab completion without locating repository files or manually copying generated scripts.

## Acceptance Criteria

1. **Install command detects shell and installs completions**
   - **Given** I run `lucius install-completions`
   - **When** the shell can be detected from an explicit `--shell` option or current process environment
   - **Then** the CLI installs the matching completion script for `bash`, `zsh`, `fish`, or `powershell`
   - **And** it prints the installed path plus any shell-specific reload/source instruction
   - **And** it exits with code `0` on success.

2. **Explicit shell override is supported**
   - **Given** I run `lucius install-completions --shell bash|zsh|fish|powershell`
   - **When** the command executes
   - **Then** the explicit shell value overrides auto-detection
   - **And** shell aliases such as `pwsh`, `powershell.exe`, and path-like shell values are normalized
   - **And** unsupported shells fail with a clean `CLIError` and a hint listing supported shells.

3. **Completion content is embedded in the binary**
   - **Given** the CLI is running as an installed wheel, Nuitka standalone build, or Nuitka onefile binary
   - **When** `install-completions` installs completion scripts
   - **Then** completion content comes from modules/data included in the binary
   - **And** runtime installation does not read `deployment/shell-completions/*`, `deployment/scripts/generate_completions.py`, the source checkout, or network resources
   - **And** a packaged binary still installs completions when the repository completion files are absent.

4. **The command is reflected in completions**
   - **Given** completion scripts are generated or installed
   - **When** users request top-level completion for `lucius`
   - **Then** `install-completions` is offered alongside existing top-level commands and entity tokens in bash, zsh, fish, and PowerShell
   - **And** `install-completions` exposes `--shell`, `--path`, `--force`, `--print`, `--help`, and `-h` where command-specific option completion is supported
   - **And** generated completion artifacts under `deployment/shell-completions/` are regenerated from the same code path used by the install command.

5. **Install paths and overwrites are safe**
   - **Given** no custom `--path` is provided
   - **When** completions are installed
   - **Then** default user-level targets are used:
     - bash: `${XDG_DATA_HOME:-~/.local/share}/bash-completion/completions/lucius`
     - zsh: `${XDG_DATA_HOME:-~/.local/share}/zsh/site-functions/_lucius`
     - fish: `${XDG_CONFIG_HOME:-~/.config}/fish/completions/lucius.fish`
     - PowerShell: a per-user Lucius completion script plus a profile hook appropriate for Windows PowerShell or PowerShell Core
   - **And** parent directories are created with user-only permissions where POSIX semantics apply
   - **And** existing completion files are not overwritten unless `--force` is supplied
   - **And** any shell startup-file/profile changes are idempotent, marker-delimited, and never duplicate prior Lucius blocks.

6. **Print-only and custom path modes are available for automation**
   - **Given** I run `lucius install-completions --print --shell <shell>`
   - **When** the command executes
   - **Then** it writes only the selected completion script to stdout
   - **And** it does not modify the filesystem.
   - **Given** I run `lucius install-completions --path <file> --shell <shell>`
   - **When** the command executes
   - **Then** it writes the selected script to that file using safe overwrite behavior
   - **And** it still reports the file path and activation guidance.

7. **Help, docs, and automated coverage are updated**
   - **Given** this story is implemented
   - **Then** `lucius --help`, `lucius install-completions --help`, `docs/CLI.md`, setup docs, and README CLI sections describe the command
   - **And** tests cover shell detection, explicit overrides, unsupported-shell errors, per-shell target paths, `--print`, `--path`, `--force`, idempotent startup hooks, embedded-content behavior without repository completion files, top-level completion exposure, command-specific option completion where supported, and no traceback/internal logs.
   - **And** source-invoked CLI E2E tests cover `install-completions` command flows via `uv run lucius ...`, without requiring a built binary.

## Tasks / Subtasks

- [ ] **Task 1: Add CLI-local `install-completions` routing** (AC: 1, 2, 4, 7)
  - [ ] 1.1 Handle `argv[0] == "install-completions"` in `src/cli/cli_entry.py` before entity resolution.
  - [ ] 1.2 Support `lucius install-completions`, `lucius install-completions --help`, and aliases only if deliberately documented; do not add this command to `CANONICAL_ROUTE_MATRIX`.
  - [ ] 1.3 Keep `call` rejected as legacy command style and keep entity/action behavior unchanged.
  - [ ] 1.4 Add root help usage for `lucius install-completions [--shell <shell>] [--path <file>] [--force] [--print]`.

- [ ] **Task 2: Centralize completion generation in importable CLI code** (AC: 3, 4)
  - [ ] 2.1 Move reusable generation logic out of `deployment/scripts/generate_completions.py` into a runtime-safe module such as `src/cli/completions.py`.
  - [ ] 2.2 Keep generation data derived from `src/cli/route_matrix.py` plus a CLI-local command registry, not from repository completion files.
  - [ ] 2.3 Include local top-level commands in one place, at minimum `help`, `version`, `list` if implemented, `auth` if implemented, and `install-completions`.
  - [ ] 2.4 Keep action options synchronized with current CLI behavior, including `--format json|table|plain|csv` and `--pretty` after Story 9.9 is implemented.
  - [ ] 2.5 Update `deployment/scripts/generate_completions.py` to become a thin file-writer around the shared `src/cli/completions.py` API.

- [ ] **Task 3: Implement embedded completion installation helpers** (AC: 1, 3, 5, 6)
  - [ ] 3.1 Add a focused module such as `src/cli/completion_installer.py` for shell detection, path resolution, safe writes, and profile-hook updates.
  - [ ] 3.2 Generate or retrieve completion text from embedded code in `src/cli/completions.py`; do not read `deployment/shell-completions/` at runtime.
  - [ ] 3.3 Use `pathlib.Path`, UTF-8 writes, temp-file replace, and POSIX `0600` file permissions where supported.
  - [ ] 3.4 Use guarded overwrite behavior: fail with a clean message if target exists and `--force` is not supplied.
  - [ ] 3.5 Add marker-delimited shell startup/profile hook helpers only where needed; hooks must be idempotent.

- [ ] **Task 4: Implement shell detection and option parsing** (AC: 1, 2, 6)
  - [ ] 4.1 Parse `--shell`, `--path`, `--force`, `--print`, `--help`, and `-h` with explicit unknown-option errors.
  - [ ] 4.2 Detection order: explicit `--shell`; then environment hints such as `$SHELL`, PowerShell-specific environment variables, and platform defaults; then clean failure with a `--shell` hint.
  - [ ] 4.3 Normalize path-like shell values by basename and extension stripping, e.g. `/bin/zsh` -> `zsh`, `powershell.exe` -> `powershell`.
  - [ ] 4.4 Keep the command fast and offline; it must not import `src.tools`, `src.main`, FastMCP, Starlette, uvicorn, or generated API clients.

- [ ] **Task 5: Update generated completion scripts and build packaging** (AC: 3, 4)
  - [ ] 5.1 Regenerate `deployment/shell-completions/lucius.bash`, `lucius.zsh`, `lucius.fish`, and `lucius.ps1`.
  - [ ] 5.2 Ensure generated top-level completion includes `install-completions`.
  - [ ] 5.3 Ensure command-specific options include `--shell`, `--path`, `--force`, `--print`, `--help`, and `-h` where the generator supports local-command option completion.
  - [ ] 5.4 Verify Nuitka build scripts do not need external completion data files for runtime installation; if any data file approach is used, update both Unix and Windows build scripts and add packaging tests proving the files are bundled.

- [ ] **Task 6: Update documentation** (AC: 1, 5, 6, 7)
  - [ ] 6.1 Update `docs/CLI.md` with `lucius install-completions` usage, supported shells, default paths, `--shell`, `--path`, `--force`, and `--print`.
  - [ ] 6.2 Update setup docs and README CLI sections to prefer the install command over manually sourcing repository files.
  - [ ] 6.3 Document shell-specific post-install behavior, including when users must restart their shell or source a profile.

- [ ] **Task 7: Add focused tests** (AC: 1-7)
  - [ ] 7.1 Add unit tests for shell normalization and detection with monkeypatched environment and platform values.
  - [ ] 7.2 Add unit tests for default per-shell paths and custom `--path`.
  - [ ] 7.3 Add tests proving `--print` writes completion text to stdout and does not write files.
  - [ ] 7.4 Add tests for existing-file behavior with and without `--force`.
  - [ ] 7.5 Add tests for idempotent marker-delimited startup/profile hooks.
  - [ ] 7.6 Add import-boundary tests proving `install-completions --help`, `--print`, and install path resolution do not import MCP/runtime/server modules.
  - [ ] 7.7 Add completion-generation tests asserting `install-completions` and its options appear in bash, zsh, fish, and PowerShell scripts.
  - [ ] 7.8 Add a packaging/binary-facing test or source-level simulation proving runtime installation does not depend on `deployment/shell-completions/` files.
  - [ ] 7.9 Extend the shared `uv run lucius` CLI E2E suite with process tests for `install-completions --help`, `--print`, explicit `--shell`, and unsupported-shell failure paths.

## Dev Notes

### Current CLI Structure

- Active CLI entry point: `src/cli/cli_entry.py`.
- The executable is configured as `lucius = "src.cli.cli_entry:main"` in `pyproject.toml`.
- Current route grammar is entity/action (`lucius <entity> <action>`), and local commands must be handled before entity resolution.
- `install-completions` is CLI-local setup. It must not be added to `src/cli/route_matrix.py`, `CANONICAL_ROUTE_MATRIX`, or `src/cli/data/tool_schemas.json` as a fake TestOps route.
- Current completion generation lives in `deployment/scripts/generate_completions.py` and writes:
  - `deployment/shell-completions/lucius.bash`
  - `deployment/shell-completions/lucius.zsh`
  - `deployment/shell-completions/lucius.fish`
  - `deployment/shell-completions/lucius.ps1`

### Embedded Completion Requirement

- The command must work from a standalone binary without the repository checkout.
- Preferred implementation: put completion generation and local-command metadata in importable runtime code under `src/cli/`, then make `deployment/scripts/generate_completions.py` call that module to write repository artifacts.
- Avoid runtime file reads from `deployment/shell-completions/`; those files are release artifacts, not the runtime source of truth.
- If implementation chooses static script strings instead of runtime generation, those strings must live under `src/cli/` so Nuitka embeds them automatically.

### Shell Detection and Installation Guidance

- Detection should be deterministic and testable:
  - explicit `--shell` has highest priority
  - `$SHELL` basename handles common Unix shells
  - PowerShell detection should handle `pwsh`, `powershell`, and `powershell.exe`
  - ambiguous or unsupported shells should fail with a hint: `Use --shell bash|zsh|fish|powershell`
- Default paths should be user-level and should not require elevated privileges.
- Do not modify system directories such as `/etc/bash_completion.d`, `/usr/share/zsh/site-functions`, or Program Files.
- Do not silently append unbounded shell code to rc/profile files. Use a small marker-delimited block and idempotent updates.
- `--print` is important for CI, package managers, and users who manage dotfiles manually.

### Completion Metadata Guardrails

- Keep top-level local commands distinct from TestOps entities.
- Completion output must include `install-completions` at the top level.
- Existing local commands from adjacent stories must not regress:
  - Story 9.7 may add `auth`
  - Story 9.8 may add `list`
  - Story 9.9 may add `--pretty`
- If those stories are not implemented yet when this story is developed, structure the local-command metadata so they can be added without duplicating shell-specific generator code.

### Project Structure Notes

- Primary implementation targets:
  - `src/cli/cli_entry.py`
  - `src/cli/completions.py` or equivalent new runtime-safe completion module
  - `src/cli/completion_installer.py` or equivalent install helper
  - `deployment/scripts/generate_completions.py`
  - `deployment/shell-completions/lucius.bash`
  - `deployment/shell-completions/lucius.zsh`
  - `deployment/shell-completions/lucius.fish`
  - `deployment/shell-completions/lucius.ps1`
  - `docs/CLI.md`
  - `docs/setup.md`
  - `README.md`
  - `tests/cli/test_cli_basics.py`
  - `tests/cli/test_e2e_mocked.py`
  - `tests/cli/test_cli_coverage_helpers.py`
  - `tests/packaging/test_cli_binaries.py` if binary embedding/build behavior is touched
- Do not change service or tool behavior for this story.
- Do not change tool output contracts from Story 9.6.

### Previous Story Intelligence

- Story 9.6 established CLI output format/data-flow contracts. This story is setup/local CLI behavior and must not route through tool execution or output renderers.
- Story 9.7 defines `auth` as a CLI-local command. The same separation rule applies: local command, not route matrix.
- Story 9.8 defines `list` as a CLI-local discovery command and completion token. Preserve that pattern if already implemented.
- Story 9.9 adds `--pretty` to action options and completions. If present, the shared completion metadata must retain it.

### Testing Requirements

- Run targeted checks after implementation:
  - `uv run --python 3.13 --extra dev pytest tests/cli -q`
  - `uv run --python 3.13 --extra dev pytest tests/packaging/test_cli_binaries.py -q` if build script or binary embedding behavior changes
  - `uv run ruff check src/cli deployment/scripts tests/cli`
  - `uv run mypy src/cli`
  - `uv run --python 3.13 python deployment/scripts/generate_completions.py`
- If implementation changes CLI build scripts, run or document the relevant packaging checks.

### References

- [Source: specs/project-planning-artifacts/epics.md#Epic 9]
- [Source: specs/prd.md#CLI Interaction Model]
- [Source: specs/prd.md#CLI Functional Requirements]
- [Source: specs/architecture.md#CLI Architecture (Service-First Course Correction)]
- [Source: specs/architecture.md#Project Structure & Boundaries]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: src/cli/cli_entry.py]
- [Source: src/cli/route_matrix.py]
- [Source: deployment/scripts/generate_completions.py]
- [Source: deployment/scripts/build_cli_unix.sh]
- [Source: deployment/scripts/build_cli_windows.bat]
- [Source: deployment/shell-completions/lucius.bash]
- [Source: deployment/shell-completions/lucius.zsh]
- [Source: deployment/shell-completions/lucius.fish]
- [Source: deployment/shell-completions/lucius.ps1]
- [Source: docs/CLI.md#Shell Completions]
- [Source: specs/implementation-artifacts/9-6-unified-cli-output-formats-json-table-csv-plain.md]
- [Source: specs/implementation-artifacts/9-7-cli-auth-command-persistent-configuration.md]
- [Source: specs/implementation-artifacts/9-8-cli-list-command-tool-table.md]
- [Source: specs/implementation-artifacts/9-9-cli-pretty-json-output-flag.md]

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

Ultimate context engine analysis completed - comprehensive developer guide created.

### File List
