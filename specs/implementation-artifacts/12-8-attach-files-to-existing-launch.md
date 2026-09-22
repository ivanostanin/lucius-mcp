---
title: 'Story 12.8: Attach Files to an Existing Launch'
type: 'feature'
created: '2026-09-22'
status: 'done'
baseline_commit: 'eedcbb9'
context:
  - '../../docs/development.md'
  - '../project-context.md'
  - 'epic-12-context.md'
---

<frozen-after-approval reason="human-owned intent renegotiated and native endpoint confirmed 2026-09-22 — do not modify unless human renegotiates">

## Intent

**Problem:** Agents need to attach launch-level evidence—logs, screenshots, traces, and other files—to an existing TestOps launch. A path-only MCP interface cannot serve remote agents or separate Kubernetes pods. The existing `/api/launch/{launchId}/upload*` endpoints ingest test results and must not be repurposed.

**Confirmed destination:** A user-supplied HAR of the TestOps web client confirms the native launch attachment workflow:

```text
POST /api/launch/attachment?launchId={launch_id}
Content-Type: multipart/form-data
part: file

200 application/json -> [{ id, name, contentType, contentLength, entity: "launch" }]

GET /api/launch/attachment?launchId={launch_id}&page={page}&size={size}
200 application/json -> paged attachment rows
```

This endpoint is absent from both checked-in OpenAPI documents, so add it as a narrow, tested overlay in `scripts/filter_openapi.py`, regenerate the client, and prove that Lucius's normal API-token authentication works against the sandbox before making it public.

**Approach:** Add the thin MCP tool `attach_file_to_launch` with two transfer modes:

- **Push:** prepare an ingress-reachable, one-use, short-lived HTTP upload URL. The agent uploads one raw file; the receiving Lucius replica streams it to the native TestOps endpoint and returns the native attachment summary only after success.
- **Pull:** securely read one file from a configured shared-volume import root and stream it to the same endpoint during the MCP call.

## Non-negotiable Scope

**Always:** `attach_file_to_launch` means a native **launch** attachment. Keep it distinct from result ingestion, structured manual results, test-result evidence, test-step evidence, fixture evidence, and test-case attachments. Stream content asynchronously with a strict byte limit; never emit file bytes, source paths, capability tokens, cookies, XSRF values, API tokens, upstream URLs, or raw upstream errors in MCP output, logs, or telemetry.

**Push contract:** `attach_file_to_launch(launch_id, name, content_type, transfer_mode="push")` validates metadata and returns `state="awaiting_upload"`, opaque `upload_url`, `upload_method`, `expires_at`, and `max_file_bytes`. The caller uploads raw bytes using the returned method before expiry; HTTP success means TestOps has accepted the attachment. The preparation response is not an attachment-success response.

**Pull contract:** `attach_file_to_launch(launch_id, name, transfer_mode="pull", source_path, content_type=None)` accepts only a regular file whose resolved path is inside `LAUNCH_ATTACHMENT_IMPORT_ROOT`, a deployment-configured shared/mounted directory. Reject traversal, symlinks, device files, unreadable paths, and files outside the root. Infer a missing content type from the filename with `application/octet-stream` fallback. Stream directly and never delete the source file.

**Multi-replica contract:** Push preparation and upload may hit different pods. Capability state must live in an atomically claimable, expiry-aware **shared durable store** (or equivalent proven distributed coordinator), giving exactly-once/replay protection. In-process maps, local state, pod affinity, and load-balancer stickiness are insufficient. A receiving replica may use a bounded private temporary file only within its already-claimed request to bridge inbound streaming to the generated multipart client; clean it on every outcome. It must never be the capability-state or cross-pod payload store.

**Authentication gate:** The HAR uses a browser session and XSRF token, while Lucius uses API-token bearer authentication. Before exposing the tool, prove `POST` and `GET` with the standard `AllureClient` authentication against the sandbox. If API-token authentication is not accepted, stop and report the compatibility blocker; do not accept browser cookies/tokens from MCP callers or create a session-login workaround.

**Ask First:** Selecting/provisioning a durable capability store, object storage, public ingress hostname, network policy exception, malware/content scanning, retention policy, a broader MIME policy, or CLI support. These are deployment/product decisions beyond the core adapter.

