# Story 8.5: Implement telemetry collection

Status: review

## Story

As a Lucius maintainer,  
I want privacy-preserving telemetry collection integrated with runtime and tool usage,  
so that I can understand real-world usage patterns and prioritize product improvements without collecting sensitive data.

## Acceptance Criteria

1. **Telemetry transport via Umami**
   - **Given** telemetry is enabled by default in `src/utils/config.py`
   - **And** Umami settings are configured
   - **When** Lucius emits telemetry events
   - **Then** events are sent to Umami using `POST /api/send`
   - **And** each request includes a valid `User-Agent` header
   - **And** request failures never break tool execution or server startup

2. **Startup telemetry event**
   - **Given** Lucius server starts
   - **When** telemetry is enabled
   - **Then** a startup event is emitted with these fields:
     - `lucius_version`
     - `python_version`
     - `platform`
     - `mcp_mode` (`stdio` or `http`)
     - `deployment_method` (`docker`, `mcpb`, `uvx+pypi`, `cli`, or `plain-code-checkout`)

3. **Tool usage telemetry event**
   - **Given** any MCP tool is invoked
   - **When** execution finishes (success or failure)
   - **Then** a tool-usage event is emitted containing:
     - `tool_name`
     - `outcome` (`success` or `error`)
     - shared runtime fields from AC #2
   - **And** telemetry emission is best-effort and non-blocking for tool output

4. **Sensitive data hashing**
   - **Given** telemetry payload may include environment-derived identifiers
   - **When** payload is constructed
   - **Then** sensitive identifiers are hashed before sending (for example project id and endpoint host)
   - **And** plaintext secret/token values are never included

5. **Silent failure behavior**
   - **Given** telemetry endpoint is unavailable, misconfigured, or rate-limited
   - **When** telemetry emission fails
   - **Then** Lucius continues normal behavior
   - **And** failure is logged at debug/warning level without noisy stack traces by default

6. **Telemetry opt-out flag**
   - **Given** telemetry can be disabled by configuration
   - **When** telemetry is disabled via `TelemetryConfig.enabled = False` or `TELEMETRY_ENABLED=false`
   - **Then** no telemetry HTTP request is made
   - **And** startup and tool execution continue unchanged

7. **Recommended metrics coverage**
   - **Given** telemetry events are implemented
   - **When** startup and tool events are emitted
   - **Then** they include an agreed baseline metrics set:
     - runtime context metrics
     - tool usage metrics
     - outcome and latency metrics
   - **And** payload excludes sensitive business/user content

8. **Configuration and startup behavior clarity**
   - **Given** telemetry defaults are resolved from `src/utils/config.py`
   - **When** Lucius starts
   - **Then** runtime behavior is explicit and deterministic:
     - telemetry is enabled by default
     - `TelemetryConfig.enabled = False` disables emission globally
     - `TELEMETRY_ENABLED` can override enabled/disabled mode per runtime environment
     - startup logs include a concise telemetry status line (`enabled`/`disabled`) without sensitive values

9. **Privacy documentation**
   - **Given** telemetry behavior is implemented
   - **When** reading project configuration documentation
   - **Then** docs clearly describe:
     - what is collected
     - what is hashed
     - how to opt out
     - what is explicitly not collected
   - **And** docs include a dedicated telemetry subsection in both `README.md` and `docs/setup.md`

10. **Automated tests**
   - **Given** telemetry implementation is complete
   - **When** unit/integration tests run
   - **Then** tests cover payload schema, hashing, opt-out behavior, silent-failure behavior, and tool event emission wrapping
   - **And** tests verify startup telemetry status behavior for enabled and disabled modes

## Tasks / Subtasks

