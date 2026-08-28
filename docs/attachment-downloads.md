# Attachment downloads

Lucius delivers verified attachment evidence through a short-lived, one-time capability URL. The URL is a bearer secret: anyone who obtains it can download the file until it is consumed or expires. Do not log, share, or persist it.

Lucius first verifies the attachment against its supplied TestOps owner, then reads it through the authenticated Allure client and writes it to a private local cache. The URL never carries an Allure token or an upstream TestOps URL. A successful `GET` streams the cached file with `Cache-Control: no-store`; the entry is then deleted. Expired, reused, malformed, and unavailable handles return the same opaque failure response.

## Limits and configuration

These optional environment variables use safe defaults and are applied only when a verified download is prepared:

| Variable | Default | Purpose |
| --- | ---: | --- |
| `ATTACHMENT_DOWNLOAD_PUBLIC_BASE_URL` | unset | Required explicit externally reachable HTTP base URL. Lucius never advertises `0.0.0.0` or guesses a proxy hostname. |
| `ATTACHMENT_DOWNLOAD_CACHE_DIR` | system temporary directory | Private parent directory for the runtime cache. The broker creates owner-only subdirectories lazily. |
| `ATTACHMENT_DOWNLOAD_MAX_FILE_BYTES` | 104857600 | Per-file limit (100 MiB). |
| `ATTACHMENT_DOWNLOAD_MAX_ENTRIES` | 32 | Active one-time entry limit. |
| `ATTACHMENT_DOWNLOAD_MAX_TOTAL_BYTES` | 536870912 | Aggregate cache budget (512 MiB). |
| `ATTACHMENT_DOWNLOAD_TTL_SECONDS` | 300 | Lifetime of an unconsumed link in seconds. |

HTTP deployments must set `ATTACHMENT_DOWNLOAD_PUBLIC_BASE_URL` to the URL that MCP clients can actually reach. A loopback URL is only safe for a persistent stdio host and client on the same machine. One-shot `lucius` CLI commands exit after rendering output, so they must use the documented `--output` delivery fallback; they must not claim to return a live URL.

The internal broker is intentionally not a public MCP tool.
