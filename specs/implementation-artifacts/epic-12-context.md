# Epic 12 Context: Enhanced Launch and Test Result Management

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Give agents complete, stable, and evidence-ready inspection of launch-wide execution state and individual test results. The epic makes result discovery and diagnosis reliable without bloating collection responses or recursively expanding related executions, while ensuring evidence downloads are exposed through safe, short-lived capability links rather than credentials or attachment bytes in tool output.

## Stories

- Story 12.1: Retrieve Complete Individual Test Result Details
- Story 12.2: Broker Authenticated Attachment Downloads Through Short-Lived Capability Links
- Story 12.3: Prepare Attachment Downloads and Teach Agents the Safe Evidence Workflow
- Story 12.4: Extend Get Launch Info with Complete Execution Results
- Story 12.5: Remove Upstream Storage Keys from Test-Result Attachment Outputs

## Requirements & Constraints

- Individual result reads must provide a curated, stable Lucius-owned contract covering core result state and available enrichment, including execution hierarchy, fixtures, attachments, relations, and evidence metadata. Do not expose generated upstream DTOs or raw API dictionaries as public output.
- Use authoritative TestOps result identity and launch context. A result ID from a launch URL is the ID to read; unrelated URL parameters must not alter it. Build entity URLs only where the context and URL pattern are verified.
- Preserve attachment ownership and hierarchy: result attachments remain with the result, fixture attachments with their verified fixture, and step attachments with the corresponding step. Unsafe or unresolved ownership must be reported as unavailable rather than guessed.
- Treat enrichment as best effort. A successful authoritative core read must remain useful when optional sections fail, are unsupported, forbidden, malformed, or incomplete. Surface explicit partial-completeness and safe unavailable-section diagnostics, while distinguishing verified empty data from unavailable data and never exposing credentials or unsafe upstream errors.
- Represent history, retries, nested results, and other related executions as typed ID/link references only. Collection and relation views must not recursively hydrate full result details or attachments.
- Attachment preparation must validate the requested attachment's verified owner and kind before fetching content. Public responses must contain only opaque, short-lived, single-use capability links and download metadata—never bearer tokens, raw attachment URLs, cache paths, file bytes, or base64.
- The attachment broker must be lazy, concurrency-safe, privately cached, bounded, and cleaned up after successful use or expiry. It must have a tested lifecycle in each supported transport mode, including direct CLI execution.
- `get_launch` must remain backward compatible when execution inclusion is disabled, and launch listing must stay compact. When execution inclusion is enabled, return the available stable launch-scoped execution views exhaustively, retaining exact result IDs and upstream result statuses.
- Exhaust pagination and hierarchy traversal with non-progress, cycle, and malformed-pagination safeguards. On partial collection, return collected data with diagnostics instead of silently truncating or looping indefinitely. Open-launch data is a timestamped mutable snapshot, not inherently partial.
- Attachment metadata must omit upstream storage implementation keys at every public serialization boundary without changing supported owner context, hierarchy, or completeness semantics.
- MCP and CLI must expose equivalent structured behavior and concrete object-root output schemas. Agent-facing descriptions and CLI help must guide agents through the safe prepare-then-GET evidence workflow.
- Verification must cover complete and partial results, pagination, non-recursion, attachment ownership, capability expiry and single use, schema/manifest output, CLI behavior, and authenticated sandbox evidence retrieval.

## Technical Decisions

- Preserve the existing service-first architecture: tools and CLI routes delegate to shared service behavior, and rendering concerns such as table and CSV output remain CLI-specific.
- Map TestOps responses into application-owned DTOs so public contracts remain stable as generated client models evolve.
- Extend the filtered OpenAPI selection only through `scripts/filter_openapi.py`, then regenerate the TestOps client with `./scripts/generate_testops_api_client.sh`; never hand-edit generated client files. Reuse existing core result, execution, history, retry, fixture, attachment, launch, flat-result, and project-tree operations where possible.
- Use targeted upstream reads and page through index endpoints only where required to assemble references or complete stable collections. Do not add client-side result membership scans before authoritative result lookup.
- Make completeness first-class in result and launch DTOs: represent partial state, unavailable sections, safe reason/status information, and retrieved counts where useful rather than conflating failed enrichment with empty data.
- Serve prepared evidence through a persistent HTTP or loopback gateway appropriate to the runtime. The broker fetches content with Lucius's authenticated client, streams a cached file with download disposition, and revokes the capability after completion.

## UX & Interaction Patterns

- Agents use result IDs from launch execution rows or TestOps launch links to inspect a single result; tree query parameters are not part of the result identifier.
- Result and launch outputs give agents stable result IDs and verified navigation links, allowing a compact launch read to lead into a detailed result read without manual TestOps API reconstruction.
- Attachment-producing output communicates a two-step workflow: inspect attachment metadata, call `prepare_attachment_download` with the verified reference, then perform an HTTP GET on the returned capability link before it expires.
- Evidence output is metadata-first and safety-oriented: no credentials or payload bytes in conversational/MCP output, and unavailable data is explicit rather than silently absent.

## Cross-Story Dependencies

- The detailed result contract supplies the result IDs, attachment references, ownership context, and completeness semantics that the evidence-download workflow depends on.
- The capability broker underpins the public preparation tool and the attachment guidance used by result and test-case outputs.
- Expanded launch execution views provide exact result IDs and compact navigation into individual result reads; they must remain non-recursive to preserve the boundary between collection and detail views.
- Storage-key removal applies across result, step, and fixture attachment serialization without changing the broker's verified owner/kind contract.
