# Telemetry & Privacy

Lucius includes privacy-preserving telemetry to help maintainers understand runtime and tool usage trends.

## Behavior

Telemetry sends best-effort runtime and tool usage metadata to Umami and never blocks tool results.

- Telemetry is enabled by default.
- Telemetry is sent to `https://stats.ostanin.me`, operated by the project owner; no third party has access to this endpoint.
- Telemetry runtime settings are defined in `src/utils/config.py` via `TelemetryConfig`.
- Umami is the single telemetry backend and emission uses the `umami-python` API client.
- To disable telemetry globally in code, set `TelemetryConfig.enabled = False`.
- To disable telemetry per runtime environment, set `TELEMETRY_ENABLED=false` (this env override takes precedence).
- To override Umami destination identity at runtime, set `TELEMETRY_WEBSITE_ID` and/or `TELEMETRY_HOSTNAME`.
- Sensitive identifiers are protected with HMAC-SHA256 using a local secret generated per installation.
- If that local secret cannot be loaded, sensitive identifier fields are emitted as `unknown` (never plain SHA-256).
- If `TelemetryConfig.umami_website_id` is unset, Lucius logs a concise warning and skips sending.
- Failures to reach Umami are swallowed and logged without stack traces.

## Runtime Overrides

| Variable | Description | Default |
|:---------|:------------|:--------|
| `TELEMETRY_ENABLED` | Optional telemetry override (`true`/`false`) | `None` (uses config default) |
| `TELEMETRY_WEBSITE_ID` | Optional Umami website ID override | `None` (uses config default) |
| `TELEMETRY_HOSTNAME` | Optional Umami hostname override | `None` (uses config default) |

## Data Dictionary

| Field | Purpose | Example | Sensitive/Protection |
|:------|:--------|:--------|:---------------------|
| `server_version` | Server version trend | `0.6.1` | No |
| `python_version` | Runtime compatibility insight | `3.13.0` | No |
| `platform` | OS/arch distribution | `darwin-arm64` | No |
| `mcp_mode` | Transport usage | `stdio` | No |
| `deployment_method` | Install/run footprint | `uvx+pypi` | No |
| `tool_name` | Tool adoption | `create_test_case` | No |
| `outcome` | Success/error ratio | `success` | No |
| `duration_bucket` | Performance trend | `100-500ms` | No |
| `error_category` | Failure classification | `validation` | No |
| `endpoint_host_hash` | Installation grouping | `f8a2...` | HMAC-SHA256 |
| `project_id_hash` | Project-level grouping | `9d71...` | HMAC-SHA256 |
| `installation_id_hash` | Longitudinal installation metric | `b02e...` | HMAC-SHA256 |

## Privacy Guardrails

- Sensitive identifiers use keyed HMAC-SHA256 before sending (for example, endpoint host and project id).
- Tool arguments, test content, API tokens, and secret values are never sent.
