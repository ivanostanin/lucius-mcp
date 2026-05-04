# Story 10.1: Include TestOps Entity URLs in Tool Responses

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want tool responses that mention TestOps entity IDs to also include browser URLs for those entities,
so that I can navigate users directly to the relevant TestOps objects without manually reconstructing links.

## Acceptance Criteria

1. **IDs remain present and URLs are added**
  - **Given** a tool response includes a stable TestOps entity ID
  - **When** the tool returns either `plain` or `json`
  - **Then** the existing ID field remains unchanged
  - **And** the response also includes a corresponding URL for that entity
  - **And** tool output modes remain limited to `plain|json`.

2. **URLs use resolved client context**
  - **Given** a tool call uses a `project_id` override or runtime auth context
  - **When** a URL is generated
  - **Then** it uses `AllureClient.get_base_url()` and `AllureClient.get_project()` from the active client
  - **And** it does not use `settings.ALLURE_PROJECT_ID` after the client context is resolved.

3. **Known entity URL patterns are implemented consistently**
  - **Given** known browser URL patterns for TestOps entities
  - **When** URLs are added
  - **Then** use this initial map:
    - `test_case`: `<base_url>/project/<project_id>/test-cases/<test_case_id>`
    - `launch`: `<base_url>/project/<project_id>/launches/<launch_id>`
    - `defect`: `<base_url>/project/<project_id>/defects/<defect_id>`
    - `test_plan`: `<base_url>/project/<project_id>/test-plans/<plan_id>`
    - `shared_step`: `<base_url>/project/<project_id>/settings/shared-steps/<shared_step_id>`
  - **And** any additional entity pattern must be verified against a sandbox TestOps UI before being used.

4. **Multiple entity references are unambiguous**
  - **Given** a response contains multiple entity IDs, such as a defect linked to a test case
  - **When** JSON output is rendered
  - **Then** every supported referenced entity has an unambiguous URL field such as `defect_url`, `test_case_url`, `launch_url`, or nested item `url`
  - **And** plain output labels each URL with its entity type.

5. **Collection items include item URLs**
  - **Given** a list/search tool returns entity items
  - **When** each item includes an entity ID
  - **Then** each item includes its own `url` in JSON
  - **And** plain output remains readable and keeps existing ID/name/status lines intact for current parsers.

6. **Unsupported or unstable entity URLs are not invented**
  - **Given** an entity type has no verified stable browser URL pattern
  - **When** the developer reaches that entity
  - **Then** they either verify the URL in a sandbox and add tests
  - **Or** intentionally omit the URL and document why
  - **And** they do not create fake links for settings-only records or API-only records.

7. **Automated coverage protects URL behavior**
  - **Given** tests run
  - **Then** they verify URL generation for test cases, launches, defects, test plans, and shared steps
  - **And** they verify resolved `base_url` and `project_id` are used
  - **And** they verify existing ID parsing and CLI output formatting do not regress.

## Tasks / Subtasks

- [x] **Task 1: Add a shared TestOps URL builder** (AC: 1, 2, 3, 6)
  - [x] 1.1 Extend `src/utils/links.py` or add a nearby helper module for browser URL construction.
  - [x] 1.2 Keep `normalize_links()` intact; it is for external issue/link DTO normalization, not TestOps entity links.
  - [x] 1.3 Implement small typed helpers such as `test_case_url(base_url, project_id, test_case_id)`, `launch_url(...)`, `defect_url(...)`, `test_plan_url(...)`, and `shared_step_url(...)`.
  - [x] 1.4 Strip duplicate slashes by relying on `AllureClient.get_base_url()` already returning a trailing-slash-free base URL; do not add URL encoding unless IDs become non-integer.
  - [x] 1.5 Move the existing shared-step URL logic out of `src/tools/shared_steps.py` into the shared helper to avoid duplicate patterns.

- [x] **Task 2: Add URLs to test case tool responses** (AC: 1, 2, 3, 5, 7)
  - [x] 2.1 Update `src/tools/create_test_case.py` so plain output includes `URL: ...` and JSON includes `url`.
  - [x] 2.2 Update `src/tools/search.py` serializers for `list_test_cases`, `search_test_cases`, and `get_test_case_details` so each test case item/detail includes `url`.
  - [x] 2.3 Update `src/tools/update_test_case.py` and `src/tools/delete_test_case.py` confirmation/success payloads where a test case ID is present.
  - [x] 2.4 Preserve existing strings such as `Created Test Case ID:` because e2e tests parse IDs from those messages.

