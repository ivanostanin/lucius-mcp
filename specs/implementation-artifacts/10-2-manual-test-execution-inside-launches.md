# Story 10.2: Manage Manual Test Execution Inside Launches

Status: done

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
   * **And** when `result_id` targets a launch-managed manual placeholder, the tool resolves that existing Test Result in place and returns its ID for follow-up actions such as evidence upload.
   * **And** explicit `launch_id` plus `test_case_id` payloads may still create a new manual result when no existing launch placeholder is being resolved.

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

- [x] **0. Regenerate API Client and expose missing controllers** (Prerequisite)
  - [x] Update `scripts/filter_openapi.py` to retain the missing controller tags needed for manual execution:
    - [x] `test-result-controller`
    - [x] `test-result-bulk-controller`
    - [x] `test-result-rerun-controller`
    - [x] `test-result-run-controller`
    - [x] `test-result-flat-controller`
    - [x] `upload-controller`
    - [x] `upload-test-result-controller`
  - [x] If step-attachment upload requires runtime fixture discovery beyond execution reads, also retain:
    - [x] `test-result-fixture-controller`
  - [x] Run `./scripts/generate_testops_api_client.sh`.
  - [x] Verify the generated client now includes controller modules equivalent to:
    - [x] `TestResultControllerApi`
    - [x] `TestResultBulkControllerApi`
    - [x] `TestResultRerunControllerApi`
    - [x] `TestResultRunControllerApi`
    - [x] `TestResultFlatControllerApi`
    - [x] `UploadControllerApi`
    - [x] `UploadTestResultControllerApi`

- [x] **1. Extend the client facade for manual execution endpoints** (AC 1-5)
  - [x] Update `src/client/client.py`.
  - [x] Add wrappers for listing launch test results, reading result execution details, bulk rerun, starting manual sessions, submitting manual results, and uploading result/step attachments.
  - [x] Keep all new HTTP interactions async and routed through `_call_api`.
  - [x] Preserve existing validation/error mapping conventions (`AllureValidationError`, `AllureNotFoundError`, `AllureAPIError`).

- [x] **2. Implement service-layer orchestration for manual launch execution** (AC 1-6)
  - [x] Add a dedicated service layer for manual launch execution.
    - [x] Preferred options:
      - [x] Extend `src/services/launch_service.py` for launch-scoped orchestration.
      - [x] Or introduce `src/services/test_result_service.py` if the result/session logic becomes too broad for `LaunchService`.
  - [x] Implement launch result discovery helpers.
  - [x] Implement manual rerun orchestration using bulk selection DTOs.
  - [x] Implement manual session creation and results submission.
  - [x] Map friendly inputs to generated DTOs such as:
    - [x] `TestResultBulkRerunDto`
    - [x] `ManualSessionRequestDto`
    - [x] `ResolveRequestV2Dto`
    - [x] `UploadResultsDto`
    - [x] `UploadTestResultDto`
    - [x] upload step DTO unions for body/expected/attachment steps
  - [x] Reuse existing attachment validation patterns from `AttachmentService` where practical instead of inventing a new format.

- [x] **3. Add or modify MCP tools for manual launch workflows** (AC 1-6)
  - [x] Update `src/tools/launches.py` or add a neighboring launch-results tool module if that keeps the interface clearer.
  - [x] Add `list_launch_test_results`.
  - [x] Add `rerun_test_results_manually`.
  - [x] Add `start_manual_test_session`.
  - [x] Add `submit_manual_test_results`.
  - [x] Add `add_test_result_attachment`.
  - [x] Add `add_test_step_attachment`.
  - [x] Update `get_launch` and `upload_test_results_to_launch` descriptions/output to distinguish launch file upload from manual execution workflow.

- [x] **4. Register tools and CLI metadata** (AC 1-6)
  - [x] Update `src/tools/__init__.py`.
  - [x] Update `deployment/mcpb/manifest.python.json`.
  - [x] Update `deployment/mcpb/manifest.uv.json`.
  - [x] Regenerate any CLI/tool schema metadata if required by the current repo flow.
  - [x] Regenerate shell completions if new entity/action routes or aliases are introduced.

- [x] **5. Unit tests** (AC 1-6)
  - [x] Add or extend unit tests for the new service logic.
  - [x] Cover:
    - [x] launch result filtering and pagination mapping
    - [x] bulk rerun DTO construction (`forceManual`, selection mapping, assignees)
    - [x] manual session creation
    - [x] manual result payload mapping for test-level and step-level statuses/messages
    - [x] result and step attachment validation
    - [x] not-found and invalid-status/timestamp errors

- [x] **6. Integration tests** (AC 1-6)
  - [x] Extend client integration coverage for every new controller wrapper.
  - [x] Verify request shapes for:
    - [x] launch result flat listing
    - [x] bulk manual rerun
    - [x] manual session start
    - [x] manual result upload
    - [x] result attachment upload
    - [x] step attachment upload

