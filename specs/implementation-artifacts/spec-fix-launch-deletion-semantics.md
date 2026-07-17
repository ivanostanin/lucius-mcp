---
title: 'Fix launch deletion semantics'
type: 'bugfix'
created: '2026-07-17'
status: 'done'
baseline_commit: 'bf78a09cdc519f6842588192b740b33409e49060'
context:
  - '{project-root}/docs/development.md'
  - '{project-root}/specs/project-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `delete_launch` reports that launches are archived and probes a launch before each deletion. TestOps has no archived-launch state: a second direct DELETE succeeds, while a GET for the deleted ID returns HTTP 500. The preflight GET therefore breaks idempotent deletion and the tool gives users inaccurate terminology.

**Approach:** Make the service delegate deletion directly to the TestOps DELETE endpoint, using only the endpoint response to determine its outcome. Report successful deletion using “deleted” terminology throughout the tool and shipped metadata, while preserving a clear already-deleted outcome when the endpoint explicitly returns 404.

## Boundaries & Constraints

**Always:** Keep tools thin and place deletion behavior in `LaunchService`; retain validation for project and launch IDs; use typed client exceptions; regenerate metadata derived from the tool signature/docstring; add focused unit, integration, and live-E2E coverage; update the manual agentic protocol so it never GETs a just-deleted launch.

**Ask First:** Expanding the correction to delete/archive semantics for entities other than launches, including historical test-case terminology or unrelated planning artifacts.

**Never:** Reintroduce a GET preflight to distinguish launch deletion states; label a launch as archived; infer an already-deleted state from an upstream 5xx; change the deferred authentication-response work in this PR.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| Delete existing launch | Valid launch ID; DELETE returns 204 | Service returns `deleted`; tool says `Deleted Launch <id>` without a launch name | N/A |
| Repeat deletion | Same ID; DELETE remains idempotent and returns 204 | Service and tool return the same `deleted` completion state; no GET is issued | N/A |
| Explicit absence | DELETE returns 404 | Service returns `already_deleted`; tool says the launch was already deleted or does not exist | No exception |
| Server failure | DELETE returns non-404 API error | Propagate the typed API error | Do not claim deletion succeeded |

</frozen-after-approval>

## Code Map

- `src/services/launch_service.py` -- owns launch deletion state and typed error handling.
- `src/tools/launches.py` -- exposes the MCP deletion tool and plain/JSON wording.
- `tests/unit/test_launch_service.py` -- service behavior and no-preflight contract.
- `tests/unit/test_launch_tools.py` and `tests/integration/test_launch_tools.py` -- rendered tool output contract.
- `tests/e2e/test_launches.py` -- TestOps lifecycle regression coverage.
- `tests/e2e/helpers/cleanup.py` -- teardown helper that must not read a deleted launch.
- `tests/agentic/agentic-tool-calls-tests.md` -- manual-agent deletion and cleanup protocol.
- `deployment/mcpb/manifest.*.json`, `src/cli/data/tool_schemas.json`, `docs/mcp_manifest.json` -- published tool metadata.

## Tasks & Acceptance

**Execution:**

- [x] `src/services/launch_service.py` -- remove the launch GET preflight; call DELETE directly, map only an explicit 404 to `already_deleted`, and use `deleted` for successful 204 responses -- aligns behavior with the TestOps endpoint and prevents reads of deleted IDs.
- [x] `src/tools/launches.py` -- change argument descriptions, docstring, text output, and JSON status to delete terminology; do not emit a deleted launch URL or name as confirmation -- makes the tool’s claims match the API contract.
- [x] `tests/unit/test_launch_service.py`, `tests/unit/test_launch_tools.py`, `tests/integration/test_launch_tools.py`, `tests/e2e/test_launches.py`, and `tests/e2e/helpers/cleanup.py` -- replace archive assertions, assert no GET during deletion, cover explicit DELETE 404, and verify two direct deletions -- protect the fixed behavior at each layer and teardown.
- [x] `tests/agentic/agentic-tool-calls-tests.md` -- exempt destructive operations from direct GET verification and add a launch-deletion cleanup step that relies on the delete confirmation -- prevents agents from probing a deleted launch.
- [x] `deployment/mcpb/manifest.python.json`, `deployment/mcpb/manifest.uv.json`, `src/cli/data/tool_schemas.json`, and `docs/mcp_manifest.json` -- synchronize user-facing generated metadata after the tool change -- prevents stale archive terminology in packaged clients.

**Acceptance Criteria:**

- Given a valid launch ID, when `delete_launch` is called, then the service calls the client DELETE exactly once and never calls GET.
- Given TestOps returns 204 for the same launch ID twice, when deletion is called twice, then both calls complete as `deleted` without a GET or 500 error.
- Given TestOps returns 404 to DELETE, when deletion is called, then the tool returns the idempotent already-deleted message without raising an error.
- Given TestOps returns another API error, when deletion is called, then the error propagates and the tool does not claim success.
- Given any launch deletion output or shipped launch-tool metadata, when inspected, then it refers to deletion and contains no archived-launch wording.
- Given the manual agentic test guide, when a launch is deleted, then its procedure does not call `get_launch` for that deleted ID.

### Review Findings

- [x] [Review][Patch] Missing JSON deletion-output coverage [tests/unit/test_launch_tools.py:310] — added JSON assertions for the deletion status and the absence of a launch name or URL in unit and integration coverage.

## Design Notes

The endpoint is already idempotent: the observed first and second direct DELETE requests both return 204. A preflight GET is therefore both unnecessary and unreliable; it also cannot safely distinguish a deleted launch because this TestOps instance responds with 500 rather than 404. A 204 confirms that TestOps accepted the requested deletion, so the tool reports `deleted`; only an explicit DELETE 404 produces `already_deleted`.

## Verification

**Commands:**

- `uv run pytest tests/unit/test_launch_service.py tests/unit/test_launch_tools.py tests/integration/test_launch_tools.py -q` -- expected: deletion semantics and rendered output pass.
- `uv run --env-file .env.test pytest tests/e2e/test_launches.py::test_create_close_reopen_launch_lifecycle -q` -- expected: two direct deletes pass against TestOps.
- `uv run ruff check src/services/launch_service.py src/tools/launches.py tests/unit/test_launch_service.py tests/unit/test_launch_tools.py tests/integration/test_launch_tools.py tests/e2e/test_launches.py` -- expected: no lint findings.
- `uv run mypy src` -- expected: no type errors.
- `uv run fastmcp inspect src/main.py --format mcp -o docs/mcp_manifest.json && uv run python scripts/build_tool_schema.py` -- expected: generated metadata contains delete-only launch wording.
