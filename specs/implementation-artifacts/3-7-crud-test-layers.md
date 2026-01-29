# Story 3.7: CRUD test layers

Status: ready-for-dev

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

- [ ] Task 1: Add service-layer support for test layers (AC: #1-4)
  - [ ] 1.1: Add service methods to list test layers (paged), create, update, and delete layers using generated client APIs.
  - [ ] 1.2: Normalize layer DTOs to simple structures (id, name) for tool formatting.
  - [ ] 1.3: Ensure errors bubble to global handler; no try/except in tools.
- [ ] Task 2: Add service-layer support for test layer schemas (AC: #5-7)
  - [ ] 2.1: Add service methods to list schemas by project, create schema, patch schema, and delete schema.
  - [ ] 2.2: Normalize schema DTOs to include schema id, key, project_id, and linked test_layer.
- [ ] Task 3: Add tools for test layers and schemas (AC: #1-8)
  - [ ] 3.1: `list_test_layers` tool with optional paging inputs.
  - [ ] 3.2: `create_test_layer`, `update_test_layer`, `delete_test_layer` tools with clear prompts.
  - [ ] 3.3: `list_test_layer_schemas`, `create_test_layer_schema`, `update_test_layer_schema`, `delete_test_layer_schema` tools.
  - [ ] 3.4: Tool output is concise, LLM-friendly text.
- [ ] Task 4: Tests (AC: #9)
  - [ ] 4.1: Unit tests for service methods (respx for API stubs).
  - [ ] 4.2: Integration or tool-output tests validating formatting and error hints.

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

gpt-5.2-codex

### Debug Log References

### Completion Notes List

### File List

