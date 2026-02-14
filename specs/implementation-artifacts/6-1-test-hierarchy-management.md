# Story 6.1: Test Hierarchy Management

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want to create and manage test suites and tree structures,
so that I can organize tests into logical hierarchies for large repositories.

## Epic Context

- Epic 6 targets advanced organization/discovery for large repositories. [Source: specs/project-planning-artifacts/epics.md:431-434]
- Story 6.2 is done and explicitly treated hierarchy as a non-goal, so this story is the place to deliver hierarchy management. [Source: specs/implementation-artifacts/6-2-advanced-search-with-aql.md:15-17,31]

## Acceptance Criteria

1. Given a Project ID, when I call `create_test_suite` with a name and parent suite (if nested), then a new suite node is created in Allure TestOps hierarchy. [Source: specs/project-planning-artifacts/epics.md:443-446]
2. Given existing test cases and a target suite, when I assign test cases to the suite, then test cases are moved/attached to that suite path in the hierarchy. [Source: specs/project-planning-artifacts/epics.md:446] [Source: openapi/allure-testops-service/report-service.json:29541-29563]
3. Given a Project ID, when I call `list_test_suites`, then I receive the hierarchical suite/tree structure. [Source: specs/project-planning-artifacts/epics.md:447] [Source: openapi/allure-testops-service/report-service.json:28614-28732,29620-29735]
4. Invalid hierarchy targets (missing tree/suite/group identifiers) return actionable validation errors through global error handling (no raw JSON dumps from tools). [Source: specs/project-context.md:33-37,45-49]
5. Tool outputs are concise, LLM-friendly text and follow existing naming/style conventions. [Source: specs/project-context.md:45-54]
6. Implementation follows Thin Tool / Fat Service, async-only patterns, and does not manually edit generated client files. [Source: specs/project-context.md:25-31,58] [Source: src/client/generated/models/tree_dto_v2.py:11]
7. Existing test-layer workflows remain regression-safe (no breaking changes to `test_layer*` and `testlayerschema*` behavior). [Source: src/client/generated/README.md:255-265] [Source: tests/unit/test_test_layer_service.py:52-323]
8. Unit, integration, and E2E coverage is added for create/list/assign hierarchy flows. [Source: specs/project-context.md:68] [Source: tests/e2e/test_test_layer_crud.py:1-240]

## Tasks / Subtasks

- [x] Task 1: Expose hierarchy endpoints in generated client inputs (AC: 1, 2, 3, 7)
  - [x] Update `scripts/filter_openapi.py` to keep required tree-related tags (`test-case-tree-controller-v-2`, `tree-controller-v-2`, `test-case-tree-bulk-controller-v-2`) in addition to existing test-layer tags.
  - [x] Regenerate client using `scripts/generate_testops_api_client.sh` after filter updates.
  - [x] Confirm generated docs include required tree operations before service/tool implementation.

- [x] Task 2: Add client wrapper methods in `AllureClient` for hierarchy operations (AC: 1, 2, 3)
  - [x] Add wrappers for tree listing/retrieval (`/api/v2/tree`, `/api/v2/tree/{id}`).
  - [x] Add wrappers for suite-node operations (`addGroup`, `upsert`, `addLeaf`, `renameLeaf`, `getTreeNode`).
  - [x] Add wrapper for test-case assignment in hierarchy (`/api/v2/test-case/tree/bulk/drag-and-drop`).

- [x] Task 3: Implement service layer for hierarchy orchestration (AC: 1, 2, 3, 4, 6)
  - [x] Create `src/services/test_hierarchy_service.py`.
  - [x] Map story language (`suite`) to underlying tree/group/leaf API entities.
  - [x] Keep idempotent-safe behavior where possible and raise typed exceptions for global handling.

- [x] Task 4: Implement MCP tools for hierarchy management (AC: 1, 2, 3, 4, 5, 6)
  - [x] Add `create_test_suite` tool (nested support via parent identifier).
  - [x] Add `list_test_suites` tool (hierarchical output).
  - [x] Add assignment tool for placing test cases into suites (`assign_test_cases_to_suite` or equivalent naming aligned with tool inventory).
  - [x] Ensure tools remain thin wrappers without `try/except`.

- [x] Task 5: Add tests (AC: 7, 8)
  - [x] Unit tests for `TestHierarchyService` methods.
  - [x] Integration tests for tool output formatting and validation paths.
  - [x] E2E tests for create/list/assign flows against sandbox TestOps.
  - [x] Regression tests verifying existing test-layer tooling remains unchanged.

## Dev Notes

### Developer Context Section

