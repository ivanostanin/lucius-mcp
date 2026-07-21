# Story 7.8: Test Code Generation Selection Options

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **AI Agent**,
I want to **select the target language, compatible test framework, and test-case metadata included when generating code**,
so that **the generated scaffold matches my automation stack and contains only the attributes I intend to synchronize**.

## Acceptance Criteria

1. **Publish constrained language selections**
   - **Given** a caller inspects the `generate_test_code` tool schema or documentation
   - **When** it reviews the `language` argument
   - **Then** it can discover these seven user-facing selections: `Java`, `Python`, `TypeScript`, `JavaScript`, `Kotlin`, `PHP`, and `.NET`
   - **And** each selection maps to an explicitly verified TestOps API wire value rather than a value guessed by lowercasing the label
   - **And** the current `python`, `ts`, and `java` inputs remain accepted through documented canonical values or backward-compatible aliases
   - **And** an omitted, blank, or unsupported language fails before an API call with an Agent Hint listing the supported selections.

2. **Publish framework selections without inventing compatibility**
   - **Given** the user-provided TestOps screenshot has `TypeScript` selected
   - **When** a caller inspects the framework choices available for that language
   - **Then** the documented TypeScript-visible choices are `CodeceptJS`, `Cucumber`, `Jasmine`, `Jest`, `Mocha`, `Playwright`, `Vitest`, `WebdriverIO`, and `ZeroStep`
   - **And** the existing `python`/`pytest`, `ts`/`playwright`, and `java`/`junit` public behavior is not removed
   - **And** Lucius does not claim that the screenshot's TypeScript-visible frameworks are compatible with every language
   - **And** verified language/framework pairs are normalized to their exact TestOps wire values
   - **And** a known-incompatible or unsupported pair fails without an API call and identifies the allowed frameworks for the selected language
   - **And** an omitted or blank framework fails before an API call with an Agent Hint listing the compatible choices for the selected language
   - **And** where TestOps remains the source of truth for an unverified pair, its validation error continues to surface as an actionable Agent Hint.

3. **Support metadata multi-selection**
   - **Given** the `metadata` argument is supplied to `generate_test_code`
   - **When** it contains any subset of `Name`, `Tags`, `Custom fields`, `Members`, `Issues`, and `Scenario`
   - **Then** only the selected attributes are enabled in the request to `POST /api/ide/testcase/{id}/testcode`
   - **And** every deselected attribute is explicitly disabled
   - **And** the verified mappings include `Name` -> `syncName`, `Tags` -> `syncTags`, `Custom fields` -> `syncFields`, and `Scenario` -> `syncScenario`
   - **And** the wire fields for `Members` and `Issues` are captured from a real TestOps request or otherwise verified against the target TestOps version before the overlay is changed; guessed field names are not acceptable
   - **And** selection order does not affect the payload, duplicate values are normalized, and unsupported values fail before an API call
   - **And** an explicit empty selection is supported and sends all verified synchronization flags as `false`.

4. **Require an explicit generation target and infer only metadata defaults**
   - **Given** `language` or `framework` is omitted
   - **When** code is generated
   - **Then** validation fails before an API call and instructs the caller to provide both selections
   - **And** neither the tool nor the service infers Python/Pytest or any other language/framework pair
   - **Given** language and framework are supplied but `metadata` is omitted
   - **When** code is generated
   - **Then** metadata defaults to the screenshot selection: `Name`, `Tags`, `Custom fields`, and `Scenario` selected; `Members` and `Issues` not selected
   - **And** omission is distinguishable from an explicitly empty metadata selection
   - **And** callers must explicitly provide language and framework on every invocation.

5. **Preserve output contracts**
   - **Given** generation succeeds with any supported selection
   - **When** `output_format="plain"` is requested
   - **Then** the generated source is returned verbatim, including literal escape sequences such as `\\n`
   - **And** the generic plain-text renderer is not used for generated source
   - **When** structured JSON is requested
   - **Then** the response retains `test_case_id`, `language`, `framework`, and `code`
   - **And** it adds the resolved metadata selection in deterministic canonical order
   - **And** the registered output schema and generated MCP manifest match the actual payload.