**Never:** Do not use `AllureClient.upload_results_to_launch`, `/api/launch/{launchId}/upload*`, `upload_test_results`, `add_test_result_attachment`, or `add_test_step_attachment`. Do not create a result/step as a substitute, cache a Lucius-only pseudo-attachment, or claim success before TestOps accepts the native launch attachment.

## I/O & Edge-Case Matrix

| Scenario | Input / state | Required behavior |
| --- | --- | --- |
| API-token compatibility | Standard Lucius API token | Sandbox proves native POST/GET works without browser session/XSRF data before registration. |
| Push preparation | Valid launch, name, and content type | Return one opaque URL/expiry/method/limit; no attachment-success claim. |
| Push finalization | Valid capability receives bounded raw stream | Atomically consume capability, stream multipart `file` to TestOps, then return sanitized native row(s). |
| Push replay / expiry | Used, malformed, revoked, or expired URL | Fail safely; no duplicate TestOps upload or state leakage. |
| Cross-replica push | Preparation and upload hit different pods | Shared state permits exactly one finalization. |
| Pull from volume | Regular file below import root | Stream to TestOps and return native attachment summary in MCP response. |
| Unsafe pull source | Traversal, symlink, non-regular/outside/unreadable path | Reject before reading/contacting TestOps. |
| Size/type violation | Exceeds configured/native limit or invalid metadata | Reject before successful completion; clean any private temporary data. |
| Native error | Missing launch, permission/auth, validation, or upstream failure | Safe actionable agent hint; never expose browser/session details or claim success. |
| Existing upload/evidence tools | Any current result upload or result/step attachment flow | Inputs, outputs, registrations, and semantics remain unchanged. |

</frozen-after-approval>

## Human-approved scope amendment — 2026-09-22

The shared durable capability-state provider is deferred to
`specs/implementation-artifacts/deferred-work.md` (D-12-7). Until that work is
completed, push uploads are single-replica only and their capability URLs are
served by Lucius's existing HTTP/Starlette server. The public tool and
documentation must state that horizontal scaling is unsupported for this
interim mode.

## Story

As an **AI Agent**,
I want to **attach evidence files to an existing launch through remote-safe push or pull workflows**,
so that **the launch can retain logs, screenshots, traces, and other evidence without sharing a pod filesystem with the agent**.

## Acceptance Criteria

1. **Generate and authenticate the native launch-attachment client**
   - Given the HAR-confirmed web-client endpoint is absent from the checked-in OpenAPI,
   - When the client generation input is updated,
   - Then `scripts/filter_openapi.py` adds only `GET` and `POST /api/launch/attachment`, typed launch-attachment rows, paging, multipart `file`, and `launchId` query parameter through a documented overlay,
   - And `./scripts/generate_testops_api_client.sh` regenerates the client with no hand edits to generated files.
   - Given normal Lucius API-token authentication,
   - When controlled sandbox tests call native GET and POST,
   - Then they succeed without browser session, cookie, or XSRF headers; otherwise the feature stops at a documented blocker and no public tool is registered.

2. **Prepare remote-safe push uploads**
   - Given a valid launch ID, non-empty safe filename, valid content type, and `transfer_mode="push"`,
   - When I call `attach_file_to_launch`,
   - Then it returns `state="awaiting_upload"`, a one-use short-lived ingress-reachable `upload_url`, its required HTTP method, expiry, and maximum byte size,
   - And no TestOps bearer token is needed at the upload URL,
   - And no attachment is reported as created until the caller actually uploads bytes.

3. **Finalize push exactly once across replicas**
   - Given a prepared capability URL,
   - When a caller sends one bounded raw file stream before expiry,
   - Then exactly one Lucius replica atomically claims it, submits multipart `file` to `POST /api/launch/attachment?launchId=...`, and returns only the native attachment summary (`id`, `name`, `content_type`, `content_length`),
   - And a replay, expiry, malformed request, metadata mismatch, oversize payload, or TestOps failure cannot create a duplicate or reveal sensitive state.

