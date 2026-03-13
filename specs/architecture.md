---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2025-12-26'
inputDocuments:
  - 'lucius-mcp/specs/prd.md'
  - 'lucius-mcp/specs/analysis/product-brief-lucius-mcp-2025-12-25.md'
workflowType: 'architecture'
project_name: 'lucius-mcp'
user_name: 'Ivan Ostanin'
date: '2025-12-26'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
16 detailed FRs defining a specialized "Agent-First" interface for Allure TestOps. Focus is **Test Authoring** (Creating/Updating/Linking Test Cases and Shared Steps).
*   **Key Capabilities:** CRUD for Cases/Steps, Shared Steps, Search.
*   **Agent-Specifics:** Runtime auth overrides, idempotent updates.

**Non-Functional Requirements:**
*   **Performance:** Low overhead (<50ms) for agent interactivity.
*   **Robustness:** "Agent-Proof" error handling with remediation hints.
*   **Quality:** Strict typing (`mypy`), linting (`ruff`), high coverage (>85%), end-to-end tests.
*   **Observability:** Structured logging with Request ID correlation.

**Scale & Complexity:**
*   **Primary domain:** API Backend / MCP Server.
*   **Complexity level:** Medium (Complex entity models, stateless server logic).
*   **Estimated components:** 5-7 (Server, Service Layer, Pydantic Models, Client Wrapper, Auth Middleware, Logger).

### Technical Constraints & Dependencies

