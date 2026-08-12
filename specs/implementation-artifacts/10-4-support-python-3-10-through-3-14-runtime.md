# Story 10.4: Support Python 3.10 Through 3.14 at Runtime

Status: in-progress

## Story

As a Lucius user,
I want to run the server and source CLI on Python 3.10 through 3.14,
so that I can use Lucius in established environments without changing unrelated package versions.

## Acceptance Criteria

1. **Runtime compatibility declaration**
   - Given Python 3.10, 3.11, 3.12, 3.13, or 3.14, when Lucius is installed from the checked-in lockfile, then the package installs, compiles, imports, and runs its supported test suites.
   - `pyproject.toml` declares `requires-python = ">=3.10,<3.15"`, has classifiers for 3.10, 3.11, 3.12, 3.13, and 3.14, sets Ruff `target-version = "py310"`, and sets mypy `python_version = "3.10"`.
   - Add the direct `tomli>=2.0.1` requirement only for `python_version < '3.11'` so the Python 3.10 source fallback has a maintained TOML parser. Apart from that conditional requirement and its required lockfile metadata, do not add, remove, upgrade, downgrade, or re-pin dependencies; verify all existing locked package version records remain unchanged.

2. **Python 3.10/3.11 syntax compatibility**
   - Given the application source is parsed by Python 3.10 or 3.11, when it encounters the existing PEP 695 aliases, then parsing succeeds.
   - Replace every application `type Alias = ...` statement with the PEP 613 pattern `Alias: TypeAlias = ...`, importing `TypeAlias` from `typing`; do not substitute `Any`, remove an alias, or change the alias's declared shape.
   - This applies to all aliases in `src/client/client.py`, `src/services/launch_service.py`, `src/services/telemetry_service.py`, `src/tools/test_code.py`, and `src/utils/telemetry.py`.

3. **Python 3.10 standard-library compatibility**
   - Given Python 3.10, when Lucius is imported from an editable/source checkout, then version fallback succeeds through `tomli`; Python 3.11+ uses `tomllib`.
   - Use the compatible TOML parser's `load` API to read `project.version` from `pyproject.toml` in binary mode, validate a non-empty version, and do not implement a hand-written TOML parser.
   - Reuse that version path in release metadata tooling and adjust documentation/packaging tests to use the shared version reader rather than importing a parser directly.
   - Replace `datetime.UTC` / `from datetime import UTC` usage with `datetime.timezone.utc` in runtime code and tests while preserving the exact UTC timestamp and rendering behavior.

4. **Python 3.12 runtime typing compatibility**
   - Given Python 3.12 evaluates annotations during import or pytest collection, when a lifespan function or fixture yields, then its return annotation is valid.
   - Annotate async generators with both required parameters, e.g. `AsyncGenerator[YieldType, None]`, and synchronous generators with all three, e.g. `Generator[YieldType, None, None]`.
   - Do not suppress annotation evaluation, remove fixture annotations, or lower type-checker strictness.

5. **Published MCPB runtime contract**
   - Given an MCPB bundle is generated for either the `uv` or `python` server, when a client examines its manifest, then `server.runtimes.python` declares the same supported range as the package: `>=3.10,<3.15`.
   - Regenerate the checked-in `deployment/mcpb/manifest.uv.json` and `deployment/mcpb/manifest.python.json` using their established generation workflow. Do not hand-edit generated output or leave either manifest at its current `>=3.14` declaration.
   - Add a packaging regression that compares both generated manifest runtime declarations with `pyproject.toml`, and validate/build/inspect both MCPB bundles so the packaged `manifest.json` retains the range.

6. **Nuitka compatibility for every supported Python minor**
   - Given any supported Python minor from 3.10 through 3.14, when the checked-in Nuitka dependency is run with that interpreter, then it builds the standalone Lucius CLI without changing the Nuitka or any other package version.
   - The produced binary passes the existing platform-appropriate `--version` and `--help` smoke checks. CI must exercise a representative Nuitka build-and-smoke lane for every supported minor; preserve the existing cross-platform binary matrix as the release-artifact lane rather than multiplying every platform by every minor.
   - Parameterize the Unix and Windows build scripts and reusable CLI workflow so their selected Python version is passed consistently to schema generation, version lookup, Nuitka, cache keys, artifact naming, and test setup. A Python version cannot be documented, published in MCPB, or classified as supported until its Nuitka lane passes.

