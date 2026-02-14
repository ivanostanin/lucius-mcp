# Lucius MCP Server

A specialized Model Context Protocol (MCP) server for Allure TestOps, built with `FastMCP` and `Starlette`.

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

| Tool Category          | Description                                      | All Tools                                                                                                                                                                                        |
|:-----------------------|:-------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Test Case Mgmt**     | Full lifecycle for test documentation.           | `create_test_case`, `update_test_case`, `delete_test_case`, `get_test_case_details`, `list_test_cases`, `get_test_case_custom_fields`                                                            |
| **Search & Discovery** | Advanced search and project metadata discovery.  | `search_test_cases`, `get_custom_fields`, `list_integrations`                                                                                                                                    |
| **Shared Steps**       | Create and manage reusable sequence sequences.   | `create_shared_step`, `list_shared_steps`, `update_shared_step`, `delete_shared_step`, `link_shared_step`, `unlink_shared_step`                                                                  |
| **Test Layers**        | Manage test taxonomy and auto-mapping schemas.   | `list_test_layers`, `create_test_layer`, `update_test_layer`, `delete_test_layer`, `list_test_layer_schemas`, `create_test_layer_schema`, `update_test_layer_schema`, `delete_test_layer_schema` |
| **Custom Fields**      | Project-level management of custom field values. | `list_custom_field_values`, `create_custom_field_value`, `update_custom_field_value`, `delete_custom_field_value`                                                                                |
| **Test Plan Mgmt**       | Organize tests into executable plans.            | `create_test_plan`, `update_test_plan`, `manage_test_plan_content`, `list_test_plans`, `delete_test_plan`                                                                                        |
| **Launch Mgmt**        | Execution tracking and launch statistics.        | `create_launch`, `get_launch`, `list_launches`                                                                                                                                                   |

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