4. **Support restricted pull from deployment storage**
   - Given `LAUNCH_ATTACHMENT_IMPORT_ROOT` is a configured shared mounted import directory and a requested file resolves to a regular file below it,
   - When I call `attach_file_to_launch(transfer_mode="pull", source_path=...)`,
   - Then Lucius streams that file to the native launch-attachment endpoint and returns `state="attached"` plus the native attachment summary,
   - And remote MCP callers do not need filesystem access to any Lucius pod.
   - Given an unsafe/outside-root/symlinked/unreadable/non-regular source,
   - Then Lucius rejects it before an upstream request.

5. **Preserve safety and existing behavior**
   - Given either transfer mode,
   - When output, telemetry, documentation, and generated metadata are inspected,
   - Then only safe state and attachment metadata are exposed—never file content, local paths, capability secrets, TestOps credentials, cookie/XSRF values, raw URLs, or raw errors.
   - And result ingestion plus result/step/fixture/test-case attachment behavior is unchanged.

6. **Register and document the final public capability**
   - Given client authentication and both transfer modes are verified,
   - Then the tool is included once in `all_tools`, owns a strict object-root output model, has additive non-idempotent annotations/tags, and appears in generated MCP metadata, both MCPB manifests, tools docs, README, and agentic inventory.
   - And CLI route/schema/completion changes are excluded unless separately approved.

## Tasks / Subtasks

- [x] **Task 1: Overlay and regenerate the missing API** (AC: 1)
  - [x] Add `launch-attachment-controller` to `KEEP_TAGS`, then add `_add_launch_attachment_endpoints()` to `scripts/filter_openapi.py`, modeled after the existing IDE overlay and tagged with that exact value so filtering retains it.
  - [x] Define only the HAR-observed GET/POST path, `launchId` query parameter, multipart `file` input, paged GET response, and attachment row fields. Preserve `entity="launch"` internally but do not require it in public output.
  - [x] Regenerate with `./scripts/generate_testops_api_client.sh`; update client facade exports only through typed generated APIs.
  - [x] Add deterministic generated-client/client-facade tests for GET pagination, multipart file name/content type, and parsed rows.

- [x] **Task 2: Prove bearer-token compatibility and create the service** (AC: 1, 3, 4)
  - [x] Add a `LaunchAttachmentService` that validates a positive launch ID, maps native rows into application-owned summaries, and translates not-found/auth/validation failures to safe agent hints.
  - [x] Add controlled sandbox coverage using `AllureClient.from_env`; it must prove GET and POST without session-cookie/XSRF fallback before feature registration.
  - [x] If that proof fails, preserve the generated seam/tests, document the blocker, and do not expose the MCP tool or a browser-auth workaround.

- [x] **Task 3: Implement single-replica push capability handling** (AC: 2, 3, 5)
  - [x] Add settings for external upload base URL, positive max bytes/TTL, and an in-process single-replica capability runtime. Validate configuration without sensitive logging.
  - [x] Implement atomic prepare/claim/complete/expire/revoke semantics within one Lucius process; document the single-replica restriction. Track durable shared-state selection, recovery, and multi-replica behavior as deferred work D-12-7.
  - [x] Add a dedicated Starlette upload route before FastMCP. Validate capability + metadata, stream with byte limit, use a private bounded temporary bridge only after claim, submit through `LaunchAttachmentService`, and clean every outcome.
  - [x] Require an externally reachable HTTPS URL in HTTP deployments. Do not implement push for stdio until its externally reachable delivery lifecycle is separately designed.

- [x] **Task 4: Implement secure pull** (AC: 4, 5)
  - [x] Add `LAUNCH_ATTACHMENT_IMPORT_ROOT`; securely resolve the source beneath it and reject symlinks/non-regular files.
  - [x] Infer absent content type from filename with `application/octet-stream` fallback; enforce max bytes while streaming and preserve source data.

- [x] **Task 5: Add MCP surface, strict outputs, and documentation** (AC: 2, 4-6)
  - [x] Add thin async `attach_file_to_launch`; it validates transfer mode and delegates all path, state, HTTP, and TestOps behavior to services.
  - [x] Model `awaiting_upload` and `attached` explicitly. Push-preparation output contains `upload_url`, method, expiry, and max bytes; pull/finalization output contains only native attachment summaries.
  - [x] Register/export once, add strict output model and write-operation annotations/tags, regenerate `docs/mcp_manifest.json`, and update both MCPB manifests plus docs/inventory after API-token proof passes.

