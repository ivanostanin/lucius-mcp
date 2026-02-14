# Story 7.2: Defect Lifecycle Management with Automation Rules

Status: review-ready

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **AI Agent**,
I want to **create, update, and track defects with automation rules**,
so that **test results can be automatically associated with defects based on error patterns, enabling streamlined defect triage and resolution tracking**.

## Acceptance Criteria

1.  **Create Defect:**
    *   **Given** a Project ID.
    *   **When** I call `create_defect(name, description=..., closed=...)`.
    *   **Then** a new Defect is created in Allure TestOps.
    *   **And** the tool returns the defect `id` and `name`.

2.  **Get Defect Details:**
    *   **Given** a valid Defect ID.
    *   **When** I call `get_defect(defect_id)`.
    *   **Then** the tool returns full defect details (id, name, description, closed status).

3.  **Update Defect:**
    *   **Given** an existing Defect ID.
    *   **When** I call `update_defect(defect_id, name=..., description=..., closed=...)`.
    *   **Then** the metadata is updated.

4.  **Delete Defect:**
    *   ⚠️ **Destructive**. Requires `confirm=True`.
    *   **Given** an existing Defect ID.
    *   **When** I call `delete_defect(defect_id, confirm=True)`.
    *   **Then** the defect is removed from Allure TestOps.
    *   **And** the tool returns a confirmation message.
    *   **And** the operation is idempotent.

5.  **List Defects:**
    *   **Given** a Project ID.
    *   **When** I call `list_defects(page=0, size=100)`.
    *   **Then** it returns a paginated list of defects with their IDs, names, and closed status.

6.  **Create Automation Rule (Defect Matcher):**
    *   **Given** a valid Defect ID.
    *   **When** I call `create_defect_matcher(defect_id, name, match_text)`.
    *   **Then** an automation rule (defect matcher) is created with a regex pattern for error messages.
    *   **And** the defect is automatically linked to future test results matching that pattern.

7.  **List Defect Matchers:**
    *   **Given** a valid Defect ID.
    *   **When** I call `list_defect_matchers(defect_id)`.
    *   **Then** it returns all automation rules associated with that defect.

8.  **Update Defect Matcher:**
    *   **Given** a valid Matcher ID.
    *   **When** I call `update_defect_matcher(matcher_id, name=..., match_text=...)`.
    *   **Then** the matcher rule is updated.

9.  **Delete Defect Matcher:**
    *   ⚠️ **Destructive**. Requires `confirm=True`.
    *   **Given** a valid Matcher ID.
    *   **When** I call `delete_defect_matcher(matcher_id, confirm=True)`.
    *   **Then** the matcher is removed.
    *   **And** the operation is idempotent.

10. **Agent-Proofing & Validation:**
    *   Inputs are validated before API calls.
    *   Missing required fields return descriptive error hints.
    *   All destructive tools (`delete_defect`, `delete_defect_matcher`) require `confirm=True`.

## Tasks / Subtasks

- [x] **0. Regenerate API Client** (Prerequisite)
  - [x] Add `"defect-controller"` and `"defect-matcher-controller"` to `KEEP_TAGS` in `scripts/filter_openapi.py`
  - [x] Run `scripts/generate_testops_api_client.sh` to regenerate the client
  - [x] Verify `DefectControllerApi` and `DefectMatcherControllerApi` appear in `src/client/generated/api/`

- [x] **1. Implement Defect Service** (AC 1-5)
  - [x] Create `src/services/defect_service.py`
  - [x] Implement `create_defect(name, description, closed)` → `DefectDto`
  - [x] Implement `get_defect(defect_id)` → `DefectDto`
  - [x] Implement `update_defect(defect_id, name, description, closed)` → `DefectDto`
  - [x] Implement `delete_defect(defect_id)` with idempotent 404 handling
  - [x] Implement `list_defects(page, size)` → `list[DefectRowDto]`
  - [x] **Constraint:** Business logic ONLY in service. Use Thin Tool / Fat Service pattern.

