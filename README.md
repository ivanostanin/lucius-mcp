# Lucius MCP Server

A Model Context Protocol (MCP) server for Allure TestOps, built with `FastMCP` and `Starlette`.

## 🚀 Features

- **FastMCP Integration**: Leverages the FastMCP framework for efficient tool and resource management.
- **Starlette Mounting**: Mounted as a Starlette application for robust HTTP handling and easy extension.
- **Structured Logging**: JSON-formatted logging with automatic secret masking (powered by `src/utils/logger.py`).
- **Global Error Handling**: User-friendly "Agent Hint" error responses optimized for LLM consumption (powered by `src/utils/error.py`).
- **Type Safety**: Fully typed codebase checked with `mypy --strict`.
- **Quality Assurance**: Linting and formatting with `ruff`.

## ⚙️ Configuration

The server can be configured using environment variables or a `.env` file.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `ALLURE_ENDPOINT` | Allure TestOps Base URL | `https://demo.testops.cloud` |
| `ALLURE_PROJECT_ID` | Default Project ID | `None` |
| `ALLURE_API_TOKEN` | Allure API Token | `None` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `HOST` | Host to bind the server to | `127.0.0.1` |
| `PORT` | Port to bind the server to | `8000` |
| `MCP_MODE` | Running mode: `http` or `stdio` | `http` |

## 🛠️ Installation

This project uses `uv` for dependency management.

1.  **Install `uv`** (if not already installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Clone the repository**:
    ```bash
    git clone https://github.com/lucius-mcp/lucius-mcp.git
    cd lucius-mcp
    ```

3.  **Install dependencies**:
    ```bash
    uv sync
    ```

## 🏃 Usage

### Running via Claude Desktop (One-Click Install)

The easiest way to use Lucius in Claude Desktop is via the `.mcpb` bundle:

1.  **Download** the latest `lucius-mcp-x.y.z.mcpb` from the [GitHub Releases](https://github.com/lucius-mcp/lucius-mcp/releases).
2.  **Open** the file with Claude Desktop (macOS or Windows).
3.  **Approve** the installation in the dialog.
4.  **Configure** your Allure TestOps credentials in the provided fields.

### Running via Stdio (Manual/Dev)

For integration with MCP clients (like Claude Code) using standard input/output.

```bash
MCP_MODE=stdio uv run lucius-mcp
```

### Running via HTTP (Legacy/Dev)

Starts the server with hot-reloading enabled (default port: 8000).

```bash
uv run lucius-mcp
```

Or customizing host and port:

```bash
HOST=0.0.0.0 PORT=9000 uv run lucius-mcp
```

### Local Workflow Testing (act)

To run GitHub Actions locally using `nektos/act`:

1.  **Install `act`**:
    ```bash
    brew install act
    ```

2.  **Run a workflow**:
    ```bash
    # Run a specific workflow (e.g., CI)
    act -W .github/workflows/pr-quality-gate.yml 
    ```

    > **Note**: The `--artifact-server-path` flag is required to handle artifact uploads/downloads locally. Artifacts will be stored in `.artifacts/`.

## 📦 Packaging (MCPB)

Lucius supports the [MCP Bundle (MCPB)](https://github.com/modelcontextprotocol/mcpb) format for easy distribution.

### Building for Claude Desktop

To build a `.mcpb` bundle locally:

1.  **Install Node.js** (v20+ recommended).
2.  **Install the mcpb CLI**:
    ```bash
    npm install -g @anthropic-ai/mcpb
    ```
3.  **Run the build script**:
    ```bash
    ./deployment/scripts/build-mcpb.sh
    ```
    The versioned bundles will be available in the `dist/` directory:
    - `lucius-mcp-<version>-uv.mcpb`
    - `lucius-mcp-<version>-python.mcpb`

### Manifests

Bundle manifests live in `deployment/mcpb/`:
- `manifest.uv.json`
- `manifest.python.json`

### Validation

Validate each manifest against the code:

```bash
python deployment/scripts/validate_mcpb.py uv
python deployment/scripts/validate_mcpb.py python
```

### UV Runtime

The `uv` bundle uses the `uv` runtime type, which means:
- Dependencies are defined in `pyproject.toml` and `uv.lock`.
- Claude Desktop will automatically manage the Python environment and dependencies for the user.
- No local Python installation is required for the end-user.


## 🧪 Testing

Run the test suite using `pytest`:

```bash
uv run pytest
```

### End-to-End (E2E) Tests

E2E tests verify the integration with a real Allure TestOps instance. They are isolated in `tests/e2e/` and strictly separated from unit/integration tests.

**Prerequisites:**

1.  **Sandbox Environment**: Access to a non-production Allure TestOps instance.
2.  **Configuration**: Create `.env.test` from `.env.test.example`:
    ```bash
    cp .env.test.example .env.test
    ```

**Running E2E Tests:**

```bash
# Load environment variables from .env.test
uv run --env-file .env.test pytest tests/e2e/
```

**Troubleshooting E2E Failures:**

*   **401 Unauthorized**: Check `ALLURE_API_TOKEN`. It might be expired.
*   **403 Forbidden**: Ensure `ALLURE_PROJECT_ID` exists and the user has Write access.
*   **Connection Errors**: Verify `ALLURE_ENDPOINT` is reachable and uses HTTPS.
*   **Flaky Tests**: Tests use unique IDs to avoid collisions, but network issues can occur. Rerunning usually fixes transient issues.

## 🛠️ Development

### Regenerating API Client

To maintain spec-fidelity while keeping the client lightweight, we use a 2-step process:
1. **Filter Spec**: `scripts/filter_openapi.py` reduces the massive OpenAPI spec to only the essential controllers (Test Cases, Shared Steps, Projects).
2. **Generate Client**: `openapi-generator-cli` builds the client from the filtered spec.

- **Generated Client (`src/client/generated/`)**: Auto-generated `ApiClient`, API controllers, and Pydantic v2 models.
- **Client Facade (`src/client/client.py`)**: `AllureClient` wrapper that handles authentication, error mapping, and helper methods.
- **Model Facade (`src/client/models/`)**: Re-exports generated models for simplified import paths and logical grouping.

**To regenerate the client after updating the spec:**

```bash
./scripts/generate_testops_api_client.sh
```

> **Note**: Do not manually edit files in `src/client/generated/`.

## 🧹 Quality Checks

**Formatting**:
```bash
uv run ruff format .
```

**Linting**:
```bash
uv run ruff check src/
```

**Type Checking**:
```bash
uv run mypy --strict src/
```
