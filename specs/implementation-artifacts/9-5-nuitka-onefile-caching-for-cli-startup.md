# Story 9.5: Nuitka Onefile Caching for CLI Startup

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Release Engineer,
I want CLI onefile binaries to reuse a persistent extraction cache (variant 2),
so that startup time is dramatically improved for subsequent runs without inflating binary size.

This story is based on measured benchmark findings from 2026-03-20:
- Variant 1 (current onefile): cold `4.644s`, warm avg `3.915s`, size `32,216,032` bytes.
- Variant 2 (onefile + cached tempdir spec + cached mode): cold `3.820s`, warm avg `0.284s`, size `32,232,336` bytes.
- Variant 3 (variant 2 + `--onefile-no-compression`): cold `5.008s`, warm avg `0.150s`, size `159,881,088` bytes.

Decision: adopt Variant 2 as default because it keeps binary size effectively unchanged while cutting warm startup from ~3.9s to ~0.28s.

## Acceptance Criteria

1. **Variant 2 becomes default onefile strategy**
   - **Given** CLI build scripts for supported platforms
   - **When** onefile binaries are built
   - **Then** builds use onefile caching via:
     - `--onefile-tempdir-spec` with a persistent cache path pattern
     - `--onefile-cache-mode=cached`
   - **And** builds do not enable `--onefile-no-compression` by default.

2. **Native cache paths are supported on every currently supported OS target**
   - **Given** the supported platform matrix (Linux/macOS/Windows, x86_64 + arm64)
   - **When** a built onefile binary runs
   - **Then** extraction cache resolves under the OS-native cache root on each OS:
     - Linux: XDG cache location (e.g., `$XDG_CACHE_HOME` or `~/.cache`)
     - macOS: `~/Library/Caches`
     - Windows: `%LOCALAPPDATA%`
   - **And** path construction is stable and version-scoped to avoid collisions across releases.

3. **Version increase invalidates previous cache usage**
   - **Given** a previously cached onefile extraction directory for version `N`
   - **When** a binary with version `N+1` is executed
   - **Then** the `N` cache is not reused by `N+1`
   - **And** extraction occurs into a version-specific cache location for `N+1`
   - **And** behavior is deterministic across Linux, macOS, and Windows.

4. **Measured startup behavior is documented and reproducible**
   - **Given** benchmark instructions in repository docs
   - **When** engineers run the documented commands
   - **Then** they can reproduce cold vs warm measurements per variant
   - **And** docs include the observed tradeoff that variant 3 is faster warm but unacceptably larger.

5. **Warm-start improvement is validated in tests**
   - **Given** packaging/runtime tests
   - **When** onefile cached binary is executed twice with identical environment
   - **Then** second run is materially faster than first run
   - **And** tests verify cache directory creation and reuse semantics for configured tempdir spec.

6. **Backward compatibility and operational safety**
   - **Given** existing CLI behavior and output contracts
   - **When** caching flags are enabled
   - **Then** command outputs, error handling, and tool behavior remain unchanged
   - **And** no HTTP runtime components are introduced by this change.

## Tasks / Subtasks

- [x] **Task 1: Apply variant 2 to build scripts** (AC: 1, 2)
  - [x] 1.1 Update `deployment/scripts/build_cli_unix.sh` to add onefile cached tempdir settings.
  - [x] 1.2 Update `deployment/scripts/build_cli_windows.bat` to add equivalent onefile cached tempdir settings.
  - [x] 1.3 Ensure output naming and existing platform/arch behavior are preserved.
  - [x] 1.4 Keep `--onefile-no-compression` disabled by default.

- [x] **Task 2: Define OS-native cache-path strategy** (AC: 2, 3)
  - [x] 2.1 Use a stable tempdir spec pattern based on Nuitka cache variables (version-scoped).
  - [x] 2.2 Confirm expected path resolution semantics for Linux/macOS/Windows.
  - [x] 2.3 Add guardrails for non-writable cache roots (clear diagnostics and fallback guidance).
  - [x] 2.4 Ensure binary version increase results in cache invalidation by path/version scoping.

- [x] **Task 3: Add benchmark and packaging validation** (AC: 4, 5)
  - [x] 3.1 Add/extend packaging tests to assert cache directory creation and reuse.
  - [x] 3.2 Add a startup regression test/assertion comparing first vs second execution timing envelope.
  - [x] 3.3 Keep tests robust across CI variability (relative assertions, not fragile absolute thresholds).
  - [x] 3.4 Add a test that simulates version bump and verifies previous cache is not reused.

- [x] **Task 4: Document benchmark evidence and decision** (AC: 4)
  - [x] 4.1 Update CLI/build docs with the variant comparison table and selected default rationale.
  - [x] 4.2 Document reproducible benchmark command sequence and environment notes.
  - [x] 4.3 Document OS-specific cache root expectations.
  - [x] 4.4 Document version-bump cache invalidation behavior and operational implications.

