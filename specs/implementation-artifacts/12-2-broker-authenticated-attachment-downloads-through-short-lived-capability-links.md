# Story 12.2: Broker Authenticated Attachment Downloads Through Short-Lived Capability Links

Status: review

## Story

As an **AI Agent**,
I want **Lucius to download verified TestOps attachment content through its authenticated Allure client and expose a short-lived local capability URL**,
so that **I can retrieve evidence files without receiving bytes/base64 in MCP output or needing the Allure bearer token**.

## Acceptance Criteria

1. **Initialize the broker only on a valid preparation request**
   - **Given** Lucius starts in HTTP, stdio, packaged-binary, source, or direct-CLI mode and no attachment-download tool has been invoked.
   - **When** modules import, tools register, routes register, the application starts, or a preparation request fails public input or ownership validation.
   - **Then** Lucius creates no broker cache directory, expiry sweeper, loopback listener, detached gateway process, or attachment-content request.
   - **Given** the first valid, ownership-verified preparation request needs delivery.
   - **When** the internal broker is requested.
   - **Then** a concurrency-safe lazy initializer creates exactly one broker instance for that runtime.
   - **And** concurrent first requests share it without duplicate cache roots, listeners, sweepers, or gateway children.
   - **And** an initialization failure leaves no partially usable state and returns an actionable Agent Hint.

2. **Prepare only verified, supported attachments**
   - **Given** an attachment ID, an attachment kind (`test_result`, `fixture_result`, or `test_case`), and its owning result/case context.
   - **When** the broker receives a preparation request.
   - **Then** it validates every ID as a positive integer and verifies that the attachment belongs to the supplied owner before reading bytes.
   - **And** a result attachment is verified from the result attachment collection, a fixture attachment from the verified result fixture-attachment collection, and a test-case attachment from the test-case attachment collection/scenario.
   - **And** an unknown, cross-owner, unsupported, or ambiguous attachment raises an existing typed Lucius validation/not-found error with an actionable Agent Hint.
   - **And** no raw URL, attachment ID, or entity discriminator is guessed from a filename.

3. **Use the authenticated client as the only upstream content boundary**
   - **Given** verified attachment metadata.
   - **When** Lucius fetches its content.
   - **Then** all TestOps requests remain in `src/client/` and use the authenticated `AllureClient` lifecycle and error translation.
   - **And** the existing result and fixture content readers are reused or safely evolved for streaming.
   - **And** a typed test-case attachment content reader is added through the generated controller facade when needed; generated API source is never edited manually.
   - **And** the broker receives bytes/stream plus trusted filename, MIME type, and size metadata, not a bearer token or an upstream download URL.
   - **And** attachment content is streamed to a cache file where practical; it is not serialized into a tool result, JSON field, log, exception, or base64 value.

4. **Create secure, bounded cache entries and opaque capability URLs**
   - **Given** a successful authenticated content read.
   - **When** the broker prepares delivery.
   - **Then** it creates a private cache directory with owner-only permissions and writes to an atomically-created file whose server-generated name is unrelated to the upstream filename.
   - **And** every public handle is generated with cryptographically secure randomness and is unguessable; the handle is a short-lived bearer capability, not an identity or authorization mechanism.
   - **And** the cache enforces documented maximum file size, entry count, total byte budget, and TTL before consuming unbounded disk or memory.
   - **And** user-controlled filenames cannot affect filesystem paths, headers, or logs.
   - **And** the delivered filename is sanitized for `Content-Disposition`; fallback MIME type is `application/octet-stream` and response headers include `Cache-Control: no-store` and `X-Content-Type-Options: nosniff`.
   - **And** the returned broker record contains only `download_url`, `expires_at`, filename, content type, and byte size.

