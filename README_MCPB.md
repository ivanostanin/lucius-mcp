# Lucius MCP Bundle

This is an MCP Bundle for the **Allure TestOps MCP Server**.

## Overview

Lucius MCP provides tools to interact with Allure TestOps directly from Claude or other MCP clients. You can create, update, search, and manage test cases and shared steps.

## Requirements

- Python >= 3.14
- `uv` package manager

## Installation & Usage

This bundle is designed to be run as an MCP server.

### Running with `uv`

The manifest specifies `server.type = "uv"`. Compatible clients (like Claude Desktop) can run this bundle directly.

To run manually:

```bash
uv run start
```

Or via the entry point:

```bash
uv run python -m src.main
```

## Tools

The bundle exposes the following tools:

- `create_test_case`: Create a new test case.
- `update_test_case`: Update an existing test case.
- `delete_test_case`: Archive a test case.
- `link_shared_step`: Link a shared step to a test case.
- `unlink_shared_step`: Unlink a shared step.
- `list_test_cases`: List test cases in a project.
- `search_test_cases`: Search by name or tag.
- `get_test_case_details`: Get full details of a test case.
- `create_shared_step`: Create a reusable shared step.
- `list_shared_steps`: List shared steps.
- `update_shared_step`: Update a shared step.
- `delete_shared_step`: Archive a shared step.

## Configuration

Ensure you have the following environment variables or configuration set:

- `ALLURE_ENDPOINT`: The URL of your Allure TestOps instance.
- `ALLURE_API_TOKEN`: Your API token.

You can set these in a `.env` file or pass them as environment variables to the runner.

## Develpment

```bash
npm install -g @anthropic-ai/mcpb
```

```bash
uv run deployment/scripts/build-mcpb.sh
```
