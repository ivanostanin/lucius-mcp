# Story 10.2: Manage Manual Test Execution Inside Launches

Status: ready-for-dev

<!-- Note: Validate upstream artifacts and this story spec before implementation when planning changes materially affect scope or test obligations. -->

## Story

As an **AI Agent**,
I want to **discover manual test results in a launch, mark failed results for manual rerun, and submit manual execution updates with evidence**,
so that **I can complete manual QA workflows inside Allure TestOps without switching back to the UI**.

## Acceptance Criteria

1. **List launch test results with manual execution metadata**
   * **Given** a valid Launch ID.
   * **When** I call `list_launch_test_results(launch_id=...)`.
   * **Then** the tool returns launch results with `result_id`, `test_case_id`, `name`, `manual`, `status`, and available assignee/tester fields.
   * **And** I can optionally filter to manual-only or failed-only results without building raw AQL by hand.

2. **Mark failed results to be rerun manually**
   * **Given** one or more failed test results in a launch.
   * **When** I call `rerun_test_results_manually(...)`.
   * **Then** TestOps schedules manual reruns for the selected results.
   * **And** the tool supports bulk rerun by selected result IDs.
   * **And** the tool can force manual rerun mode and optionally target assignees when the upstream API supports it.

3. **Start a manual test session for a launch**
   * **Given** a launch that contains original manual tests or newly scheduled manual reruns.
   * **When** I call `start_manual_test_session(launch_id=..., environment=...)`.
   * **Then** TestOps creates a manual session and returns the `test_session_id` required for result submission.

4. **Submit manual execution results with test and step status updates**
   * **Given** a valid `test_session_id` and manual results payload.
   * **When** I call `submit_manual_test_results(test_session_id=..., results=[...])`.
   * **Then** I can set per-test `status`, `start`, `stop`, `message`, and other execution fields.
   * **And** I can set per-step status, timing, comments/messages, and expected outcome/body data.
   * **And** the tool returns created/updated Test Result IDs for follow-up actions such as evidence upload.

5. **Attach evidence to manual test results and steps**
   * **Given** a created or existing manual test result.
   * **When** I call `add_test_result_attachment(...)` or `add_test_step_attachment(...)`.
   * **Then** the attachment is uploaded and linked to the correct result or step context.
   * **And** the tool accepts the same attachment input patterns already used elsewhere in the repo (`content` or `url` plus metadata).

6. **Validation and recovery guidance**
   * **Given** invalid launch IDs, result IDs, session IDs, timestamps, status values, or malformed step payloads.
   * **When** I call any manual execution tool.
   * **Then** the server returns an actionable validation error with Agent Hints instead of a raw traceback.
   * **And** not-found cases identify whether the missing resource is the launch, result, or session.

7. **NFR11 end-to-end verification is mandatory**
   * **Given** `specs/prd.md` defines NFR11 as verifying tool execution results against a sandbox TestOps instance or project.
   * **When** this story is implemented.
   * **Then** the test plan includes end-to-end coverage for launch result discovery, manual rerun scheduling, manual session start, manual result submission, and result or step evidence upload.
   * **And** story completion is blocked until those E2E checks validate behavior against the sandbox instance or project, unless the story status is explicitly marked blocked by unavailable upstream sandbox capabilities.

## Recommended Tool Surface

### New tools

- `list_launch_test_results`
- `rerun_test_results_manually`
- `start_manual_test_session`
- `submit_manual_test_results`
- `add_test_result_attachment`
- `add_test_step_attachment`

### Existing tools to modify or clarify

- `get_launch`
  - Add a compact manual-execution summary or guidance pointing agents to `list_launch_test_results` for detailed result-level work.
- `upload_test_results_to_launch`
  - Keep this tool focused on archive/file upload and explicitly document that manual interactive execution uses the new manual-session workflow instead.

## Tasks / Subtasks

- [ ] **0. Regenerate API Client and expose missing controllers** (Prerequisite)
  - [ ] Update `scripts/filter_openapi.py` to retain the missing controller tags needed for manual execution:
    - [ ] `test-result-controller`
    - [ ] `test-result-bulk-controller`
    - [ ] `test-result-rerun-controller`
    - [ ] `test-result-flat-controller`
    - [ ] `upload-controller`
    - [ ] `upload-test-result-controller`
  - [ ] If step-attachment upload requires runtime fixture discovery beyond execution reads, also retain:
    - [ ] `test-result-fixture-controller`
  - [ ] Run `./scripts/generate_testops_api_client.sh`.
  - [ ] Verify the generated client now includes controller modules equivalent to:
    - [ ] `TestResultControllerApi`
    - [ ] `TestResultBulkControllerApi`
    - [ ] `TestResultRerunControllerApi`
    - [ ] `TestResultFlatControllerApi`
    - [ ] `UploadControllerApi`
    - [ ] `UploadTestResultControllerApi`

