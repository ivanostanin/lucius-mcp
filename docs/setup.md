# Configuration & Setup

Lucius can be run in different modes and environments. This guide covers how to get it up and running.

## ⚙️ Environment Variables

The server is configured via environment variables or a `.env` file.

| Variable            | Description                              | Default                      |
|:--------------------|:-----------------------------------------|:-----------------------------|
| `ALLURE_ENDPOINT`   | Allure TestOps Base URL                  | `https://demo.testops.cloud` |
| `ALLURE_PROJECT_ID` | Default Project ID                       | `None`                       |
| `ALLURE_API_TOKEN`  | Allure API Token                         | `None`                       |
| `LOG_LEVEL`         | Logging level (`DEBUG`, `INFO`, `ERROR`) | `INFO`                       |
| `LOG_FORMAT`        | Logging format (`json`, `console`)       | `json`                       |
| `MCP_MODE`          | Running mode: `stdio` or `http`          | `stdio`                      |
| `TELEMETRY_ENABLED` | Optional telemetry override (`true`/`false`) | `None` (uses config default) |
| `TELEMETRY_WEBSITE_ID` | Optional Umami website ID override | `None` (uses config default) |
| `TELEMETRY_HOSTNAME` | Optional Umami hostname override | `None` (uses config default) |

## 🔐 Telemetry Behavior

Telemetry sends best-effort runtime and tool usage metadata to Umami and never blocks tool results.

- Telemetry defaults are code-defined in `src/utils/config.py` (`TelemetryConfig`).
- Umami is the single telemetry backend and emission uses the `umami-python` API client.
- Default mode is enabled (`TelemetryConfig.enabled = True`).
- To disable telemetry globally in code, set `TelemetryConfig.enabled = False`.
- To disable telemetry per runtime environment, set `TELEMETRY_ENABLED=false` (this env override takes precedence).
- To override Umami destination identity at runtime, set `TELEMETRY_WEBSITE_ID` and/or `TELEMETRY_HOSTNAME`.
- If `TelemetryConfig.umami_website_id` is unset, Lucius logs a concise warning and skips sending.
- Failures to reach Umami are swallowed and logged without stack traces.

### Telemetry Data Dictionary

| Field | Purpose | Sample | Sensitive/Hashed |
|:------|:--------|:-------|:-----------------|
| `server_version` | Version trend | `0.6.1` | No |
| `python_version` | Runtime compatibility | `3.14.0` | No |
| `platform` | OS/arch distribution | `darwin-arm64` | No |
| `mcp_mode` | Transport usage | `stdio` | No |
| `deployment_method` | Deployment footprint | `docker` | No |
| `tool_name` | Tool adoption | `search_test_cases` | No |
| `outcome` | Success/error trend | `success` | No |
| `duration_bucket` | Latency trend | `100-500ms` | No |
| `error_category` | Error grouping | `api` | No |
| `endpoint_host_hash` | Endpoint grouping | `1d75...` | Hashed |
| `project_id_hash` | Project grouping | `7f03...` | Hashed |
| `installation_id_hash` | Install grouping | `a8cc...` | Hashed |

## 🔌 Claude Desktop Integration

The easiest way to use Lucius in Claude Desktop is via the `.mcpb` bundle:

1. Download the latest `lucius-mcp.mcpb` from Releases.
2. Open with Claude Desktop.
3. Configure your Allure credentials in the UI.

## 💻 Claude Code Integration

To add Lucius to Claude Code, use the following command from within your project directory:

```bash
claude mcp add testops-mcp --transport stdio \
   --env ALLURE_ENDPOINT=https://example.testops.cloud\
   --env ALLURE_PROJECT_ID=123 \
   --env ALLURE_API_TOKEN=your_token \
   --env MCP_MODE=stdio \
   -- uvx --from lucius-mcp --refresh start
```

Alternatively, you can manually add it to your `~/.claude.json`:

```json
{
  "mcpServers": {
    "lucius-mcp": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "lucius-mcp",
        "start"
      ],
      "env": {
        "ALLURE_ENDPOINT": "https://example.testops.cloud",
        "ALLURE_PROJECT_ID": "123",
        "MCP_MODE": "stdio",
        "ALLURE_API_TOKEN": "<your API token>"
      }
    }
  }
}
```

## 🛠️ Manual Installation

### Prerequisites

- Python 3.14 or later.
- [uv](https://astral.sh/uv/) for dependency management.

### Steps

1. **Clone the repo**:
   ```bash
   git clone https://github.com/lucius-mcp/lucius-mcp.git
   cd lucius-mcp
   ```
2. **Install dependencies**:
   ```bash
   uv sync
   ```

## 🏃 Running the Server

### Stdio Mode (for Claude Code / Desktop)

```bash
uv run --env-file .env start
```

### HTTP Mode (for web-based clients)

```bash
MCP_MODE=http uv run --env-file .env start
```
