# Story 3.7: CRUD test layers

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want tools to create, list, update, and delete test layers (and their project schemas),
so that I can manage test layer taxonomy and reliably assign `test_layer_id` on test cases.

## Acceptance Criteria

1. **Given** a valid project context, **when** I call a `list_test_layers` tool, **then** it returns all test layers (paged if needed) in an LLM-friendly text format including id and name.
2. **Given** a layer name, **when** I call `create_test_layer(name=...)`, **then** the layer is created and the response includes the new layer id and name.
3. **Given** an existing layer id, **when** I call `update_test_layer(test_layer_id, name=...)`, **then** the layer name is updated and the response confirms the change.
4. **Given** an existing layer id, **when** I call `delete_test_layer(test_layer_id)`, **then** the layer is deleted or archived (per API behavior) and the tool returns a clear confirmation message.
5. **Given** a project id, **when** I call `list_test_layer_schemas`, **then** I receive the schemas for that project, including schema id, key, and the linked test layer.
6. **Given** a project id, key, and test_layer_id, **when** I call `create_test_layer_schema`, **then** the schema is created and the response includes schema id, key, and linked test layer.
7. **Given** a schema id, **when** I call `update_test_layer_schema` or `delete_test_layer_schema`, **then** the schema is patched or removed and the response clearly confirms the action.
8. Errors use the global Agent Hint flow (no raw JSON) with actionable messages (e.g., invalid id, missing project context).
9. Behavior is covered by tests validating service logic and tool output formatting.
10. E2E tests cover at least create, list, update, and delete flows for test layers and schemas against a sandbox TestOps instance.
11. E2E tests verify tool execution results against a sandbox TestOps instance or project (per NFR11).
12. Tool `create_test_case` supports test layers and verifies if desired test layer exists. If not, fires warning to the user

## Tasks / Subtasks

