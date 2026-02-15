# Story 7.6: Get Projects Tool

Status: ready-for-dev

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

- [ ] **0. Regenerate API Client** (Prerequisite)
  - [ ] Check `src/client/generated/api` for `ProjectController` endpoints.
  - [ ] Ensure `ProjectController` is included in `scripts/filter_openapi.py`.
  - [ ] Run `scripts/generate_testops_api_client.sh`.

- [ ] **1. Implement Service Layer** (AC 1-3)
  - [ ] Create/Update `src/services/project_service.py`.
  - [ ] Implement `get_project_by_name(name: str) -> Project`.
  - [ ] Implement `list_projects() -> list[Project]`.
  - [ ] Logic: Fetch all projects (or search if API supports), then filter by name locally if needed. *Dev Note: TestOps API usually has `findAll`.*

- [ ] **2. Implement MCP Tool** (AC 1-4)
  - [ ] Create `src/tools/projects.py`.
  - [ ] Add `get_project(name: str | None = None)`.
  - [ ] If `name` is provided, return specific project.
  - [ ] If `name` is None, return list of all projects (summary).
  - [ ] Add docstrings.

- [ ] **3. Register Tool**
  - [ ] Update `src/tools/__init__.py`.
  - [ ] Update `deployment/mcpb/manifest.python.json`.
  - [ ] Update `deployment/mcpb/manifest.uv.json`.

- [ ] **4. Unit Tests**
  - [ ] Create `tests/unit/test_project_service.py`.
  - [ ] Test case-insensitive matching.
  - [ ] Test "not found" scenario.

- [ ] **5. Integration Tests**
  - [ ] Create `tests/integration/test_project_tools.py`.
  - [ ] Mock API response with list of projects.
  - [ ] Verify tool logic.

- [ ] **6. E2E Tests**
  - [ ] Create `tests/e2e/test_project_discovery.py`.
  - [ ] Scenario: Authenticate -> List Projects -> Get Specific Project by Name -> Verify ID matches.

- [ ] **7. Update Agentic Workflow**
  - [ ] Add scenario **Project Discovery** to `tests/agentic/agentic-tool-calls-tests.md`.
  - [ ] Include tools: `get_project`.
  - [ ] Update **Tool inventory** and **Coverage matrix** sections.
  - [ ] Update **Execution plan** section.

- [ ] **8. Update Documentation**
  - [ ] Update `docs/tools.md` (New "Project Management" or "General" section).
  - [ ] Update `README.md`.

- [ ] **9. Validation**
  - [ ] Run full test suite: `./scripts/full-test-suite.sh`

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
