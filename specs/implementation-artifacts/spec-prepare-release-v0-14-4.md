---
title: 'Prepare patch release v0.14.4'
type: 'chore'
created: '2026-08-24'
status: 'done'
baseline_commit: '6650c60fcbb49dc58d6b79fcf93c52cdadf3948c'
context:
  - '/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/scripts/prepare-release.md'
  - '/Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/scripts/update-changelog.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The repository is ready for a new patch release after the latest dependency and Docker workflow updates, but its release metadata and artifacts still identify v0.14.3.

**Approach:** Prepare v0.14.4 from up-to-date `main` on `release/v0.14.4`, synchronizing the project version, lockfile/environment, MCP manifest, changelog, local MCPB bundles, and MCP Registry metadata. Create the release commit and PR, but leave the PR unmerged.

## Boundaries & Constraints

**Always:** Preserve existing changelog format and repository URL references; use `uv` for environment and validation commands; derive registry hashes from freshly built local MCPB artifacts; keep the release scoped to v0.14.4.

**Ask First:** Any release version other than v0.14.4; any request to merge the release PR or create/push the version tag.

**Never:** Do not merge the PR, push a release tag, rewrite unrelated history, or include unrelated working-tree changes.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | Clean release branch based on current `origin/main` | Versioned metadata, manifest, changelog, MCPB bundles, registry hashes, commit, and unmerged PR are ready | N/A |
| QA_FAILURE | Full validation suite fails | Release preparation stops before release artifacts are finalized | Report failing command and preserve diagnostics |
| ARTIFACT_FAILURE | MCPB build or hash update cannot produce all packages | Release preparation stops without claiming readiness | Report missing or invalid artifact |

</frozen-after-approval>

## Code Map

- `pyproject.toml` -- canonical project version.
- `uv.lock` -- synchronized dependency lockfile.
- `docs/mcp_manifest.json` -- generated MCP documentation manifest.
- `CHANGELOG.md` -- release notes and comparison references.
- `deployment/scripts/build-mcpb.sh` -- local MCPB bundle build.
- `deployment/scripts/update_mcp_registry_metadata.py` -- server version and MCPB hash update.
- `server.json` -- MCP Registry package metadata.
- `scripts/full-test-suite.sh` -- mandatory release quality gate.

## Tasks & Acceptance

**Execution:**
- [x] Run `./scripts/full-test-suite.sh` on the release branch before release finalization -- enforce the release quality gate.
- [x] Update `pyproject.toml` to `0.14.4` and run `uv sync --all-extras` -- synchronize release version and dependencies.
- [x] Regenerate `docs/mcp_manifest.json` and run its focused test -- publish accurate version/tool metadata.
- [x] Update `CHANGELOG.md` with the v0.14.4 notes and links, including PR #351 -- document user-visible release changes.
- [x] Build local MCPB bundles and update `server.json` hashes -- make registry metadata match release artifacts.
- [x] Run focused release checks, review the diff, commit, push the branch, and create an unmerged PR to `main` -- hand off the release for review.

**Acceptance Criteria:**
- Given current `origin/main`, when release preparation completes, then all release metadata identifies v0.14.4 and local package hashes match the generated MCPB files.
- Given the release PR exists, when the task is handed off, then it targets `main` and remains unmerged with no v0.14.4 tag pushed.
- Given any mandatory validation or artifact step fails, when the failure occurs, then no success claim is made and the failure is reported.

## Verification

**Commands:**
- `./scripts/full-test-suite.sh` -- expected: success.
- `uv run --locked pytest tests/docs/test_mcp_manifest.py -q` -- expected: success.
- `git diff --check` -- expected: no whitespace errors.
- `git status --short --branch` -- expected: only intended release changes on `release/v0.14.4`.

## Suggested Review Order

**Release identity**

- Confirm the canonical package version before reviewing generated release files.
  [`pyproject.toml:3`](../../pyproject.toml#L3)

- Verify the lockfile editable package version matches the project metadata.
  [`uv.lock:1256`](../../uv.lock#L1256)

**Published metadata**

- Check the generated MCP manifest exposes the new server version.
  [`mcp_manifest.json:9`](../../docs/mcp_manifest.json#L9)

- Verify registry versions, artifact URLs, and hashes point to v0.14.4.
  [`server.json:10`](../../server.json#L10)

**Release communication**

- Review the user-facing release note and comparison-link transition.
  [`CHANGELOG.md:10`](../../CHANGELOG.md#L10)
