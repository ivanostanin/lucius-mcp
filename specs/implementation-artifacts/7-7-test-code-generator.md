# Story 7.7: Test Code Generation Tool

Status: done

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

- [x] **0. Regenerate/Patch API Client** (Prerequisite)
  - [x] **Critical:** The endpoint `/api/ide/testcase/{id}/testcode` was absent from the standard public OpenAPI spec.
  - [x] Check `src/client/generated/` for `IdeController` or similar.
  - [x] **If missing:**
    - [x] Option A (Preferred): Add an `ide-controller` OpenAPI overlay in `scripts/filter_openapi.py` and regenerate the client.
    - [x] Option B (Fallback): Not required; the generated `IdeControllerApi` is used instead of a raw HTTP request.
  - [x] Run `scripts/generate_testops_api_client.sh` to generate `IdeControllerApi` and its DTOs.

- [x] **1. Implement Service Layer** (AC 1-3)
  - [x] Create `src/services/test_code_service.py`.
  - [x] Implement `generate_code(test_case_id: int, lang: str, framework: str) -> str`.
  - [x] Handle the POST request body:
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
  - [x] Parse response JSON `{"code": "..."}`.

- [x] **2. Implement MCP Tool** (AC 1-4)
  - [x] Create `src/tools/test_code.py` (or add to `cases.py` if "Fat Tool" pattern permitted, but separate is cleaner).
  - [x] Add `generate_test_code(...)`.
  - [x] Add docstrings and argument descriptions.
  - [x] Provide default values (`language="python"`, `framework="pytest"`).

- [x] **3. Register Tool**
  - [x] Update `src/tools/__init__.py`.
  - [x] Update `deployment/mcpb/manifest.python.json`.
  - [x] Update `deployment/mcpb/manifest.uv.json`.

- [x] **4. Unit Tests**
  - [x] Create `tests/unit/test_test_code_service.py`.
  - [x] Mock API response.
  - [x] Test request payload construction.

- [x] **5. Integration Tests**
  - [x] Create `tests/integration/test_test_code_tool.py`.
  - [x] Verify tool wiring.

- [x] **6. E2E Tests**
  - [x] Create `tests/e2e/test_code_generation.py`.
  - [x] Scenario: Create Test Case -> Generate Code -> Verify "import" or "test" strings in output.

- [x] **7. Update Agentic Workflow**
  - [x] Add scenario **Generate Test Code** to `tests/agentic/agentic-tool-calls-tests.md`.
  - [x] Include tools: `generate_test_code`.
  - [x] Update **Tool inventory** and **Coverage matrix** sections.
  - [x] Update **Execution plan** section.

- [x] **8. Update Documentation**
  - [x] Update `docs/tools.md` (New "Automation" or "Generation" section).
  - [x] Update `README.md`.

- [x] **9. Validation**
  - [x] Run full test suite: `./scripts/full-test-suite.sh`

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

Codex (GPT-5)

### Implementation Plan

- Overlay the missing IDE endpoint and DTOs during OpenAPI filtering, then regenerate the client.
- Use `IdeControllerApi` from the service and retain the standard generated-client error mapping.
- Expose a read-only MCP tool with structured and plain output contracts, then cover it through unit, integration, and live E2E tests.

### Completion Notes List
- Story created based on provided HAR file analysis.
- Added an OpenAPI overlay for the absent IDE endpoint, generated `IdeControllerApi`, and implemented the thin MCP tool plus `TestCodeService` using the generated client.
- Added generated-client, service, tool, unit, integration, live E2E, MCP manifest, agentic workflow, MCPB manifest, and documentation coverage.
- Validation passed: `./scripts/full-test-suite.sh`; focused live E2E `uv run --env-file .env.test pytest tests/e2e/test_code_generation.py -q` (1 passed); strict mypy and focused lint/schema checks passed.

### File List

- README.md
- deployment/mcpb/manifest.python.json
- deployment/mcpb/manifest.uv.json
- docs/mcp_manifest.json
- docs/tools.md
- openapi/allure-testops-service/filtered-report-service.json
- scripts/filter_openapi.py
- specs/implementation-artifacts/7-7-test-code-generator.md
- specs/implementation-artifacts/sprint-status.yaml
- src/client/generated/README.md
- src/client/generated/__init__.py
- src/client/generated/api/__init__.py
- src/client/generated/api/ide_controller_api.py
- src/client/generated/docs/IdeControllerApi.md
- src/client/generated/docs/TestCodeGenerationRequestDto.md
- src/client/generated/docs/TestCodeGenerationResponseDto.md
- src/client/generated/models/__init__.py
- src/client/generated/models/test_code_generation_request_dto.py
- src/client/generated/models/test_code_generation_response_dto.py
- src/services/test_code_service.py
- src/tools/__init__.py
- src/tools/annotations.py
- src/tools/output_schemas.py
- src/tools/test_code.py
- tests/agentic/agentic-tool-calls-tests.md
- tests/e2e/test_code_generation.py
- tests/integration/test_test_code_tool.py
- tests/unit/test_test_code_service.py

### Change Log

- 2026-07-21: Implemented native TestOps test-code generation with a generated IDE API client, MCP tool, tests, manifests, and documentation.

### Review Findings

- [x] [Review][Patch] Preserve literal escape sequences in plain generated code [src/tools/test_code.py:48] — `render_output()` normalizes every literal `\\n` to a newline for plain output. Generated source may legitimately contain `\\n` inside a string literal, so the tool can return code with changed meaning or invalid syntax. Render generated source verbatim for `output_format="plain"` (or add an explicit lossless rendering path).
