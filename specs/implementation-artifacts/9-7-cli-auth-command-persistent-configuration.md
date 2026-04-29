# Story 9.7: CLI Auth Command with Persistent Configuration

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer or QA Engineer,
I want `lucius auth` to prompt for my Allure TestOps URL, API token, and default project,
so that subsequent CLI launches can reuse those credentials without requiring environment variables every time.

## Acceptance Criteria

1. **Interactive auth setup**
   - **Given** I run `lucius auth`
   - **When** no non-interactive values are supplied
   - **Then** the CLI prompts for Allure TestOps base URL, API token, and project ID
   - **And** token input is masked and never echoed to stdout/stderr
   - **And** project ID is validated as a positive integer.

2. **Non-interactive auth setup for automation and tests**
   - **Given** I run `lucius auth --url <url> --token <token> --project <id>`
   - **When** all values are supplied
   - **Then** the command validates and saves the values without prompting
   - **And** partial non-interactive input prompts only for missing values.

3. **Credential validation before persistence**
   - **Given** URL, token, and project ID are entered
   - **When** the command validates the credentials
   - **Then** it performs real authentication through existing Allure client token exchange
   - **And** it verifies the configured project is accessible to that token
   - **And** invalid URL, token, project, network, and permission failures return clean `CLIError` messages without tracebacks.

4. **Cross-platform config location**
   - **Given** auth succeeds
   - **When** credentials are saved
   - **Then** the file is stored at `platformdirs.user_config_path("lucius", appauthor=False, ensure_exists=True) / "auth.json"`
   - **And** this resolves to native user config locations:
     - Linux/Unix: `$XDG_CONFIG_HOME/lucius/auth.json` or `~/.config/lucius/auth.json`
     - macOS: `~/Library/Application Support/lucius/auth.json` unless XDG overrides are explicitly set
     - Windows: `%LOCALAPPDATA%\lucius\auth.json` under normal shell-folder resolution
   - **And** no repo-local, current-working-directory, or `~/.lucius` config file is used.

5. **Secure file write behavior**
   - **Given** the config file is written
   - **When** the platform supports POSIX permissions
   - **Then** the file is owner read/write only (`0600`) and the directory is owner-only where practical
   - **And** writes are atomic enough to avoid corrupting an existing valid config on failure
   - **And** logs, exceptions, and success output do not include the raw token.

6. **Reuse on later CLI launches**
   - **Given** a valid auth config exists
   - **When** I run any TestOps command such as `lucius test_case list --args '{}'`
   - **Then** the CLI uses stored `ALLURE_ENDPOINT`, `ALLURE_API_TOKEN`, and `ALLURE_PROJECT_ID` if those environment variables are absent
   - **And** explicit tool arguments such as `api_token` or `project_id` still override the default auth context
   - **And** real environment variables override saved config values.

7. **Auth status and replacement behavior**
   - **Given** I run `lucius auth status`
   - **Then** the CLI reports whether auth config exists and shows URL/project only, never token
   - **And** running `lucius auth` again replaces saved URL/token/project only after validation succeeds.

8. **Help, docs, and tests**
   - **Given** this story is implemented
   - **Then** `lucius --help` and `lucius auth --help` document the command
   - **And** `docs/CLI.md`, `docs/setup.md`, and README CLI auth sections are updated
   - **And** shell completion generation includes `auth` as a top-level command plus `status`, `--help`, `--url`, `--token`, and `--project` where appropriate
   - **And** regenerated completion files under `deployment/shell-completions/` reflect the new auth command for bash, zsh, fish, and PowerShell
   - **And** unit/process tests cover Linux, macOS, and Windows path resolution via monkeypatched `platformdirs`
   - **And** tests verify masked input, permission behavior where supported, config fallback precedence, validation failures, no tracebacks, token redaction, and completion coverage.
   - **And** source-invoked CLI E2E tests cover `lucius auth` and `lucius auth status` via `uv run lucius ...`, without depending on a built binary.

## Tasks / Subtasks