7. **Documentation and scope boundaries**
   - README, setup, development, and current architecture documentation consistently describe runtime support as Python 3.10-3.14.
   - They state that the same Python 3.10-3.14 range is validated for MCPB runtime declarations and Nuitka CLI compilation; do not retain a stale claim that Nuitka is Python 3.13-only.
   - They explicitly retain the exclusions: Python 3.9 cannot resolve the pinned `starlette==1.3.1` requirement, and Python 3.15 is deferred because the current native dependency set does not build for it. Do not add a 3.15 classifier or CI lane.

8. **Enforced regression coverage**
   - Pull-request CI runs the portable runtime suite on 3.10, 3.11, 3.12, 3.13, and 3.14 using the lockfile.
   - The reusable Python workflow's existing `run-cli-tests` input actually controls a CLI test step; it must not remain a no-op.
   - Lint and strict mypy run against the 3.10 compatibility baseline; MCPB packaging and representative Nuitka checks verify the same published range without changing package versions.

## Tasks / Subtasks

- [x] **1. Lower the declared runtime and static-analysis baseline** (AC: 1, 7)
  - [x] Update only Python compatibility metadata in `pyproject.toml`: the `requires-python` range, 3.10-3.14 classifiers, Ruff target, and mypy version.
  - [x] Add the direct conditional `tomli>=2.0.1; python_version < '3.11'` dependency and regenerate `uv.lock`; inspect it to ensure package versions other than the added direct requirement remain unchanged. Do not use `uv add` or `uv remove`.

- [x] **2. Replace all PEP 695 aliases with PEP 613 aliases** (AC: 2)
  - [x] `src/client/client.py`: convert `ApiType`, `NormalizedScenarioDict`, `ScenarioStepsMap`, and `AttachmentsMap` near lines 206-245.
  - [x] `src/services/launch_service.py`: convert `LaunchListItem` near line 80.
  - [x] `src/services/telemetry_service.py`: convert `TelemetryOutcome`, `TelemetryErrorCategory`, `DeploymentMethod`, and `MpcMode` near lines 29-32.
  - [x] `src/tools/test_code.py`: convert `LanguageSelection`, `FrameworkSelection`, `MetadataSelection`, and `SchemaMetadataSelection` near lines 12-119.
  - [x] `src/utils/telemetry.py`: convert `ToolFn` near line 17.
  - [x] Add only `typing.TypeAlias` imports necessary for these declarations. Keep all existing `Literal`, `Annotated`, callable, and union definitions intact.

- [x] **3. Provide the Python 3.10 TOML parser fallback** (AC: 3)
  - [x] `src/version.py`: use `tomllib` on Python 3.11+ and `tomli` when `tomllib` is unavailable; parse the `[project]` `version` fallback through the compatible parser while retaining the installed-distribution fast path and the `RuntimeError` for missing/blank project versions.
  - [x] `deployment/scripts/update_mcp_registry_metadata.py`: reuse the same version-reading behavior rather than importing `tomllib` or duplicating a permissive TOML parser.
  - [x] `src/cli/auth_config.py`, `src/cli/formatting.py`, `src/services/telemetry_service.py`, and `src/utils/logger.py`: replace `UTC` with `timezone.utc` while preserving current timestamp output and UTC table fallback behavior.
  - [x] Do not change telemetry's privacy guarantees, event payload fields, or log timestamp format.

- [x] **4. Correct generator annotations in source and tests** (AC: 4)
  - [x] `src/main.py:57`: use `typing.AsyncGenerator[None, None]` for `lifespan`.
  - [x] `tests/e2e/conftest.py:27,57` and `tests/support/fixtures/allure_client_fixture.py:14`: use `AsyncGenerator[YieldType, None]`.
  - [x] `tests/e2e/test_telemetry_collection_e2e.py:44`, `tests/support/fixtures/logger_fixture.py:20`, `tests/support/fixtures/client_fixture.py:9`, and `tests/cli/subprocess_helpers.py:41`: use `Generator[YieldType, None, None]`.
  - [x] `tests/integration/test_test_create_tool.py:10,16`, `tests/integration/test_test_update_tool.py:11,17`, and `tests/integration/test_delete_tool.py:13,20`: use `typing.Generator[Mock, None, None]`.