- [ ] **1. Extend the client facade for manual execution endpoints** (AC 1-5)
  - [ ] Update `src/client/client.py`.
  - [ ] Add wrappers for listing launch test results, reading result execution details, bulk rerun, starting manual sessions, submitting manual results, and uploading result/step attachments.
  - [ ] Keep all new HTTP interactions async and routed through `_call_api`.
  - [ ] Preserve existing validation/error mapping conventions (`AllureValidationError`, `AllureNotFoundError`, `AllureAPIError`).

- [ ] **2. Implement service-layer orchestration for manual launch execution** (AC 1-6)
  - [ ] Add a dedicated service layer for manual launch execution.
    - [ ] Preferred options:
      - [ ] Extend `src/services/launch_service.py` for launch-scoped orchestration.
      - [ ] Or introduce `src/services/test_result_service.py` if the result/session logic becomes too broad for `LaunchService`.
  - [ ] Implement launch result discovery helpers.
  - [ ] Implement manual rerun orchestration using bulk selection DTOs.
  - [ ] Implement manual session creation and results submission.
  - [ ] Map friendly inputs to generated DTOs such as:
    - [ ] `TestResultBulkRerunDto`
    - [ ] `ManualSessionRequestDto`
    - [ ] `UploadResultsDto`
    - [ ] `UploadTestResultDto`
    - [ ] upload step DTO unions for body/expected/attachment steps
  - [ ] Reuse existing attachment validation patterns from `AttachmentService` where practical instead of inventing a new format.

- [ ] **3. Add or modify MCP tools for manual launch workflows** (AC 1-6)
  - [ ] Update `src/tools/launches.py` or add a neighboring launch-results tool module if that keeps the interface clearer.
  - [ ] Add `list_launch_test_results`.
  - [ ] Add `rerun_test_results_manually`.
  - [ ] Add `start_manual_test_session`.
  - [ ] Add `submit_manual_test_results`.
  - [ ] Add `add_test_result_attachment`.
  - [ ] Add `add_test_step_attachment`.
  - [ ] Update `get_launch` and `upload_test_results_to_launch` descriptions/output to distinguish launch file upload from manual execution workflow.

- [ ] **4. Register tools and CLI metadata** (AC 1-6)
  - [ ] Update `src/tools/__init__.py`.
  - [ ] Update `deployment/mcpb/manifest.python.json`.
  - [ ] Update `deployment/mcpb/manifest.uv.json`.
  - [ ] Regenerate any CLI/tool schema metadata if required by the current repo flow.
  - [ ] Regenerate shell completions if new entity/action routes or aliases are introduced.

- [ ] **5. Unit tests** (AC 1-6)
  - [ ] Add or extend unit tests for the new service logic.
  - [ ] Cover:
    - [ ] launch result filtering and pagination mapping
    - [ ] bulk rerun DTO construction (`forceManual`, selection mapping, assignees)
    - [ ] manual session creation
    - [ ] manual result payload mapping for test-level and step-level statuses/messages
    - [ ] result and step attachment validation
    - [ ] not-found and invalid-status/timestamp errors

- [ ] **6. Integration tests** (AC 1-6)
  - [ ] Extend client integration coverage for every new controller wrapper.
  - [ ] Verify request shapes for:
    - [ ] launch result flat listing
    - [ ] bulk manual rerun
    - [ ] manual session start
    - [ ] manual result upload
    - [ ] result attachment upload
    - [ ] step attachment upload

- [ ] **7. E2E tests** (AC 1-7, NFR11)
  - [ ] Extend `tests/e2e/test_launches.py` or add a dedicated manual-execution E2E file.
  - [ ] Required sandbox-verification scenario:
    - [ ] create or reuse a launch
    - [ ] ensure manual test cases are present in the launch
    - [ ] list launch test results
    - [ ] schedule a failed result for manual rerun
    - [ ] start a manual session
    - [ ] submit manual results with step updates
    - [ ] upload result/step evidence
    - [ ] verify the updated result state via TestOps reads
  - [ ] Do not treat unit or integration coverage as a substitute for this scenario.
  - [ ] Skip only when sandbox credentials or required upstream capabilities are missing, and document the exact blocker in the story record.

- [ ] **8. Documentation and agentic coverage** (AC 1-6)
  - [ ] Update `docs/tools.md`.
  - [ ] Update `README.md` if launch/manual execution is listed there.
  - [ ] Update `tests/agentic/agentic-tool-calls-tests.md` to cover the manual launch workflow.
  - [ ] Keep the tool inventory and coverage matrix aligned with the new tool set.