- [x] **Task 3: Add URLs to launch tool responses** (AC: 1, 2, 3, 5, 7)
  - [x] 3.1 Update `src/tools/launches.py` `_launch_payload()` to include `url` when `id` and project context are available.
  - [x] 3.2 Because `_launch_payload()` currently receives only a launch object, change its signature to accept `base_url` and `project_id` or a compact URL context.
  - [x] 3.3 Add URLs to `create_launch`, `list_launches`, `get_launch`, `delete_launch`, `close_launch`, and `reopen_launch` outputs where applicable.
  - [x] 3.4 Keep runtime auth behavior in `_launch_client_context()` unchanged.

- [x] **Task 4: Add URLs to defect and defect-link responses** (AC: 1, 2, 3, 4, 5, 7)
  - [x] 4.1 Update `src/tools/defects.py` create/get/update/list/delete responses with defect URLs.
  - [x] 4.2 Update `link_defect_to_test_case` JSON payload to include both `defect_url` and `test_case_url`.
  - [x] 4.3 Update `list_defect_test_cases` items to include each linked test case URL and include the parent defect URL at the top level.
  - [x] 4.4 Do not add URLs to defect matcher responses unless a stable matcher browser URL is verified.

- [x] **Task 5: Add URLs to test plan and shared-step responses** (AC: 1, 2, 3, 5, 7)
  - [x] 5.1 Update `src/tools/plans.py` create/update/manage/list/delete responses with test plan URLs.
  - [x] 5.2 Refactor `src/tools/shared_steps.py` to use the shared helper for create output.
  - [x] 5.3 Add shared-step URLs to `list_shared_steps`, `update_shared_step`, and `delete_shared_step` responses where a step ID is present.
  - [x] 5.4 Preserve existing `create_shared_step` JSON contract fields: `id`, `name`, `project_id`, and `url`.

- [x] **Task 6: Verify or explicitly exclude other ID-bearing entities** (AC: 6)
  - [x] 6.1 Review ID-bearing tool outputs for `test_suite`, `test_layer`, `test_layer_schema`, `custom_field`, `custom_field_value`, `integration`, and `defect_matcher`.
  - [x] 6.2 For each entity, either verify a stable UI URL in the TestOps sandbox and add helper/tests, or document in this story's Dev Agent Record why no URL was added.
  - [x] 6.3 For test suites, prefer a verified tree/test-cases URL only if it reliably opens the suite node; otherwise do not invent a suite detail URL.

- [x] **Task 7: Add regression tests and docs** (AC: 1, 2, 3, 4, 5, 7)
  - [x] 7.1 Add focused unit tests for URL helper output.
  - [x] 7.2 Extend integration tests in `tests/integration/test_test_create_tool.py`, `tests/integration/test_launch_tools.py`, `tests/integration/test_defect_tools.py`, `tests/integration/test_plan_tools.py`, and `tests/integration/test_shared_step_tools.py`.
  - [x] 7.3 Update e2e tests that parse plain IDs only enough to assert URL presence without making them brittle.
  - [x] 7.4 Add JSON-mode tests proving URLs appear in payloads and nested collection items.
  - [x] 7.5 Update `docs/tools.md` to state that supported entity responses include TestOps browser URLs alongside IDs.

## Dev Notes

### Current Implementation Snapshot

- Tool output rendering is centralized in `src/tools/output_contract.py`.
- Tools still support only `plain|json`; do not add `table` or `csv` to tool-level output modes.
- `AllureClient` stores a normalized trailing-slash-free base URL and exposes it via `get_base_url()`.
- `AllureClient.get_project()` returns the resolved project for the active client, including explicit `project_id` overrides.
- `src/tools/shared_steps.py` already includes a local `_shared_step_url()` helper and an integration test proving `create_shared_step(..., output_format="json")` returns `https://example.com/project/456/settings/shared-steps/11`.
- Existing test case e2e tests parse IDs from plain text like `Created Test Case ID: 123 Name: ...`; preserve that substring and append URL information rather than rewriting the message format.

### URL Pattern Research

- User-provided verified test case example: `https://<testops-url>/project/<project-id>/test-cases/<test-case-id>`.
- Official Allure TestOps documentation describes project sections for Test cases, Launches, Defects, and Test plans; use their section names as the first-pass path names.
- Qameta Help Desk gives a concrete TestOps URL example for the test case section: `https://demo.testops.cloud/project/338/test-cases?treeId=0`, plus the deleted-list route `.../project/1/test-cases-list`.
- Existing project code already uses and tests shared-step URLs under `/project/<project_id>/settings/shared-steps/<step_id>`.
- Launch, defect, and test-plan direct detail paths are inferred from documented section names and common TestOps routing. Validate these against a sandbox instance during implementation; if a route redirects but still lands on the entity, keep it and document the behavior.

