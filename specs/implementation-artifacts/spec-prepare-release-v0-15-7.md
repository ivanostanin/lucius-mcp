---
title: 'Prepare patch release v0.15.7'
type: 'chore'
created: '2026-09-21'
status: 'done'
baseline_commit: '807f64b3d98fce3e4fad1174c55932adc55f52c2'
context:
  - '{project-root}/scripts/prepare-release.md'
  - '{project-root}/scripts/update-changelog.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `origin/main` contains the dependency and Docker workflow updates from PR #405, while release metadata still identifies v0.15.6.

**Approach:** Prepare v0.15.7 from the fetched `origin/main` state on `release/v0.15.7`, synchronizing release metadata, generated documentation, changelog, MCPB bundles, and registry hashes. Leave the release unmerged and do not create or push a tag.

## Boundaries & Constraints

**Always:** Use `uv` for environment and project commands; preserve the changelog format and repository comparison-link pattern; include PR #405 in the v0.15.7 notes; keep the release scoped to the fetched mainline changes; skip binary tests as explicitly requested.

**Ask First:** Any release version other than v0.15.7; merging the release PR; creating or pushing the v0.15.7 tag.

**Never:** Merge the release branch or PR, push a release tag, rewrite unrelated history, run binary tests, or include unrelated working-tree changes.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | Clean `release/v0.15.7` based on fetched `origin/main` | Release metadata and generated artifacts identify v0.15.7; changelog documents PR #405; branch is ready for review | N/A |
| VALIDATION_LIMIT | Full release suite includes binary tests | Run applicable non-binary checks only and explicitly report skipped binary tests | Do not claim full-suite success |
| ARTIFACT_FAILURE | MCPB build or registry hash update cannot produce all packages | Stop before claiming release readiness | Report the failing command and preserve diagnostics |

</frozen-after-approval>

## Code Map

- `pyproject.toml` -- canonical project version.
- `uv.lock` -- synchronized project lockfile.
- `docs/mcp_manifest.json` -- generated MCP documentation manifest.
- `CHANGELOG.md` -- v0.15.7 release notes and comparison references.
- `server.json` -- MCP Registry package metadata and MCPB hashes.
- `deployment/scripts/build-mcpb.sh` -- local MCPB bundle build.
- `deployment/scripts/update_mcp_registry_metadata.py` -- version and hash updater.

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml` and `uv.lock` -- set v0.15.7 and synchronize dependencies -- keep package metadata consistent.
- [x] `docs/mcp_manifest.json` -- regenerate from the synchronized project -- publish v0.15.7 metadata.
- [x] `CHANGELOG.md` -- add the v0.15.7 section for PR #405 and update links -- document the patch release.
- [x] `dist/*.mcpb` and `server.json` -- build both MCPB variants and refresh registry hashes -- align published artifact metadata.
- [x] Release branch and commit -- review and commit only intended release changes -- hand off an unmerged release candidate.

**Acceptance Criteria:**
- Given fetched `origin/main`, when preparation completes, then all release metadata and generated artifacts identify v0.15.7 and registry hashes match local MCPB files.
- Given the release branch is ready, when the task is handed off, then no merge or v0.15.7 tag has been performed.
- Given binary tests are explicitly excluded, when validation runs, then non-binary focused checks are reported separately and binary tests are clearly identified as skipped.

## Verification

**Commands:**
- `uv sync --all-extras` -- expected: lockfile and environment synchronize successfully.
- `uv run --locked fastmcp inspect src/main.py --format mcp -o docs/mcp_manifest.json` -- expected: manifest regenerates successfully.
- `uv run --locked pytest tests/docs/test_mcp_manifest.py -q` -- expected: focused manifest test passes.
- `uv run --extra dev ruff check scripts src tests deployment` -- expected: non-binary lint passes.
- `uv run --extra dev mypy src` -- expected: type checks pass.
- `uv run --extra dev pytest tests/unit tests/integration tests/docs tests/packaging --ignore=tests/packaging/test_cli_binaries.py` -- expected: non-binary tests pass; CLI binary tests are skipped.
- `git diff --check` -- expected: no whitespace errors.

## Suggested Review Order

**Release identity**

- Confirm the canonical package version before reviewing generated release metadata.
  [`pyproject.toml:3`](../../pyproject.toml#L3)

- Verify the editable package version in the lockfile matches the project metadata.
  [`uv.lock:1248`](../../uv.lock#L1248)

**Published metadata**

- Check the generated MCP manifest exposes the new server version and runtime.
  [`mcp_manifest.json:3`](../../docs/mcp_manifest.json#L3)

- Verify registry package versions, artifact URLs, and hashes target v0.15.7.
  [`server.json:10`](../../server.json#L10)

**Release communication**

- Review the user-facing release note and comparison-link transition.
  [`CHANGELOG.md:10`](../../CHANGELOG.md#L10)