- [ ] **9. Validation**
  - [ ] Run focused checks first:
    - [ ] `uv run pytest tests/unit/test_launch_service.py tests/unit/test_launch_tools.py tests/integration/test_launch_client.py`
    - [ ] plus any new unit/integration files added for manual execution
  - [ ] Run launch/manual focused E2E coverage with `.env.test` to satisfy NFR11 sandbox verification.
  - [ ] Run `uv run ruff check ...` and `uv run mypy --strict src/` on touched paths.

## Dev Notes

### Architecture Patterns (MUST FOLLOW)

- **Thin Tool / Fat Service:** Keep business logic, DTO construction, and endpoint choreography in services.
- **Async only:** Use `httpx` async patterns exclusively.
- **Generated code boundary:** Do not manually edit `src/client/generated/`; regenerate instead.
- **Validation-first mapping:** Friendly tool inputs must be translated into strict generated DTOs before crossing the client boundary.

### Missing Controller and Endpoint Inventory

The generated package already contains supporting DTOs such as `ManualSessionRequestDto`, `TestResultBulkRerunDto`, `UploadResultsDto`, and `UploadTestResultDto`, but the controller classes are currently filtered out. The story must restore the controller tags that expose at least these operations:

- **Launch result discovery**
  - `GET /api/v2/launch/{launchId}/test-result/flat`
- **Result inspection**
  - `GET /api/testresult/{id}`
  - `GET /api/testresult/{id}/execution`
- **Manual rerun**
  - `POST /api/testresult/bulk/rerun`
  - `POST /api/testresult/{testResultId}/rerun`
- **Manual session workflow**
  - `POST /api/upload/session`
  - `POST /api/upload/test-result`
- **Evidence upload**
  - `POST /api/upload/test-result/{id}/attachment`
  - `POST /api/upload/test-fixture-result/{id}/attachment` if upstream step attachment semantics require it

### Source Tree Impact

| Component | Path | Action |
|:----------|:-----|:-------|
| OpenAPI filter | `scripts/filter_openapi.py` | **MODIFY** |
| Generated client | `src/client/generated/` | **REGENERATE** |
| Client facade | `src/client/client.py` | **MODIFY** |
| Services | `src/services/launch_service.py` and/or new result/manual execution service | **MODIFY / NEW** |
| Tools | `src/tools/launches.py` and possibly new launch-results module | **MODIFY / NEW** |
| Tool registry | `src/tools/__init__.py` | **MODIFY** |
| Manifests | `deployment/mcpb/manifest.*.json` | **MODIFY** |
| Unit tests | `tests/unit/` | **MODIFY / NEW** |
| Integration tests | `tests/integration/` | **MODIFY / NEW** |
| E2E tests | `tests/e2e/` | **MODIFY / NEW** |
| Agentic coverage | `tests/agentic/agentic-tool-calls-tests.md` | **MODIFY** |
| Docs | `docs/tools.md`, `README.md` | **MODIFY** |

### Previous Story Intelligence

- **Story 5.4** already established launch lifecycle helpers and the launch-focused tool/service/test layout.
- **Story 5.5** is adjacent but intentionally different: it uploads files/archives to a launch, while this story adds interactive/manual result execution through JSON session APIs.
- Existing attachment handling in `AttachmentService`, `TestCaseService`, and `SharedStepService` should be reused for validation and binary upload patterns where possible.

### Testing and Implementation Risks

- The manual execution flow spans multiple controller families (`launch`, `test-result`, `upload`), so E2E verification against the sandbox instance is important before declaring attachment semantics complete.
- Step attachment upload may require an extra read step to resolve the runtime step/fixture identifier accepted by the upstream endpoint. If the API does not expose stable IDs for scenario steps directly, document and encapsulate that lookup in the service rather than leaking it to the tool user.
- Keep `upload_test_results_to_launch` backward compatible; do not silently repurpose the existing archive/file upload tool for JSON manual-session uploads.
- PRD NFR11 applies directly to this story, so mocked coverage alone is insufficient for completion.

### References

- [Source: specs/project-planning-artifacts/epics.md#Epic 10]
- [Source: specs/prd.md#NFR11 - End-to-End Tests]
- [Source: specs/implementation-artifacts/5-1-create-and-list-launches.md]
- [Source: specs/implementation-artifacts/5-4-close-finalize-and-reopen-launch.md]
- [Source: specs/implementation-artifacts/5-5-expose-upload-results-to-launch.md]
- [Source: specs/architecture.md#Implementation Patterns & Consistency Rules]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: docs/development.md#Adding a New Tool]

## Dev Agent Record

### Agent Model Used

gpt-5-codex

### Completion Notes List

- Story created from current launch/manual-execution gaps in the codebase and OpenAPI surface.
- Moved this story from Epic 5 to Epic 10 as Story 10.2 to reflect API-coverage and usability scope better than launch CRUD scope.
- Made PRD NFR11 explicit in the acceptance criteria, E2E tasks, and validation notes so sandbox verification is required for completion.
