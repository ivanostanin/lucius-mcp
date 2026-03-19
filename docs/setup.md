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

## 🔌 Claude Desktop Integration

The easiest way to use Lucius in Claude Desktop is via the `.mcpb` bundle:

1. Download the latest `lucius-mcp.mcpb` from Releases.
2. Open with Claude Desktop.
3. Configure your Allure credentials in the UI.

## 💻 Claude Code Integration

To add Lucius to Claude Code, use the following command from within your project directory:

```bash
claude mcp add --transport stdio --scope project \
  --env ALLURE_ENDPOINT=https://example.testops.cloud \
  --env ALLURE_PROJECT_ID=123 \
  --env ALLURE_API_TOKEN=<your_api_token> \
  --env MCP_MODE=stdio \
  testops-mcp -- uvx --from lucius-mcp --refresh start
```

Project text config example (`.mcp.json`):

```json
{
  "mcpServers": {
    "testops-mcp": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "lucius-mcp",
        "--refresh",
        "start"
      ],
      "env": {
        "ALLURE_ENDPOINT": "https://example.testops.cloud",
        "ALLURE_PROJECT_ID": "123",
        "MCP_MODE": "stdio",
        "ALLURE_API_TOKEN": "<your_api_token>"
      }
    }
  }
}
```

## 🧠 Codex Integration

To add Lucius to Codex (CLI or IDE extension), use:

```bash
codex mcp add testops-mcp \
  --env ALLURE_ENDPOINT=https://example.testops.cloud \
  --env ALLURE_PROJECT_ID=123 \
  --env ALLURE_API_TOKEN=<your_api_token> \
  --env MCP_MODE=stdio \
  -- uvx --from lucius-mcp --refresh start
```

Text config example (`~/.codex/config.toml` or project `.codex/config.toml`):

```toml
[mcp_servers.testops-mcp]
command = "uvx"
args = ["--from", "lucius-mcp", "--refresh", "start"]

[mcp_servers.testops-mcp.env]
ALLURE_ENDPOINT = "https://example.testops.cloud"
ALLURE_PROJECT_ID = "123"
ALLURE_API_TOKEN = "<your_api_token>"
MCP_MODE = "stdio"
```

## 🛠️ Manual Installation

### Prerequisites

- Python 3.13 or later.
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

## 🔐 Telemetry & Privacy

Telemetry behavior, privacy guarantees, and the full data dictionary are documented in [Telemetry & Privacy](telemetry.md).