### Implementation Guardrails

- Add URLs in tools/serializers, not services. Services should continue returning structured API/domain data only.
- Prefer a small shared helper over copying f-strings across every tool module.
- Never expose API tokens or auth data in URLs.
- Do not fetch additional API data only to build URLs unless project ID is missing. The active client already knows base URL and project ID.
- Keep JSON compact rendering behavior unchanged; `url` fields naturally serialize through `render_output()`.
- For delete/confirmation responses, include URLs only when the response references a still meaningful entity. For already-deleted responses, a URL is acceptable if it points to the former entity and can aid user investigation, but tests should not require the object to exist.
- Do not treat external issue URLs in `links`/`issues` as TestOps entity URLs; those are separate user-supplied links.

### File Structure Requirements

- Primary helper:
  - `src/utils/links.py`
- Primary tools:
  - `src/tools/create_test_case.py`
  - `src/tools/search.py`
  - `src/tools/update_test_case.py`
  - `src/tools/delete_test_case.py`
  - `src/tools/launches.py`
  - `src/tools/defects.py`
  - `src/tools/plans.py`
  - `src/tools/shared_steps.py`
- Candidate review-only tools:
  - `src/tools/create_test_suite.py`
  - `src/tools/list_test_suites.py`
  - `src/tools/assign_test_cases_to_suite.py`
  - `src/tools/delete_test_suite.py`
  - `src/tools/create_test_layer.py`
  - `src/tools/list_test_layers.py`
  - `src/tools/create_test_layer_schema.py`
  - `src/tools/list_test_layer_schemas.py`
  - `src/tools/get_custom_fields.py`
  - `src/tools/list_custom_field_values.py`
  - `src/tools/list_integrations.py`
- Tests:
  - `tests/unit/test_links.py` or equivalent
  - `tests/integration/test_test_create_tool.py`
  - `tests/integration/test_launch_tools.py`
  - `tests/integration/test_defect_tools.py`
  - `tests/integration/test_plan_tools.py`
  - `tests/integration/test_shared_step_tools.py`
  - selected e2e files that already validate tool outputs
- Docs:
  - `docs/tools.md`

### Previous Story Intelligence

- Story 2 shared-step work established shared-step management and the current code already has URL output for `create_shared_step`.
- Story 5 launch work established `src/tools/launches.py` and `_launch_client_context()` for runtime auth/project resolution. Do not bypass that context.
- Story 7 defect work established `src/tools/defects.py`; extend it rather than creating a parallel defects module.
- Story 9.3 established the service-first CLI route model. Tool output changes flow through CLI rendering; do not add a CLI-specific URL layer.
- Story 9.6 established the tool output contract. This story adds fields/content within `plain|json`; it does not add output modes or alter CLI-only renderer boundaries.
- Current worktree already contains ready-for-dev Epic 9 story files and modified planning/status artifacts; do not reformat or revert unrelated edits.

### Testing Requirements

- Targeted validation commands after implementation:
  - `uv run --python 3.13 --extra dev pytest tests/unit/test_links.py tests/integration/test_test_create_tool.py tests/integration/test_launch_tools.py tests/integration/test_defect_tools.py tests/integration/test_plan_tools.py tests/integration/test_shared_step_tools.py -q`
  - `uv run --python 3.13 --extra dev pytest tests/e2e/test_tool_outputs.py tests/e2e/test_defect_management.py tests/e2e/test_launches.py tests/e2e/test_plan_management.py -q`
  - `uv run ruff check src/tools src/utils tests/unit tests/integration`
  - `uv run mypy src/tools src/utils`
- If e2e sandbox URL verification is not possible in the dev environment, mark the exact route patterns that still need manual UI verification in the Dev Agent Record.

### References

