# Architecture & Design

Lucius is built with a focus on simplicity, type safety, and AI-first interaction.

## 🏗️ Core Patterns

### Thin Tool / Fat Service

To ensure maintainability and testability, Lucius strictly follows the "Thin Tool / Fat Service" pattern:

- **Tools (`src/tools/`)**: Responsible only for defining the MCP interface and delegating to services. They should
  contain minimal logic.
- **Services (`src/services/`)**: Contain all business logic, validation, and API coordination. Services are designed to
  be independent of the MCP transport.

### Agent Hints

Standard error messages are often too cryptic for AI agents to act upon. Lucius implements a "Global Exception
Handler" (`src/utils/error.py`) that converts technical errors into **Agent Hints**:

- Descriptive error names (e.g., `ResourceNotFoundError`).
- Context-specific advice (e.g., "Check if the Project ID is correct").
- Actionable suggestions for the agent's next step.

## 🛠️ Technology Stack

- **Core**: Python 3.14+
- **Frameworks**: FastMCP (MCP implementation), Starlette (HTTP transport).
- **Client**: **Accurate and Up-to-Date**: The API client is generated directly from the latest Allure TestOps
  definitions, so you can trust that it works correctly with the real platform.
- **Dependency Management**: `uv`.
- **Quality Tools**: `ruff` (linting/formatting), `mypy` (strict typing), `pytest` (testing).

## 📂 Folder Structure

- `src/main.py`: Application entry point and server initialization.
- `src/tools/`: MCP tool definitions grouped by feature.
- `src/services/`: Reusable business logic services.
- `src/client/`: API client (generated and facade).
- `src/utils/`: Shared utilities (logging, error handling, auth).
- `specs/`: Implementation artifacts and design specs.
- `tests/`: Comprehensive test suite (unit, integration, e2e).
