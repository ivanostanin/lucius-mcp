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

### Running via HTTP (Default)

Starts the server with hot-reloading enabled (default port: 8000).

```bash
uv run lucius-mcp
```

Or customizing host and port:

```bash
HOST=0.0.0.0 PORT=9000 uv run lucius-mcp
```

### Running via Stdio

For integration with MCP clients (like Claude Desktop) using standard input/output.

```bash
MCP_MODE=stdio uv run lucius-mcp
```


## 🧪 Testing

Run the test suite using `pytest`:

```bash
uv run pytest
```

## 🛠️ Development

### Regenerating API Models

The Allure TestOps API exposes a massive surface area with thousands of entities. To maintain both spec-fidelity and usability, we use a **Model Facade Pattern**:

- **Internal (`src/client/models/_generated.py`)**: A monolithic, auto-generated file containing 5,800+ lines of Pydantic models with 100% schema fidelity.
- **Facade (`src/client/models/`)**: A categorized package providing functional submodules for easier discovery:
  - `common.py`: Pagination, Categories, Custom Fields.
  - `test_cases.py`: Models specific to Test Case operations.
  - `shared_steps.py`: Models for Shared Step management.

**To regenerate internal models after updating the spec:**

```bash
./scripts/generate_models.sh
```

> **Note**: Do not manually edit `src/client/models/_generated.py`. For refinements or logical groupings, update the facade modules in `src/client/models/`.

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
