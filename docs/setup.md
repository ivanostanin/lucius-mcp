# Configuration & Setup

Lucius can be run in different modes and environments. This guide covers how to get it up and running.

## CLI Authentication Choice

For direct CLI usage, you can either:

- set `ALLURE_ENDPOINT`, `ALLURE_API_TOKEN`, and `ALLURE_PROJECT_ID` in the environment, or
- save them once with `lucius auth`

Example:

```bash
lucius auth --url https://example.testops.cloud --token <your_api_token> --project 123
lucius auth status
lucius auth clear
```

Saved CLI auth location:

- Linux/Unix: `$XDG_CONFIG_HOME/lucius/auth.json` or `~/.config/lucius/auth.json`
- macOS: `~/Library/Application Support/lucius/auth.json` unless XDG overrides are explicitly set
- Windows: `%LOCALAPPDATA%\lucius\auth.json`

CLI auth precedence:

1. Explicit tool args such as `api_token` or `project_id`
2. Environment variables
3. Saved CLI auth config
4. Defaults

## CLI Shell Completions

For standalone CLI usage, install embedded shell completions from the binary or
wheel:

```bash
lucius install-completions
lucius install-completions --shell bash
lucius install-completions --shell zsh
lucius install-completions --shell fish
lucius install-completions --shell powershell
```

The command installs to user-level targets by default:

- bash: `${XDG_DATA_HOME:-~/.local/share}/bash-completion/completions/lucius`
- zsh: `${XDG_DATA_HOME:-~/.local/share}/zsh/site-functions/_lucius`
- fish: `${XDG_CONFIG_HOME:-~/.config}/fish/completions/lucius.fish`
- PowerShell: per-user Lucius completion script plus an idempotent profile hook

Use `--print --shell <shell>` to send the script to stdout without changing files.
Use `--path <file>` for custom destinations and `--force` to overwrite existing
completion files. Restart the shell after installation. Zsh users can activate
the default install path in the current session with
`fpath=(${XDG_DATA_HOME:-~/.local/share}/zsh/site-functions $fpath); autoload -Uz compinit && compinit`;
PowerShell profile hooks take effect in new sessions.

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

3. **Optional: save CLI auth for local command usage**:
   ```bash
   uv run lucius auth
   ```

4. **Optional: install CLI shell completions**:
   ```bash
   uv run lucius install-completions --shell zsh
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