- [x] **5. Make the affected tests portable and add focused regressions** (AC: 1, 3, 4, 5, 6)
  - [x] Remove `tomllib` imports from `tests/docs/test_mcp_manifest.py`, `tests/docs/test_mcp_registry.py`, and `tests/packaging/test_cli_python_313_contract.py`; assert the relevant project metadata via the shared narrow version helper or explicit TOML-text contract checks, not a new TOML dependency.
  - [x] Update `tests/unit/test_remaining_coverage.py` to test missing/blank project versions and TOML-parser version extraction; run it under Python 3.10 to exercise `tomli`.
  - [x] Update UTC test imports/usages in `tests/cli/test_e2e_mocked.py` and `tests/cli/test_cli_coverage_helpers.py` to `timezone.utc`, keeping identity and rendered-output assertions.
  - [x] Rename or retarget the packaging metadata contract test so it asserts the runtime range/classifiers/analysis baseline and that the CLI build scripts/workflow accept the selected supported interpreter rather than hard-coding Python 3.13.
  - [x] Extend `tests/packaging/test_mcpb_manifests.py` (and bundle verification where appropriate) to require `server.runtimes.python == ">=3.10,<3.15"` in both manifest variants and in each built bundle's packaged `manifest.json`.
  - [x] Add a focused test or static check that prevents reintroducing PEP 695 aliases and verifies the source fallback version reader under the Python 3.10 execution path.

- [x] **6. Regenerate and validate MCPB runtime declarations** (AC: 5)
  - [x] Locate and use the repository's existing MCPB manifest generation/update workflow to regenerate `deployment/mcpb/manifest.uv.json` and `deployment/mcpb/manifest.python.json`; the checked-in JSON is generated output, not a second source of truth.
  - [x] Keep `deployment/scripts/build-mcpb.sh`, `deployment/scripts/validate_mcpb.py`, `deployment/scripts/verify_mcpb_bundles.py`, and `.github/workflows/_mcpb_build.yml` aligned so both bundle types validate, build, and retain `>=3.10,<3.15`.

- [x] **7. Enforce the runtime and Nuitka matrices in CI** (AC: 6, 8)
  - [x] Update `.github/workflows/_python_check.yml` so dependency installation uses the checked-in lockfile and its `run-cli-tests` input runs `tests/cli/` when enabled.
  - [x] Update `.github/workflows/pr-quality-gate.yml` to keep the existing quality lane and add a 3.10-3.14 reusable-workflow matrix for portable runtime tests. Avoid duplicating heavy Docker, MCPB, and E2E sandbox jobs across the matrix.
  - [x] Parameterize `deployment/scripts/build_cli_unix.sh`, `deployment/scripts/build_cli_windows.bat`, `.github/workflows/_cli_build_test.yml`, and their build/test contract checks to use the caller-selected Python version instead of literal `3.13`.
  - [x] Add a representative-platform Nuitka build-and-smoke matrix for Python 3.10, 3.11, 3.12, 3.13, and 3.14. Retain the existing full multi-platform CLI artifact matrix for its release purpose; do not turn all five minors into a six-platform artifact matrix.
  - [x] Keep workflow permissions least-privilege (`contents: read`).

- [x] **8. Align user and developer documentation** (AC: 7)
  - [x] Update `README.md`, `docs/setup.md`, `docs/development.md`, and `docs/architecture.md` together; remove stale statements that 3.12 and earlier are unsupported.
  - [x] Update MCPB and CLI-build guidance to state that the generated MCPB manifests and the tested Nuitka compiler matrix cover Python 3.10-3.14.
  - [x] State the tested command pattern for a selected interpreter, e.g. `uv sync --locked --all-extras --python 3.10` followed by the relevant `uv run --python 3.10 ...` checks.

- [ ] **9. Validate from clean environments** (AC: 1-8)
  - [ ] For each Python 3.10, 3.11, 3.12, 3.13, and 3.14: create/sync a clean environment from `uv.lock`; run `python -m compileall -q src tests deployment/scripts`; smoke-import `src.main`, `src.cli.cli_entry`, and `src.version`; run `pytest tests/unit tests/integration tests/docs tests/cli -q` with the selected interpreter. The complete five-version runtime suite remains unrun.
  - [x] Run focused checks first: compatibility/version tests, `tests/unit/test_main.py`, `tests/unit/test_telemetry_service.py`, `tests/cli/test_cli_coverage_helpers.py`, `tests/docs/test_mcp_manifest.py`, and the retargeted packaging metadata test.
  - [ ] Validate both regenerated MCPB manifests and build/inspect both bundles. For each 3.10-3.14 interpreter, run the selected-platform Nuitka build and the produced binary's `--version` and `--help` checks; complete the existing full-platform CLI artifact lane at least once. The all-minor Nuitka binary matrix remains unrun.
  - [x] Run `uv run ruff check` and `uv run mypy --strict src` after lowering their configured baseline.
  - [x] Record any unrelated environment failures separately; do not weaken tests, pin new packages, or change dependency versions to bypass a compatibility result.

## Dev Notes

### Exact blocker inventory