- [x] **Task 6: Test the complete lifecycle** (AC: 1-6)
  - [x] Cover overlay generation, API-token compatibility, native row mapping, path containment, symlinks, size/type checks, output redaction, expiry/replay, native errors, and unchanged existing upload/evidence tools.
  - [x] Add ASGI HTTP tests for prepare → upload → native confirmation. Two-runtime shared-state coverage is deferred with D-12-7 because the user-approved interim design is intentionally single-replica.
  - [x] Run sandbox E2E against the actual endpoint and verify the attachment appears in `GET /api/launch/attachment`; report exact environment limitations rather than weakening regression tests.
  - [x] Run focused tests, `uv run ruff check`, `uv run mypy --strict src`, docs/manifest/MCPB tests, and relevant deployment checks.

### Review Findings

- [x] [Review][Patch] Preserve the declared multipart content type [src/services/launch_attachment_service.py:51] — Fixed by carrying the declared or inferred type through a streaming multipart adapter.
- [x] [Review][Patch] Stream bounded attachments instead of materializing them in memory [src/services/launch_attachment_upload_gateway.py:47] — Fixed by forwarding bounded async file streams from both pull and push paths.

## Dev Notes

### Confirmed API contract and generation decision

| Capability | Verified request | Response | Generation direction |
| --- | --- | --- |
| Attach file | `POST /api/launch/attachment?launchId={id}`; multipart `file` | JSON array of launch attachment rows | Add exact overlay; regenerate typed controller/client. |
| List attachments | `GET /api/launch/attachment?launchId={id}&page=&size=&sort=` | Paged rows with `id`, `name`, `contentType`, `contentLength` | Add exact overlay; use for E2E verification and future discovery only if separately exposed. |
| Result ingestion (forbidden) | `/api/launch/{launchId}/upload*` | `LaunchUploadResponseDto` | Existing handwritten path; do not generate/use for this story. |

- The HAR is evidence of endpoint shape, not a credential source. It contains browser session/XSRF values and must not be committed, cited by local path, copied into fixtures, logs, or documentation.
- Full and filtered checked-in OpenAPI specs contain no `/api/launch/attachment` path. This is an intentional small overlay, exactly like the existing IDE endpoint overlay—not a broad regeneration of undocumented UI APIs.
- The generated endpoint must be validated against bearer API-token auth because the HAR used browser authentication. Never add cookies or XSRF headers to Lucius.
- The TestOps response includes an `entity` field with value `launch`; preserve it only as an adapter assertion, not a public caller-controlled field.

### Architecture and privacy guardrails

- Tool: thin MCP facade only. Service: destination mapping, source validation, and safe error translation. Client: generated API invocation/multipart transport. Gateway: one-use upload lifecycle only.
- Use `pathlib.Path`, async streaming, no unbounded reads, no `requests`, no tool-level `try/except`, and no new global mutable state.
- The shared capability provider is required for push in horizontally scaled HTTP mode. Its data is opaque capability state, expiry, expected metadata, and atomic claim—not payload content or TestOps secrets.
- Do not reuse attachment-download's local cache/holder, change its contracts, or weaken its existing privacy rules.
- The native endpoint accepts generic file evidence; do not force it through the old attachment MIME allowlist without a separate agreed policy. Enforce a configurable byte limit and validate supplied/inferred content-type syntax.

### Project Structure Notes

| Area | Files | Direction |
| --- | --- | --- |
| API overlay/generation | `scripts/filter_openapi.py`, filtered OpenAPI, `src/client/generated/` | Add only launch attachment GET/POST overlay; regenerate, never hand-edit output. |
| Typed facade/service | `src/client/client.py`, `src/services/launch_attachment_service.py` | Add native rows/pagination and application-owned summaries. |
| Push runtime | `src/main.py`, new upload gateway/runtime, `src/utils/config.py` | Add route before FastMCP, external URL/configuration, and distributed state. |
| MCP interface | `src/tools/launches.py`, `src/tools/__init__.py`, `src/tools/output_schemas.py`, annotations | Add tool/strict models only after bearer proof. |
| Deployment | Helm values/templates, setup docs | Configure ingress, public URL, state provider, volume root, and resource limits. |
| Tests | client/service/tool/ASGI/deployment/docs/MCPB suites | Prove native behavior, remote safety, exactly once, and privacy. |