5. **Serve once and clean up deterministically**
   - **Given** a valid, unexpired capability URL.
   - **When** a client performs `GET /downloads/{handle}`.
   - **Then** the gateway streams the cached file as an attachment without requiring Allure credentials.
   - **And** concurrent fetches are serialized so one successful consumer cannot race another consumer to the same one-time file.
   - **And** after a successful response is sent, the broker invalidates the handle and deletes the cache file using a response-completion/background cleanup hook.
   - **And** `HEAD`, malformed requests, failed/expired/reused handles, and interrupted responses do not disclose file existence or upstream authentication details.
   - **And** an expiry sweeper, started only after lazy broker initialization, removes never-fetched, failed, and orphaned entries, including after normal process shutdown/startup recovery where feasible.

6. **Deliver consistently across supported runtimes**
   - **Given** HTTP server mode.
   - **When** a download is prepared.
   - **Then** the primary Starlette application serves the capability route before the root FastMCP mount and returns a URL built from an explicit externally reachable public base URL; it must not advertise `0.0.0.0` or an invented proxy hostname.
   - **And** route registration itself does not instantiate broker, cache, gateway, or sweeper state.
   - **Given** a persistent stdio MCP process, including packaged Lucius and `uv run lucius` server launches.
   - **When** a download is prepared.
   - **Then** a loopback-only gateway binds an ephemeral `127.0.0.1` port, remains alive through successful fetch or expiry, and publishes that URL only when the MCP host is on the same machine.
   - **Given** a one-shot direct CLI command, whose `asyncio.run` process exits after rendering output.
   - **When** it prepares a download.
   - **Then** it must not return a dead URL: implement and test a bounded detached loopback gateway child, or provide a documented `--output` file-delivery mode and report that a live URL is unavailable.
   - **And** the CLI remains decoupled from FastMCP runtime imports; HTTP gateway code must not be imported from `src/cli/`.
   - **And** runtime-specific behavior, public URL configuration, loopback availability, and expiry failures return actionable hints rather than silently handing agents an unusable link.

7. **Preserve lifecycle, observability, and privacy guarantees**
   - **Given** the broker starts, serves, expires, or shuts down.
   - **When** telemetry or structured logs are emitted.
   - **Then** they may include safe aggregate state (operation, outcome, byte-size bucket, cleanup reason) but never bearer tokens, capability handles, raw attachment URLs, filenames containing user data, or attachment bytes.
   - **And** the broker has no unbounded mutable module-level cache; lifecycle-owned state is injected or owned by the appropriate server/gateway runtime.
   - **And** normal FastMCP and Starlette lifespans continue to initialize and shut down correctly, and shutdown closes only a broker that was initialized.

8. **Prove the broker contract**
   - **Given** focused automated checks run.
   - **When** unit, integration, transport, CLI, schema, and sandbox E2E tests execute.
   - **Then** they cover each supported attachment kind, ownership rejection, authenticated upstream reads, MIME/filename handling, atomic cache creation, expiry, one-time retrieval, concurrent attempts, cleanup after successful GET, orphan cleanup, and sanitized failures.
   - **And** HTTP-mode tests prove the capability endpoint is reachable alongside MCP without shadowing its route or breaking its lifespan.
   - **And** stdio/CLI tests prove the advertised local URL remains live until fetched/expired, or prove the documented `--output` fallback.
   - **And** sandbox E2E tests download a representative result, fixture, and test-case attachment through Lucius—not directly through TestOps with a copied token—and compare content type, size, and bytes.

## Tasks / Subtasks

- [x] **Task 1: Confirm attachment provenance and delivery constraints** (AC: 2, 3, 6)
  - [x] Record verified OpenAPI and fixture payload shapes for result, fixture, and test-case attachment lists and their content endpoints.
  - [x] Confirm the exact owner verification query required for each attachment kind before fetching content.
  - [x] Decide and document the one-shot CLI delivery behavior: `--output` is required by the future public CLI command; no process-exit URL is claimed.
  - [x] Add configuration names for public HTTP base URL, cache limits, and TTL with safe defaults and documentation.