- Epic wording uses “suites/trees”; current generated client surface in this repository is focused on `test-layer` and `test-layer-schema` controllers plus bulk endpoints. This story must bridge that gap safely. [Source: specs/project-planning-artifacts/epics.md:435-447] [Source: src/client/generated/README.md:255-265,208,212]
- The source OpenAPI includes full tree endpoints needed for hierarchy management, but current filtering excludes their controller tags from generated APIs. [Source: openapi/allure-testops-service/report-service.json:28177-28732,29620-29735] [Source: scripts/filter_openapi.py:8-39]

### Technical Requirements

- Use these endpoint families for hierarchy features:
  - Tree catalog: `GET /api/v2/tree`, `GET /api/v2/tree/{id}`. [Source: openapi/allure-testops-service/report-service.json:29620-29735]
  - Tree node management: `POST/PUT /api/v2/project/{projectId}/test-case/tree/group`, `POST /api/v2/project/{projectId}/test-case/tree/leaf`, `PUT /api/v2/project/{projectId}/test-case/tree/leaf/{leafId}/name`, `GET /api/v2/project/{projectId}/test-case/tree/tree-node`. [Source: openapi/allure-testops-service/report-service.json:28177-28732]
  - Assignment/move operation: `POST /api/v2/test-case/tree/bulk/drag-and-drop`. [Source: openapi/allure-testops-service/report-service.json:29541-29563]
- Keep existing test-layer APIs intact and avoid conflating test-layer taxonomy CRUD with suite hierarchy CRUD. [Source: src/client/generated/README.md:255-265] [Source: src/services/test_layer_service.py:11-183]

### Architecture Compliance

- Enforce Thin Tool / Fat Service: business logic in services, tools only validate/dispatch/format. [Source: specs/project-context.md:25-31]
- Do not add `try/except` in tools; rely on global exception handling and typed service exceptions. [Source: specs/project-context.md:33-37]
- Do not manually edit files under `src/client/generated/`; regenerate instead. [Source: specs/project-context.md:58] [Source: src/client/generated/models/tree_dto_v2.py:11]
- Keep async-only flows and existing project boundaries (`src/tools`, `src/services`, `src/client`). [Source: specs/project-context.md:55-67]

### Library / Framework Requirements

- Python 3.14 + `uv`, Starlette/FastMCP, Pydantic v2 strict, async httpx stack. [Source: specs/project-context.md:15-21]
- Client generation pipeline uses filtered spec (`filtered-report-service.json`) via OpenAPI generator config. [Source: scripts/openapi-generator-config.yaml:1-5] [Source: scripts/generate_testops_api_client.sh:7-16]
- Current generated models indicate OpenAPI document version `25.4.1`; remain compatible with that contract. [Source: src/client/generated/models/tree_dto_v2.py:8]

### File Structure Requirements

- Expected implementation touchpoints:
  - `scripts/filter_openapi.py`
  - `src/client/client.py`
  - `src/services/test_hierarchy_service.py` (new)
  - `src/tools/create_test_suite.py` (new)
  - `src/tools/list_test_suites.py` (new)
  - `src/tools/assign_test_cases_to_suite.py` (new, or aligned equivalent)
  - `src/tools/__init__.py`
  - `tests/unit/test_test_hierarchy_service.py` (new)
  - `tests/integration/test_test_hierarchy_tools.py` (new)
  - `tests/e2e/test_test_hierarchy_management.py` (new)

### Testing Requirements

- Run unit/integration suite:
  - `uv run --env-file .env.test pytest tests/unit/ tests/integration/`
- Run E2E hierarchy tests:
  - `uv run --env-file .env.test pytest tests/e2e/`
  - If full E2E run finds failures, rerun only failing E2E tests individually.
- Ensure regressions do not break existing search and test-layer workflows.

### Previous Story Intelligence

- Story 6.2 already delivered AQL enhancements and explicitly deferred hierarchy concerns; implement hierarchy here without regressing AQL behavior. [Source: specs/implementation-artifacts/6-2-advanced-search-with-aql.md:15-17,30-33]

### Latest Technical Information

- No external dependency upgrade is required for this story; repository OpenAPI/client generation artifacts already define current API contracts to implement against. [Source: src/client/generated/models/tree_dto_v2.py:8] [Source: scripts/openapi-generator-config.yaml:1-5]

### Project Context Reference

- Story implementation must honor project guardrails in `specs/project-context.md`, especially tool/service separation, error handling strategy, and file boundaries. [Source: specs/project-context.md:25-62]

### Story Completion Status

- Status: review
- Completion note: Implementation complete with hierarchy client wrappers, service/tool delivery, and full test validation.

### Project Structure Notes

- Alignment with unified project structure (paths, modules, naming):
  - New business logic should be in `src/services/`; tool entrypoints in `src/tools/`; generated API code only via regeneration scripts. [Source: specs/project-context.md:55-62] [Source: scripts/generate_testops_api_client.sh:7-20]