### References

- User-supplied HAR, 2026-09-22: sanitized observed native POST/GET contract. Do not commit the HAR or its browser credentials.
- [Source: `scripts/filter_openapi.py:_add_ide_test_code_endpoint`] — established narrow OpenAPI overlay pattern.
- [Source: `src/services/attachment_download_service.py`, `src/services/attachment_download_gateway.py`, `src/main.py`] — capability lifecycle/gateway precedent; not reusable process-local state.
- [Source: `src/client/client.py:upload_results_to_launch`] — explicitly forbidden result-ingestion path.
- [Source: `docs/development.md`, `specs/project-context.md`] — generated client, service-first, strict-schema, async, and telemetry constraints.

## Dev Agent Record

### Agent Model Used

GPT-5

### Completion Notes List

- Replaced the result-ingestion assumption with the HAR-confirmed native launch-attachment endpoint.
- The approved interim serves opaque push capabilities through Lucius's existing HTTPS server and is limited to one replica; D-12-7 tracks the required shared durable state for horizontal scaling.
- API-token compatibility is a mandatory gate because HAR browser authentication cannot be reused by Lucius.
- Added the filtered-spec overlay and regenerated the typed native launch-attachment controller/facade; focused client tests, Ruff, and strict mypy pass.
- Confirmed native launch-attachment GET and POST with `AllureClient.from_env` after removing cookie/XSRF state; the sandbox test creates and deletes its temporary launch.
- Added `LaunchAttachmentService` to map native rows into safe application-owned summaries and translate upstream failures without exposing raw details.
- Sandbox pagination omits the row `entity`; the generated overlay accepts that observed response while the typed facade restores and asserts the implicit `launch` owner.

### Implementation Plan

- Keep the HAR-confirmed endpoint as a generated-client overlay and make the service the only application boundary for native row mapping.
- Expose push only through the existing HTTP/Starlette server with an externally reachable HTTPS base URL and one Lucius replica; D-12-7 owns the later shared durable provider.

### File List

- `specs/project-planning-artifacts/epics.md`
- `specs/implementation-artifacts/sprint-status.yaml`
- `specs/implementation-artifacts/epic-12-context.md`
- `specs/implementation-artifacts/12-8-attach-files-to-existing-launch.md`
- `scripts/filter_openapi.py`
- `openapi/allure-testops-service/filtered-report-service.json`
- `src/client/client.py`
- `src/client/__init__.py`
- `src/client/generated/`
- `tests/unit/test_filter_openapi.py`
- `tests/integration/test_launch_client.py`
- `src/services/launch_attachment_service.py`
- `src/services/launch_attachment_upload_service.py`
- `src/services/launch_attachment_upload_runtime.py`
- `src/services/launch_attachment_upload_gateway.py`
- `src/services/__init__.py`
- `tests/unit/test_launch_attachment_service.py`
- `tests/unit/test_launch_attachment_upload_service.py`
- `tests/unit/test_launch_attachment_upload_runtime.py`
- `tests/unit/test_launch_attachment_upload_gateway.py`
- `tests/unit/test_launch_attachment_upload_tools.py`
- `tests/e2e/test_launch_attachments.py`
- `src/main.py`
- `src/utils/config.py`
- `src/tools/launches.py`
- `src/tools/__init__.py`
- `src/tools/annotations.py`
- `src/tools/output_schemas.py`
- `docs/mcp_manifest.json`
- `docs/tools.md`
- `README.md`
- `deployment/mcpb/manifest.python.json`
- `deployment/mcpb/manifest.uv.json`
- `tests/agentic/agentic-tool-calls-tests.md`
- `specs/implementation-artifacts/deferred-work.md`

## Change Log

- 2026-09-22: Implemented and verified the native launch-attachment API overlay, typed facade, safe service seam, and bearer-token sandbox proof.
- 2026-09-22: Implemented the approved single-replica HTTP push broker, secure import-root pull path, strict MCP output contract, manifests, and documentation. Distributed shared capability state remains deferred as D-12-7.
