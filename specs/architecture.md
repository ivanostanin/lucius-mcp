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
user_name: 'Anmaro'
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
*   **Core Library:** `mcp` (Python SDK) - leveraging built-in `FastMCP` or `Server` classes.
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
*   **Generation:** `datamodel-code-generator` from `openapi.json` at build time.
*   **Validation:** Strict Input validation at MCP layer; Output validation skipped for speeed.

### Authentication & Security
*   **Middleware:** Starlette Middleware to normalize Auth (Env vs Header vs Tool Arg).
*   **Secrets:** Never logged; `SecretStr` used in Pydantic models.

### API & Communication Patterns
*   **Client:** Async `httpx` client wrapper (generated or thin wrapper).
*   **Transport:** `fastmcp` mounted on `Starlette` app to support Streamable HTTP.
*   **Error Handling:** Global Exception Handler converting `AllureAPIError` to informative text responses.

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

### Structure Patterns

**Project Organization:**
*   **Logic Location:** NO logic in `@mcp.tool` functions. Tools must be thin wrappers calling a Service Layer (e.g., `services/test_case_service.py`).
*   **Tests:** Co-located `__tests__` directory or standard `tests/` at root? -> **Pattern: `tests/` at root** matching Python standards.

### Communication Patterns (Agent Interface)

**Tool Prompts:**
*   All tools MUST return simple, text-based success messages ("Successfully created X") or informative error explanations.
*   NO raw JSON dumps unless specifically requested by the tool contract.

**Error Handling:**
*   `try/except` blocks in tools are **FORBIDDEN**.
*   Let the global exception handler catch `AllureError` and format the "Agent Hint".

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
│   │   ├── client.py           # Auto-generated/Wrapped httpx client
│   │   └── models.py           # Generated Pydantic Models for Allure
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
*   **Deployment:** `deployment/` defines the infrastructure boundary. The app must run identically in Docker (`deployment/Dockerfile`) as it does locally via `uv`.

### Requirements to Structure Mapping

**Feature/Epic Mapping:**
*   **Test Case Management:** `src/tools/cases.py` + `src/services/case_service.py`
*   **Shared Steps:** `src/tools/shared_steps.py`
*   **Search/Discovery:** `src/tools/search.py`

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


