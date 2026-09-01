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

**Problem:** `test_e2e_hierarchy_delete_parent_suite_with_children` exposed two production problems: `delete_suite` recursively scanned every project hierarchy even after its primary delete succeeded, and `list_test_suites` serially fetched each suite node while omitting child pages after the first 500 results. Those shared-tree reads caused timeouts under parallel E2E load.

**Approach:** Return immediately after a successful primary delete and use a targeted requested-suite lookup only when the delete API errors. Make full hierarchy traversal page-complete, bounded-concurrent, and retryable for transient failures. Keep every E2E assertion on public service or tool APIs rather than direct client calls.

## Boundaries & Constraints

**Always:** Keep the change scoped to hierarchy deletion/listing and directly supporting client parsing; retain real TestOps deletion coverage; use service APIs in E2E tests; distinguish an absent suite from a transient request failure.

**Ask First:** Expanding the change to product-service retry/timeout behavior or changing TestOps client defaults.

**Never:** Suppress a persistent transport/API error as a passing deletion; weaken the test to check only the parent; modify generated client code; alter remote TestOps configuration or cleanup policy.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| Cascaded parent deletion | Known parent and child suite names are removed asynchronously | Service lookup eventually reports that each uniquely named suite is absent | Poll until the existing deadline |
| Successful primary deletion | Tree-group delete returns successfully | Delete returns immediately | Do not inspect unrelated hierarchy nodes |
| Large hierarchy page | A parent has more than 500 children | List includes children from every page | Fetch subsequent pages before traversal |
| Transient tree read | A hierarchy request raises a transport exception or 5xx API error | Service retries a complete snapshot | Raise after bounded attempts |
| Raw non-success response | Tree-node endpoint returns 401, 404, or 500 JSON | Client raises its mapped typed exception | Never parse it as an empty node |
| Persistent non-absence | Suite still resolves as its own node | Test fails with its existing suite-specific message | Do not convert it to success |
| API-error fallback in a multi-tree project | Requested suite belongs to a non-default tree | Inspect only that node in each candidate tree, then delete its backing value | Propagate the original delete error if the suite cannot be located |

</frozen-after-approval>

## Code Map

- `tests/e2e/test_test_hierarchy_management.py` -- verifies deletion through the public hierarchy service.
- `src/services/test_hierarchy_service.py` -- contains targeted deletion fallback and bounded, page-complete hierarchy traversal.
- `src/client/client.py` -- preserves tree-node metadata and translates raw non-success responses into typed client exceptions.
- `tests/unit/test_client_facade_coverage.py` -- covers tree-node response parsing and typed non-success mappings.

## Tasks & Acceptance

**Execution:**
- [x] `src/services/test_hierarchy_service.py` and `tests/unit/test_test_hierarchy_service.py` -- return on primary delete success and use a requested-suite-only fallback after API errors -- prevents unrelated hierarchy traversal during deletion.
- [x] `src/services/test_hierarchy_service.py` and `tests/unit/test_test_hierarchy_service.py` -- fetch all child pages, cap concurrent tree reads, and retry transient snapshot failures -- makes `list_test_suites` complete and scalable.
- [x] `tests/e2e/test_test_hierarchy_management.py` -- verify deletion through `TestHierarchyService.resolve_suite_id_by_name` using run-unique names -- uses real service behavior without direct client calls.
- [x] `src/services/test_hierarchy_service.py` and `tests/e2e/test_test_hierarchy_management.py` -- use public, targeted suite reads for assignment verification -- keeps E2E coverage off raw client calls and away from shared-tree scans.
- [x] `src/client/client.py` and `tests/unit/test_client_facade_coverage.py` -- preserve tree-node backing-value metadata and validate raw response status mappings -- enables targeted fallback without false empty-node results.

**Acceptance Criteria:**
- Given a primary tree-group delete succeeds, when `delete_suite` completes, then it does not make list-tree, get-tree-node, or custom-field deletion calls.
- Given the primary delete API errors and the requested suite still has a backing custom-field value, when fallback runs, then it fetches only that suite and deletes that value.
- Given a hierarchy parent has multiple pages of children, when `list_test_suites` runs, then every group page contributes to the result.
- Given a parent suite with a nested suite and assigned test case, when the parent delete reports success, then the E2E verifies both uniquely named suites are absent through the hierarchy service.
- Given a raw non-success tree-node response, when the client facade receives it, then it raises the existing typed client exception rather than returning an empty node.
- Given a primary deletion API error for a suite in another tree, when fallback runs, then it checks that suite node in the relevant tree and never reports an unverified deletion as idempotent success.

## Design Notes

The full list tool must read every hierarchy group to render a complete tree, but it now limits concurrent child requests and preserves result order. Deletion must not initiate that scan after success. The E2E uses the public service's exact-name resolver with run-unique names, while separate coverage validates complete hierarchy listing.

## Verification

**Commands:**
- `uv run pytest tests/unit/test_test_hierarchy_service.py tests/e2e/test_test_hierarchy_management.py -q` -- expected: focused unit and hierarchy E2E coverage passes with configured TestOps credentials.
- `uv run --env-file .env.test pytest tests/e2e/test_test_hierarchy_management.py::test_e2e_hierarchy_delete_parent_suite_with_children -q` -- expected: the previously failing scenario passes without recursive tree-read timeouts.
- `uv run pytest tests/unit/test_client_facade_coverage.py -q` -- expected: tree-node status mappings pass.
- `uv run ruff check src/client/client.py tests/unit/test_client_facade_coverage.py tests/e2e/test_test_hierarchy_management.py` -- expected: no lint violations.

## Spec Change Log

- 2026-09-01: User rejected direct-client E2E polling. Replaced every direct-client E2E read with public service behavior and corrected the production deletion/listing paths that caused the timeout.

## Suggested Review Order

**Production deletion path**

- Return immediately after a successful tree-group delete; only API failures use the targeted fallback.
  [`test_hierarchy_service.py:127`](../../src/services/test_hierarchy_service.py#L127)

**Complete hierarchy listing**

- Retry transient snapshots and cap concurrent tree-node reads while preserving hierarchy order.
  [`test_hierarchy_service.py:71`](../../src/services/test_hierarchy_service.py#L71)

- Read every child page before building the resulting suite tree.
  [`test_hierarchy_service.py:231`](../../src/services/test_hierarchy_service.py#L231)

**Service-level verification**

- Poll deletion via the public hierarchy service and run-unique suite names.
  [`test_test_hierarchy_management.py:18`](../../tests/e2e/test_test_hierarchy_management.py#L18)

**Regression coverage**

- Verify targeted fallback and page-complete hierarchy output.
  [`test_test_hierarchy_service.py:270`](../../tests/unit/test_test_hierarchy_service.py#L270)
