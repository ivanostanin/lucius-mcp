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
2. **Setup Credentials**: Create a `.env` file with `ALLURE_ENDPOINT`, `ALLURE_PROJECT_ID`, and `ALLURE_API_TOKEN`.
3. **Run Server**: `uv run start`

### 🔌 Claude Desktop Integration

The easiest way to use Lucius in Claude Desktop is via the `.mcpb` bundle:

1. Download the latest `lucius-mcp.mcpb` from Releases.
2. Open with Claude Desktop.
3. Configure your Allure credentials in the UI.

### 💻 Claude Code Integration

To add Lucius to Claude Code, use the following command from within your project directory:

```bash
claude mcp add testops-mcp --transport stdio \
   --env ALLURE_ENDPOINT=https://example.testops.cloud\
   --env ALLURE_PROJECT_ID=123 \
   --env ALLURE_API_TOKEN=your_token \
   --env MCP_MODE=stdio \
   -- uvx --from lucius-mcp --refresh start
```

For detailed setup, including Claude Desktop (MCPB) integration, see [Setup Guide](docs/setup.md).

### 🧪 Development

Set up a development environment:

```bash
# Clone the repo
git clone https://github.com/ivanostanin/lucius-mcp.git

# Install dependencies with uv
uv sync --extra dev

# Run unit tests
uv run pytest tests/ -v
```

## 🔐 Telemetry & Privacy

Lucius includes privacy-preserving telemetry to help maintainers understand runtime and tool usage trends.

- Telemetry is enabled by default.
- Telemetry runtime settings are defined in [`src/utils/config.py`](src/utils/config.py) via `TelemetryConfig`.
- Umami is the single telemetry backend and events are sent via the `umami-python` client.
- To disable telemetry at runtime without code edits, set `TELEMETRY_ENABLED=false`.
- Payloads include runtime/tool metadata (version, platform, mode, deployment method, outcome, duration bucket).
- Sensitive identifiers are hashed before sending (for example endpoint host and project id).
- Tool arguments, test content, API tokens, and secret values are never sent.

### Telemetry Data Dictionary

| Field | Purpose | Example | Sensitive/Hashed |
|:------|:--------|:--------|:-----------------|
| `server_version` | Server version trend | `0.6.1` | No |
| `python_version` | Runtime compatibility insight | `3.14.0` | No |
| `platform` | OS/arch distribution | `darwin-arm64` | No |
| `mcp_mode` | Transport usage | `stdio` | No |
| `deployment_method` | Install/run footprint | `uvx+pypi` | No |
| `tool_name` | Tool adoption | `create_test_case` | No |
| `outcome` | Success/error ratio | `success` | No |
| `duration_bucket` | Performance trend | `100-500ms` | No |
| `error_category` | Failure classification | `validation` | No |
| `endpoint_host_hash` | Installation grouping | `f8a2...` | Hashed |
| `project_id_hash` | Project-level grouping | `9d71...` | Hashed |
| `installation_id_hash` | Longitudinal installation metric | `b02e...` | Hashed |

## 📂 Documentation

Full documentation is available in the [docs/](docs/index.md) folder:

- [Architecture & Design](docs/architecture.md)
- [Tool Reference](docs/tools.md)
- [Configuration & Setup](docs/setup.md)
- [Development Guide](docs/development.md)
- [AI Agent Protocol](docs/agent-documentation-protocol.md)

## 🤝 Contributing

Contributions are welcome! Please see the [Contribution Guidelines](CONTRIBUTING.md) and
the [Development Guide](docs/development.md) for more details.