| Python version | Confirmed blocker in current branch | Required resolution |
| --- | --- | --- |
| 3.10 | PEP 695 aliases; `tomllib`; `datetime.UTC`; one-parameter generator annotations | All tasks in this story |
| 3.11 | PEP 695 aliases; `datetime.UTC`; one-parameter generator annotations | Alias, UTC, and generator tasks |
| 3.12 | One-parameter `typing.AsyncGenerator`/`typing.Generator` annotations fail at import/collection | Generator task |
| 3.13-3.14 | Runtime-compatible baseline | Retain regression coverage |
| 3.9 | `starlette==1.3.1` requires Python >=3.10 | Explicitly out of scope |
| 3.15 | Current native dependencies fail to build for the available beta | Explicitly out of scope; await upstream releases |

### Architecture and implementation guardrails

- Use `uv`, never bare `pip` or an unpinned resolver path. Do not modify generated client files under `src/client/generated/`.
- This is a compatibility-only change. Preserve the thin-tool/fat-service boundary, tool output schemas, CLI behavior, public API, telemetry payload fields, and telemetry privacy constraints.
- A Python 3.10 runtime floor does not change the Docker base image or its existing default CI variable. The Nuitka build interpreter is deliberately broadened only through the selected-version scripts/workflow and required compiler matrix; do not change package versions to make a compiler lane pass.
- Declare `tomli` only for Python `<3.11` and use it solely as the compatible `tomllib` fallback for the static `project.version` reader. Do not implement a hand-written TOML parser or introduce another parser dependency.
- `typing.TypeAlias` is the compatible replacement for the current PEP 695 statements. Do not hide aliases behind `if TYPE_CHECKING` because runtime consumers and introspection may need them.
- `datetime.timezone.utc` is the compatible UTC singleton. Preserve `Z` normalization in saved CLI auth timestamps and the current UTC rendering fallback in CLI tables.
- The previous Epic 10 story changed launch DTO contracts. Do not touch `src/services/launch_service.py` except its one alias declaration; preserve the compact-list/rich-detail behavior and tests.

### Source tree impact

| Area | Files | Intended change |
| --- | --- | --- |
| Runtime typing | `src/client/client.py`, `src/services/launch_service.py`, `src/services/telemetry_service.py`, `src/tools/test_code.py`, `src/utils/telemetry.py`, `src/main.py` | PEP 613 aliases and complete generator annotations |
| Standard library | `src/version.py`, `src/cli/auth_config.py`, `src/cli/formatting.py`, `src/utils/logger.py`, `deployment/scripts/update_mcp_registry_metadata.py` | Use conditional `tomli`/`tomllib` version parsing and replace `UTC` with scoped standard-library compatibility code |
| Tests | affected fixture, integration, CLI, docs, packaging, and coverage files named in Tasks 4-5 | Portable annotations/imports and explicit metadata assertions |
| Packaging | generated `deployment/mcpb/manifest.uv.json`, generated `deployment/mcpb/manifest.python.json`, MCPB validation/build/verification scripts and tests | Regenerated `>=3.10,<3.15` runtime declaration preserved in both bundle types |
| CI and CLI build | `pyproject.toml`, `uv.lock`, `.github/workflows/_python_check.yml`, `.github/workflows/pr-quality-gate.yml`, `.github/workflows/_cli_build_test.yml`, `deployment/scripts/build_cli_unix.sh`, `deployment/scripts/build_cli_windows.bat` | Runtime declaration, unchanged locked versions, 3.10-3.14 runtime matrix, and selected-version Nuitka matrix |
| Documentation | `README.md`, `docs/setup.md`, `docs/development.md`, `docs/architecture.md` | One accurate 3.10-3.14 statement covering runtime, generated MCPB manifests, Nuitka, and 3.9/3.15 caveats |

### Previous-story intelligence

- Story 10.3 established an active Epic 10 and strong regression discipline around source, service, tool, CLI, schema, and documentation behavior. This story must be narrower: it is not a launch feature change.
- Existing project standards require `ruff`, strict `mypy`, pytest suites, least-privilege GitHub workflow permissions, and `uv` commands. Preserve those standards while changing only the language/runtime baseline.

### References