- [x] **Task 5: Verify no behavioral regressions** (AC: 6)
  - [x] 5.1 Run CLI smoke and packaging tests on the cached onefile build.
  - [x] 5.2 Verify output format behavior and error messaging parity.
  - [x] 5.3 Verify no additional HTTP runtime imports/components in CLI path.

## Dev Notes

### Context and Decision Record

- The major startup bottleneck is onefile extraction to a fresh temp directory on every run in current config.
- Variant 2 (`onefile` + cached tempdir + cached mode) gives the best practical tradeoff:
  - Large warm-start gain (~14x vs current in measured run)
  - Essentially unchanged artifact size vs current onefile.
- Variant 3 improves warm startup further but increases artifact size from ~31MB to ~152MB, which is not acceptable as default.

### Benchmarks Captured (2026-03-20)

| Variant | Config | Cold Start | Warm Avg | Size |
|---|---|---:|---:|---:|
| v1_current | current onefile | 4.644s | 3.915s | 32,216,032 B |
| v2_cached | onefile + cached mode + persistent tempdir spec | 3.820s | 0.284s | 32,232,336 B |
| v3_cached_nocomp | v2 + no compression | 5.008s | 0.150s | 159,881,088 B |

### Supported Platform Scope

- Linux: arm64, x86_64
- macOS: arm64, x86_64
- Windows: arm64, x86_64

### References

- [Source: specs/implementation-artifacts/9-2-fastmcp-cli-integration.md]
- [Source: specs/implementation-artifacts/9-3-service-first-cli-entity-action.md]
- [Source: specs/implementation-artifacts/9-4-python-3-13-compatibility-for-nuitka-cli-builds.md]
- [Source: deployment/scripts/build_cli_unix.sh]
- [Source: deployment/scripts/build_cli_windows.bat]
- [Source: deployment/scripts/build_all_cli.sh]
- [Source: tests/packaging/test_cli_binaries.py]

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

- `UV_CACHE_DIR=/tmp/uv-cache uv run --python 3.13 --extra dev pytest tests/packaging/test_cli_binaries.py::TestBinaryBuildScriptConfiguration tests/packaging/test_cli_binaries.py::TestBinaryStartupCacheBehavior -q` -> `4 passed`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --python 3.13 --extra dev pytest tests/cli/test_cli_basics.py tests/packaging/test_cli_binaries.py::TestBinaryNoHTTPComponents::test_cli_source_has_no_http_imports -q` -> `12 passed`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --python 3.13 --extra dev ruff check tests/packaging/test_cli_binaries.py` -> `All checks passed`
- `uv run --python 3.13 --extra dev pytest tests/packaging/test_cli_binaries.py::TestBinaryBuildScriptConfiguration -q` -> `4 passed`
- `uv run --python 3.13 --extra dev pytest tests/packaging/test_cli_binaries.py::TestBinaryStartupCacheBehavior -q` -> `1 passed`

### Completion Notes List

- Implemented Variant 2 onefile caching defaults in Unix and Windows build scripts:
  - `--onefile-tempdir-spec={CACHE_DIR}/{COMPANY}/{PRODUCT}/{VERSION}`
  - `--onefile-cache-mode=cached`
- Kept `--onefile-no-compression` disabled by default to avoid artifact-size explosion.
- Added packaging tests that enforce cache-mode flag presence, version-scoped tempdir spec, and no default no-compression.
- Added optional runtime startup cache behavior test that validates second start is faster and cache files are created.
- Added deterministic version-bump cache-path simulation coverage to verify `N` and `N+1` resolve to distinct cache paths from the shared onefile template.
- Added benchmark reproduction build switches in Unix/Windows scripts:
  - `--onefile-cache-mode cached|off`
  - `--onefile-no-compression`
- Updated CLI/README docs with onefile cache behavior, native cache roots, version-scoped invalidation semantics, and non-writable cache-root guidance.
- Added reproducible benchmark command sequence and variant comparison guidance to docs.
- Verified no-HTTP CLI import boundary and CLI basics remain green.

### File List

- deployment/scripts/build_cli_unix.sh
- deployment/scripts/build_cli_windows.bat
- tests/packaging/test_cli_binaries.py
- docs/CLI.md
- README.md
- specs/implementation-artifacts/9-5-nuitka-onefile-caching-for-cli-startup.md
- specs/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-03-20: Implemented Story 9.5 (Variant 2 default onefile caching), added version-scoped cache invalidation guardrails, updated docs, and added packaging/runtime validation tests.
- 2026-03-20: Addressed review follow-ups by adding version-bump cache-path simulation tests, reproducible benchmark workflow commands, and explicit non-writable cache-root diagnostics/fallback guidance.
