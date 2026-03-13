# Story 9.4: Python 3.13 Compatibility for Nuitka CLI Builds

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Release Engineer,
I want lucius-mcp to be compatible with Python 3.13 for CLI builds,
so that Nuitka-based binaries can be built reliably without breaking existing functionality.

## Acceptance Criteria

1. **Packaging metadata updated for Python 3.13 compatibility**
   - **Given** `pyproject.toml`
   - **When** Python compatibility metadata is updated
   - **Then** `requires-python` allows Python 3.13
   - **And** classifiers include Python 3.13 compatibility tag
   - **And** existing Python 3.14 compatibility remains declared.

2. **Static analysis/tooling config aligned to 3.13 baseline**
   - **Given** repository lint/type-check settings
   - **When** compatibility baseline is adjusted
   - **Then** Ruff target version and mypy `python_version` are compatible with Python 3.13.

3. **Codebase runs on Python 3.13 without behavior regressions**
   - **Given** application, CLI, and tests
   - **When** executed on Python 3.13
   - **Then** no Python 3.14-only syntax/runtime assumptions remain
   - **And** test suites selected for release confidence pass.

4. **CLI build scripts enforce Python 3.13 for Nuitka flow**
   - **Given** local build scripts in `deployment/scripts/`
   - **When** building CLI binaries
   - **Then** schema generation and Nuitka build steps run under Python 3.13
   - **And** scripts fail fast with an actionable message if Python 3.13 is unavailable.

5. **CLI build CI pipeline stays pinned to Python 3.13**
   - **Given** `.github/workflows/cli-build.yml`
   - **When** CLI build/test/release jobs execute
   - **Then** they use Python 3.13 consistently for CLI build-related jobs
   - **And** pipeline still produces expected CLI artifacts.

6. **Documentation reflects new compatibility contract**
   - **Given** setup and architecture docs
   - **When** Python version requirements are documented
   - **Then** docs clearly state Python 3.13 compatibility and CLI Nuitka rationale
   - **And** outdated Python 3.14-only statements are corrected where applicable.

## Tasks / Subtasks

- [ ] **Task 1: Update Python compatibility metadata** (AC: 1, 2)
  - [ ] 1.1 Update `pyproject.toml` `requires-python` from `>=3.14` to `>=3.13`.
  - [ ] 1.2 Add/update classifiers to include `Programming Language :: Python :: 3.13` (retain `3.14`).
  - [ ] 1.3 Update Ruff `target-version` to `py313`.
  - [ ] 1.4 Update mypy `python_version` to `3.13`.

- [ ] **Task 2: Resolve Python 3.13 code compatibility gaps** (AC: 3)
  - [ ] 2.1 Audit source/scripts/tests for 3.14-only features and adjust code where needed.
  - [ ] 2.2 Keep behavior parity for CLI and server paths after compatibility changes.
  - [ ] 2.3 Add or update tests that specifically guard against version-regression edge cases.

- [ ] **Task 3: Enforce Python 3.13 in CLI build scripts** (AC: 4)
  - [ ] 3.1 Update `deployment/scripts/build_cli_linux_arm64.sh`.
  - [ ] 3.2 Update `deployment/scripts/build_cli_linux_x86_64.sh`.
  - [ ] 3.3 Update `deployment/scripts/build_cli_macos_arm64.sh`.
  - [ ] 3.4 Update `deployment/scripts/build_cli_macos_x86_64.sh`.
  - [ ] 3.5 Update `deployment/scripts/build_cli_windows_arm64.bat`.
  - [ ] 3.6 Update `deployment/scripts/build_cli_windows_x86_64.bat`.
  - [ ] 3.7 Update `deployment/scripts/build_all_cli.sh` to validate and communicate the 3.13 requirement.

- [ ] **Task 4: Validate CLI pipeline/build wiring** (AC: 5)
  - [ ] 4.1 Verify `cli-build.yml` uses Python 3.13 for all CLI build/test/release jobs.
  - [ ] 4.2 Ensure any CLI build helper action inputs default safely to 3.13 in this workflow.
  - [ ] 4.3 Confirm artifact naming and upload paths remain unchanged.

- [ ] **Task 5: Documentation updates** (AC: 6)
  - [ ] 5.1 Update `docs/setup.md` Python prerequisite text.
  - [ ] 5.2 Update `docs/architecture.md` compatibility note.
  - [ ] 5.3 Update `README.md` references to runtime compatibility examples where needed.

- [ ] **Task 6: Verification and regression confidence** (AC: 3, 4, 5)
  - [ ] 6.1 Run CLI tests on Python 3.13: `uv run pytest tests/cli/ --cov=src/cli`.
  - [ ] 6.2 Run packaging checks relevant to CLI binaries.
  - [ ] 6.3 Run lint/type checks on Python 3.13 (`ruff`, `mypy`) and fix any failures.
  - [ ] 6.4 Run targeted non-CLI regression tests to ensure no breakage outside CLI build path.

## Dev Notes

### Context and Rationale

- Current metadata/config still declares Python 3.14 baseline in `pyproject.toml` despite CLI build flow already being pinned to Python 3.13 in `.github/workflows/cli-build.yml`.
- Story 9.2 already documented the Nuitka compatibility issue and recommended Python 3.13 for binary builds; this story formalizes and completes that migration.
- Scope includes code/config adjustments required for Python 3.13 compatibility, not only CI pinning.

### Constraints

- Keep existing functionality stable; this is a compatibility migration, not a CLI feature redesign.
- Keep CLI architecture decisions from Story 9.2/9.3 intact (service-first, clean error output, output format behavior).
- Do not regress server runtime support on Python 3.14 while lowering minimum supported version.

### Source Tree Impact

| Component | Path | Action |
|:----------|:-----|:-------|
| Project metadata | `pyproject.toml` | **MODIFY** |
| CLI build workflow | `.github/workflows/cli-build.yml` | **VERIFY/MODIFY if needed** |
| CLI build scripts | `deployment/scripts/build_cli_*` | **MODIFY** |
| Master CLI build script | `deployment/scripts/build_all_cli.sh` | **MODIFY** |
| Setup docs | `docs/setup.md` | **MODIFY** |
| Architecture docs | `docs/architecture.md` | **MODIFY** |
| README | `README.md` | **MODIFY** |
| CLI tests | `tests/cli/` | **VERIFY/EXTEND** |
| Packaging tests | `tests/packaging/test_cli_binaries.py` | **VERIFY/EXTEND** |

### References

- [Source: specs/project-planning-artifacts/epics.md#Epic 9]
- [Source: specs/implementation-artifacts/9-2-fastmcp-cli-integration.md]
- [Source: pyproject.toml]
- [Source: .github/workflows/cli-build.yml]
- [Source: deployment/scripts/build_cli_linux_x86_64.sh]
- [Source: deployment/scripts/build_cli_linux_arm64.sh]
- [Source: deployment/scripts/build_cli_macos_x86_64.sh]
- [Source: deployment/scripts/build_cli_macos_arm64.sh]
- [Source: deployment/scripts/build_cli_windows_x86_64.bat]
- [Source: deployment/scripts/build_cli_windows_arm64.bat]

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Completion Notes List

- Story created for Epic 9 as `ready-for-dev` with explicit Python 3.13 migration scope for Nuitka CLI build compatibility.