6. **Keep the generated-client boundary intact**
   - **Given** the IDE endpoint is maintained as a local OpenAPI overlay because it is absent from the public TestOps OpenAPI document
   - **When** verified member/issue synchronization fields are added
   - **Then** `scripts/filter_openapi.py` is updated first
   - **And** the filtered specification and `src/client/generated/` client are regenerated with the existing generation script
   - **And** generated files are never edited manually
   - **And** `TestCodeService` owns normalization, compatibility validation, metadata mapping, and request construction while the MCP tool remains a thin adapter.

7. **Verify selections end to end**
   - **Given** automated validation runs
   - **Then** unit tests cover every metadata flag, omitted/empty/all/subset selections, deterministic normalization, duplicate selections, invalid values, known-incompatible pairs, backward-compatible aliases, and absence of API calls after local validation failures
   - **And** integration tests cover tool-to-service argument wiring, structured output, and lossless plain output
   - **And** published-schema tests prove that the MCP schema exposes selectable language, framework, and metadata values
   - **And** a live sandbox E2E test covers at least TypeScript + Playwright with `Name`, `Tags`, `Custom fields`, and `Scenario` selected
   - **And** agentic workflow documentation, user documentation, and generated manifests are updated.

8. **Exercise every verified generation pair in the live sandbox**
   - **Given** the complete compatibility matrix verified from the target TestOps version
   - **When** the live TestOps E2E suite runs
   - **Then** it generates code successfully for all 32 supported pairs: Java (`JUnit 5`, `JUnit 4`, `TestNG`, `Cucumber`); Python (`Behave`, `Pytest`, `Pytest BDD`); TypeScript (`CodeceptJS`, `Cucumber`, `Jasmine`, `Jest`, `Mocha`, `Playwright`, `Vitest`, `WebdriverIO`, `ZeroStep`); JavaScript (`CodeceptJS`, `Cucumber`, `Jasmine`, `Jest`, `Mocha`, `Playwright`, `Vitest`, `WebdriverIO`); Kotlin (`JUnit 5`, `JUnit 4`, `TestNG`); PHP (`PHPUnit`, `Codeception`); and .NET (`NUnit`, `XUnit`, `SpecFlow`)
   - **And** each parameterized case uses the verified wire values and the story-default metadata selection: `Name`, `Tags`, `Custom fields`, and `Scenario`

## Tasks / Subtasks

- [x] **1. Verify the private TestOps request contract** (AC: 1-3, 6)
  - [x] Capture the request produced by the TestOps **Generate code** dialog for representative selections without recording credentials, headers, or business content.
  - [x] Record the exact wire tokens and capitalization for all seven language labels.
  - [x] Record the exact wire tokens for the nine TypeScript-visible framework labels.
  - [x] Toggle `Members` and `Issues` independently and verify their actual request fields and boolean semantics.
  - [x] Confirm that all six metadata flags are sent explicitly when deselected; do not infer missing-field semantics.
  - [x] Document the verified label-to-wire mappings in code comments/tests so future UI label changes do not silently alter the API contract.

- [x] **2. Extend the OpenAPI overlay and regenerate the client** (AC: 3, 6)
  - [x] Update `TestCodeGenerationRequestDto` in `scripts/filter_openapi.py` with the verified member/issue fields.
  - [x] Keep all request fields typed and required if the observed endpoint always sends explicit booleans.
  - [x] Run `./scripts/generate_testops_api_client.sh`.
  - [x] Review the filtered spec and generated DTO diff; do not hand-edit `src/client/generated/`.

- [x] **3. Add selection models and service behavior** (AC: 1-4, 6)
  - [x] Define schema-friendly language, framework, and metadata selection types in the existing test-code feature boundary.
  - [x] Keep UI labels separate from verified API wire values.
  - [x] Preserve verified aliases while requiring callers to supply both language and framework; remove their function defaults.
  - [x] Implement metadata `None`/omitted semantics separately from an explicit empty collection; avoid mutable argument defaults.
  - [x] Build every request with explicit booleans for all six verified metadata fields.
  - [x] Add only verified language/framework compatibility rules; retain TestOps API validation for combinations not proven by available UX/API evidence.
  - [x] Raise typed validation errors with supported-value or compatible-framework hints.

