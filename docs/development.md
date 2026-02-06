# Development Guide

This guide is for developers looking to extend or contribute to Lucius MCP.

## Prerequisites

Install Python packages

```bash
uv sync --all-extras
```

## 🛠️ Adding a New Tool

1. **Define the Service**: Add a new method to the relevant service in `src/services/` (or create a new service).
2. **Create the Tool**: Add a new function `src/tools/` and add it to `__all__` variable in `src/tools/__init__.py`.
   Ensure it follows the "Thin Tool" pattern.
3. **Register the Tool**: Once added to `src/tools/__init__.py`, new tool will be registered automatically .

## 🔄 Regenerating the API Client

We use a filtered OpenAPI spec to keep the client lightweight.

1. Update `scripts/filter_openapi.py` if you need new controllers.
2. Run the regeneration script:
   ```bash
   ./scripts/generate_testops_api_client.sh
   ```

## 🧹 Quality Checks

Before submitting a PR, ensure all checks pass:

- **Formatting**: `uv run ruff format .`
- **Linting**: `uv run ruff check .`
- **Type Checking**: `uv run mypy --strict src/`

## 🧪 Testing

### Unit & Integration Tests

```bash
uv run pytest tests/unit/ tests/integration/
```

### E2E Tests

Requires access to a sandbox Allure TestOps instance and all environment variables necessary to start the server set.

```bash
uv run --env-file .env.test pytest tests/e2e -n auto
```

### Full Linting and Testing Suite

```bash
uv run ruff format . && \
uv run ruff check . --fix --unsafe-fixes && \
uv run mypy src && \
uv run pytest tests/unit tests/integration && \
uv run --env-file .env.test pytest tests/e2e -n auto && \
uv run pytest tests/docs && \
uv run pytest tests/packaging  

```

## Building Distribution Packages

### MCP Bundles

Lucius can be packaged as an MCP Bundle (`.mcpb`) for easy installation in Claude Desktop.

#### Manifests

The configuration for the bundle is defined in `deployment/mcpb/`:

- `manifest.uv.json`: Recommended manifest that uses `uv` for high-performance dependency management and execution.
- `manifest.python.json`: Standard manifest using the system Python interpreter.

These manifests define the server metadata, required environment variables, and the entry point command. When adding new
tools, ensure they are listed in the `tools` section of the manifests if you want them to be prominently featured in the
MCPB installer UI.

#### Building

To build the bundle, you need the `@anthropic-ai/mcpb` package:

```bash
npm install -g @anthropic-ai/mcpb
```

Then run the build script:

```bash
uv run deployment/scripts/build-mcpb.sh
```

The script will generate the `.mcpb` file in the project root.

### Python Package

```bash
uv build
```

### Paackaging Tests

```bash
uv run pytest tests/packaging/
```

## Release process

1. Bump version in `pyproject.toml`.
2. Run `uv sync --all-extras` to update dependencies.
3. Write release notes in `CHANGELOG.md`.
4. Commit changes and push them to `main` via PR.
5. Create a tag for the new version on `main`.
6. Push tag.