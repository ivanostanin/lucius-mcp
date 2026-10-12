---
title: 'Preserve expanded launch data after optional response schema errors'
type: 'bugfix'
created: '2026-10-12'
status: 'done'
baseline_commit: 'd5f8eceeec8c3b63514cdd5d753b13bff6046134'
context: []
---

<frozen-after-approval reason="user authorized issue reproduction, fix, and PR">

## Intent

**Problem:** Issue #435 reports that expanded `get_launch` aborts when optional member statistics contain a status outside the generated enum. The generated response parser raises Pydantic ValidationError, which escapes best-effort collection and can be reported by MCP as invalid caller parameters.

**Approach:** Handle response validation failures at existing optional read boundaries. Retain successfully collected launch fields, pages, trees, and branches; continue independent reads; return explicit sanitized completeness diagnostics.

## Boundaries & Constraints

**Always:** Preserve the authoritative core read as fatal. Keep selected-tree project validation fatal. Use fixed diagnostics without exception text, input, or raw response data. Preserve existing API-error reasons, pagination safeguards, deterministic ordering, and item-count semantics. Maintain the service-owned orchestration and thin-tool architecture.

**Ask First:** Any expansion into changing the upstream status contract or unrelated launch behavior.

**Never:** Edit generated models or enums, accept unknown statuses as valid data, catch arbitrary programming errors, or inspect/publish live user data to reproduce the synthetic failure.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Simple section | Optional response raises Pydantic ValidationError | Other sections continue; core and successful duplicate fields remain | Fixed upstream_schema_error with no status |
| First page | Optional page cannot deserialize | Empty section; subsequent optional reads continue | items_retrieved=0 |
| Later page | Earlier pages succeeded | Earlier items retained; failed section stops paging | Accurate collected count |
| Tree catalog or selection | Optional tree metadata cannot deserialize | Retain earlier catalog pages and process available trees | Safe trees diagnostic |
| Tree widget | Optional widget page cannot deserialize | Retain previous widget items and collect hierarchy | Safe widget diagnostic |
| Hierarchy | A page or child branch cannot deserialize | Retain successful nodes, sibling branches, and previous diagnostics | Safe branch diagnostic with existing count semantics |
| Core failure | Authoritative core response fails | Expanded call fails | Error propagates |
| Project mismatch | Explicit tree belongs to another project | Expanded call fails | Existing caller validation propagates |
| Programming error | Optional read raises unrelated exception | Call fails visibly | No broad exception handling |

</frozen-after-approval>

## Code Map

- `src/services/launch_service.py` -- launch aggregate, safe diagnostic helper, six optional read boundaries.
- `src/client/client.py` -- generated response calls escape Pydantic errors; no client changes required.
- `tests/unit/test_launch_service.py` -- existing launch fixtures and collector regression coverage.
- `tests/e2e/test_launches.py` -- controlled local HTTP upstream exercising the public tool through real deserialization and serialization.
- `specs/implementation-artifacts/12-4-extend-get-launch-info-with-complete-execution-results.md` -- existing authoritative-base and best-effort optional collection contract.

## Tasks & Acceptance

**Execution:**
- [x] `tests/e2e/test_launches.py` -- reproduce nested member-statistic enum failure using a synthetic local HTTP response; establish failing baseline.
- [x] `src/services/launch_service.py` -- classify Pydantic failures and catch them only in optional collectors; retain collected items and diagnostics.
- [x] `tests/unit/test_launch_service.py` -- test simple, paginated, tree, and fatal boundaries, sanitization, and preservation of previously collected data.
- [x] `tests/e2e/test_launches.py` -- validate successful serialized partial response after the fix, preserving earlier member-statistic pages and later sections.
- [x] `specs/implementation-artifacts/spec-gh-435-launch-schema-errors.md` -- record validation and review outcomes consistently with the final code.
- [x] `docs/tools.md` -- explain the fixed schema-error diagnostic and retained-data behavior.

**Acceptance Criteria:**
- Given the issue's synthetic malformed member-statistics response, when the public expanded launch tool runs against a controlled upstream, then the regression fails before the fix and returns a serialized partial launch afterward.
- Given successful core data and an optional schema failure, when collection completes, then consumers receive safe upstream_schema_error diagnostics and retained data without the offending synthetic status or exception inputs.
- Given existing valid or API-error scenarios, when launch collection runs, then existing behavior and public output schemas remain compatible.

## Spec Change Log

## Design Notes

Pydantic ValidationError is distinct from the application's AllureValidationError. Generated nested response parsing raises it directly, so widening existing optional catches is sufficient. The diagnostic helper must check the Pydantic type before accessing HTTP-status attributes. Hierarchy failures must also preserve already collected child-branch diagnostics when a later page fails. No new dependency, manifest, schema, or CLI route is required.

## Verification

**Commands:**
- `uv run pytest tests/e2e/test_launches.py -k controlled_later_page -q` -- controlled HTTP API and schema failures return preserved partial output after the fix; schema case fails on baseline.
- `uv run pytest tests/unit/test_launch_service.py tests/unit/test_launch_tools.py tests/integration/test_launch_client.py tests/integration/test_launch_tools.py -q` -- relevant launch regressions pass.
- `uv run ruff check .` -- project lint passes.
- `uv run ruff format --check .` -- project formatting passes.
- `uv run mypy --strict src/` -- source type checks pass.

Baseline reproduction: schema-error case failed with TestStatusCount ValidationError at status/type=enum; the existing API-error case passed. Only synthetic inputs were used.

Final validation: all 1,249 unit/integration/docs tests passed, all 26 packaging tests excluding compiled CLI binaries passed, and both controlled HTTP cases passed. Project-wide Ruff lint/format and strict mypy passed. Three independent reviewers found no actionable defects. Live TestOps E2E and compiled CLI tests were not run.

The controlled HTTP regression verifies basic reads succeed, earlier member-statistics pages survive, later result indexes are collected, and both JSON and plain output expose safe partial diagnostics. Its server backlog accommodates the aggregate's concurrent optional reads.

## Suggested Review Order

- Fixed diagnostics classify upstream schema failures without exposing invalid inputs.
  [launch_service.py:166](../../src/services/launch_service.py#L166)
- Optional collectors retain data while core failures remain outside the catches.
  [launch_service.py:573](../../src/services/launch_service.py#L573)
- Hierarchy failures preserve earlier sibling diagnostics.
  [launch_service.py:786](../../src/services/launch_service.py#L786)
- Boundary regressions cover pages, trees, fatal errors, and exact diagnostics.
  [test_launch_service.py:125](../../tests/unit/test_launch_service.py#L125)
- Controlled HTTP verifies generated deserialization and public JSON/plain responses.
  [test_launches.py:85](../../tests/e2e/test_launches.py#L85)