- [x] **4. Extend the MCP tool and output schema** (AC: 1-5)
  - [x] Update `src/tools/test_code.py` to expose the typed selections and metadata multi-select while keeping it a thin wrapper.
  - [x] Update Google-style docstrings with the exact visible choices, required language/framework behavior, metadata default, aliases, and compatibility caveat.
  - [x] Preserve the special verbatim return for `output_format="plain"`.
  - [x] Add the canonical metadata selection to structured JSON and update `@output_fields(...)` plus the concrete output model/schema.
  - [x] Do not re-register the existing tool or add a second generation tool.

- [x] **5. Expand automated coverage** (AC: 1-7)
  - [x] Extend `tests/unit/test_test_code_service.py` for wire mappings, every metadata flag, subsets, omitted vs empty, aliases, invalid values, compatibility rules, and API error propagation.
  - [x] Assert validation failures do not instantiate or call the generated endpoint.
  - [x] Extend `tests/integration/test_test_code_tool.py` for required target validation, forwarding, canonical JSON metadata, metadata defaults, and literal-escape preservation.
  - [x] Add schema/manifest assertions that all selections are discoverable to MCP clients.
  - [x] Extend `tests/e2e/test_code_generation.py` with a parameterized live-sandbox matrix covering all 32 verified language/framework pairs after the wire contract is verified against the sandbox.

- [x] **6. Update agent and user documentation** (AC: 1-2, 4-5, 7)
  - [x] Update `docs/tools.md` and `README.md` examples.
  - [x] Update the generate-code scenario and coverage matrix in `tests/agentic/agentic-tool-calls-tests.md`.
  - [x] Regenerate `docs/mcp_manifest.json` using the repository schema build process; do not edit generated manifest content manually.
  - [x] Update Story 7.7 references only where they would otherwise state that all metadata flags are permanently hard-coded `true`.

- [x] **7. Validate** (AC: 7)
  - [x] Run focused tests: `uv run pytest tests/unit/test_test_code_service.py tests/integration/test_test_code_tool.py tests/docs/test_mcp_manifest.py`.
  - [x] Run focused lint/type checks for touched source and test files with `uv run ruff` and `uv run mypy`.
  - [x] Run the live E2E test separately with the configured `.env.test` sandbox.
  - [x] Run `./scripts/full-test-suite.sh`; record the unrelated packaging artifact failure below.

## Dev Notes

### Developer Context

Story 7.7 delivered the generated `IdeControllerApi`, `TestCodeService`, and `generate_test_code` tool. This story must extend those components rather than introduce a parallel API path or tool. The current service accepts free-form language/framework strings and hard-codes `syncFields`, `syncName`, `syncTags`, and `syncScenario` to `true`.

The screenshot is a UX source, not a complete API contract. It proves the seven language labels, the six metadata labels, and the frameworks visible while TypeScript is selected. It does **not** establish a global framework cross-product, exact private-API tokens, or member/issue request field names. Treat the live TestOps request as authoritative for wire values.

### Selection Contract

| Selection | User-visible values | Required behavior |
|---|---|---|
| Language | Java, Python, TypeScript, JavaScript, Kotlin, PHP, .NET | Required on every call; publish as constrained choices; map to verified API tokens; retain verified aliases. |
| Framework (TypeScript-visible) | CodeceptJS, Cucumber, Jasmine, Jest, Mocha, Playwright, Vitest, WebdriverIO, ZeroStep | Required on every call; do not represent this list as compatible with every language. Preserve existing Pytest and JUnit as explicit selections. |
| Metadata | Name, Tags, Custom fields, Members, Issues, Scenario | Multi-select; omitted defaults to Name/Tags/Custom fields/Scenario; explicit empty disables all. |

Known metadata mappings:

| User-visible metadata | Current/verified request field | Default |
|---|---|---:|
| Name | `syncName` | `true` |
| Tags | `syncTags` | `true` |
| Custom fields | `syncFields` | `true` |
| Members | **Verify against TestOps request** | `false` |
| Issues | **Verify against TestOps request** | `false` |
| Scenario | `syncScenario` | `true` |

### Architecture Compliance

- Follow the existing **Thin Tool / Fat Service** boundary: validation/mapping/request construction belongs in `TestCodeService`; the tool delegates and renders.
- Keep all TestOps HTTP access behind `src/client/`; use the generated `IdeControllerApi` and `_client._call_api` error translation.
- Modify the local OpenAPI overlay and regenerate. Never patch generated client files by hand.
- Use strict, schema-discoverable types. No new runtime dependency is required.
- Let typed exceptions bubble to the global Agent Hint handler; do not add `try/except` in the tool.
- Preserve the established `plain|json` tool output contract and the lossless generated-source exception for plain output.