- [x] **2. Implement Defect Matcher Service** (AC 6-9)
  - [x] Add matcher methods in `src/services/defect_service.py` (same service)
  - [x] Implement `create_defect_matcher(defect_id, name, match_text)` → `DefectMatcherDto`
  - [x] Implement `list_defect_matchers(defect_id)` → `list[DefectMatcherDto]`
  - [x] Implement `update_defect_matcher(matcher_id, name, match_text)` → `DefectMatcherDto`
  - [x] Implement `delete_defect_matcher(matcher_id)` with idempotent 404 handling

- [x] **3. Implement MCP Tools** (AC 1-9)
  - [x] Create `src/tools/defects.py`
  - [x] `create_defect` tool — thin wrapper, detailed docstring
  - [x] `get_defect` tool 
  - [x] `update_defect` tool
  - [x] `delete_defect` tool — ⚠️ destructive, `confirm=True` safeguard
  - [x] `list_defects` tool
  - [x] `create_defect_matcher` tool
  - [x] `list_defect_matchers` tool
  - [x] `update_defect_matcher` tool
  - [x] `delete_defect_matcher` tool — ⚠️ destructive, `confirm=True` safeguard

- [x] **4. Register Tools** (AC 10)
  - [x] Add all defect tools to `src/tools/__init__.py` (imports, `__all__`, `all_tools`)
  - [x] Add to `deployment/mcpb/manifest.python.json` tools array (mark destructive with ⚠️ desc)
  - [x] Add to `deployment/mcpb/manifest.uv.json` tools array (same)

- [x] **5. Unit Tests**
  - [x] Create `tests/unit/test_defect_service.py`
  - [x] Mock `AllureClient` → `DefectControllerApi` and `DefectMatcherControllerApi`
  - [x] Test create, get, update, delete (including 404 idempotency), list defects
  - [x] Test create, list, update, delete matchers
  - [x] Test validation error handling (missing name, etc.)

- [x] **6. Integration Tests**
  - [x] Create `tests/integration/test_defect_tools.py`
  - [x] Mock service layer to test full tool stack
  - [x] Verify tool outputs match expected string formats
  - [x] Verify `confirm=True` gate on destructive tools

- [x] **7. E2E Tests**
  - [x] Create `tests/e2e/test_defect_management.py`
  - [x] Test full lifecycle: create → get → update → list → create matcher → list matchers → delete matcher → delete defect
  - [x] Add `track_defect(defect_id)` to `CleanupTracker` in `tests/e2e/helpers/cleanup.py`
  - [x] Use `delete_defect` with `confirm=True` for cleanup (per project convention)
  - [x] Add `DefectService` cleanup in `CleanupTracker.cleanup_all()`

- [x] **8. Update Agentic Workflow**
  - [x] Add scenario **11. Defect Lifecycle** to `tests/agentic/agentic-tool-calls-tests.md`
  - [x] Include tools: `create_defect`, `get_defect`, `update_defect`, `list_defects`, `delete_defect`, `create_defect_matcher`, `list_defect_matchers`, `update_defect_matcher`, `delete_defect_matcher`
  - [x] Add defect tools to **Tool inventory** and **Coverage matrix** sections
  - [x] Add defect tools to **Execution plan** section

- [x] **9. Update Documentation**
  - [x] Add **🐛 Defect Management** section to `docs/tools.md`
  - [x] Add **Defect Mgmt** row to `README.md` tool table
  - [x] Include all 9 defect tools with descriptions and key parameters

- [x] **10. Validation**
  - [x] Run the full test suite — 393 unit/integration tests pass


## Dev Notes

### Architecture Patterns (MUST FOLLOW)