- [x] **Task 1: Add CLI-local auth command routing** (AC: 1, 2, 7, 8)
  - [x] 1.1 Handle top-level `lucius auth` in `src/cli/cli_entry.py` before entity resolution and route-matrix validation.
  - [x] 1.2 Support `lucius auth`, `lucius auth --help`, `lucius auth status`, and non-interactive `--url`, `--token`, `--project`.
  - [x] 1.3 Keep `auth` out of `CANONICAL_ROUTE_MATRIX` and `src/cli/data/tool_schemas.json`; it is CLI-local setup, not a TestOps tool route.

- [x] **Task 2: Implement persistent auth config helpers** (AC: 4, 5, 6)
  - [x] 2.1 Add a small CLI config module such as `src/cli/auth_config.py`.
  - [x] 2.2 Add direct dependency `platformdirs` in `pyproject.toml` using `uv add platformdirs`; do not rely on transitive lockfile entries.
  - [x] 2.3 Store JSON with fields `allure_endpoint`, `allure_api_token`, `allure_project_id`, `created_at`, and `updated_at`.
  - [x] 2.4 Use `pathlib.Path`, UTF-8 JSON, atomic temp-file replace, and POSIX `0600` permissions where `os.chmod` semantics are available.
  - [x] 2.5 Add config parse validation with clear repair hints for malformed JSON, missing fields, or invalid project ID.

- [x] **Task 3: Validate credentials through existing client behavior** (AC: 3)
  - [x] 3.1 Add a validation helper that constructs `AllureClient(base_url=url, token=SecretStr(token), project=project_id)`.
  - [x] 3.2 Trigger token exchange through `async with AllureClient(...)` so invalid tokens fail before saving.
  - [x] 3.3 Verify project access with an existing generated Project API path or a minimal `AllureClient` helper wrapping `ProjectControllerApi.calculate_stats(id=project_id)`.
  - [x] 3.4 Map auth, network, permission, and validation exceptions to `CLIError` with actionable hints and no traceback.

- [x] **Task 4: Apply saved config before tool import** (AC: 6)
  - [x] 4.1 In action execution, load saved auth config before `_load_tool_function()` imports `src.tools`.
  - [x] 4.2 Inject only missing `ALLURE_ENDPOINT`, `ALLURE_API_TOKEN`, and `ALLURE_PROJECT_ID` into `os.environ` so explicit environment variables win.
  - [x] 4.3 Preserve existing runtime override behavior in `src/utils/auth.py`; do not store state in module globals.
  - [x] 4.4 Keep help/version/entity-discovery paths fast and avoid importing `src.tools`, `src.main`, or `fastmcp`.

- [x] **Task 5: Update user-facing documentation** (AC: 8)
  - [x] 5.1 Document `lucius auth`, `lucius auth status`, and non-interactive usage in `docs/CLI.md`.
  - [x] 5.2 Update setup docs and README so users can choose either environment variables or saved CLI auth.
  - [x] 5.3 Document exact native config path behavior and the precedence order: explicit tool args > environment variables > saved auth config > defaults.
  - [x] 5.4 Document that completion scripts must be regenerated after auth command changes.

- [x] **Task 6: Add focused tests** (AC: 1-8)
  - [x] 6.1 Unit-test config path resolution and JSON read/write behavior with monkeypatched `platformdirs.user_config_path`.
  - [x] 6.2 Unit-test redaction, malformed config handling, POSIX permission calls, and atomic write failure handling.
  - [x] 6.3 Process-test `lucius auth --url ... --token ... --project ...` with mocked validation and a temporary config root.
  - [x] 6.4 Process-test `lucius auth status` never displays the token.
  - [x] 6.5 Test config fallback by running an action command without auth env vars and asserting the tool receives env-derived auth.
  - [x] 6.6 Test env vars override saved config and existing `api_token` / `project_id` args override default context.
  - [x] 6.7 Add CLI import-boundary tests proving help/version/status paths do not import `fastmcp` or `src.main`.
  - [x] 6.8 Add completion-generation tests asserting `auth`, `status`, `--url`, `--token`, and `--project` appear in generated bash, zsh, fish, and PowerShell scripts.
  - [x] 6.9 Extend the shared `uv run lucius` CLI E2E suite with process tests for `lucius auth`, `lucius auth status`, non-interactive setup, and saved-config fallback behavior.