- [Source: specs/project-planning-artifacts/epics.md#Epic 10]
- [Source: specs/architecture.md#CLI Output Format Data Flow]
- [Source: specs/project-context.md#Critical Implementation Patterns]
- [Source: src/tools/output_contract.py]
- [Source: src/client/client.py]
- [Source: src/utils/links.py]
- [Source: src/tools/shared_steps.py]
- [Source: tests/integration/test_shared_step_tools.py]
- [Source: docs/tools.md]
- [External: Allure TestOps Test cases docs](https://docs.qameta.io/allure-testops/briefly/test-cases/)
- [External: Allure TestOps Launches docs](https://docs.qameta.io/allure-testops/briefly/launches/)
- [External: Allure TestOps Defects docs](https://docs.qameta.io/allure-testops/briefly/defects/)
- [External: Allure TestOps Test plans docs](https://docs.qameta.io/allure-testops/briefly/test-plans/)
- [External: Qameta Help Desk test-case URL example](https://help.qameta.io/support/solutions/articles/101000489484-how-to-restore-deleted-test-cases)

## Dev Agent Record

### Agent Model Used

GPT-5

### Debug Log References

- 2026-05-04: Added shared URL helper tests and confirmed initial red failure for missing helper imports.
- 2026-05-04: Added URL helpers and threaded resolved `base_url`/`project_id` through supported tool output serializers.
- 2026-05-04: Full validation passed by component: unit/integration, docs, CLI, e2e, and packaging suites.

### Implementation Plan

- Implement shared URL helpers in `src/utils/links.py` for test cases, launches, defects, test plans, and shared steps.
- Add URLs only in tool-layer serializers/output payloads so service return contracts stay unchanged.
- Preserve existing plain ID lines and add labeled URL lines below or after current output to avoid breaking parsers.
- Add JSON `url` fields for single-entity and collection item payloads; use explicit `defect_url` and `test_case_url` for mixed defect links.

### Completion Notes List

Ultimate context engine analysis completed - comprehensive developer guide created.

- Added shared TestOps entity URL helpers and reused them in shared-step output.
- Added resolved-context URLs to test case, launch, defect, test-plan, and shared-step tool responses for both `plain` and `json` output.
- Kept unsupported ID-bearing entities URL-free: test suites, test layers, test layer schemas, custom fields, custom field values, integrations, and defect matchers do not have verified stable detail routes in this implementation. Test suite tree-node URLs were intentionally not invented.
- Manual UI verification is still recommended for the inferred direct routes `/launches/<launch_id>`, `/defects/<defect_id>`, and `/test-plans/<plan_id>` in a TestOps browser sandbox. Test case and shared-step patterns have verified examples in project context/tests.
- Added Hatch build excludes for local `.codex` and cache/build artifacts after packaging validation exposed that workspace-local symlinks could enter sdists.
- Validation: `uv run --python 3.13 --extra dev pytest tests/unit/test_links.py tests/integration/test_test_create_tool.py tests/integration/test_launch_tools.py tests/integration/test_defect_tools.py tests/integration/test_plan_tools.py tests/integration/test_shared_step_tools.py -q` passed (41 passed).
- Validation: `uv run --python 3.13 --extra dev pytest tests/e2e/test_tool_outputs.py tests/e2e/test_defect_management.py tests/e2e/test_launches.py tests/e2e/test_plan_management.py -q` skipped all 9 tests without live e2e config in direct invocation.
- Validation: `uv run --python 3.13 --extra dev ruff check src/tools src/utils tests/unit tests/integration` passed.
- Validation: `uv run --python 3.13 --extra dev mypy src/tools src/utils` passed.
- Validation: full regression components passed: 496 unit/integration, 11 docs, 233 CLI, 113 e2e with 1 skip, and 34 packaging tests.

### File List

- docs/tools.md
- pyproject.toml
- specs/implementation-artifacts/10-1-include-testops-entity-urls-in-tool-responses.md
- specs/implementation-artifacts/sprint-status.yaml
- src/tools/create_test_case.py
- src/tools/defects.py
- src/tools/delete_test_case.py
- src/tools/launches.py
- src/tools/plans.py
- src/tools/search.py
- src/tools/shared_steps.py
- src/tools/update_test_case.py
- src/utils/__init__.py
- src/utils/links.py
- tests/e2e/test_create_test_case.py
- tests/e2e/test_tool_outputs.py
- tests/integration/test_defect_tools.py
- tests/integration/test_delete_tool.py
- tests/integration/test_integration_tools.py
- tests/integration/test_launch_tools.py
- tests/integration/test_plan_tools.py
- tests/integration/test_shared_step_tools.py
- tests/integration/test_test_create_tool.py
- tests/integration/test_test_update_tool.py
- tests/unit/test_launch_tools.py
- tests/unit/test_links.py
- tests/unit/test_search_service.py
- tests/unit/test_tool_structured_outputs.py

### Change Log

- 2026-05-04: Implemented TestOps entity URLs in supported tool responses and moved story to review.