- **Thin Tool / Fat Service:** `src/tools/defects.py` is a thin wrapper. All business logic in `src/services/defect_service.py`.
- **Async:** All service calls use `await`. Tools use `async with AllureClient.from_env() as client:`.
- **Error Handling:** Service catches `AllureNotFoundError` for idempotent deletes. Validation via `AllureValidationError`.
- **Destructive Tools:** `delete_defect` and `delete_defect_matcher` MUST implement the `confirm=True` safeguard pattern (see `src/tools/plans.py:delete_test_plan` or `src/tools/delete_test_case.py`).
- **Docstrings:** All tools MUST have Google-style docstrings with Args/Returns sections and clear purpose descriptions (see `src/tools/plans.py` for reference).

### Client Regeneration (CRITICAL)

The defect APIs are **NOT** currently available in the generated client because `defect-controller` and `defect-matcher-controller` are not in `KEEP_TAGS` in `scripts/filter_openapi.py`. 

**Steps to regenerate:**
1. Edit `scripts/filter_openapi.py` — add `"defect-controller"` and `"defect-matcher-controller"` to `KEEP_TAGS`
2. Run `scripts/generate_testops_api_client.sh`
3. Verify new API files appear in `src/client/generated/api/`:
   - `defect_controller_api.py` — CRUD for defects
   - `defect_matcher_controller_api.py` — CRUD for automation rules/matchers

### Available OpenAPI Endpoints (from spec)

| Endpoint                          | Methods        | Purpose                          |
|:----------------------------------|:---------------|:---------------------------------|
| `/api/defect`                     | GET, POST      | List/Create defects              |
| `/api/defect/{id}`                | GET, PATCH, DELETE | Get/Update/Delete defect      |
| `/api/defect/matcher`             | POST           | Create defect matcher            |
| `/api/defect/matcher/{id}`        | PATCH, DELETE  | Update/Delete matcher            |
| `/api/defect/{id}/matcher`        | GET            | List matchers for a defect       |

### Generated Models (already exist, will surface after regeneration)

- `DefectCreateDto` — name, description, closed fields
- `DefectDto` — full defect model
- `DefectPatchDto` — for partial updates
- `DefectRowDto` — for list responses (`PageDefectRowDto`)
- `DefectMatcherCreateDto` — name, match_text
- `DefectMatcherDto` — full matcher model
- `DefectMatcherPatchDto` — for matcher updates

### Source Tree Impact

| Component | Path | Action |
|:----------|:-----|:-------|
| OpenAPI filter | `scripts/filter_openapi.py` | **MODIFY** — add defect tags to `KEEP_TAGS` |
| Generated client | `src/client/generated/` | **REGENERATE** via script |
| Service | `src/services/defect_service.py` | **NEW** |
| Service init | `src/services/__init__.py` | **MODIFY** — export `DefectService` |
| Tools | `src/tools/defects.py` | **NEW** |
| Tools init | `src/tools/__init__.py` | **MODIFY** — register all defect tools |
| Manifest (python) | `deployment/mcpb/manifest.python.json` | **MODIFY** — add tool entries |
| Manifest (uv) | `deployment/mcpb/manifest.uv.json` | **MODIFY** — add tool entries |
| Unit tests | `tests/unit/test_defect_service.py` | **NEW** |
| Integration tests | `tests/integration/test_defect_tools.py` | **NEW** |
| E2E tests | `tests/e2e/test_defect_management.py` | **NEW** |
| E2E cleanup | `tests/e2e/helpers/cleanup.py` | **MODIFY** — add defect tracking/cleanup |
| Agentic tests | `tests/agentic/agentic-tool-calls-tests.md` | **MODIFY** — add scenario 11 |
| Docs tools | `docs/tools.md` | **MODIFY** — add Defect Management section |
| README | `README.md` | **MODIFY** — add Defect Mgmt row |

### Testing Standards

- `pytest` for all tests
- `respx` for mocking `httpx` in unit/integration tests
- Coverage > 85%
- E2E tests use `CleanupTracker` with `delete_defect(confirm=True)` for cleanup

### Previous Story Intelligence (7.1 + 7.3)