- [x] **Task 7: Update shell completions** (AC: 8)
  - [x] 7.1 Update `deployment/scripts/generate_completions.py` to include CLI-local top-level commands separately from entity/action route data.
  - [x] 7.2 Keep `auth` out of `CANONICAL_ROUTE_MATRIX` while still completing it as a top-level command.
  - [x] 7.3 Complete `lucius auth status` and auth-specific options `--url`, `--token`, `--project`, `--help`, and `-h`.
  - [x] 7.4 Regenerate `deployment/shell-completions/lucius.bash`, `lucius.zsh`, `lucius.fish`, and `lucius.ps1`.

## Dev Notes

### Current CLI Structure

- The active CLI entry point is `src/cli/cli_entry.py`; there is no `src/cli/main.py`.
- CLI routes are in `src/cli/route_matrix.py`, but `auth` must not be added there because it is not an Allure TestOps entity/action backed by an MCP tool.
- The executable is configured as `lucius = "src.cli.cli_entry:main"` in `pyproject.toml`.
- Current CLI action execution lazy-loads tool callables through `src/cli/tool_resolver.py`. Apply saved auth config before that import path loads `src.tools`, because tool imports eventually reach `src.utils.config.settings`.
- Shell completion generation currently reads only `CANONICAL_ROUTE_MATRIX` through `deployment/scripts/generate_completions.py`; this story must add a separate completion data path for CLI-local commands so `auth` is not missed.

### Config Location Decision

- Use `platformdirs.user_config_path("lucius", appauthor=False, ensure_exists=True) / "auth.json"`.
- This is config, not cache or data: credentials and default project are user preferences required for later launches and must not be placed under the Nuitka extraction cache.
- Use `appauthor=False` to avoid duplicated Windows paths such as `AppData\Local\lucius\lucius`.
- Keep `roaming=False` (platformdirs default) so Windows stores secrets under Local AppData rather than roaming the token across domain profiles.
- Let `platformdirs` honor user-provided XDG overrides on Unix/macOS and native shell-folder resolution on Windows; do not hard-code these paths manually.
- Do not use `~/.lucius`, repo-local `.lucius`, `tempfile`, or the current working directory; those are less native and easier to leak into projects.

### Auth Resolution Order

1. Runtime tool args (`api_token`, `project_id`) remain highest priority through existing tool/auth behavior.
2. Real environment variables (`ALLURE_ENDPOINT`, `ALLURE_API_TOKEN`, `ALLURE_PROJECT_ID`) override saved config.
3. Saved CLI auth config fills missing environment variables for CLI-launched tool execution.
4. Existing settings defaults are last resort.

### Security Guardrails

- Never print or log the token. Output may show URL and project ID only.
- Use `SecretStr` when passing token into `AllureClient`.
- Do not write config until validation succeeds.
- If validation succeeds but the file write fails, return a clear error and leave any previous config intact.
- On Windows, avoid pretending `chmod(0o600)` enforces ACLs. The security boundary is the per-user Local AppData directory; tests should assert graceful behavior rather than POSIX permission parity.

### Project Structure Notes

- Likely files to change:
  - `src/cli/cli_entry.py`
  - `src/cli/auth_config.py` (new)
  - `tests/cli/test_cli_auth.py` (new)
  - `tests/cli/test_cli_basics.py`
  - `docs/CLI.md`
  - `docs/setup.md`
  - `README.md`
  - `deployment/scripts/generate_completions.py`
  - `deployment/shell-completions/lucius.bash`
  - `deployment/shell-completions/lucius.zsh`
  - `deployment/shell-completions/lucius.fish`
  - `deployment/shell-completions/lucius.ps1`
  - `pyproject.toml` and `uv.lock` after `uv add platformdirs`
- Avoid editing generated client files under `src/client/generated/`.
- If adding an `AllureClient` helper for project validation, place it in `src/client/client.py` and cover it with unit tests or mock-based CLI tests.

### Previous Story Intelligence

- Story 9.3 established the service-first CLI and import boundary: help/list paths must not import FastMCP or `src.main`.
- Story 9.6 established CLI output behavior: action calls default to tool `json`, `plain/json` are passthrough, and `table/csv` are CLI-only renderers. Auth command output can be simple human-facing text, but it must still avoid tracebacks and internal logs.
- Existing draft auth story files in this workspace mention stale paths and `~/.lucius/config.yaml`; do not copy those locations or command architecture.

### Testing Requirements

