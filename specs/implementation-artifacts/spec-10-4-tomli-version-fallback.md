---
title: "Use tomli for the Python 3.10 project-version fallback"
type: "bugfix"
created: "2026-08-10"
status: "done"
baseline_commit: "878f5bb74aff39965e16bdf588d203b3a5c035f1"
context:
  - "{project-root}/docs/development.md"
  - "{project-root}/specs/implementation-artifacts/10-4-support-python-3-10-through-3-14-runtime.md"
---

# Use tomli for the Python 3.10 project-version fallback

## Intent (frozen after approval)

Revise Story 10-4 so Python 3.10 is supported through the maintained `tomli`
backport rather than a hand-written TOML parser. At runtime, use the standard
library `tomllib` on Python 3.11 and newer, and use `tomli` only where
`tomllib` is unavailable (Python 3.10 in the supported matrix).

## Problem

`tomllib` was removed from `src/version.py` because it is unavailable in
Python 3.10. That replacement was a narrow regular-expression parser for
`pyproject.toml`; it is less robust than a TOML parser and conflicts with the
revised compatibility decision. `tomli` is the backport of `tomllib` and has
the compatible `load` and `loads` API needed here.

## Approach

- Add a direct conditional runtime dependency on `tomli` for Python versions
  below 3.11, and regenerate `uv.lock` without upgrading unrelated packages.
- Import `tomllib` when available; otherwise import `tomli` under the same
  module name used by the version reader.
- Parse `pyproject.toml` in binary mode and read `[project].version` through
  that parser, preserving the current installed-package metadata fast path and
  the existing clear error for a missing or blank version.
- Update Story 10-4's acceptance criteria, tasks, guardrails, and status to
  describe this approved exception to its former no-runtime-dependency rule.
- Add or adjust focused unit tests for version extraction and fallback behavior.

## Constraints

### Always

- Keep `importlib.metadata.version()` as the first choice for installed
  packages.
- Restrict the direct `tomli` requirement to `python_version < '3.11'`.
- Keep Python 3.11+ free of the `tomli` runtime dependency.
- Preserve the public `read_project_version(Path) -> str` helper used by the
  deployment metadata updater.
- Keep the changes limited to Story 10-4 compatibility and its tests/docs.

### Ask first

- Any dependency upgrade other than adding the conditional direct `tomli`
  declaration and the lockfile changes it necessitates.
- Changing the supported Python range or packaging format.

### Never

- Reintroduce a hand-written TOML parser.
- Change the package version, release artifacts, telemetry behavior, or
  unrelated dependencies.

## I/O behavior

| Situation | Expected result |
| --- | --- |
| Installed package | Return `importlib.metadata.version("lucius-mcp")`. |
| Source checkout on Python 3.11+ | Parse `pyproject.toml` with `tomllib`. |
| Source checkout on Python 3.10 | Parse `pyproject.toml` with `tomli`. |
| Missing or blank `[project].version` | Raise the existing descriptive `RuntimeError`. |

## Code map

- `pyproject.toml` — declares the conditional direct runtime dependency.
- `uv.lock` — records that declared dependency and its resolution.
- `src/version.py` — selects `tomllib` or `tomli` and reads the project
  version through that parser.
- `tests/unit/test_remaining_coverage.py` — verifies project-version parsing
  and error handling; add fallback coverage where practical.
- `specs/implementation-artifacts/10-4-support-python-3-10-through-3-14-runtime.md`
  — updates the story description and implementation guardrails.
- `specs/implementation-artifacts/sprint-status.yaml` — returns Story 10-4
  to in-progress while this correction is implemented.

## Tasks and acceptance criteria

1. [x] Declare conditional `tomli` support.
   - `pyproject.toml` directly requires `tomli` only for Python `<3.11`.
   - `uv.lock` is regenerated without unrelated dependency upgrades.

2. [x] Use the compatible TOML parser in the version fallback.
   - Python 3.11+ uses `tomllib`; Python 3.10 uses `tomli`.
   - `read_project_version()` still returns a trimmed string version and
     retains its current invalid-project error behavior.

3. [x] Revise Story 10-4 to record the dependency decision.
   - Its description, acceptance criteria, tasks, and guardrails no longer
     prohibit the conditional `tomli` dependency or demand a manual parser.

4. [x] Prove the focused behavior.
   - Run the focused version-reader unit tests under the project environment.
   - Run Ruff and strict mypy for the changed source.
   - Run the packaging/version-reader test group where available under Python
     3.10 and the default supported interpreter; report any matrix coverage
     that remains unrun.

## Verification commands

```bash
uv run pytest tests/unit/test_remaining_coverage.py -q
uv run ruff check src/version.py tests/unit/test_remaining_coverage.py
uv run mypy --strict src/version.py
uv run --python 3.10 pytest tests/unit/test_remaining_coverage.py -q
```

## Risks and rollback

- A misplaced environment marker could install `tomli` unnecessarily on
  newer Python versions. The lockfile and marker inspection mitigate this.
- An import fallback can mask a packaging omission on Python 3.10. Running a
  Python 3.10 test through `uv` verifies the dependency resolves.
- Rollback is limited to reverting the conditional dependency, parser import,
  tests, and matching story status/documentation changes.

## Suggested Review Order

**Dependency and compatibility contract**

- The marker installs the backport only where the standard-library parser is unavailable.
  [`pyproject.toml:32`](../../pyproject.toml#L32)

- The lock records the direct conditional requirement without package-version churn.
  [`uv.lock:1207`](../../uv.lock#L1207)

**Runtime fallback**

- The source fallback preserves installed metadata while selecting a compatible TOML parser.
  [`src/version.py:7`](../../src/version.py#L7)

**Regression coverage**

- Tests cover valid TOML plus missing and blank project-version failures.
  [`test_remaining_coverage.py:296`](../../tests/unit/test_remaining_coverage.py#L296)

**Story record**

- The acceptance criteria now permit only this scoped dependency exception.
  [`10-4-support-python-3-10-through-3-14-runtime.md:13`](10-4-support-python-3-10-through-3-14-runtime.md#L13)

- The active story status accurately retains the unrun matrix work.
  [`sprint-status.yaml:146`](sprint-status.yaml#L146)