- [x] **7. E2E tests** (AC 1-7, NFR11)
  - [x] Extend `tests/e2e/test_launches.py` or add a dedicated manual-execution E2E file.
  - [x] Required sandbox-verification scenario:
    - [x] create or reuse a launch
    - [x] ensure manual test cases are present in the launch
    - [x] list launch test results
    - [x] schedule a failed result for manual rerun
    - [x] start a manual session
    - [x] submit manual results with step updates
    - [x] upload result/step evidence
    - [x] verify the updated result state via TestOps reads
  - [x] Do not treat unit or integration coverage as a substitute for this scenario.
  - [x] Skip only when sandbox credentials or required upstream capabilities are missing, and document the exact blocker in the story record.

- [x] **8. Documentation and agentic coverage** (AC 1-6)
  - [x] Update `docs/tools.md`.
  - [x] Update `README.md` if launch/manual execution is listed there.
  - [x] Update `tests/agentic/agentic-tool-calls-tests.md` to cover the manual launch workflow.
  - [x] Keep the tool inventory and coverage matrix aligned with the new tool set.

- [x] **9. Validation**
  - [x] Run focused checks first:
    - [x] `uv run pytest tests/unit/test_launch_service.py tests/unit/test_launch_tools.py tests/integration/test_launch_client.py`
    - [x] plus any new unit/integration files added for manual execution
  - [x] Run launch/manual focused E2E coverage with `.env.test` to satisfy NFR11 sandbox verification.
  - [x] Run `uv run ruff check ...` and `uv run mypy --strict src/` on touched paths.

### Review Findings

- [x] [Review][Patch] Implement real manual-step attachment support instead of fixture-only attachment routing [src/services/launch_service.py:616]
- [x] [Review][Patch] Restrict attachment URL fetching to avoid SSRF and pre-limit remote downloads before buffering whole responses [src/services/launch_service.py:1283]
- [x] [Review][Patch] Align `submit_manual_test_results` tool contract with the service requirement for `name`/`full_name`, or infer those fields before validation [src/tools/launches.py:341]
- [x] [Review][Patch] Make manual rerun 404 errors identify whether the missing resource is the launch or the selected result IDs [src/services/launch_service.py:468]
- [x] [Review][Patch] Accept the attachment upload status codes the workflow already treats as valid, rather than hard-failing on HTTP 200 [src/client/client.py:1500]
- [x] [Review][Patch] Strengthen the mandatory E2E proof to read TestOps state back after rerun scheduling and evidence uploads [tests/e2e/test_launch_manual_execution.py:93]

#### Implementation Plan for Real Manual-Step Attachment Support

1. Confirm the upstream TestOps read or upload surface for attachments linked to actual manual scenario steps instead of fixture results, including the target identifier that must be supplied after `submit_manual_test_results`.
2. Extend the client facade with the minimal non-generated wrapper needed for step-level attachment linkage if the current generated controller set does not already expose it.
3. Replace the fixture-only resolution path in `LaunchService.add_test_step_attachment` with a step-target resolver that can map friendly inputs such as result ID plus step name or ordinal to the upstream step identifier.
4. Update the MCP tool contract and docs so `add_test_step_attachment` clearly accepts manual-step selectors, while preserving any fixture support only as an explicit fallback if the upstream API requires it.
5. Add focused unit coverage for step resolution, ambiguous matches, not-found behavior, and attachment upload payload mapping.
6. Extend integration and E2E coverage so the manual execution workflow attaches evidence to a submitted manual step and verifies the linkage through a TestOps read path.

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
  - `GET /api/testresult/{id}/execution?v2=true`
- **Resolve active manual result in place**
  - `POST /api/testresult/{id}/resolve?v2=true`
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
- Resolved manual-result executions may require `GET /api/testresult/{id}/execution?v2=true`; the non-`v2` execution read can return an empty payload even after a successful resolve.
- Keep `upload_test_results_to_launch` backward compatible; do not silently repurpose the existing archive/file upload tool for JSON manual-session uploads.
- PRD NFR11 applies directly to this story, so mocked coverage alone is insufficient for completion.

### Observed Sandbox Semantics