- Run targeted checks:
  - `uv run --python 3.13 --extra dev pytest tests/cli -q`
  - `uv run ruff check src/cli tests/cli`
  - `uv run mypy src/cli`
- Also run `python3 deployment/scripts/generate_completions.py` after implementation and verify the generated completion files are committed.
- Add focused tests instead of broad E2E network tests. Mock validation for process tests; keep one optional/live validation path only if existing E2E conventions already support it.

### References

- [Source: specs/project-planning-artifacts/epics.md#Epic 9]
- [Source: specs/prd.md#CLI Interaction Model]
- [Source: specs/prd.md#Authentication Model]
- [Source: specs/architecture.md#CLI Architecture]
- [Source: specs/architecture.md#CLI Output Format Data Flow]
- [Source: docs/CLI.md#Command Model]
- [Source: src/cli/cli_entry.py]
- [Source: src/cli/route_matrix.py]
- [Source: src/utils/config.py]
- [Source: src/utils/auth.py]
- [Source: src/client/client.py]
- [External: platformdirs user config directories](https://platformdirs.readthedocs.io/en/latest/explanation.html)
- [External: platformdirs parameter reference](https://platformdirs.readthedocs.io/en/latest/parameters.html)

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

- `uv add platformdirs`
- `python3 deployment/scripts/generate_completions.py`
- `uv run --python 3.13 --extra dev pytest tests/cli -q`
- `uv run ruff check src/cli tests/cli`
- `uv run mypy src/cli`
- `uv run --python 3.13 --extra dev pytest -q`

### Completion Notes List

- Added CLI-local `lucius auth` / `lucius auth status` handling ahead of entity routing, including dedicated help output and auth-specific completion tokens.
- Added persistent auth config helpers using `platformdirs.user_config_path(...)/auth.json`, UTF-8 JSON, atomic temp-file replacement, and POSIX permission hardening where supported.
- Added live credential validation through `AllureClient` token exchange plus `ProjectControllerApi.calculate_stats()` access checks before config persistence.
- Injected saved auth into missing `ALLURE_ENDPOINT`, `ALLURE_API_TOKEN`, and `ALLURE_PROJECT_ID` values before tool resolution so existing env vars and runtime tool args still win.
- Expanded CLI tests with unit, subprocess, and `uv run lucius` coverage for config persistence, redaction, precedence, import boundaries, and completion generation.
- Updated README, CLI docs, setup docs, and regenerated bash/zsh/fish/PowerShell completions.
- Fixed two existing CLI/telemetry test-isolation issues uncovered by full-suite regression runs:
  - restored logging disable state after `src.cli.cli_entry.main()`
  - restored `src.main` module references in import-boundary tests and re-bound telemetry singleton in `tests/unit/test_main.py`
- Validation results:
  - `uv run --python 3.13 --extra dev pytest tests/cli -q` -> 156 passed
  - `uv run ruff check src/cli tests/cli` -> passed
  - `uv run mypy src/cli` -> passed
  - `python3 deployment/scripts/generate_completions.py` -> regenerated bash/zsh/fish/PowerShell completion files
  - `uv run --python 3.13 --extra dev pytest -q` -> 701 passed, 100 skipped

### File List

- README.md
- deployment/scripts/generate_completions.py
- deployment/shell-completions/lucius.bash
- deployment/shell-completions/lucius.fish
- deployment/shell-completions/lucius.ps1
- deployment/shell-completions/lucius.zsh
- docs/CLI.md
- docs/setup.md
- pyproject.toml
- specs/implementation-artifacts/9-7-cli-auth-command-persistent-configuration.md
- specs/implementation-artifacts/sprint-status.yaml
- src/cli/auth_command.py
- src/cli/auth_config.py
- src/cli/cli_entry.py
- src/cli/help_output.py
- src/cli/local_commands.py
- src/cli/runtime.py
- src/client/client.py
- tests/cli/subprocess_helpers.py
- tests/cli/test_cli_auth.py
- tests/cli/test_cli_basics.py
- tests/cli/test_e2e_mocked.py
- tests/unit/test_main.py
- uv.lock

### Change Log

- 2026-04-29: Implemented CLI-local persistent auth command, config fallback injection, docs/completion updates, and focused CLI regression coverage.