### File Structure Requirements

Expected modifications:

- `scripts/filter_openapi.py`
- `openapi/allure-testops-service/filtered-report-service.json` (generated)
- `src/client/generated/` IDE DTO artifacts (generated)
- `src/services/test_code_service.py`
- `src/tools/test_code.py`
- `src/tools/output_schemas.py` if structured output gains `metadata`
- `tests/unit/test_test_code_service.py`
- `tests/integration/test_test_code_tool.py`
- `tests/e2e/test_code_generation.py`
- `tests/agentic/agentic-tool-calls-tests.md`
- `docs/tools.md`
- `README.md`
- `docs/mcp_manifest.json` (generated)

The tool is already registered in `src/tools/__init__.py`, annotated in `src/tools/annotations.py`, and listed in both MCPB manifests. Do not churn those files unless the actual public tool inventory changes. The tool is not currently a canonical CLI entity/action route, so adding CLI routing is out of scope.

The screenshot describes the TestOps selection experience; it is not a request to build a Lucius UI. Expose the choices through the existing MCP input schema and documentation. Do not add a second options-discovery tool unless TestOps exposes a verified dynamic-options API and a separate story approves that scope.

### Testing Requirements

- Keep service tests request-exact: assert the complete alias-based DTO payload, including `false` values.
- Parameterize selection cases rather than duplicating near-identical tests.
- Test both schema discoverability and runtime normalization; a documented list without an enum/selectable schema does not satisfy AC 1 or 2.
- Verify no endpoint call occurs for local validation failures.
- Keep the existing literal `\\n` regression test.
- Use a stable sandbox test case and parameterize the live E2E test across all 32 verified language/framework pairs; exhaustive wire-mapping assertions still belong in unit tests.

### Previous Story Intelligence

- Story 7.7 intentionally allowed TestOps to validate free-form language/framework values. Replace that behavior only for mappings confirmed by this story; do not guess a full compatibility matrix.
- The IDE endpoint is absent from the public OpenAPI document. Story 7.7 solved this with `_add_ide_test_code_endpoint()` in `scripts/filter_openapi.py` and generated client code.
- Story 7.7's review found that generic plain rendering can mutate generated source by expanding literal escape sequences. Retain the direct plain return path.
- Recent implementation commit `c69b650` contains the complete feature introduction and is the best diff reference for generated-client, service, tool, test, manifest, and documentation patterns.

### Latest Technical Information

- Current official TestOps documentation describes code generation as a sequence of selecting a programming language, selecting a testing framework, and choosing which test-case attributes to include. It does not publish the private IDE request schema or the full compatibility matrix.
- TestOps release notes identify code generation as a product feature introduced in the 25.1.1 release. This story does not require upgrading Python dependencies or framework adapters; the named frameworks are TestOps generation targets, not lucius-mcp runtime dependencies.

### Project Structure Notes

- Actual runtime/tool contracts in the repository take precedence over stale planning statements. In particular, use `pyproject.toml` for the supported Python baseline and inspect `DEFAULT_OUTPUT_FORMAT` rather than relying on older architecture prose.
- There is no UX design document in the planning artifacts. The user-provided screenshot is the source for the visible selection inventory and default state.
- Epic 7 and Story 7.7 were complete before this follow-up. Sprint tracking is reopened only for this directly related extension.

### References

