---
title: Experimental Python 3.15 support
type: feature
created: 2026-10-26
status: done
baseline_commit: 540b6e8
context: []
---

<frozen-after-approval reason="user-requested scope">

## Intent

**Problem:** Python 3.15 is excluded from package metadata and CI, despite a request to evaluate experimental support.

**Approach:** Permit and test Python 3.15 experimentally, document dependency and platform limitations, and preserve existing release defaults.

## Boundaries & Constraints

**Always:** Preserve existing user changes; keep Python 3.10–3.14 support and platform-specific cryptography pins; avoid promising unverified platform support.

**Never:** Claim wheel availability or working platform builds without evidence; change default release compiler version.

</frozen-after-approval>

## Code Map

- `pyproject.toml`, `uv.lock` — Python compatibility and dependency resolution.
- `.github/workflows/pr-quality-gate.yml` — runtime and compiler coverage.
- `deployment/mcpb/manifest.*.json` — generated runtime metadata.
- `docs/development.md`, `tests/packaging/test_cli_python_versions_contract.py` — compatibility guidance and contracts.

## Tasks & Acceptance

**Execution:**
- [x] Update Python metadata and dependency constraints as needed, regenerate lock and manifests.
- [x] Add an experimental CI check and update compatibility guidance and contracts.
- [x] Run focused Python 3.15 tests and identify unsupported or unverified platform cases.

**Acceptance Criteria:**
- Given Python 3.15, when project dependencies are installed and tests run, then experimental compatibility is tested without changing the release compiler default.
- Given missing wheels or platform tests, when developers read compatibility guidance, then the limitations are explicit.

## Spec Change Log

## Verification

Run relevant packaging and runtime tests with Python 3.15 and existing supported Python where feasible; report platform limitations.

- Python 3.15.0 on macOS ARM64: locked all-extras sync succeeded; the CI test selection passed (1528 tests).
- Python 3.14.2 on macOS ARM64: locked all-extras sync and 12 packaging contract and manifest tests passed.
- Linux and Windows 3.15 installations and macOS x86-64 remain unverified; wheel availability limitations are documented in the development guide. The PR quality gate now runs the regular runtime checks on 3.15 and builds and tests CLI binaries on all six platform and architecture combinations.

## Suggested Review Order

**Compatibility and limitations**

- Permit Python 3.15 and select compatible dependency versions.
  [`pyproject.toml:10`](../../pyproject.toml#L10)
- Document experimental platform and source-build limitations.
  [`development.md:48`](../../docs/development.md#L48)

**Validation**

- Run Python 3.15 runtime and CLI build checks in the PR quality gate.
  [`pr-quality-gate.yml:18`](../../.github/workflows/pr-quality-gate.yml#L18)
- Check metadata and release-build defaults.
  [`test_cli_python_versions_contract.py:28`](../../tests/packaging/test_cli_python_versions_contract.py#L28)