- **Review Note from 7.1:** Some DTO fields (like `description`, `tags`) may NOT be supported by the generated client DTOs. Always verify actual DTO fields after regeneration before implementing.
- **Pattern from 7.3:** Idempotent delete: wrap in `try/except AllureNotFoundError` and log info instead of raising.
- **Pattern from 7.3:** `confirm=True` safeguard must return a warning message when `confirm=False`, asking the agent to explicitly confirm.
- **Registration Pattern:** Tools must be added to `__init__.py` (import, `__all__`, `all_tools` list), both manifests, and agentic test file.

### Project Structure Notes

- New service file follows `plan_service.py` pattern exactly (constructor takes `AllureClient`, `_project_id` from `client.get_project()`, `_api` property returning the generated controller).
- New tool file follows `plans.py` pattern (each tool is a standalone async function with `Annotated` type hints).
- E2E test follows `test_plan_management.py` pattern (lifecycle test with `CleanupTracker`).

### References

- [Source: epics.md — Story 7.2](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/specs/project-planning-artifacts/epics.md#L483-L497)
- [Source: filter_openapi.py — KEEP_TAGS](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/scripts/filter_openapi.py#L8-L42)
- [Source: generate_testops_api_client.sh](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/scripts/generate_testops_api_client.sh)
- [Pattern: plans.py — tool implementation](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/src/tools/plans.py)
- [Pattern: plan_service.py — service implementation](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/src/services/plan_service.py)
- [Pattern: cleanup.py — E2E cleanup tracker](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/tests/e2e/helpers/cleanup.py)
- [Pattern: test_plan_management.py — E2E test](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/tests/e2e/test_plan_management.py)

## Dev Agent Record

### Agent Model Used

Antigravity (Google DeepMind)

### Debug Log References

- Searched `src/client/generated/api/` for defect controllers — none found.
- Confirmed `defect-controller` and `defect-matcher-controller` are OpenAPI spec tags not in `filter_openapi.py:KEEP_TAGS`.
- Verified OpenAPI spec has 13+ defect endpoints available.
- Verified generated models already exist (DefectDto, DefectCreateDto, etc.) because schema filtering is not aggressive.
- Analyzed 5 recent commits: latest is `feat/7-3-delete-test-plan` branch with delete_test_plan implementation.

### Completion Notes List

- Story created from Epic 7 / Story 7.2 in epics.md.
- Exhaustive analysis of project structure, patterns, and available APIs completed.
- Identified that client regeneration is required (defect APIs filtered out).
- Documented all 9 tools to implement with safeguard patterns.
- Included registration requirements for manifests, agentic workflow, and documentation.

### File List

- `scripts/filter_openapi.py` — **MODIFIED** (added defect tags to `KEEP_TAGS`)
- `src/client/generated/` — **REGENERATED** (includes defect APIs)
- `src/services/defect_service.py` — **NEW** (DefectService with 8 CRUD methods)
- `src/services/__init__.py` — **MODIFIED** (exports DefectService)
- `src/tools/defects.py` — **NEW** (9 MCP tool wrappers)
- `src/tools/__init__.py` — **MODIFIED** (registered all 9 defect tools)
- `tests/unit/test_defect_service.py` — **NEW** (16 unit tests)
- `tests/integration/test_defect_tools.py` — **NEW** (13 integration tests)
- `tests/e2e/test_defect_management.py` — **NEW** (2 E2E lifecycle tests)
- `tests/e2e/helpers/cleanup.py` — **MODIFIED** (added track_defect + defect cleanup)
- `tests/agentic/agentic-tool-calls-tests.md` — **MODIFIED** (added Section 11 + inventory/coverage)
- `docs/tools.md` — **MODIFIED** (added 🐛 Defect Management section)
- `deployment/mcpb/manifest.python.json` — **MODIFIED** (added defect tools)
- `deployment/mcpb/manifest.uv.json` — **MODIFIED** (added defect tools)