- [Source: `docs/development.md` — Python compatibility and validation commands]
- [Source: `pyproject.toml:10-42,101-122` — current Python declaration, classifiers, Ruff, and mypy settings]
- [Source: `src/client/client.py:206-245`; `src/services/launch_service.py:80`; `src/services/telemetry_service.py:29-32`; `src/tools/test_code.py:12-119`; `src/utils/telemetry.py:17` — PEP 695 aliases]
- [Source: `src/version.py:3-15`; `deployment/scripts/update_mcp_registry_metadata.py:8,34-39` — `tomllib` use]
- [Source: `src/cli/auth_config.py:10,61-63`; `src/cli/formatting.py:14,81-153`; `src/services/telemetry_service.py:60`; `src/utils/logger.py:25` — `datetime.UTC` use]
- [Source: `src/main.py:57`; `tests/e2e/conftest.py:27,57`; `tests/support/fixtures/allure_client_fixture.py:14`; `tests/integration/test_test_create_tool.py:10,16`; `tests/integration/test_test_update_tool.py:11,17`; `tests/integration/test_delete_tool.py:13,20` — invalid generator annotations]
- [Source: `.github/workflows/_python_check.yml`; `.github/workflows/pr-quality-gate.yml` — current quality workflow and unused CLI-test input]
- [Source: `deployment/mcpb/manifest.uv.json:330-332`; `deployment/mcpb/manifest.python.json:331-333`; `deployment/scripts/build-mcpb.sh`; `deployment/scripts/validate_mcpb.py`; `deployment/scripts/verify_mcpb_bundles.py`; `tests/packaging/test_mcpb_manifests.py` — generated MCPB runtime declarations and bundle checks]
- [Source: `deployment/scripts/build_cli_unix.sh:139-201`; `deployment/scripts/build_cli_windows.bat:77-112`; `.github/workflows/_cli_build_test.yml`; `tests/packaging/test_cli_python_313_contract.py` — current hard-coded Python 3.13 Nuitka contract]
- [Source: `specs/project-context.md`; `specs/architecture.md`; `specs/prd.md#Non-Functional Requirements` — project boundaries and quality requirements]

## Dev Agent Record

### Agent Model Used

GPT-5

### Debug Log References

- Existing compatibility probes on the pre-story branch: Python 3.10 dependency resolution succeeded but source parsing failed on PEP 695 aliases; Python 3.11 failed on the same aliases; Python 3.12 compiled but failed on generator annotation evaluation; Python 3.13/3.14 passed source smoke checks; Python 3.15 native dependency builds failed.
- Static Python 3.10 grammar scan confirmed the five application files containing PEP 695 `type` statements. No source or test implementation files were edited while creating this story.

### Completion Notes List

- Ultimate context analysis completed: the story identifies all known Python 3.10, 3.11, and 3.12 blockers and confines implementation to compatible source, metadata, generated MCPB manifests, Nuitka, CI, tests, and documentation changes.
- Python 3.9 and 3.15 are explicitly excluded. The revised Python 3.10 source-version fallback permits only the conditional `tomli` dependency; other dependency versions must remain unchanged.
- Implementation is in progress: prior standard-library-only version parsing is superseded by the approved conditional `tomli`/`tomllib` approach. Earlier validation does not cover this revised dependency path or the complete binary/packaging matrix.
- The revised version-reader unit tests passed on Python 3.10 (confirming `tomli`) and Python 3.14. Focused documentation and packaging contracts also passed on both versions; the full five-minor packaging and Nuitka matrices remain outstanding.

### File List

- `pyproject.toml`, `uv.lock`
- `src/version.py`, `src/main.py`, `src/client/client.py`, `src/services/launch_service.py`, `src/services/telemetry_service.py`, `src/tools/test_code.py`, `src/utils/telemetry.py`, `src/utils/logger.py`, `src/cli/auth_config.py`, `src/cli/formatting.py`
- `.github/actions/setup-python/action.yml`, `.github/workflows/_python_check.yml`, `.github/workflows/_cli_build_test.yml`, `.github/workflows/_cli_nuitka_smoke.yml`, `.github/workflows/pr-quality-gate.yml`
- `deployment/mcpb/manifest.uv.json`, `deployment/mcpb/manifest.python.json`, `deployment/scripts/update_mcpb_runtime.py`, `deployment/scripts/update_mcp_registry_metadata.py`, `deployment/scripts/verify_mcpb_bundles.py`, `deployment/scripts/build_all_cli.sh`, `deployment/scripts/build_cli_unix.sh`, `deployment/scripts/build_cli_windows.bat`
- `tests/conftest.py`, affected CLI, docs, integration, packaging, fixture, E2E, and unit compatibility tests
- `README.md`, `docs/setup.md`, `docs/development.md`, `docs/architecture.md`, `specs/implementation-artifacts/sprint-status.yaml`

- `specs/project-planning-artifacts/epics.md`
- `specs/implementation-artifacts/sprint-status.yaml`
- `specs/implementation-artifacts/10-4-support-python-3-10-through-3-14-runtime.md`
