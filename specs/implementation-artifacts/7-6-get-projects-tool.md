# Story 7.6: Get Projects Tool

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **AI Agent**,
I want to **retrieve project details by name**,
so that **I can resolve a human-readable project name to its numeric ID for subsequent API calls**.

## Acceptance Criteria

1.  **Get Project by Name:**
    *   **Given** a project name (e.g., "Lucius MCP").
    *   **When** I call `get_project(name="Lucius MCP")`.
    *   **Then** the tool returns the Project details (ID, Name, Description, etc.).
    *   **And** the search is case-insensitive.

2.  **Ambiguity Handling:**
    *   **Given** multiple projects matching the name (unlikely if unique, but possible with partial matching).
    *   **Then** the tool returns the exact match if one exists.
    *   **Or** returns a clear error/list if multiple candidates are found.

3.  **Error Handling:**
    *   **Given** a non-existent project name.
    *   **When** I call the tool.
    *   **Then** it returns a clear "Project not found" message.

4.  **List Projects (Optional/Fallback):**
    *   **When** I call `get_project` without arguments (or a separate `list_projects` if preferred).
    *   **Then** it returns a straightforward list of available projects (ID + Name) to help the agent discover the correct name.

## Tasks / Subtasks

- [x] **0. Regenerate API Client** (Prerequisite)
  - [x] Check `src/client/generated/api` for `ProjectController` endpoints.
  - [x] Ensure `ProjectController` is included in `scripts/filter_openapi.py`.
  - [x] Run `scripts/generate_testops_api_client.sh`.

- [x] **1. Implement Service Layer** (AC 1-3)
  - [x] Create/Update `src/services/project_service.py`.
  - [x] Implement `get_project_by_name(name: str) -> Project`.
  - [x] Implement `list_projects() -> list[Project]`.
  - [x] Logic: Fetch all projects (or search if API supports), then filter by name locally if needed. *Dev Note: TestOps API usually has `findAll`.*

- [x] **2. Implement MCP Tool** (AC 1-4)
  - [x] Create `src/tools/projects.py`.
  - [x] Add `get_project(name: str | None = None)`.
  - [x] If `name` is provided, return specific project.
  - [x] If `name` is None, return list of all projects (summary).
  - [x] Add docstrings.

- [x] **3. Register Tool**
  - [x] Update `src/tools/__init__.py`.
  - [x] Update `deployment/mcpb/manifest.python.json`.
  - [x] Update `deployment/mcpb/manifest.uv.json`.

- [x] **4. Unit Tests**
  - [x] Create `tests/unit/test_project_service.py`.
  - [x] Test case-insensitive matching.
  - [x] Test "not found" scenario.

- [x] **5. Integration Tests**
  - [x] Create `tests/integration/test_project_tools.py`.
  - [x] Mock API response with list of projects.
  - [x] Verify tool logic.

- [x] **6. E2E Tests**
  - [x] Create `tests/e2e/test_project_discovery.py`.
  - [x] Scenario: Authenticate -> List Projects -> Get Specific Project by Name -> Verify ID matches.

- [x] **7. Update Agentic Workflow**
  - [x] Add scenario **Project Discovery** to `tests/agentic/agentic-tool-calls-tests.md`.
  - [x] Include tools: `get_project`.
  - [x] Update **Tool inventory** and **Coverage matrix** sections.
  - [x] Update **Execution plan** section.

- [x] **8. Update Documentation**
  - [x] Update `docs/tools.md` (New "Project Management" or "General" section).
  - [x] Update `README.md`.

- [x] **9. Validation**
  - [x] Run full test suite: `./scripts/full-test-suite.sh`

## Dev Notes

### Architecture Patterns (MUST FOLLOW)

- **Thin Tool / Fat Service:** Logic in `ProjectService`.
- **Caching:** Projects rarely change. Consider `@lru_cache` for `list_projects` in the service if performance is an issue, but standard API call is fine for now.
- **API Specifics:** Check `ProjectController` -> `findAll`. This likely returns all projects the user has access to.

### Source Tree Impact

| Component | Path | Action |
|:----------|:-----|:-------|
| OpenAPI filter | `scripts/filter_openapi.py` | **CHECK/MODIFY** |
| Generated client | `src/client/generated/` | **REGENERATE** |
| Service | `src/services/project_service.py` | **NEW** |
| Tool | `src/tools/projects.py` | **NEW** |
| Manifests | `deployment/mcpb/manifest.*.json` | **MODIFY** |
| Unit Tests | `tests/unit/test_project_service.py` | **NEW** |
| E2E Tests | `tests/e2e/test_project_discovery.py` | **NEW** |
| Agentic Tests | `tests/agentic/agentic-tool-calls-tests.md` | **MODIFY** |

### Testing Standards

- **Coverage:** > 85%.

### Dev Agent Record

### Agent Model Used

Antigravity (Google DeepMind)

### Completion Notes List
- Story created and pre-enhanced with full technical details.
- Implemented `ProjectService` with paginated discovery, case-insensitive exact-name preference, unambiguous partial matching, and clear ambiguity/not-found errors.
- Added the read-only `get_project` MCP tool with structured project details or a concise ID/name list, including manifest, schema, annotation, documentation, and agentic workflow registration.
- Added unit, integration, and E2E coverage. Focused project-service coverage is 95%; the final full suite passed with 964 unit/integration tests, 24 documentation tests, and 90.58% overall coverage.

### File List

- README.md
- deployment/mcpb/manifest.python.json
- deployment/mcpb/manifest.uv.json
- docs/mcp_manifest.json
- docs/tools.md
- src/services/__init__.py
- src/services/project_service.py
- src/tools/__init__.py
- src/tools/annotations.py
- src/tools/output_schemas.py
- src/tools/projects.py
- tests/agentic/agentic-tool-calls-tests.md
- tests/e2e/test_project_discovery.py
- tests/integration/test_project_tools.py
- tests/unit/test_project_service.py

### Change Log

- 2026-07-21: Implemented project discovery and registered the `get_project` MCP tool with tests and documentation.

### Review Findings

- [x] [Review][Patch] Allow project discovery without a configured default project [src/client/client.py:364-391] — `get_project()` now uses the opt-in projectless client mode, while project-scoped tools continue to require a valid default project ID.
- [x] [Review][Patch] Apply the configured request timeout to project-list requests [src/services/project_service.py:37] — every paginated request now uses `AllureClient`'s configured timeout.
