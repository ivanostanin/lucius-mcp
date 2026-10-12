---
title: 'Preserve structured MCP output in plain presentation mode'
type: 'bugfix'
created: '2026-10-12'
status: 'done'
baseline_commit: 'd5f8eceeec8c3b63514cdd5d753b13bff6046134'
context: []
---

<frozen-after-approval reason="human-owned intent — issue reproduction and fix authorized by user">

## Intent

**Problem:** Issue #436 reports that `get_test_case_details` succeeds with JSON output but fails with plain output because its successful MCP response lacks the structured content required by its advertised output schema. This was reproduced on v0.16.4 with an in-memory MCP client and synthetic TestOps details: JSON validates and plain raises the reported missing-structured-content error.

**Approach:** Preserve the original structured payload alongside the existing human-readable text when a tool runs through the schema-bearing MCP registration boundary. Keep the existing CLI and direct-call output formats, using the single service execution that already produces both presentations.

## Boundaries & Constraints

**Always:** Successful MCP responses must satisfy each tool's declared schema for every presentation format. Direct and CLI plain calls must continue returning strings. Preserve payload shape, explicit null fields, text formatting, metadata, error results, and request isolation. Validate successful MCP structured payloads using the existing Pydantic model boundary. Respect the telemetry privacy constraints in `docs/development.md`.

**Ask First:** Changes to the public tool signatures or schemas, CLI behavior, dependencies, or unrelated service behavior require a new scope decision.

**Never:** Execute a tool twice to recover its payload, parse human-readable text into structured fields, modify generated TestOps client models, expose private TestOps data, or use process-wide mutable request state. Do not change the default output format or expand supported presentation formats.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| MCP plain success | Registered tool, `output_format="plain"` | Existing text plus original schema-valid structured payload | Payload validation remains enforced |
| MCP JSON or default | Registered tool, JSON or omitted format | Existing structured payload, no added text | Existing validation behavior |
| Direct or CLI plain | Tool called outside MCP wrapper | Existing plain string | Existing exception behavior |
| Mutation | Plain MCP tool changes data | One execution, both presentations of that result | Never repeat mutation |
| Empty or confirmation response | Shared collection or confirmation helper in MCP plain mode | Existing text and valid branch-specific payload | Normal successful protocol result |
| Tool exception or explicit error | Tool raises, or returns an error result | Ordinary MCP error behavior | No successful-output-schema requirement for error results |
| Concurrent requests | MCP and direct calls overlap | MCP presentation state does not affect direct calls | Restore caller context on every exit |

</frozen-after-approval>

## Code Map

- `src/tools/output_contract.py` -- all registered tools use shared rendering helpers; plain currently discards `json_payload`.
- `src/utils/telemetry.py` -- MCP-only registration wrapper and Pydantic validation; currently converts strings to text-only results.
- `src/main.py` -- registers each tool with a schema and telemetry wrapper; should retain existing registration metadata.
- `src/tools/search.py` -- reported tool assembles both details presentations after one service call.
- `tests/unit/test_tool_structured_outputs.py` -- existing plain `Tool.run` test explicitly expects missing structured content and bypasses protocol validation.
- `tests/unit/test_output_contract.py` -- direct helper contracts and format validation.
- `tests/cli/` and `tests/e2e/test_cli_output_formats_uv_run.py` -- plain string rendering and CLI output compatibility.
- `docs/tools.md` -- public description of tool presentation behavior.

## Tasks & Acceptance

**Execution:**
- [x] `src/tools/output_contract.py` -- add request-local MCP rendering context and retain text plus original payload for plain output only inside that context; apply consistently to shared helpers.
- [x] `src/utils/telemetry.py` -- establish and restore that context around one tool execution when a schema model is provided; preserve output validation, metadata, and normal errors.
- [x] `tests/unit/test_tool_structured_outputs.py` -- replace the obsolete text-only assertion, add actual in-memory MCP client coverage for details in all formats, verify one mutation execution, context restoration/isolation, and errors.
- [x] `tests/unit/test_output_contract.py` -- verify shared helper rendering and direct plain compatibility, including newline normalization and collection/confirmation branches.
- [x] `docs/tools.md` -- document MCP plain text plus structured content and unchanged CLI plain rendering.

