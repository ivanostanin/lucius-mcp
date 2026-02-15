# Story 7.7: Test Code Generation Tool

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **AI Agent**,
I want to **generate test code for a Test Case using Allure TestOps native generation**,
so that **I can quickly scaffold automated tests in my target language and framework without manual translation**.

## Acceptance Criteria

1.  **Generate Test Code:**
    *   **Given** a valid Test Case ID.
    *   **When** I call `generate_test_code(test_case_id, language="python", framework="pytest")`.
    *   **Then** the tool calls the TestOps API (`/api/ide/testcase/{id}/testcode`).
    *   **And** returns the generated code snippet as a string.

2.  **Framework/Language Support:**
    *   **Given** different language/framework combinations (e.g., `ts`/`playwright`, `java`/`junit`).
    *   **Then** the tool accepts these arguments and passes them to the API.
    *   **And** validates against a known list of supported options if possible, or passes through for API validation.

3.  **Sync Options:**
    *   **When** calling the tool.
    *   **Then** it defaults synchronization flags (`syncFields`, `syncName`, `syncTags`, `syncScenario`) to `true` to ensure the code reflects the latest test case state.

4.  **Error Handling:**
    *   **Given** an invalid Test Case ID or unsupported framework.
    *   **Then** the tool returns a clear error message from the API.

## Tasks / Subtasks

- [ ] **0. Regenerate/Patch API Client** (Prerequisite)
  - [ ] **Critical:** The endpoint `/api/ide/testcase/{id}/testcode` might NOT be in the standard public OpenAPI spec.
  - [ ] Check `src/client/generated/` for `IdeController` or similar.
  - [ ] **If missing:**
    - [ ] Option A (Preferred): Add `ide-controller` tag to `scripts/filter_openapi.py` if present in source spec.
    - [ ] Option B (Fallback): Implement a raw HTTP request method in `TestCodeService` using `self.client.client.request` (bypassing generated models).
  - [ ] Run `scripts/generate_testops_api_client.sh` to see if it picks up.

- [ ] **1. Implement Service Layer** (AC 1-3)
  - [ ] Create `src/services/test_code_service.py`.
  - [ ] Implement `generate_code(test_case_id: int, lang: str, framework: str) -> str`.
  - [ ] Handle the POST request body:
    ```json
    {
      "lang": "python",
      "testFramework": "pytest",
      "syncFields": true,
      "syncName": true,
      "syncTags": true,
      "syncScenario": true
    }
    ```
  - [ ] Parse response JSON `{"code": "..."}`.

- [ ] **2. Implement MCP Tool** (AC 1-4)
  - [ ] Create `src/tools/test_code.py` (or add to `cases.py` if "Fat Tool" pattern permitted, but separate is cleaner).
  - [ ] Add `generate_test_code(...)`.
  - [ ] Add docstrings and argument descriptions.
  - [ ] Provide default values (`lang="python"`, `framework="pytest"`).

- [ ] **3. Register Tool**
  - [ ] Update `src/tools/__init__.py`.
  - [ ] Update `deployment/mcpb/manifest.python.json`.
  - [ ] Update `deployment/mcpb/manifest.uv.json`.

- [ ] **4. Unit Tests**
  - [ ] Create `tests/unit/test_test_code_service.py`.
  - [ ] Mock API response.
  - [ ] Test request payload construction.

- [ ] **5. Integration Tests**
  - [ ] Create `tests/integration/test_test_code_tool.py`.
  - [ ] Verify tool wiring.

- [ ] **6. E2E Tests**
  - [ ] Create `tests/e2e/test_code_generation.py`.
  - [ ] Scenario: Create Test Case -> Generate Code -> Verify "import" or "test" strings in output.

- [ ] **7. Update Agentic Workflow**
  - [ ] Add scenario **Generate Test Code** to `tests/agentic/agentic-tool-calls-tests.md`.
  - [ ] Include tools: `generate_test_code`.
  - [ ] Update **Tool inventory** and **Coverage matrix** sections.
  - [ ] Update **Execution plan** section.

- [ ] **8. Update Documentation**
  - [ ] Update `docs/tools.md` (New "Automation" or "Generation" section).
  - [ ] Update `README.md`.

- [ ] **9. Validation**
  - [ ] Run full test suite: `./scripts/full-test-suite.sh`

## Dev Notes

### Architecture Patterns (MUST FOLLOW)

- **Thin Tool / Fat Service:** Logic in `TestCodeService`.
- **API Discovery:** The `/api/ide` path suggests an internal or IDE-specific API. If the OpenAPI generator fails to produce this, use `src/client/client.py`'s underlying `httpx` client to make a direct authenticated request. Do not waste time trying to fix upstream OpenAPI specs if `ide` tag is missing.
- **Payload:** Based on HAR, body requires specific booleans (`syncFields` etc). Hardcode these to `True` for best agent experience (Agents always want the latest version).

### Source Tree Impact

| Component | Path | Action |
|:----------|:-----|:-------|
| Generated client | `src/client/generated/` | **CHECK** |
| Service | `src/services/test_code_service.py` | **NEW** |
| Tool | `src/tools/test_code.py` | **NEW** |
| Manifests | `deployment/mcpb/manifest.*.json` | **MODIFY** |
| Unit Tests | `tests/unit/test_test_code_service.py` | **NEW** |
| E2E Tests | `tests/e2e/test_code_generation.py` | **NEW** |
| Agentic Tests | `tests/agentic/agentic-tool-calls-tests.md` | **MODIFY** |

### Testing Standards

- **Coverage:** > 85%.

### Dev Agent Record

### Agent Model Used

Antigravity (Google DeepMind)

### Completion Notes List
- Story created based on provided HAR file analysis.
