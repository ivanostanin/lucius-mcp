---
title: 'Use generated typed deserialization for hierarchy tree nodes'
type: 'bugfix'
created: '2026-09-01'
status: 'done'
baseline_commit: '3caeede01d6de59fdb2c9a113bc92e9e009fa8cc'
context:
  - '{project-root}/docs/development.md'
  - '{project-root}/specs/project-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `AllureClient.get_tree_node` bypasses the generated typed API method and manually parses a raw HTTP response because the upstream hierarchy schema does not discriminate group and leaf children. This direct call duplicates client deserialization logic and leaves the hierarchy implementation dependent on a fragile local workaround.

**Approach:** Correct the maintained OpenAPI filtering overlay so the named hierarchy base node maps wire values `GROUP` and `LEAF` to concrete generated models, make page content refer to that node type, regenerate the client, and call the generated `get_tree_node` method through normal exception handling.

## Boundaries & Constraints

**Always:** Keep the OpenAPI source-of-truth in `scripts/filter_openapi.py`; preserve concrete group/leaf model values for hierarchy services; use the generated typed endpoint in the facade; adapt service traversal to consume direct typed page items; test mixed group/leaf payloads, HTTP error translation, and the existing hierarchy workflows.

**Ask First:** Changing TestOps endpoint semantics, broadening this migration to other raw-response facade methods, or accepting a generated-client representation that cannot distinguish `GROUP` from `LEAF` safely.

**Never:** Hand-edit generated files as the durable fix; retain a hierarchy-specific raw response parser; change E2E tests to call client, service, generated, or raw API methods directly; weaken pagination, deletion, or parallel-isolation coverage.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| Mixed tree page | Generated endpoint returns `GROUP` and `LEAF` children | Page content contains typed `TestCaseLightTreeNodeDto` and `TestCaseTreeLeafDtoV2` instances directly | Fail contract test if the discriminator mapping is ambiguous |
| Node root | Response includes group metadata and children | Generated `TestCaseFullTreeNodeDto` preserves ID, name, parent, custom-field value, and children | Normal Pydantic/generated validation applies |
| API failure | Generated endpoint returns 401, 404, or 5xx | Facade maps it to existing `Allure*` exception types | No raw-response-specific error path |
| Regeneration | Filtered spec is rebuilt from upstream source | Overlay is reapplied and regenerated client remains reproducible | Test generated output rather than patching it manually |

</frozen-after-approval>

## Code Map

- `scripts/filter_openapi.py` -- durable contract overlay applied before every generated-client build.
- `openapi/allure-testops-service/filtered-report-service.json` -- regenerated filtered OpenAPI contract.
- `src/client/generated/` -- generated typed endpoint and hierarchy models; modified only by the repository generator.
- `src/client/client.py` -- facade delegates `get_tree_node` to the generated endpoint and standard exception mapper.
- `src/services/test_hierarchy_service.py` -- traverses direct typed generated page items instead of wrapper envelopes.
- `tests/unit/test_client_facade_coverage.py` -- validates typed hierarchy child deserialization and error mapping.
- `tests/unit/test_test_hierarchy_service.py` and `tests/e2e/test_test_hierarchy_management.py` -- retain service and public-tool regression coverage.

## Tasks & Acceptance

**Execution:**

- [x] `scripts/filter_openapi.py` -- add an idempotent hierarchy-schema overlay that maps `GROUP` and `LEAF` to concrete schemas on `TestCaseTreeNodeDto`, makes page items reference that named discriminated schema, and adds required root metadata missing upstream -- makes regeneration own the response contract.
- [x] `openapi/allure-testops-service/filtered-report-service.json` and `src/client/generated/` -- run the repository generator, inspect the generated one-of model, and retain only generated changes attributable to the overlay -- keeps the fix reproducible.
- [x] `src/client/client.py` -- replace the raw `get_tree_node_without_preload_content` call and manual tree-child parser with the typed generated `get_tree_node` call via `_call_api` -- eliminates the direct hierarchy API workaround.
- [x] `src/services/test_hierarchy_service.py` and `tests/unit/test_test_hierarchy_service.py` -- consume direct typed page items rather than `actual_instance` wrapper envelopes and retain bounded traversal coverage -- keeps hierarchy behavior aligned with the regenerated contract.
- [x] `tests/unit/test_client_facade_coverage.py` -- replace raw-response fixtures with typed generated-endpoint fixtures; assert mixed group/leaf types, forwarded arguments, and existing mapped errors -- protects the client boundary.
- [x] `tests/unit/test_test_hierarchy_service.py` and `tests/e2e/test_test_hierarchy_management.py` -- run existing focused service and tool-only E2E checks without adding direct client access -- protects end-user hierarchy behavior and parallel independence.