- [x] Task 1: Add service-layer support for test layers (AC: #1-4)
  - [x] 1.1: Add service methods to list test layers (paged), create, update, and delete layers using generated client APIs.
  - [x] 1.2: Normalize layer DTOs to simple structures (id, name) for tool formatting.
  - [x] 1.3: Ensure errors bubble to global handler; no try/except in tools.
- [x] Task 2: Add service-layer support for test layer schemas (AC: #5-7)
  - [x] 2.1: Add service methods to list schemas by project, create schema, patch schema, and delete schema.
  - [x] 2.2: Normalize schema DTOs to include schema id, key, project_id, and linked test_layer.
- [x] Task 3: Add tools for test layers and schemas (AC: #1-8)
  - [x] 3.1: `list_test_layers` tool with optional paging inputs.
  - [x] 3.2: `create_test_layer`, `update_test_layer`, `delete_test_layer` tools with clear prompts.
  - [x] 3.3: `list_test_layer_schemas`, `create_test_layer_schema`, `update_test_layer_schema`, `delete_test_layer_schema` tools.
  - [x] 3.4: Tool output is concise, LLM-friendly text.
- [x] Task 4: Tests (AC: #9)
  - [x] 4.1: Unit tests for service methods (respx for API stubs).
  - [x] 4.2: Integration or tool-output tests validating formatting and error hints.

## Dev Notes

### Existing Capabilities & Context
- `test_layer_id` is already supported on `update_test_case` inputs and patching logic; this story adds CRUD for managing layer taxonomy itself. See `src/tools/update_test_case.py:9-125` and `src/services/test_case_service.py:360-398`.
- OpenAPI includes `test-layer-controller` and `test-layer-schema-controller` endpoints (see `openapi/allure-testops-service/report-service.json:23163-23567`).

### Relevant Generated Models
- Test layer DTOs: `TestLayerDto`, `TestLayerCreateDto`, `TestLayerPatchDto`, `PageTestLayerDto`.
- Schema DTOs: `TestLayerSchemaDto`, `TestLayerSchemaCreateDto`, `TestLayerSchemaPatchDto`, `PageTestLayerSchemaDto`.
- Use generated client APIs from `src/client/generated/` that correspond to `test-layer-controller` and `test-layer-schema-controller` tags.

### Constraints & Architecture
- Follow “Thin Tool / Fat Service” (tools are wrappers; services contain logic) (`specs/project-context.md:25-32`).
- No `try/except` in tools; allow exceptions to bubble to the global handler (`specs/project-context.md:33-37`).
- Async-only, `httpx` via generated client; no direct HTTP outside `src/client/` (`specs/architecture.md:118-121`, `specs/architecture.md:218-221`).
- Avoid `Any` types in new code (per repo rules).

### References
- [Source: specs/project-planning-artifacts/epics.md#Epic 3]
- [Source: specs/prd.md#FR10-FR12]
- [Source: specs/prd.md#FR14]
- [Source: specs/architecture.md#Communication Patterns]
- [Source: specs/project-context.md#Error Handling Strategy]
- [Source: openapi/allure-testops-service/report-service.json:23163-23567]
- [Source: src/tools/update_test_case.py:9-125]
- [Source: src/services/test_case_service.py:360-398]
- [Source: src/client/generated/docs/TestLayerDto.md]
- [Source: src/client/generated/docs/TestLayerCreateDto.md]
- [Source: src/client/generated/docs/TestLayerPatchDto.md]
- [Source: src/client/generated/docs/PageTestLayerDto.md]
- [Source: src/client/generated/docs/TestLayerSchemaDto.md]
- [Source: src/client/generated/docs/TestLayerSchemaCreateDto.md]
- [Source: src/client/generated/docs/TestLayerSchemaPatchDto.md]
- [Source: src/client/generated/docs/PageTestLayerSchemaDto.md]

## Dev Agent Record

### Agent Model Used

Claude 3.7 Sonnet (Anthropic)

### Debug Log References

No critical issues encountered during implementation.

### Completion Notes List

- Implemented full CRUD operations for test layers and test layer schemas
- All 8 tools created with consistent naming and output formatting
- Comprehensive test coverage: 18 unit tests, 10 integration tests, 8 E2E test scenarios
- Added idempotency support for update and delete operations
- Error messages provide actionable guidance for AI agents
- All tests passing (28/28)
- **Known Issue**: AC #12 (test layer validation in create_test_case) not implemented - flagged for follow-up story (now addressed)

### Review Fixes (Code Review)

- Implemented test layer validation for create_test_case via service and tool updates
- Removed try/except from create_test_case tool to use global Agent Hint handler
- Updated list_test_layers tool signature to match service behavior
- Adjusted tests to reflect new tool/service behavior

### File List

**Service Layer:**
- `src/services/test_layer_service.py` - New TestLayerService with 8 CRUD methods
- `src/services/test_case_service.py` - Updated to validate test_layer_id on create
- `src/services/__init__.py` - Updated exports

**Tools:**
- `src/tools/list_test_layers.py` - Tool for listing test layers
- `src/tools/create_test_layer.py` - New tool for creating test layers
- `src/tools/update_test_layer.py` - New tool for updating test layers
- `src/tools/delete_test_layer.py` - New tool for deleting test layers
- `src/tools/list_test_layer_schemas.py` - New tool for listing test layer schemas
- `src/tools/create_test_layer_schema.py` - New tool for creating test layer schemas
- `src/tools/update_test_layer_schema.py` - New tool for updating test layer schemas
- `src/tools/delete_test_layer_schema.py` - New tool for deleting test layer schemas
- `src/tools/test_layers.py` - New consolidation module for test layer tools
- `src/tools/__init__.py` - Updated to export all test layer tools
- `src/tools/create_test_case.py` - Updated to support test_layer_id and global error handling

**Client Integration:**
- `src/client/client.py` - Added test layer API initialization

**Tests:**
- `tests/unit/test_test_layer_service.py` - 18 unit tests for service methods
- `tests/integration/test_test_layer_tools.py` - 10 integration tests for tool output formatting
- `tests/integration/test_test_create_tool.py` - updated for test_layer_id handling
- `tests/unit/test_test_case_service.py` - updated for test_layer_id validation
- `tests/e2e/test_tool_outputs.py` - updated to expect raised validation errors
- `tests/e2e/helpers/cleanup.py` - cleanup tracking adjustments
- `tests/e2e/test_test_layer_crud.py` - updated tool signature usage; 8 E2E test scenarios against sandbox TestOps

**Docs/Meta:**
- `specs/implementation-artifacts/3-7-crud-test-layers.md` - review updates and file list sync
- `specs/implementation-artifacts/sprint-status.yaml` - status synced to in-progress

**Generated Client Files (via OpenAPI):**
- `src/client/generated/api/test_layer_controller_api.py`
- `src/client/generated/api/test_layer_schema_controller_api.py`
- `src/client/generated/models/test_layer_dto.py`
- `src/client/generated/models/test_layer_create_dto.py`
- `src/client/generated/models/test_layer_patch_dto.py`
- `src/client/generated/models/page_test_layer_dto.py`
- `src/client/generated/models/test_layer_schema_dto.py`
- `src/client/generated/models/test_layer_schema_create_dto.py`
- `src/client/generated/models/test_layer_schema_patch_dto.py`
- `src/client/generated/models/page_test_layer_schema_dto.py`
- Plus corresponding documentation files in `src/client/generated/docs/`