- The TestOps UI completes an existing launch-created manual result with `POST /api/testresult/{id}/resolve?v2=true` under `test-result-run-controller`.
- `submit_manual_test_results(...)` should therefore resolve the active launch placeholder in place when the payload supplies `result_id`.
- After `rerun_test_results_manually(...)`, TestOps creates a new visible active placeholder for the rerun phase; callers must refresh launch results and switch to that new `result_id` before submitting the rerun execution or attachments.
- `GET /api/testresult/{id}/execution?v2=true` returns the resolved step tree for these results, while the non-`v2` execution read may remain empty.
- When step evidence is attached after resolution, the `v2` execution payload can materialize it as a nested attachment child step under the selected manual step rather than as a top-level `attachments` array.
- The explicit `launch_id` plus `test_case_id` submission path remains a separate fallback for creating a new manual result outside the active launch-placeholder workflow.

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
- Restored the missing launch/test-result/upload controllers in the filtered OpenAPI spec and regenerated the client with manual-execution APIs plus fixture endpoints.
- Added launch-scoped manual execution tools and service orchestration for result discovery, rerun scheduling, manual session start, result submission, and result/step evidence upload.
- Patched around live sandbox contract drift: `/api/upload/session` also requires `projectId`, `jobUid`, and `jobRunUid`, plus a preceding `/api/upload/run` bootstrap that is absent from the published request schema.
- Patched around live upload response drift: `/api/upload/test-result` and fixture uploads return `results[].id` rather than `resultIds`, so the client now parses raw response bodies for created IDs.
- Live sandbox submissions also require a stable `name` plus generated `uuid`/`historyId`; the service now supplies those fields and returns created result IDs for attachment follow-up.
- Sandbox readback caveat: fixture attachment uploads succeed and return a fixture target ID, but the current fixture-attachment listing endpoint remains empty immediately afterward, so E2E coverage verifies successful upload and fixture existence rather than attachment-row readback.
- HAR evidence from the TestOps UI showed that launch-managed manual completion uses `POST /api/testresult/{id}/resolve?v2=true` from `test-result-run-controller`, not the upload/create flow.
- The client and launch service now resolve existing launch-created manual results in place, so result status updates and attachments stay attached to the active launch result across initial execution and reruns.
- Step verification for resolved manual results uses `GET /api/testresult/{id}/execution?v2=true` because the non-`v2` execution read can be empty for these runs.
- Live sandbox verification also showed step attachments read back as nested attachment child steps in the `v2` execution tree, so E2E assertions follow that server shape instead of assuming `step.attachments`.
- Validation passed:
  - `uv run pytest tests/unit/test_launch_service.py tests/unit/test_launch_tools.py tests/integration/test_launch_client.py -q`
  - `uv run --env-file .env.test pytest tests/e2e/test_launch_manual_execution.py -q`
  - `uv run pytest tests/unit/test_launch_service.py tests/integration/test_launch_client.py tests/unit/test_launch_tools.py -q`
  - `uv run --env-file .env.test pytest tests/e2e/test_launch_manual_execution.py::test_manual_launch_execution_workflow -q`
  - `uv run ruff check src/client/client.py src/services/launch_service.py src/tools/launches.py tests/unit/test_launch_service.py tests/integration/test_launch_client.py tests/e2e/test_launch_manual_execution.py tests/unit/test_launch_tools.py`
  - `uv run mypy --strict src/client/client.py src/services/launch_service.py src/tools/launches.py`
  - `uv run ruff check src/client/client.py src/services/launch_service.py src/tools/launches.py src/tools/__init__.py src/tools/annotations.py src/cli/route_matrix.py tests/unit/test_launch_service.py tests/integration/test_launch_client.py tests/unit/test_launch_tools.py scripts/filter_openapi.py tests/e2e/test_launch_manual_execution.py`
  - `uv run mypy src/client/client.py src/services/launch_service.py src/tools/launches.py`
  - `uv --quiet run --python 3.13 --extra dev python scripts/build_tool_schema.py`
  - `uv run --python 3.13 python deployment/scripts/generate_completions.py`

### File List

- deployment/mcpb/manifest.python.json
- deployment/mcpb/manifest.uv.json
- deployment/shell-completions/lucius.bash
- deployment/shell-completions/lucius.fish
- deployment/shell-completions/lucius.ps1
- deployment/shell-completions/lucius.zsh
- docs/tools.md
- openapi/allure-testops-service/filtered-report-service.json
- scripts/filter_openapi.py
- specs/implementation-artifacts/10-2-manual-test-execution-inside-launches.md
- specs/implementation-artifacts/sprint-status.yaml
- src/cli/data/tool_schemas.json
- src/cli/route_matrix.py
- src/client/client.py
- src/client/generated/
- src/services/launch_service.py
- src/tools/__init__.py
- src/tools/annotations.py
- src/tools/launches.py
- tests/agentic/agentic-tool-calls-tests.md
- tests/e2e/test_launch_manual_execution.py
- tests/integration/test_launch_client.py
- tests/unit/test_launch_service.py
- tests/unit/test_launch_tools.py

### Change Log

- 2026-07-03: Implemented manual launch execution workflow, regenerated client/schema/completions, and verified the sandbox E2E path.
- 2026-07-05: Repaired manual launch execution to use direct test-result APIs for status updates and result/step attachments; reran focused unit, integration, and sandbox E2E validation successfully.