- Detected conflicts or variances (with rationale):
  - Epic API names (`create_test_suite`, `list_test_suites`) are not currently present in generated client due OpenAPI filtering choices; implementation should map these tools to existing tree endpoints after expanding filter tags. [Source: specs/project-planning-artifacts/epics.md:444-447] [Source: scripts/filter_openapi.py:8-39] [Source: openapi/allure-testops-service/report-service.json:28177-28732,29620-29735]

### References

- [Source: specs/project-planning-artifacts/epics.md:431-447]
- [Source: specs/implementation-artifacts/sprint-status.yaml:96-100]
- [Source: specs/implementation-artifacts/6-2-advanced-search-with-aql.md:15-17,30-33]
- [Source: specs/project-context.md:15-21,25-37,45-62,68]
- [Source: scripts/filter_openapi.py:8-39]
- [Source: scripts/generate_testops_api_client.sh:7-20]
- [Source: scripts/openapi-generator-config.yaml:1-5]
- [Source: openapi/allure-testops-service/report-service.json:28177-28732,29541-29563,29620-29735]
- [Source: src/client/generated/README.md:151,208,212,255-265]
- [Source: src/client/client.py:42-43,271-272,418-419]
- [Source: src/client/generated/models/tree_dto_v2.py:8,11]
- [Source: src/client/generated/models/page_tree_dto_v2.py:28-43]
- [Source: src/client/generated/models/test_case_tree_selection_dto_v2.py:25-39]
- [Source: src/client/generated/models/test_case_bulk_drag_and_drop_dto_v2.py:26-33]
- [Source: src/services/test_layer_service.py:11-183]
- [Source: tests/unit/test_test_layer_service.py:52-323]

## Dev Agent Record

### Agent Model Used

gpt-5.3-codex

### Debug Log References

- Added hierarchy controller tags to OpenAPI filter and regenerated client artifacts.
- Implemented and validated hierarchy wrappers in `AllureClient` using generated APIs.
- Implemented `TestHierarchyService` for create/list/assign suite operations with typed validation.
- Added hierarchy tools and registrations in tools exports/grouping.
- Added new unit/integration/e2e tests for hierarchy flows.
- Fixed assignment flow semantics to move test-case leaf nodes into requested suite node (AC2 compliance).
- Added E2E verification that assigned test cases appear under the target suite node.
- Executed full unit/integration and full e2e suites successfully.

### Completion Notes List

- Delivered Story 6.1 end-to-end: OpenAPI filtering, regenerated client APIs, wrappers, service, tools, and tests.
- `create_test_suite`, `list_test_suites`, and `assign_test_cases_to_suite` are implemented with concise tool outputs and typed validation errors.
- Preserved Thin Tool / Fat Service architecture and async-only patterns; no manual edits in generated model files.
- Verified regressions: existing test-layer workflows remain passing.
- Test results:
  - `uv run --env-file .env.test pytest tests/unit/ tests/integration/` → 362 passed
  - `uv run --env-file .env.test pytest tests/e2e/ -n auto --dist loadfile` → 91 passed, 1 skipped
  - `uv run --env-file .env.test pytest tests/e2e/test_test_hierarchy_management.py` → 3 passed
  - `uv run --env-file .env.test pytest tests/unit/test_test_hierarchy_service.py tests/integration/test_test_hierarchy_tools.py tests/e2e/test_test_hierarchy_management.py tests/unit/test_test_layer_service.py` → 37 passed
  - `./scripts/full-test-suite.sh` → unit/integration/docs/packaging passed; one parallel e2e run had transient 500s, and all three failing tests passed when re-run individually

### File List

- scripts/filter_openapi.py
- openapi/allure-testops-service/filtered-report-service.json
- src/client/client.py
- src/client/generated/README.md
- src/client/generated/__init__.py
- src/client/generated/api/__init__.py
- src/client/generated/api/tree_controller_v2_api.py
- src/client/generated/api/test_case_tree_controller_v2_api.py
- src/client/generated/api/test_case_tree_bulk_controller_v2_api.py
- src/client/generated/docs/TreeControllerV2Api.md
- src/client/generated/docs/TestCaseTreeControllerV2Api.md
- src/client/generated/docs/TestCaseTreeBulkControllerV2Api.md
- src/services/test_hierarchy_service.py
- src/services/__init__.py
- src/tools/create_test_suite.py
- src/tools/list_test_suites.py
- src/tools/assign_test_cases_to_suite.py
- src/tools/test_layers.py
- src/tools/__init__.py
- tests/unit/test_test_hierarchy_service.py
- tests/integration/test_test_hierarchy_tools.py
- tests/e2e/test_test_hierarchy_management.py
- specs/implementation-artifacts/6-1-test-hierarchy-management.md
- specs/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-02-14: Implemented Story 6.1 hierarchy management end-to-end and moved status to review.