**Acceptance Criteria:**

- Given a generated tree-node response with group and leaf children, when `AllureClient.get_tree_node` is called, then page content holds the correct concrete generated models directly and no manual payload parsing occurs.
- Given a non-success tree-node response, when the facade invokes the generated endpoint, then the existing `AllureAuthError`, `AllureNotFoundError`, or `AllureAPIError` mapping is preserved.
- Given the filtered OpenAPI spec is regenerated, when generated artifacts are recreated, then no manual source edit is needed to restore typed hierarchy deserialization.
- Given the hierarchy E2Es run with multiple workers, when they use hierarchy reads and deletion verification, then all calls remain through registered tools and the suite stays independent.

## Spec Change Log

- 2026-09-01: Edge-case review found that generated leaves can omit `testCaseId`, whereas the removed parser used the leaf node ID as a fallback. Restored that compatibility rule in the hierarchy service and added regression coverage, avoiding lost assignment or suite-content IDs without restoring raw response parsing.

## Design Notes

The upstream contract already carries `type` values (`GROUP` and `LEAF`) but its named base-node discriminator maps class names rather than those wire values. An inline child-union discriminator does not affect the pinned generator. The overlay therefore makes page items reference the corrected named base schema, allowing generated deserialization to produce concrete group and leaf instances. The facade remains responsible only for argument validation and mapping generated-client exceptions to the project’s error types.

## Verification

**Commands:**

- `uv run python scripts/filter_openapi.py && ./scripts/generate_testops_api_client.sh` -- expected: generated hierarchy models expose a discriminator-aware child union.
- `uv run ruff check scripts/filter_openapi.py src/client/client.py tests/unit/test_client_facade_coverage.py` -- expected: no lint violations.
- `uv run mypy src/client/client.py` -- expected: no type errors.
- `uv run pytest tests/unit/test_client_facade_coverage.py tests/unit/test_test_hierarchy_service.py -q` -- expected: typed facade and hierarchy service contracts pass.
- `uv run --env-file .env.test pytest tests/e2e/test_test_hierarchy_management.py -n 5 --dist load -q` -- expected: five public-tool workflows pass safely in parallel.

## Suggested Review Order

**Schema-owned polymorphism**

- Corrects upstream wire discriminator values before source generation.
  [`filter_openapi.py:172`](../../scripts/filter_openapi.py#L172)

- Generated page content now dispatches directly to concrete node models.
  [`page_test_case_tree_node_dto.py:29`](../../src/client/generated/models/page_test_case_tree_node_dto.py#L29)

**Facade and hierarchy behavior**

- Uses the generated operation and standard project error mapping.
  [`client.py:3589`](../../src/client/client.py#L3589)

- Traverses direct generated node types without wrapper-specific branching.
  [`test_hierarchy_service.py:271`](../../src/services/test_hierarchy_service.py#L271)

- Retains leaf-ID compatibility without reverting raw response parsing.
  [`test_hierarchy_service.py:539`](../../src/services/test_hierarchy_service.py#L539)

**Regression coverage**

- Exercises generated JSON model dispatch and facade argument forwarding.
  [`test_client_facade_coverage.py:273`](../../tests/unit/test_client_facade_coverage.py#L273)

- Locks in the legacy leaf-ID fallback.
  [`test_test_hierarchy_service.py:198`](../../tests/unit/test_test_hierarchy_service.py#L198)
