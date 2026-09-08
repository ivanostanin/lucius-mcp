---
title: 'Align E2E tests with MCP 2.x'
type: 'bugfix'
created: '2026-09-08'
status: 'done'
baseline_commit: 'e0f3bc028a7c07198f32b93859abf955825a57c8'
context: ['{project-root}/docs/development.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The dependency update on `main` upgraded FastMCP/MCP to 4.0.2/2.1.1, and the full validation suite now fails because telemetry E2E tests reference the removed `CallToolResult.isError` field. HTTP lifecycle E2E tests also treat the MCP 2.x response to an intentionally incomplete readiness GET (`400 Bad Request`) as a startup failure, even though the server is listening and fully initialized.

**Approach:** Update only the affected E2E expectations to match the installed MCP 2.x client model and streamable HTTP behavior. Keep production code, dependency versions, test intent, and release workflow unchanged.

## Boundaries & Constraints

**Always:** Use the current `CallToolResult.is_error` field; keep telemetry success/error assertions semantically identical; treat an explicit HTTP 400 from `/mcp` as a reachable server response; follow the repository's `uv`-based validation commands.

**Ask First:** No additional design decisions are required unless validation reveals a production-code or dependency-resolution issue.

**Never:** Do not add a compatibility shim to production code, roll back the MCP dependency upgrade, weaken telemetry payload assertions, accept connection failures as readiness, or merge the resulting PR.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| MCP_RESULT_SUCCESS | MCP 2.x `CallToolResult` with `is_error=False` | Telemetry success test passes using `is_error` | Assertion failure indicates an incompatible client contract |
| MCP_RESULT_ERROR | MCP 2.x `CallToolResult` with `is_error=True` | Telemetry error test still verifies the validation event | Preserve the existing event and payload assertions |
| HTTP_READY_WITH_400 | Running `/mcp` endpoint returns HTTP 400 to incomplete GET | Readiness helper returns successfully | Continue polling only on connection failures |
| HTTP_NOT_READY | Port is closed or request cannot connect | Readiness helper keeps polling until timeout | Raise the existing startup timeout error |

</frozen-after-approval>

## Code Map

- `tests/e2e/test_telemetry_collection_e2e.py` -- Assertions for MCP tool-call success and error results during telemetry collection.
- `tests/e2e/test_mcp_server_lifecycle.py` -- Shared HTTP server readiness probe used by source and unpacked-bundle lifecycle tests.
- `src/utils/telemetry.py` -- Existing production telemetry wrapper using the MCP 2.x `is_error` field; reference only, no change expected.

## Tasks & Acceptance

**Execution:**
- [x] `tests/e2e/test_telemetry_collection_e2e.py` -- Replace the three `isError` assertions with `is_error` while preserving their boolean expectations -- align tests with MCP 2.1.1 without changing coverage intent.
- [x] `tests/e2e/test_mcp_server_lifecycle.py` -- Add HTTP 400 to the explicit readiness response set, document why it is valid for an incomplete MCP 2.x GET, and update both streamable HTTP client unpacking sites to the MCP 2.x two-value API -- prevent false startup and client-protocol failures while retaining connection-failure detection.
- [x] Both E2E modules -- Run focused serial validation, then the available safe validation checks -- prove the compatibility fixes resolve the identified release blocker.

**Acceptance Criteria:**
- Given MCP 2.1.1 is installed, when telemetry E2E tests call tools, then success and validation-error results are evaluated through `is_error` and the existing telemetry payload assertions remain active.
- Given the MCP HTTP server is listening, when the readiness probe receives HTTP 400 for its incomplete GET request, then the helper treats the server as ready.
- Given the server is not reachable, when the readiness probe cannot connect, then it continues polling and eventually raises the existing timeout error.
- Given the fixes are applied, when the focused E2E tests and `./scripts/full-test-suite.sh` run, then all required tests pass.

## Spec Change Log

## Verification

**Commands:**
- `uv run --extra dev --env-file .env.test pytest tests/e2e/test_telemetry_collection_e2e.py tests/e2e/test_mcp_server_lifecycle.py -q -n 0 -rs` -- expected: focused tests pass or only documented environment skips remain.
- `./scripts/full-test-suite.sh` -- expected: formatting, linting, type checks, unit/integration/docs/E2E/packaging checks all pass.

## Suggested Review Order

**MCP HTTP readiness**

- The readiness probe recognizes MCP 2.x’s valid incomplete-request response.
  [`test_mcp_server_lifecycle.py:150`](../../tests/e2e/test_mcp_server_lifecycle.py#L150)

- Both HTTP lifecycle paths now consume the MCP 2.x client stream shape.
  [`test_mcp_server_lifecycle.py:279`](../../tests/e2e/test_mcp_server_lifecycle.py#L279)

- The unpacked Python bundle follows the same updated streamable HTTP contract.
  [`test_mcp_server_lifecycle.py:301`](../../tests/e2e/test_mcp_server_lifecycle.py#L301)

**Telemetry result contract**

- Success and validation-error assertions use the current MCP result field.
  [`test_telemetry_collection_e2e.py:167`](../../tests/e2e/test_telemetry_collection_e2e.py#L167)

- The opt-out path validates the same current result contract.
  [`test_telemetry_collection_e2e.py:220`](../../tests/e2e/test_telemetry_collection_e2e.py#L220)