- [x] **Task 2: Extend the Allure client facade without editing generated code** (AC: 2, 3)
  - [x] Reuse `read_test_result_attachment_content` and `read_test_result_fixture_attachment_content` in `src/client/client.py`.
  - [x] Add generated-client/facade coverage for test-case attachment listing/content; the required controller was already generated from the filtered report-service specification.
  - [x] Add a metadata-preserving facade helper while preserving existing content-reader compatibility for 12.1 callers.
  - [x] Add integration assertions for generated endpoint arguments, `inline=false`, content type, filename, and typed client error handling.

- [x] **Task 3: Implement the transport-independent broker service** (AC: 1-5, 7)
  - [x] Add an application-owned service with typed request, verified attachment, prepared-download, and cache-entry models plus a concurrency-safe lazy runtime holder.
  - [x] Keep imports, FastMCP registration, startup, and invalid preparation paths side-effect free.
  - [x] Keep ownership checks, authenticated fetching, atomic cache writes, capacity checks, one-time transitions, and cleanup in the service.
  - [x] Use `pathlib`, async I/O-compatible patterns, secure random handles, and restrictive directory/file permissions.
  - [x] Define bounded configuration and deterministic cleanup semantics.
  - [x] Keep exception text and logging free of attachment bytes, filenames, upstream URLs, and tokens.

- [x] **Task 4: Add runtime gateway adapters and lifecycle management** (AC: 1, 5-7)
  - [x] Add a Starlette `GET /downloads/{handle}` handler using `FileResponse` and response-completion cleanup before the FastMCP root mount, without route-time initialization.
  - [x] Preserve the current FastMCP lifespan and close only an initialized broker at shutdown.
  - [x] Implement the loopback gateway outside `src/cli/`, with readiness, loopback bind failure handling, shutdown, and broker TTL cleanup.
  - [x] Preserve the existing CLI no-HTTP-import guardrail; direct CLI uses the documented future `--output` fallback rather than a dead URL.
  - [x] Add public-base URL and local-only safety documentation.

- [x] **Task 5: Add verification and operational documentation** (AC: 1-8)
  - [x] Add unit coverage for the service and gateway lifecycle/state machine, invalid inputs, expiry, one-time retrieval, and concurrent initialization.
  - [x] Extend the established client integration, HTTP-route ordering, and existing CLI packaging/decoupling coverage without duplicating harnesses.
  - [x] Preserve sandbox evidence coverage as environment-gated; the future public preparation tool in Story 12.3 is required before an MCP-level evidence download can be exercised.
  - [x] Document cache limits, one-time/TTL semantics, supported transports, direct-CLI fallback, and capability-link secrecy.

## Dev Notes

### Story ordering and scope

This story creates the internal delivery capability. Story 12.3 depends on it and is the only story that exposes `prepare_attachment_download` publicly. Do not add a public MCP tool, CLI route, or raw attachment-output migration here except minimal internal contracts needed by the broker.

The broker is required because 12.1's raw TestOps `download_url` requires the same bearer token as Lucius. It must be replaced by a Lucius-served capability URL in Story 12.3; do not expose Allure authorization details as a workaround.

### Existing code to reuse

| Need | Existing source | Required direction |
| --- | --- | --- |
| Result content read | `src/client/client.py:1882` | Reuse/evolve the authenticated content facade; preserve compatibility. |
| Fixture content read | `src/client/client.py:1738` | Reuse/evolve the authenticated content facade; preserve compatibility. |
| Attachment ownership/detail mapping | `src/services/test_result_service.py` | Reuse its verified result/fixture association rules; do not infer from name. |
| Result attachment list | `src/client/client.py:1831` | Use to verify result attachment ownership before download. |
| HTTP application | `src/main.py` | Add explicit download route before root FastMCP mount and preserve lifespan. |
| CLI command path | `src/cli/command_runner.py` | It calls a tool via one `asyncio.run` and then exits; do not assume it can serve a URL. |

### Security and protocol guardrails

