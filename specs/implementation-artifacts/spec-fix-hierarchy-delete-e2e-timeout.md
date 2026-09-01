---
title: 'Make hierarchy deletion E2E verification resilient'
type: 'bugfix'
created: '2026-08-31'
status: 'done'
baseline_commit: 'd169108e6042e3f4759499d4406fe3268507b0cc'
context:
  - '{project-root}/docs/development.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `test_e2e_hierarchy_delete_parent_suite_with_children` intermittently fails after a successful deletion because its polling helper calls `list_test_suites`, which recursively fetches every suite in the shared TestOps tree. A read timeout in an unrelated branch aborts the poll before it can observe the two suites under test disappearing. The tree-node endpoint also returns persistent 500 responses for a just-deleted node, so it is not a reliable absence probe.

**Approach:** Verify deletion through the bounded suite-suggestion lookup using the test’s unique suite names, retrying transient transport and server failures during the eventual-consistency window. Validate raw tree-node response statuses in the client facade so non-success responses never appear as empty nodes.

## Boundaries & Constraints

**Always:** Keep the change scoped to hierarchy deletion and the directly supporting raw tree-node client validation; retain real TestOps deletion coverage; distinguish an absent suite from a transient request failure; preserve the current retry deadline and diagnostic assertions.

**Ask First:** Expanding the change to product-service retry/timeout behavior or changing TestOps client defaults.

**Never:** Suppress a persistent transport/API error as a passing deletion; weaken the test to check only the parent; modify generated client code; alter remote TestOps configuration or cleanup policy.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| Cascaded parent deletion | Known parent and child suite names are removed asynchronously | Each bounded lookup eventually reports that its uniquely named suite is absent | Poll until the existing deadline |
| Busy unrelated tree branch | A full hierarchy walk would time out | Deletion verification does not traverse unrelated suites | Avoid the full-tree listing entirely |
| Transient HTTP failure | A targeted lookup raises a transport exception or 5xx API error | Poll continues and can still observe deletion | Retry with the existing delay; fail at deadline if absence is never confirmed |
| Raw non-success response | Tree-node endpoint returns 401, 404, or 500 JSON | Client raises its mapped typed exception | Never parse it as an empty node |
| Persistent non-absence | Suite still resolves as its own node | Test fails with its existing suite-specific message | Do not convert it to success |

</frozen-after-approval>

## Code Map

- `tests/e2e/test_test_hierarchy_management.py` -- owns deletion lifecycle scenarios and the bounded absence-poll helper.
- `src/client/client.py` -- translates raw tree-node non-success responses into typed client exceptions before parsing.
- `tests/unit/test_client_facade_coverage.py` -- covers tree-node response parsing and typed non-success mappings.

## Tasks & Acceptance

**Execution:**
- [x] `tests/e2e/test_test_hierarchy_management.py` -- replace full-tree polling with a direct, exact-name-and-ID suite-suggestion lookup, retrying only transport and 5xx service failures -- removes dependence on unrelated hierarchy branches, repeated tree resolution, and the deleted-node endpoint while preserving cascade verification.
- [x] `tests/e2e/test_test_hierarchy_management.py` -- obtain the relevant tree once and pass it to parent and nested-suite absence checks -- avoids repeated tree discovery and makes the checked resource explicit.
- [x] `src/client/client.py` and `tests/unit/test_client_facade_coverage.py` -- validate raw tree-node response statuses and cover 401/404/500 mappings -- prevents non-success JSON from being misread as an absent suite.

**Acceptance Criteria:**
- Given a parent suite with a nested suite and assigned test case, when the parent delete reports success, then the E2E test independently verifies both uniquely named suites are absent without enumerating the full hierarchy.
- Given a transient transport or 5xx API failure during absence polling, when subsequent targeted lookups can complete, then the test retries and passes only after the requested suite is absent.
- Given a suite remains present through the retry deadline, when deletion verification ends, then the test fails rather than treating its transport history as success.
- Given a raw non-success tree-node response, when the client facade receives it, then it raises the existing typed client exception rather than returning an empty node.

## Design Notes

The direct suite-suggestion request uses the already resolved tree ID, an exact run-scoped name, and the suite ID created by the test. No matching ID/name pair proves the specific parent or nested suite is gone without reading unrelated branches, re-resolving the tree, or querying a deleted node. The E2E poll retries only transport failures and server-side 5xx responses; authentication, validation, and rate-limit failures remain visible. Raw tree-node response validation uses the client’s established exception mapping.

## Verification

**Commands:**
- `uv run pytest tests/unit/test_test_hierarchy_service.py tests/e2e/test_test_hierarchy_management.py -q` -- expected: focused unit and hierarchy E2E coverage passes with configured TestOps credentials.
- `uv run --env-file .env.test pytest tests/e2e/test_test_hierarchy_management.py::test_e2e_hierarchy_delete_parent_suite_with_children -q` -- expected: the previously failing scenario passes without recursive tree-read timeouts.
- `uv run pytest tests/unit/test_client_facade_coverage.py -q` -- expected: tree-node status mappings pass.
- `uv run ruff check src/client/client.py tests/unit/test_client_facade_coverage.py tests/e2e/test_test_hierarchy_management.py` -- expected: no lint violations.

## Suggested Review Order

**Deletion verification**

- Poll only the unique parent or child suite, never the complete shared hierarchy.
  [`test_test_hierarchy_management.py:22`](../../tests/e2e/test_test_hierarchy_management.py#L22)

- See the parent-cascade assertion use the resolved tree and original suite identities.
  [`test_test_hierarchy_management.py:323`](../../tests/e2e/test_test_hierarchy_management.py#L323)

**Raw API boundaries**

- Convert raw non-success tree-node responses into the facade's established typed errors.
  [`client.py:3620`](../../src/client/client.py#L3620)

**Regression coverage**

- Exercise success parsing and 401, 404, and 500 status mappings at the facade boundary.
  [`test_client_facade_coverage.py:291`](../../tests/unit/test_client_facade_coverage.py#L291)