*   **Stack:** Python, `uv`, `starlette`.
*   **Core Library (Server Runtime):** `mcp` (Python SDK) - leveraging built-in `FastMCP` or `Server` classes.
*   **CLI Runtime Constraint:** CLI command execution must not depend on FastMCP runtime wiring (`src.main` import path).
*   **Validation:** `pydantic` models generated strictly from Allure OpenAPI 3.1.
*   **Transport:**
    *   `stdio` (Default for CLI/Desktop apps).
    *   `streamable http` (Via `mcp` SDK's standardized transport endpoint, mounted on Starlette).

### Cross-Cutting Concerns Identified

1.  **Authentication Context:** Handling static (Env) and dynamic (Tool Arg) auth transparently.
2.  **Agent-Optimized Error Handling:** Global translation of faults into "Agent Hints".
3.  **Schema Consistency:** Preventing runtime failures by strictly adhering to the generated spec.

## Starter Template Evaluation

### Primary Technology Domain
**Python API Backend (MCP Server)**

### Starter Options Considered
1.  **FastMCP (Recommended):** High-level framework, decorator-based, native Starlette support, production-ready.
2.  **SDK `Server` Class:** Low-level, explicit protocol handling. Overkill for this phase.

### Selected Starter: FastMCP

**Rationale for Selection:**
FastMCP abstract away the protocol complexity (serialization, transport, error handling), allowing focus on the Architectural Drivers (Pydantic Models + TestOps Logic). It natively supports the "Streamable HTTP" requirement and integrates easily with Starlette.

**Initialization Command:**

```bash
# Using uv for dependency management (modern, fast)
uv init lucius-mcp --app --python 3.14
uv add "mcp[cli,fastapi]" pydantic starlette uvicorn
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
*   Python 3.14 (Bleeding edge performance).
*   Managed via `uv`.

**Transports:**
*   **Stdio:** Default for local/desktop agent use.
*   **HTTP (SSE/Post):** Native support via `mcp` SDK for web/remote agents.

**Code Organization:**
*   Decorator-based registration (`@mcp.tool`, `@mcp.resource`).
*   Pydantic for data validation.

**Testing:**
*   `pytest` as testing framework.
*   `allure-pytest` for test reporting.
*   `unit`, `integration`, `e2e` test types.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
*   **Schema Strategy:** Build-time generation via `datamodel-code-generator` to ensure type safety.
*   **Response Format:** Text-based "Agent Hints" for 4xx/5xx errors (No silent failures).

### Data Architecture
*   **Models:** Pydantic v2 (Strict Mode).
*   **Generation:** `openapi-generator` (python generator) from `report-service.json` at build time into `src/client/generated/`. Generates both Pydantic v2 models and typed async API client methods.
*   **Pattern: Model Facade:**
    *   **Internal (`src/client/generated/`):** Auto-generated package containing `ApiClient`, controllers, and Pydantic Models. These files should NEVER be edited manually.
    *   **Facade Package (`src/client/models/`):** A public-facing package that categorizes internal models into functional modules.
*   **Validation:** Strict Input validation at MCP layer; Output validation skipped for speed.

### Authentication & Security
*   **JWT Token Exchange:** API tokens are exchanged for JWT Bearer tokens via `POST /api/uaa/oauth/token`.
*   **Automatic Renewal:** Tokens are refreshed 60 seconds before expiry to ensure uninterrupted operation.
*   **Middleware:** Starlette Middleware to normalize Auth (Env vs Header vs Tool Arg).
*   **Secrets:** Never logged; `SecretStr` used in Pydantic models.

### API & Communication Patterns
*   **Client:** Async API client auto-generated by `openapi-generator` using `httpx` for HTTP transport. Custom exception handling layer wraps generated client.
*   **Transport:** `fastmcp` mounted on `Starlette` app to support Streamable HTTP.
*   **Error Handling:** Global Exception Handler converting `AllureAPIError` to informative text responses.

### CLI Architecture (Service-First Course Correction)
*   **Command Model:** `lucius <entity> <action>` is the primary CLI grammar.
*   **Entity Discovery:** `lucius <entity>` returns available actions for that entity.
*   **Action Help:** `lucius <entity> <action> --help` shows description, parameters, and examples.
*   **Execution Path:** CLI routes entity/action commands to existing service behavior while preserving current tool semantics.
*   **Layering Rule:** Thick Service -> Thin CLI adapter. No new business layer and no new tool layer are introduced for CLI migration.

### Infrastructure & Deployment
*   **Runtime:** Python 3.14 (managed via `uv`).
*   **Dependency Management:** `pyproject.toml` managed by `uv`.

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
4 areas where AI agents could make different choices (Naming, Structure, Communication, Enforcement).

### Naming Patterns

**Code Naming Conventions:**
*   **Pydantic Models:** `PascalCase` (e.g., `TestCaseCreate`), strictly matching OpenAPI schema names where possible.
*   **Variables:** `snake_case` (e.g., `test_case_id`).
*   **Files:** `snake_case` (e.g., `test_ops_client.py`).
*   **Tools:** `snake_case` with explicit verb-noun (e.g., `create_test_case`, not `add_case`).
*   **CLI Entities:** `snake_case` singular canonical names (e.g., `test_case`, `test_plan`, `custom_field_value`) with optional plural aliases.
*   **CLI Actions:** `snake_case` verbs or verb phrases matching existing behavior (e.g., `create`, `list`, `delete_archived`, `manage_content`).

### Structure Patterns

**Project Organization:**
*   **Logic Location:** NO logic in `@mcp.tool` functions. Tools must be thin wrappers calling a Service Layer (e.g., `services/test_case_service.py`).
*   **Tests:** Co-located `__tests__` directory or standard `tests/` at root? -> **Pattern: `tests/` at root** matching Python standards.

### Communication Patterns (Agent Interface)

**Tool Prompts:**
*   All tools MUST return simple, text-based success messages ("Successfully created X") or informative error explanations.
*   NO raw JSON dumps unless specifically requested by the tool contract.
*   CLI actions MUST preserve equivalent behavior and support `json|table|plain` output formats (`json` default).

**Error Handling:**
*   `try/except` blocks in tools are **FORBIDDEN**.
*   Let the global exception handler catch `AllureError` and format the "Agent Hint".
*   **Actionable Error Handling:** The exception handler MUST supports "Schema Hints" by introspecting tool signatures to provide simplified usage examples when validation fails.

### Enforcement Guidelines

**All AI Agents MUST:**
*   Run `ruff` to enforce PEP8.
*   Run `mypy --strict` to enforce typing.
*   **Agent Rule:** "If you change a Pydantic model, you MUST re-run the generator."

## Project Structure & Boundaries

### Complete Project Directory Structure

```text
lucius-mcp/
├── deployment/                 # Infrastructure Configuration
│   ├── Dockerfile              # Multi-stage build for production
│   ├── .dockerignore
│   ├── scripts/                # Shell scripts for build, run, and push operations.
│   └── charts/                 # Helm Charts for Kubernetes deployment
│       └── lucius-mcp/
│           ├── Chart.yaml
│           ├── values.yaml
│           └── templates/
├── pyproject.toml              # Project dependencies and tool config (uv)
├── uv.lock                     # Lock file
├── README.md
├── .gitignore
├── .env.example                # Template for environment variables
├── src/
│   ├── main.py                 # Application Entrypoint (FastMCP)
│   ├── client/                 # Allure TestOps API Client
│   │   ├── client.py           # Wrapped httpx client
│   │   └── models/             # PUBLIC: Facade package for categorized access
│   │       ├── __init__.py     # Re-exports everything for convenience
│   │       ├── _generated.py   # INTERNAL: Monolithic auto-generated Pydantic Models
│   │       ├── common.py       # Pagination, Categories, Custom Fields
│   │       ├── test_cases.py   # Test Case specific DTOs
│   │       └── shared_steps.py # Shared Step specific DTOs
│   ├── tools/                  # MCP Tool Definitions (The "Interface")
│   │   ├── cases.py            # Test Case CRUD Tools
│   │   ├── shared_steps.py     # Shared Steps Tools
│   │   └── search.py           # RQL/Search Tools
│   ├── services/               # Business Logic Layer (The "Implementation")
│   │   ├── case_service.py     # Logic for manipulating Test Cases
│   │   └── auth_service.py     # Logic for credential validation
│   └── utils/                  # Shared Utilities
│       ├── auth.py             # Authentication Middleware
│       ├── error.py            # Global Exception Handler (Agent Hints)
│       └── logger.py           # Structured JSON Logger
└── tests/
    ├── __init__.py
    ├── conftest.py             # Pytest fixtures
    ├── unit/                   # Unit tests for Services
    │   └── test_case_service.py
    └── integration/            # End-to-end MCP Server tests
        └── test_tools.py
```

### Architectural Boundaries

**API Boundaries:**
*   **External:** `src/client/` is the strict boundary for all Allure TestOps API communication. No direct HTTP calls allowed outside this directory.
*   **Internal:** `src/tools/` is the entry boundary for MCP Protocol requests.

**Component Boundaries:**
*   **Tools vs Services:** Tools (`src/tools/`) are strictly parsing/validation layers. They MUST delegate all logic to Services (`src/services/`).
*   **CLI vs Services:** CLI (`src/cli/`) is a command adapter/formatter. It MUST delegate operational behavior to existing services and must not import MCP server runtime to execute commands.
*   **Deployment:** `deployment/` defines the infrastructure boundary. The app must run identically in Docker (`deployment/Dockerfile`) as it does locally via `uv`.

### Requirements to Structure Mapping

**Feature/Epic Mapping:**
*   **Test Case Management:** `src/tools/cases.py` + `src/services/case_service.py`
*   **Shared Steps:** `src/tools/shared_steps.py`
*   **Search/Discovery:** `src/tools/search.py`
*   **CLI Entity/Action Routing:** `src/cli/cli_entry.py` + static route metadata (`src/cli/data/tool_schemas.json`) mapped to existing `src/services/*`.

**Cross-Cutting Concerns:**
*   **Authentication:** `src/utils/auth.py` (Middleware) + `src/services/auth_service.py`
*   **Error Handling:** `src/utils/error.py`
*   **Deployment:** `deployment/` directory

### File Organization Patterns

**Configuration Files:**
*   **Build/Dep:** `pyproject.toml` (root)
*   **Runtime:** `.env` (root, excluded from git)
*   **Deployment:** `deployment/` (Directory for all K8s/Docker config)

**Source Organization:**
*   **Modules:** Grouped by Feature (`cases`, `shared_steps`) in `tools/` and `services/`.
*   **Entrypoint:** Single `src/main.py` for simplicity.

### Development Workflow Integration

**Build Process Structure:**
*   `uv` manages local venv.
*   `deployment/Dockerfile` uses `uv` for reproducible builds in production.

**Deployment Structure:**
*   **Docker:** Multi-stage build to keep image size small (no build tools in final image).
*   **Helm:** Standard chart structure in `deployment/charts/`.

### Automated Test Coverage Strategy

**CLI Coverage Model:**
*   **Unit Tests (`tests/cli/test_cli_basics.py`):**
    *   command grammar parsing for `lucius <entity> <action>`
    *   entity-only action listing behavior
    *   action help rendering shape and required sections
    *   output formatter behavior (`json|table|plain`)
*   **Mocked Integration Tests (`tests/cli/test_e2e_mocked.py`):**
    *   route-to-service invocation parity with representative action flows
    *   validation and confirm-gate behavior parity
    *   error hint parity and non-traceback guarantees
*   **E2E CLI Execution Tests:**
    *   real CLI process invocation for key entity/action flows
    *   startup/help/discovery latency and correctness checks
    *   FastMCP-decoupling guard (CLI path must not require `src.main` import)

**Coverage Gates:**
*   **Global:** maintain project threshold (>85%).
*   **CLI-specific:** enforce >=90% line coverage for `src/cli/`.
*   **Route coverage:** canonical CLI route table must have 100% automated test representation (at least one test per canonical `entity/action` command).

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
*   `FastMCP` + `Starlette` + `uv` create a cohesive modern Python stack.
*   `deployment/` folder cleanly separates infra from app logic.

**Structure Alignment:**
*   Strict `src/tools/` vs `src/services/` split enforces the decided business logic separation.

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:**
*   All 16 FRs map to specific Tool definitions in `src/tools/`.
*   Deployment requirements covered by dedicated `deployment/` folder.

**Non-Functional Requirements Coverage:**
*   **Quality:** CI/CD ready structure.
*   **Maintainability:** Clear separation of concerns.

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High

**Key Strengths:**
1.  **Strict Logic Separation:** Prevents "God Tools" by forcing logic into Services.
2.  **Modern Stack:** Python 3.14 + uv + FastMCP is bleeding edge but stable.
3.  **Clean Root:** Moving deployment files keeps the workspace tidy.

### Implementation Handoff

**First Priority:** Initialize project with `uv` and scaffold the directory tree including `deployment/`.

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅
**Total Steps Completed:** 8
**Date Completed:** 2025-12-26
**Document Location:** specs/architecture.md

### Final Architecture Deliverables

**📋 Complete Architecture Document**
*   All architectural decisions documented with specific versions.
*   Implementation patterns ensuring AI agent consistency.
*   Complete project structure with all files and directories.
*   Requirements to architecture mapping.
*   Validation confirming coherence and completeness.

**🏗️ Implementation Ready Foundation**
*   **Decisions:** FastMCP, Pydantic (Strict), Build-time Generation, Agent Hints.
*   **Patterns:** "Thin Tool" / "Fat Service", Strict logic separation.
*   **Structure:** Modern Python 3.14 + uv structure with dedicated `deployment/`.
*   **Requirements:** Full coverage of 16 FRs + NFRs.

**📚 AI Agent Implementation Guide**
*   Follow the "Agent Rules" for strict typing and error handling.
*   Use the `deployment/` folder for all infra work.
*   Respect the `src/tools/` vs `src/services/` boundary.

### Implementation Handoff

**For AI Agents:**
This architecture document is your complete guide for implementing `lucius-mcp`. Follow all decisions, patterns, and structures exactly as documented.

**First Implementation Priority:**
Initialize project using `uv` and scaffold the directory tree.

**Quality Assurance Checklist**
*   ✅ **Architecture Coherence:** Validated FastMCP + Starlette stack.
*   ✅ **Requirements Coverage:** Mapped all PRD items to structure.
*   ✅ **Implementation Readiness:** Detailed patterns for consistent coding.

### Project Success Factors
*   **Clean Separation:** Strict logic boundaries prevent tech debt.
*   **Modern Stack:** Leverages the latest Python ecoystem tools.
*   **Agent-Native:** Designed from the ground up for LLM interaction.

---

**Architecture Status:** READY FOR IMPLEMENTATION ✅

**Next Phase:** Begin implementation using the architectural decisions and patterns documented herein.