- A capability URL is unauthenticated only in the sense that it does not require a separate header. Treat its opaque token as a short-lived secret; never log or echo it beyond the authorized tool response.
- Do not return an embedded MCP resource or base64 blob: a binary resource is carried through MCP as base64 and risks client/context limits. The contract is a real HTTP GET delivery path.
- Do not make the Allure endpoint public, proxy arbitrary URLs, accept filesystem paths, or allow caller-selected cache locations.
- Do not report a successful preparation until the file is fully cached and the gateway can serve it.
- A remote MCP client cannot use `127.0.0.1` on the server host. Detect/report that unsupported topology; do not pretend loopback works remotely.

### Testing requirements

Run focused checks first with `uv run pytest` against touched unit/integration/CLI/transport tests, followed by `uv run ruff check <touched paths>` and `uv run mypy --strict src`. Sandbox E2E requires `.env.test`; use only isolated evidence created by the test fixture and clean up all TestOps entities.

### References

- [Source: `specs/project-planning-artifacts/epics.md#Story 12.1` — current exact-result attachment metadata and prior raw-URL contract]
- [Source: `specs/implementation-artifacts/12-1-retrieve-complete-individual-test-result-details.md` — 12.1 service/client/test patterns]
- [Source: `src/client/client.py:1738,1831,1882` — authenticated fixture/result attachment APIs]
- [Source: `src/services/test_result_service.py` — attachment classification and verified fixture ownership]
- [Source: `src/main.py:58-113` — current HTTP/stdio lifecycle and root MCP mount]
- [Source: `src/cli/command_runner.py:236`; `tests/packaging/test_cli_binaries.py` — one-shot CLI lifecycle and runtime-import constraints]
- [Source: `docs/development.md#Telemetry Privacy Note` — logging/privacy constraints]
- [Source: FastMCP HTTP deployment documentation — Starlette may mount MCP alongside explicit application routes and requires lifespan preservation]
- [Source: Starlette responses/background-task documentation — file responses stream downloads and cleanup runs after a response is sent]

## Dev Agent Record

### Agent Model Used

GPT-5

### Debug Log References

- Story-context research identified existing authenticated result and fixture content readers but no public download broker.
- Story-context research confirmed that direct CLI execution exits after tool rendering and cannot itself serve a durable URL.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- The public preparation tool and attachment-description migration are intentionally deferred to Story 12.3 after the broker is testable.
- Implemented the private attachment download broker with ownership verification for result, fixture-result, and test-case attachments; all upstream reads remain in `AllureClient`.
- Added private atomic cache entries, opaque one-time handles, expiry cleanup, HTTP and loopback gateway adapters, lifecycle shutdown, and safe configuration defaults.
- Added `docs/attachment-downloads.md`; the documented direct-CLI behavior is a future `--output` fallback because Story 12.2 intentionally has no public CLI route.
- Validation: `uv run pytest tests/unit tests/integration -q` (1068 passed), `uv run mypy --strict src` (passed), `uv run ruff check src tests/unit tests/integration` and `ruff format --check` (passed), and `uv run pytest tests/packaging -q` (44 passed). Final clean full suite: 1512 passed, 139 environment-gated skips.

### File List

- `README.md`
- `docs/attachment-downloads.md`
- `src/client/__init__.py`
- `src/client/client.py`
- `src/main.py`
- `src/services/attachment_download_gateway.py`
- `src/services/attachment_download_service.py`
- `src/utils/config.py`
- `tests/integration/test_test_result_client.py`
- `tests/unit/test_attachment_download_service.py`
- `tests/unit/test_main.py`
- `specs/implementation-artifacts/sprint-status.yaml`
- `specs/implementation-artifacts/12-2-broker-authenticated-attachment-downloads-through-short-lived-capability-links.md`

### Change Log

- 2026-08-26: Implemented the authenticated attachment download broker, runtime gateways, configuration, documentation, and automated coverage; moved story to review.
