# Allure TestOps MCP Server

Lucius is a specialized Model Context Protocol (MCP) server for Allure TestOps, built with `FastMCP` and `Starlette`.

## 🎯 Motivation

Allure TestOps is a powerful tool with a huge API. When you're using an AI agent to manage your tests, it can easily get
lost in the details or fail because of a small technical mistake.

Lucius makes this easier by giving your AI tools that are simple to use and hard to break:

- **Clear Tools**: Every tool is designed for a specific task, like "finding a test case" or "updating a launch".
- **Helpful Errors**: If an AI makes a mistake, Lucius doesn't just return a code—it provides an "Agent Hint" that
  explains exactly what went wrong and how to fix it.
- **Solid Foundation**: We follow a clean "Thin Tool" structure, meaning the logic is consistent and easy for both
  humans and AI to follow.

## 🛠️ Supported Tools

| Tool Category          | Description                                      | All Tools                                                                                                                                                                                                                                |
|:-----------------------|:-------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Test Case Mgmt**     | Full lifecycle for test documentation.           | `create_test_case`, `update_test_case`, `delete_test_case`, `delete_archived_test_cases`, `get_test_case_details`, `list_test_cases`, `get_test_case_custom_fields`                                                                      |
| **Search & Discovery** | Advanced search and project metadata discovery.  | `search_test_cases`, `get_custom_fields`, `list_integrations`                                                                                                                                                                            |
| **Shared Steps**       | Create and manage reusable sequence sequences.   | `create_shared_step`, `list_shared_steps`, `update_shared_step`, `delete_shared_step`, `delete_archived_shared_steps`, `link_shared_step`, `unlink_shared_step`                                                                          |
| **Test Layers**        | Manage test taxonomy and auto-mapping schemas.   | `list_test_layers`, `create_test_layer`, `update_test_layer`, `delete_test_layer`, `list_test_layer_schemas`, `create_test_layer_schema`, `update_test_layer_schema`, `delete_test_layer_schema`                                         |
| **Test Hierarchy**     | Organize suites and assign tests in tree paths.  | `create_test_suite`, `list_test_suites`, `assign_test_cases_to_suite`, `delete_test_suite`                                                                                                                                               |
| **Custom Fields**      | Project-level management of custom field values. | `list_custom_field_values`, `create_custom_field_value`, `update_custom_field_value`, `delete_custom_field_value`, `delete_unused_custom_fields`                                                                                         |
| **Test Plans**         | Manage Test Plans and their content.             | `create_test_plan`, `update_test_plan`, `delete_test_plan`, `list_test_plans`, `manage_test_plan_content`                                                                                                                                |
| **Defect Mgmt**        | Track defects, linkage, and automation rules.    | `create_defect`, `get_defect`, `update_defect`, `delete_defect`, `list_defects`, `link_defect_to_test_case`, `list_defect_test_cases`, `create_defect_matcher`, `list_defect_matchers`, `update_defect_matcher`, `delete_defect_matcher` |

## 🚀 Quick Start

1. **Install uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **Setup Credentials**: Create a `.env` file with the variables below.
3. **Run Server**: `uv run start`

### Basic `.env` for Quick Start

| Variable | Description | Example |
|:---------|:------------|:--------|
| `ALLURE_ENDPOINT` | Allure TestOps base URL | `https://example.testops.cloud` |
| `ALLURE_PROJECT_ID` | Default Allure project ID | `123` |
| `ALLURE_API_TOKEN` | Allure API token | `<your_api_token>` |
| `MCP_MODE` | MCP transport mode for Lucius runtime | `stdio` |

### 🔌 Claude Desktop Integration

The easiest way to use Lucius in Claude Desktop is via the `.mcpb` bundle:

1. Download the latest `lucius-mcp.mcpb` from Releases.
2. Open with Claude Desktop.
3. Configure your Allure credentials in the UI.

### 💻 Claude Code Integration

To add Lucius to Claude Code, use the following command from within your project directory:

```bash
claude mcp add --transport stdio --scope project \
  --env ALLURE_ENDPOINT=https://example.testops.cloud \
  --env ALLURE_PROJECT_ID=123 \
  --env ALLURE_API_TOKEN=<your_api_token> \
  --env MCP_MODE=stdio \
  testops-mcp -- uvx --from lucius-mcp --refresh start
```

Project-scoped text config example (`.mcp.json`):

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
        "ALLURE_API_TOKEN": "<your_api_token>",
        "MCP_MODE": "stdio"
      }
    }
  }
}
```

### 🧠 Codex Integration

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

For detailed setup, including Claude Desktop (MCPB) integration, see [Setup Guide](docs/setup.md).

### 💻 Command-Line Interface (CLI)

Lucius also provides a universal CLI entry point for direct tool execution from the command line:

```bash
# Download pre-built binary for your platform
wget https://github.com/ivanostanin/lucius-mcp/releases/latest/download/lucius-linux-x86_64
chmod +x lucius-linux-x86_64
./lucius-linux-x86_64 --help

# List available actions for an entity
./lucius-linux-x86_64 test_case

# Execute an action
./lucius-linux-x86_64 test_case get --args '{"test_case_id": 1234}'

# Show help for a specific entity/action
./lucius-linux-x86_64 test_case get --help
```

**CLI Features:**
- 🎯 Type-safe entity/action invocation with validation
- 📊 Multiple output formats (JSON, table, csv, plain)
- 🔍 Per-action help with parameters and examples
- 🛡️ Clean error messages with guidance
- 📦 Standalone binaries for Linux, macOS, and Windows

For local CLI binary builds with Nuitka, use Python 3.13 (the build scripts and CI workflow enforce this).

For full CLI documentation and installation instructions, see [CLI Guide](docs/CLI.md).

### Shell Completions

Pre-generated shell completions are available in `deployment/shell-completions/`
for bash, zsh, fish, and PowerShell. They are generated from the current
entity/action route matrix:

```bash
python3 deployment/scripts/generate_completions.py
```

Load one in your shell profile, for example:

```bash
source deployment/shell-completions/lucius.bash
```

## 📂 Documentation

Full documentation is available in the [docs/](docs/index.md) folder:

- [Architecture & Design](docs/architecture.md)
- [Tool Reference](docs/tools.md)
- [Configuration & Setup](docs/setup.md)
- [Telemetry & Privacy](docs/telemetry.md)
- [Development Guide](docs/development.md)
- [AI Agent Protocol](docs/agent-documentation-protocol.md)

## 🤝 Contributing

Contributions are welcome! Please see the [Contribution Guidelines](CONTRIBUTING.md) and
the [Development Guide](docs/development.md) for more details.
