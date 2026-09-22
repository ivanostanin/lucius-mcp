# Deferred Work

## D-12-7: Distributed launch-attachment upload capability state

**Status:** Deferred

**Source:** Story 12.8, `12-8-attach-files-to-existing-launch.md`

**Decision:** On 2026-09-22, the shared durable capability-state provider was deferred. The current implementation may serve upload capability URLs directly from Lucius's existing HTTP/Starlette server, but is explicitly limited to a single Lucius replica. It must not claim cross-pod replay protection or horizontal-scale support.

**Deferred scope:**

- Select, provision, and document a shared durable state provider (for example, Redis/Valkey or an equivalent deployment-owned coordinator).
- Persist opaque capability metadata, expiry, and atomic claim/complete/revoke state without storing file payloads or TestOps credentials.
- Provide exactly-once behavior when capability preparation and HTTP upload are handled by different Lucius replicas, including recovery after process failure and provider outages.
- Restore a multi-replica deployment contract, including Helm/ingress configuration, cleanup behavior, and tests using two independent Lucius runtimes against the same provider.
- Revisit retention, network policy, public ingress, and operational observability before enabling more than one replica.

**Interim constraints:**

- Run one Lucius HTTP replica for push uploads.
- Use the MCP server's externally reachable HTTPS address for upload URLs.
- Keep capability secrets opaque; never return source paths, file bytes, TestOps credentials, cookies, XSRF values, raw upstream errors, or provider details to MCP callers.
