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
| `MCP_MODE`          | Running mode: `stdio` or `http`          | `stdio`                      |

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