**Acceptance Criteria:**
- Given the published schema for `get_test_case_details`, when an MCP client calls the same synthetic case and project with default, JSON, and plain formats, then all successful responses validate and have identical structured payloads.
- Given a mutation tool using shared rendering helpers, when called once in plain MCP mode, then its service executes once and the result includes both presentations.
- Given overlapping MCP and direct calls, when rendering completes or raises, then direct plain results remain strings and no context leaks into later calls.
- Given normal error behavior, when a tool fails or returns an explicit error result, then the MCP client receives the ordinary error response without a missing-structured-content failure.

## Spec Change Log

- 2026-10-12: Blind, edge-case, and acceptance reviews found no actionable source defects. Clarified successful-response documentation, bounded concurrency-test waits, and added MCP client coverage for empty collections and confirmation responses. All captured intent and implementation constraints remain unchanged.

## Design Notes

Use a dedicated `ContextVar` for the MCP output boundary. It has different semantics from the existing direct-CLI attachment lifetime flag. Keep the structured payload at rendering time, where both presentations already exist, rather than reconstructing it after plain formatting. The telemetry wrapper supplies the narrowly scoped context and its `finally` block restores the previous value even on cancellation or failure.

FastMCP passes a prebuilt `ToolResult` through `Tool.run` without enforcing its schema. Regression coverage must therefore include `Client(FastMCP(...))`, whose MCP session validates successful results against advertised schemas. Synthetic backend fixtures make this deterministic without TestOps credentials. Tool signatures and published schemas remain unchanged, so manifest regeneration should produce no contract diff.

## Verification

**Completed checks:**
- `uv run pytest tests/unit/test_output_contract.py tests/unit/test_tool_structured_outputs.py tests/unit/test_main.py tests/cli -q` -- 288 focused output, wrapper, telemetry, and CLI checks pass.
- `uv run pytest tests/e2e/test_cli_output_formats_uv_run.py -q` -- 9 source-invoked CLI format checks pass.
- `uv run ruff format --check src/tools/output_contract.py src/utils/telemetry.py tests/unit/test_output_contract.py tests/unit/test_tool_structured_outputs.py` -- touched files pass formatting.
- `uv run ruff check src/tools/output_contract.py src/utils/telemetry.py tests/unit/test_output_contract.py tests/unit/test_tool_structured_outputs.py` -- touched files pass lint.
- `uv run mypy --strict src/tools/output_contract.py src/utils/telemetry.py` -- both changed source files pass strict type checks.
- `uv run ruff check .` and `uv run ruff format --check .` -- repository lint and formatting pass (289 formatted files), verified by the coordinating agent.
- `uv run mypy --strict src/` -- all 103 source files pass strict typing, verified by the coordinating agent.
- `uv run pytest tests/unit/test_output_contract.py tests/unit/test_tool_structured_outputs.py -q` -- 24 checks pass after review additions.
- `uv run pytest tests/unit tests/integration tests/docs tests/packaging --ignore=tests/packaging/test_cli_binaries.py -q` -- 1,257 checks pass; three existing FastMCP annotation deprecation warnings.

Live TestOps E2E tests and prebuilt CLI binary tests were not run. The issue was reproduced through the MCP protocol with synthetic TestOps responses; no private instance data was needed.

## Suggested Review Order

- Scope the MCP presentation context around one tool execution.
  [telemetry.py:37](../../src/utils/telemetry.py#L37)

- Retain both presentations while preserving direct plain strings.
  [output_contract.py:80](../../src/tools/output_contract.py#L80)

- Validate successful payloads and preserve ordinary error results.
  [telemetry.py:66](../../src/utils/telemetry.py#L66)

- Exercise the reported tool through actual MCP client schema validation.
  [test_tool_structured_outputs.py:181](../../tests/unit/test_tool_structured_outputs.py#L181)

- Prove a plain MCP mutation invokes its service exactly once.
  [test_tool_structured_outputs.py:213](../../tests/unit/test_tool_structured_outputs.py#L213)

- Document successful MCP and direct plain presentation behavior.
  [tools.md:6](../../docs/tools.md#L6)