- [Source: specs/implementation-artifacts/7-7-test-code-generator.md#Acceptance-Criteria]
- [Source: specs/implementation-artifacts/7-7-test-code-generator.md#Dev-Notes]
- [Source: src/tools/test_code.py]
- [Source: src/services/test_code_service.py]
- [Source: scripts/filter_openapi.py]
- [Source: specs/architecture.md#Implementation-Patterns--Consistency-Rules]
- [Source: specs/project-context.md#The-Thin-Tool--Fat-Service-Pattern-STRICT]
- [Source: docs/development.md#Regenerating-the-API-Client]
- [Source: user-provided Generate code screenshot, 2026-07-21]
- [Source: https://docs.qameta.io/use-testops/test-cases/#generating-code-for-test-case-automation]
- [Source: https://docs.qameta.io/reference/release-notes/]

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

- 2026-07-21: Existing live sandbox check `uv run --env-file .env.test pytest tests/e2e/test_code_generation.py -q` passed (1 passed). The sandbox API credentials do not authenticate the TestOps browser UI, and the available browser surface cannot inspect network payloads. No verified source for the seven UI wire tokens or the `Members`/`Issues` boolean field names is available in the repository; implementation is paused before changing the overlay, as required by Task 1.
- 2026-07-21: Authenticated live TestOps UI enumeration in project 166 verified the visible matrix: Java → JUnit 5, JUnit 4, TestNG, Cucumber; Python → Behave, Pytest, Pytest BDD; TypeScript → CodeceptJS, Cucumber, Jasmine, Jest, Mocha, Playwright, Vitest, WebdriverIO, ZeroStep; JavaScript → CodeceptJS, Cucumber, Jasmine, Jest, Mocha, Playwright, Vitest, WebdriverIO; Kotlin → JUnit 5, JUnit 4, TestNG; PHP → PHPUnit, Codeception; .NET → NUnit, XUnit, SpecFlow. Selecting TypeScript + Playwright in this current TestOps UI showed all six metadata options selected by default. The browser does not expose network requests, and inspected public frontend chunks did not contain the request mapping; Task 1 remains incomplete until wire tokens and member/issue fields are captured or otherwise verified.
- 2026-07-21: Chrome DevTools verification completed against the authenticated target version. A live TypeScript + Playwright request was `POST /api/ide/testcase/{id}/testcode` with `lang: "ts"`, `testFramework: "playwright"`, and all six flags: `syncName`, `syncTags`, `syncFields`, `syncMembers`, `syncIssues`, and `syncScenario`. The loaded code-generation module verifies labels map to language tokens Java → `java`, Python → `python`, TypeScript → `ts`, JavaScript → `js`, Kotlin → `kotlin`, PHP → `php`, .NET → `dotnet`; and TypeScript framework tokens CodeceptJS → `codeceptjs`, Cucumber → `cucumber-js`, Jasmine → `jasmine`, Jest → `jest`, Mocha → `mocha`, Playwright → `playwright`, Vitest → `vitest`, WebdriverIO → `wdio`, ZeroStep → `zerostep`. Its metadata enum maps Custom fields to `Fields`, so the request builder derives `syncFields`; Members and Issues derive `syncMembers` and `syncIssues`. The current TestOps source sends only selected metadata as `true` and defaults all six selected, which conflicts with this story's four-default/explicit-false requirements; preserve the story requirement unless product direction changes it.
- 2026-07-21: Implemented the verified matrix and regenerated the generated client and MCP manifest. The live sandbox matrix passed in bounded language groups: Java 4/4, Python 3/3, TypeScript 9/9, JavaScript 8/8, Kotlin/PHP/.NET 8/8 (32/32 total). Focused unit/integration/manifest tests passed (63), repository unit/integration tests passed (1023), documentation tests passed (24), and repository ruff/mypy checks passed. Packaging tests have three unrelated failures because the checked-in macOS binary is `lucius-0.12.3-macos-arm64` while the packaging suite expects version `0.13.0`; no story code changes were made to packaging artifacts.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Implemented selectable, schema-published code-generation targets and metadata synchronization with validated TestOps wire mappings.
- Preserved Python/Pytest, TypeScript/Playwright, and Java/JUnit aliases; target selections are now required.
- Added canonical metadata to JSON output and a live 32-pair generation matrix.

### File List

- README.md
- docs/mcp_manifest.json
- docs/tools.md
- openapi/allure-testops-service/filtered-report-service.json
- scripts/filter_openapi.py
- src/client/generated/docs/TestCodeGenerationRequestDto.md
- src/client/generated/models/test_code_generation_request_dto.py
- src/services/test_code_service.py
- src/tools/output_schemas.py
- src/tools/test_code.py
- tests/agentic/agentic-tool-calls-tests.md
- tests/docs/test_mcp_manifest.py
- tests/e2e/test_code_generation.py
- tests/integration/test_test_code_tool.py
- tests/unit/test_test_code_service.py

### Change Log

- 2026-07-21: Created Story 7.8 for selectable test-code language, framework, and metadata options.
- 2026-07-21: Implemented verified language/framework choices, metadata selection, generated-client support, documentation, and all-pairs live E2E coverage.