- [x] Task 1: Add telemetry configuration surface (AC: #1, #6, #8)
  - [x] 1.1 Add telemetry config structure in `src/utils/config.py`:
    - [x] `enabled` (bool, default `True`; opt-out)
    - [x] `umami_base_url` (default `https://cloud.umami.is`)
    - [x] `umami_website_id` (optional string)
    - [x] `umami_hostname` (default hostname string)
    - [x] `hash_salt` (optional string)
  - [x] 1.2 Document telemetry config usage in `README.md` and `docs/setup.md`; add `TELEMETRY_ENABLED` runtime override in `.env.example`

- [x] Task 2: Implement telemetry service (AC: #1, #2, #3, #4, #5)
  - [x] 2.1 Create `src/services/telemetry_service.py` (thin integration API, full logic in service)
  - [x] 2.2 Add event payload builder for startup and tool events
  - [x] 2.3 Add deterministic hashing helper (SHA-256, salt-aware)
  - [x] 2.4 Add Umami sender using the `umami-python` async API client
  - [x] 2.5 Ensure all send errors are swallowed after log emission

- [x] Task 3: Detect deployment/runtime context (AC: #2)
  - [x] 3.1 Add deployment detection helper:
    - [x] `docker` detection (`/.dockerenv` and container heuristics)
    - [x] `mcpb` detection (bundle/runtime path markers)
    - [x] `uvx+pypi` detection (runtime command heuristics)
    - [x] `cli` detection (installed script execution)
    - [x] fallback `plain-code-checkout`
  - [x] 3.2 Persist detection rules in service docstrings/comments for maintainability

- [x] Task 4: Hook telemetry into startup and tool execution (AC: #2, #3, #5)
  - [x] 4.1 Emit startup event in `src/main.py` at application startup path
  - [x] 4.2 Wrap tool registration so each tool call emits success/error telemetry event
  - [x] 4.3 Guarantee wrapper does not alter returned tool text or raised domain exceptions

- [x] Task 5: Implement opt-out behavior (AC: #6)
  - [x] 5.1 Add single guard (`is_enabled`) in telemetry service
  - [x] 5.2 Ensure all emit entry points short-circuit when disabled
  - [x] 5.3 Add explicit startup log line indicating telemetry enabled/disabled
  - [x] 5.4 Ensure startup status line does not leak endpoint query params, tokens, or other sensitive config values

- [x] Task 6: Documentation updates (AC: #9)
  - [x] 6.1 Update `README.md` with a dedicated telemetry subsection under configuration/privacy
  - [x] 6.2 Update `docs/setup.md` telemetry section to document `TelemetryConfig` (code-based defaults and opt-out)
  - [x] 6.3 Add a telemetry data dictionary table (field, purpose, sample value, sensitive/hashed flag)
  - [x] 6.4 Add short privacy note in `docs/development.md` for contributors

- [x] Task 7: Tests (AC: #10)
  - [x] 7.1 Add `tests/unit/test_telemetry_service.py`:
    - [x] payload fields
    - [x] hashing behavior
    - [x] opt-out short-circuit
    - [x] silent failure guarantees
  - [x] 7.2 Extend `tests/unit/test_main.py` for startup/tool wrapper emission flow and startup telemetry status logging
  - [x] 7.3 Add `tests/integration/test_telemetry_integration.py` with mocked Umami endpoint (`respx`)
  - [x] 7.4 Verify no regression in existing tool output and lifecycle tests

- [x] Task 8: Baseline metric set implementation (AC: #7)
  - [x] 8.1 Add startup metrics payload fields (version/runtime/deployment context)
  - [x] 8.2 Add tool metrics payload fields (tool name/outcome/duration bucket)
  - [x] 8.3 Add error classification field (`validation`, `auth`, `api`, `unexpected`)
  - [x] 8.4 Validate payload does not include tool arguments, token values, or raw endpoint paths with secrets

## Dev Notes

### Developer Context (Guardrails)

- Keep MCP tools thin. Telemetry logic belongs in service/util layers, not tool functions.
- Do not introduce synchronous HTTP calls; telemetry transport must use async `httpx`.
- Never leak token values or raw secrets in telemetry payloads or logs.
- Telemetry must be best-effort only. A telemetry outage must not fail user-facing operations.

### Technical Requirements

- Umami ingestion endpoint: `POST /api/send`.
- Payload shape includes `type: "event"` and `payload` object with event metadata.
- Umami requires a proper `User-Agent` header for event registration.
- Event naming should stay concise and stable (for example `lucius_startup`, `lucius_tool_use`).
- Telemetry must be enabled by default, disabled via `TelemetryConfig.enabled = False`, and overridable via `TELEMETRY_ENABLED`.
- Startup path must emit a concise telemetry status log entry that confirms the resolved mode without exposing sensitive values.

### Recommended Metrics

- Runtime context:
  - `lucius_version`
  - `python_version`
  - `platform` (OS family + architecture)
  - `mcp_mode`
  - `deployment_method`
- Lifecycle:
  - startup event count
  - process start timestamp (or derived session id)
  - uptime bucket at shutdown (if shutdown event is added later)
- Tool usage:
  - `tool_name`
  - invocation count
  - outcome (`success`/`error`)
  - duration bucket (`<100ms`, `100-500ms`, `500ms-2s`, `>2s`)
  - error category (`validation`, `auth`, `api`, `unexpected`) when failed
- Adoption/footprint:
  - hashed installation identifier
  - hashed project identifier
- Privacy constraints:
  - do not collect tool arguments/values
  - do not collect test case names/descriptions/step text
  - do not collect API tokens, raw headers, or full endpoint URLs with credentials

### Architecture Compliance

- Follow existing "Thin Tool / Fat Service" pattern.
- Integrate at runtime registration boundary in `src/main.py` instead of duplicating logic across all tools.
- Reuse existing logging config (`src/utils/logger.py`) and avoid ad hoc logging styles.

### Library/Framework Requirements

- Use existing project stack only:
  - `umami-analytics` (`umami-python`) for telemetry transport
  - `pydantic-settings` for config
  - `pytest` + `respx` for tests
- No new external telemetry SDK should be introduced for this story.

### File Structure Requirements

New/updated files expected:
- `src/services/telemetry_service.py` (new)
- `src/services/__init__.py` (update export)
- `src/utils/config.py` (new telemetry settings)
- `src/utils/telemetry.py` (tool wrapper helper)
- `src/main.py` (startup + tool wrapper hooks)
- `tests/unit/test_telemetry_service.py` (new)
- `tests/integration/test_telemetry_integration.py` (new)
- `tests/unit/test_main.py` (update)
- `README.md` (update)
- `docs/setup.md` (update)
- `docs/development.md` (update)

### Testing Requirements

- Run unit + integration:
  - `uv run --env-file .env.test pytest tests/unit tests/integration`
- Run docs + packaging:
  - `uv run pytest tests/docs`
  - `uv run pytest tests/packaging`
- Optional full suite:
  - `bash scripts/full-test-suite.sh`

### Project Context Reference

- Enforce constraints from `specs/project-context.md`:
  - async-only IO
  - strict typing
  - no `Any`
  - no bypassing lint/type checks

### References

- Runtime entrypoint: `src/main.py`
- Config model: `src/utils/config.py`
- Logging: `src/utils/logger.py`
- Packaging manifests: `deployment/mcpb/manifest.uv.json`, `deployment/mcpb/manifest.python.json`
- Umami sending stats API: `https://docs.umami.is/docs/api/sending-stats`

## Story Completion Status

- Status: review

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `uv run ruff check src/main.py src/services/telemetry_service.py src/utils/config.py src/services/__init__.py tests/unit/test_main.py tests/unit/test_telemetry_service.py tests/integration/test_telemetry_integration.py`
- `uv run mypy src`
- `uv run --env-file .env.test pytest tests/unit/test_main.py tests/unit/test_telemetry_service.py tests/integration/test_telemetry_integration.py -q`
- `uv run --env-file .env.test pytest tests/unit tests/integration -q`
- `uv run pytest tests/docs -q`
- `uv run pytest tests/packaging -q`

### Completion Notes List

- Implemented a new telemetry service with Umami `POST /api/send` transport, deterministic hashing, runtime/deployment context detection, and non-blocking best-effort dispatch.
- Implemented Umami telemetry transport through the `umami-python` client API.
- Added startup and per-tool telemetry instrumentation in `src/main.py` while preserving tool outputs/exceptions and logging concise telemetry status (`enabled`/`disabled`).
- Moved telemetry configuration defaults to `src/utils/config.py` (`TelemetryConfig`) and added `TELEMETRY_ENABLED` runtime opt-out override.
- Added unit/integration tests for payload shape, hashing, opt-out, silent-failure behavior, and runtime instrumentation flow.
- Added startup status assertions for both telemetry-enabled and telemetry-disabled startup modes.
- Added explicit async fire-and-forget telemetry scheduling coverage; no shutdown flush is used by design to preserve non-blocking behavior.
- Verified no regressions: full `tests/unit` + `tests/integration` + `tests/docs` + `tests/packaging` all pass.

### File List

- .env.example
- .gitignore
- README.md
- docs/development.md
- docs/setup.md
- src/main.py
- src/services/__init__.py
- src/services/telemetry_service.py
- src/utils/config.py
- src/utils/telemetry.py
- pyproject.toml
- tests/integration/test_telemetry_integration.py
- tests/e2e/test_telemetry_collection_e2e.py
- tests/unit/test_main.py
- tests/unit/test_telemetry_service.py
- specs/implementation-artifacts/issue-64-implement-telemetry-collection.md (superseded by 8-5 story file)
- specs/implementation-artifacts/sprint-status.yaml
- specs/implementation-artifacts/8-5-implement-telemetry-collection.md

### Change Log

- 2026-03-02: Implemented telemetry collection for startup and tool usage with privacy-preserving hashing, documentation updates, and comprehensive automated tests.
