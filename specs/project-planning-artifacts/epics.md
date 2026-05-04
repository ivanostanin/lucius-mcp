---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - 'specs/prd.md'
  - 'specs/architecture.md'
---

# lucius-mcp - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for lucius-mcp, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Agents can create new Test Cases with mandatory fields (Name) and optional metadata (Description, Preconditions).
FR2: Agents can define linear Test Steps (Action + Expected Result) to a Test Case.
FR3: Agents can attach shared/reusable steps to a Test Case by reference ID.
FR4: Agents can apply Tags, Custom Fields (e.g., Layer, Component), and Automation Status to Test Cases.
FR5: Agents can soft-delete Test Cases to archive them.
FR6: Agents can update existing Test Cases idempotently (partial updates supported).
FR7: Agents can create reusable Shared Steps with a set of child steps.
FR8: Agents can modify existing Shared Steps, propagating changes to all linked Test Cases.
FR9: Agents can list available Shared Steps to discover reusable logic.
FR10: Agents can list Test Cases filtered by Project ID.
FR11: Agents can retrieve the full details of a specific Test Case by its Allure ID.
FR12: Agents can search for Test Cases by Name or Tag (basic filtering).
FR13: Agents can authenticate operations using Environment Variables by default.
FR14: Agents can override authentication context (Token, Project ID) via tool arguments at runtime.
FR15: The system validates all inputs against strict schemas before sending to upstream API.
FR16: The system provides descriptive error hints when validation fails (e.g., "Missing field X").

### NonFunctional Requirements

NFR1: Tool execution overhead (deserialization -> API call -> serialization) must be < 50ms.
NFR2: Server startup time must be < 2 seconds.
NFR3: Agent-Proofing: The server must NEVER crash on invalid input; always return structured error hints.
NFR4: Schema fidelity must be 100% compliant with Allure Open API 3.1.
NFR5: API Tokens passed via environment variables must be masked in all logs.
NFR6: Input content is sanitized to prevent injection attacks.
NFR7: Unit Test coverage > 85%.
NFR8: 100% mypy strict type checking compliance.
NFR9: Code style and strict linting enforced via ruff.
NFR10: LLM-optimized docstrings for all Tools.
NFR11: End-to-End Tests: Implemented involving verification of tool execution results in sandbox TestOps instance or project.
NFR12: Structured Logging: All events must be logged in structured JSON format (level, timestamp, logger, message, context).
NFR13: Traffic Inspection: Logs must capture Tool Input arguments and (truncated) Output results for debugging.
NFR14: Correlation: Every tool call should generate a Request ID.
NFR15: Operational Metrics: The server must expose metrics (via logs or generic endpoint).

### Additional Requirements

- **Starter Template:** FastMCP (RECOMMENDED from Architecture).
- **Core Stack:** Python 3.14, uv, Starlette.
- **Implementation Pattern:** Strict separation of Tools (`src/tools/`) vs Services (`src/services/`).
- **Implementation Pattern:** Pydantic models generated from Allure OpenAPI 3.1 spec (`datamodel-code-generator`).
- **Implementation Pattern:** Global Exception Handler converting `AllureAPIError` to informative "Agent Hints".
- **Deployment:** Docker containerization and Helm support in (`deployment/`).
- **Auth:** Middleware to handle both Env vars and Runtime args transparently.
- **Client:** Async `httpx` client wrapper.

### FR Coverage Map

FR1: Epic 1 - Foundation & Test Case Management
FR2: Epic 1 - Foundation & Test Case Management
FR3: Epic 2 - Shared Step Reusability
FR4: Epic 1 - Foundation & Test Case Management
FR5: Epic 1 - Foundation & Test Case Management
FR6: Epic 1 - Foundation & Test Case Management
FR7: Epic 2 - Shared Step Reusability
FR8: Epic 2 - Shared Step Reusability
FR9: Epic 2 - Shared Step Reusability
FR10: Epic 3 - Search & Contextual Access
FR11: Epic 3 - Search & Contextual Access
FR12: Epic 3 - Search & Contextual Access
FR13: Epic 1 - Foundation & Test Case Management
FR14: Epic 3 - Search & Contextual Access
FR15: Epic 1 - Foundation & Test Case Management
FR16: Epic 1 - Foundation & Test Case Management

## Epic List

### Epic 1: Foundation & Test Case Management (MVP)
Establish the MCP server foundation and enable Agents to manage the core "Test Case" entity, allowing for autonomous documentation of test scenarios. This includes the core architecture, authentication, and error handling mechanisms.
**FRs covered:** FR1, FR2, FR4, FR5, FR6, FR13, FR15, FR16

### Epic 2: Shared Step Reusability (MVP)
Enable Agents to maintain a high-quality, reusable test library by managing Shared Steps and linking them to Test Cases. This prevents duplication and allows for scalable test maintenance.
**FRs covered:** FR3, FR7, FR8, FR9

### Epic 3: Search & Contextual Access (MVP)
Enable Agents to discover existing artifacts through listing and basic search, and support dynamic context switching (Runtime Auth). This enables "Read-before-Write" workflows essential for refactoring and updates.
**FRs covered:** FR10, FR11, FR12, FR14

### Epic 4: Production Operations (Phase 2 Priority)
Provide production-grade deployment capabilities, including Docker containerization and Helm charts, to allow enterprise users to deploy the MCP server in managed environments.
**FRs covered:** Derived from Phase 2 Requirements (Docker, Helm, CI/CD)

### Epic 5: Execution Management (Phase 2)
Enable Agents manage Launches in Allure TestOps.
**FRs covered:** Derived from Phase 2 Requirements (Launches, Reporting)

### Epic 6: Advanced Organization & Discovery (Phase 2)
Enable Agents to manage complex test hierarchies (Trees, Suites) and perform advanced search operations, facilitating management of large-scale test repositories.
**FRs covered:** Derived from Phase 2 Requirements (Hierarchy, Rich Search)

### Epic 7: Test Planning & Governance (Phase 3)
Enable Agents to manage high-level Test Plans and Defects, supporting full lifecycle quality assurance and governance workflows.
**FRs covered:** Derived from Phase 3 Requirements (Test Plans, Defects)

### Epic 8: Enterprise Security & Intelligence (Phase 3)
Implement advanced security protocols (OAuth, TLS) and higher-order "Agent Skills" for autonomous repository maintenance and complex reasoning workflows.
**FRs covered:** Derived from Phase 3 Requirements (Security, Skills)

## Epic 1: Foundation & Test Case Management

Establish the MCP server foundation and enable Agents to manage the core "Test Case" entity, allowing for autonomous documentation of test scenarios. This includes the core architecture, authentication, and error handling mechanisms.

### Story 1.1: Project Initialization & Core Architecture

As a Developer,
I want to initialize the lucius-mcp repository with uv, fastmcp, and starlette,
So that I have a production-ready, structured foundation for the MCP server.

**Acceptance Criteria:**

**Given** a new repository
**When** I run the initialization scripts
**Then** the project structure is created including `src/main.py`, `src/services/`, and `src/utils/`
**And** `uv` dependency management is configured with Python 3.14
**And** FastMCP is mounted on a Starlette application
**And** Structured JSON logging and the global exception handler for "Agent Hints" are implemented.

### Story 1.2: Generated Client & Data Models

As a Developer,
I want to generate Pydantic models from the Allure TestOps OpenAPI spec,
So that I can interact with the API with 100% schema fidelity and strict type safety.

**Acceptance Criteria:**

**Given** the Allure TestOps OpenAPI 3.1 spec
**When** I run the model generator
**Then** Pydantic v2 models are successfully created in `src/client/models.py`
**And** a thin `httpx` based `AllureClient` is created in `src/client/client.py`
**And** `mypy --strict` passes for the generated models and client.

### Story 1.3: Comprehensive Test Case Creation Tool

As an AI Agent,
I want to create a new Test Case with all available metadata (Name, Description, Precondition, Steps, Checks, Tags, Custom Fields, Attachments),
So that I can document complex test scenarios in a single operation.

**Acceptance Criteria:**

**Given** a valid Allure API Token and Project ID
**When** I call the `create_test_case` tool with comprehensive metadata (including Steps, Tags, and Custom Fields)
**Then** the tool validates the input against the full Pydantic schema
**And** it successfully creates the test case with all provided fields correctly mapped in Allure TestOps
**And** it handles attachments (Base64 or URL) according to the API spec
**And** it returns a clear success message with the new Test Case ID.

### Story 1.4: Idempotent Update & Maintenance

As an AI Agent,
I want to update fields of an existing test case idempotently,
So that I can refine test documentation without creating duplicates or losing data.

**Acceptance Criteria:**

**Given** an existing Test Case ID
**When** I call `update_test_case` with partial fields
**Then** the system performs a partial update without overwriting unspecified fields
**And** repeated calls with the same data result in no state change (idempotency)
**And** the server returns a confirmation of the update.

### Story 1.5: Soft Delete & Archive

As an AI Agent,
I want to archive obsolete test cases,
So that the test repository remains focused on the current product state.

**Acceptance Criteria:**

**Given** an existing Test Case
**When** I call `delete_test_case`
**Then** the test case status is updated to "Archived" or moved to the soft-delete bin in Allure
**And** the tool returns a confirmation of the archival.

### Story 1.6: Comprehensive End-to-End Tests

As a Developer,
I want comprehensive end-to-end tests that verify tool execution results against a sandbox TestOps instance,
So that I can ensure the MCP server correctly integrates with Allure TestOps in real-world scenarios.

**Acceptance Criteria:**

**Given** a sandbox Allure TestOps instance
**When** I run the E2E test suite
**Then** all Test Case CRUD operations are verified against actual API responses
**And** tests validate that tool outputs match expected formats (Agent Hint messages)
**And** tests run in CI/CD pipeline with configurable sandbox credentials
**And** test execution is isolated (cleanup after each test run).

### Story 1.7: Tool Error Hints & Validation Feedback

As an AI Agent,
I want to receive clear, actionable error hints when my tool inputs are invalid or incomplete,
So that I can autonomously correct my requests and successfully execute the tool.

**Acceptance Criteria:**

**Given** a tool call (e.g., `create_test_case`, `update_test_case`) with missing mandatory fields or invalid data types
**When** the validation fails
**Then** the tool returns a structured error message indicating EXACTLY which fields failed and why
**And** the error message includes a "Hint" section with the correct schema or expected format
**And** comprehensive integration tests verify this behavior by simulating erroneous and incomplete LLM inputs
**And** these tests validate that the correction hints are present and accurate in the error response.

## Epic 2: Shared Step Reusability

Enable Agents to maintain a high-quality, reusable test library by managing Shared Steps and linking them to Test Cases. This prevents duplication and allows for scalable test maintenance.

### Story 2.1: Create & List Shared Steps

As an AI Agent,
I want to create reusable Shared Steps and list them,
So that I can build a library of common test logic for discovery and reuse.

**Acceptance Criteria:**

**Given** a Project ID
**When** I call `create_shared_step` with a name and a list of steps
**Then** the shared step is created in the Allure library
**And** when I call `list_shared_steps`, it returns the new step among others
**And** the tools provide LLM-optimized descriptions for discovery.

### Story 2.2: Update & Delete Shared Steps

As an AI Agent,
I want to modify or remove Shared Steps in the library,
So that the reusable library can evolve alongside the product requirements.

**Acceptance Criteria:**

**Given** an existing Shared Step
**When** I call `update_shared_step` to modify its steps or metadata
**Then** the changes are saved and propagated where applicable
**And** when I call `delete_shared_step`, it is removed/archived from the library.

### Story 2.3: Link Shared Step to Test Case

As an AI Agent,
I want to attach a Shared Step to a Test Case by reference ID,
So that I can maintain consistency and reduce manual duplication of test logic.

**Acceptance Criteria:**

**Given** a Test Case and a Shared Step ID
**When** I add the shared step reference to the Test Case's step list
**Then** the Allure API correctly links the shared logic to the test case
**And** the test case reflects the shared steps in its execution flow.

## Epic 3: Search & Contextual Access

Enable Agents to discover existing artifacts through listing and basic search, and support dynamic context switching (Runtime Auth). This enables "Read-before-Write" workflows essential for refactoring and updates.
**FRs covered:** FR10, FR11, FR12, FR14

### Story 3.1: List Test Cases by Project

As an AI Agent,
I want to list all Test Cases within a specific project,
So that I can get an overview of the existing test documentation.

**Acceptance Criteria:**

**Given** a valid Project ID
**When** I call `list_test_cases`
**Then** the tool returns a list of Test Cases (e.g., ID, Name, Tags) for that project
**And** the list can be paginated or filtered for large results.

### Story 3.2: Retrieve Full Test Case Details

As an AI Agent,
I want to retrieve the complete details of a specific Test Case,
So that I can understand its full context, steps, and metadata.

**Acceptance Criteria:**

**Given** a valid Test Case ID
**When** I call `get_test_case_details`
**Then** the tool returns the full Test Case object, including all steps, tags, and custom fields
**And** it handles cases where the Test Case ID is not found with a clear error.

### Story 3.3: Search Test Cases by Name or Tag

As an AI Agent,
I want to search for Test Cases using keywords in their name or by specific tags,
So that I can quickly find relevant test documentation.

**Acceptance Criteria:**

**Given** a search query (e.g., "login flow" or "tag:smoke")
**When** I call `search_test_cases`
**Then** the tool returns a list of matching Test Cases
**And** the search is case-insensitive for names and tags.

### Story 3.4: Runtime Authentication Override

As an AI Agent,
I want to override the default authentication context (API Token, Project ID) at runtime,
So that I can operate across different projects or with different credentials within a single session.

**Acceptance Criteria:**

**Given** a tool call that requires authentication
**When** I provide `api_token` and `project_id` arguments directly to the tool
**Then** these arguments override any environment variables or default configurations
**And** the operation is executed successfully with the provided context.

## Epic 4: Production Operations

Provide production-grade deployment capabilities, including Docker containerization and Helm charts, to allow enterprise users to deploy the MCP server in managed environments.
**FRs covered:** Derived from Phase 2 Requirements (Docker, Helm, CI/CD)

### Story 4.1: Docker Containerization

As a DevOps Engineer,
I want the lucius-mcp server to be packaged as a Docker image,
So that it can be easily deployed and managed in containerized environments.

**Acceptance Criteria:**

**Given** the lucius-mcp source code
**When** I run `docker build`
**Then** a Docker image is successfully created
**And** the image can be run to start the Starlette server on a specified port
**And** environment variables for configuration (e.g., `ALLURE_API_TOKEN`) are correctly consumed.

### Story 4.2: Helm Chart for Kubernetes Deployment

As a DevOps Engineer,
I want a Helm chart for lucius-mcp,
So that I can deploy and manage the server on Kubernetes clusters.

**Acceptance Criteria:**

**Given** a Kubernetes cluster
**When** I run `helm install lucius-mcp ./helm/lucius-mcp`
**Then** the lucius-mcp application is deployed as a Pod and Service
**And** configuration values (e.g., replica count, resource limits, environment variables) can be customized via `values.yaml`
**And** the deployment includes readiness and liveness probes.

### Story 4.3: GitHub Actions CI/CD

As a Developer,
I want to implement GitHub Actions workflows for continuous integration and delivery,
So that code quality is automatically validated and Docker images are built on releases.

**Acceptance Criteria:**

**Given** a pull request or release tag
**When** the GitHub Actions workflow is triggered
**Then** it runs linting with `ruff`, type checking with `mypy --strict`, and unit tests
**And** on release tags, it builds the Docker image and pushes it to the container registry
**And** on pull requests, it runs integration tests
**And** on pull requests, it builds the Docker image with feature tags and pushes it to the container registry
**And** the workflow reports pass/fail status to the pull request.

## Epic 5: Execution Management

Enable Agents to manage Launches in Allure TestOps.

### Story 5.1: Create & List Launches

As an AI Agent,
I want to create new test launches and list existing ones,
So that I can organize test execution sessions in Allure TestOps.

**Acceptance Criteria:**

**Given** a valid Project ID
**When** I call `create_launch` with a name and optional metadata
**Then** a new launch is created in Allure TestOps
**And** when I call `list_launches`, it returns all launches for the project including the newly created one.

### Story 5.2: Get Launch Details

As an AI Agent,
I want to retrieve the full details of a specific launch,
So that I can inspect its status, test results, and execution context.

**Acceptance Criteria:**

**Given** a valid Launch ID
**When** I call `get_launch`
**Then** the server returns the complete launch information including status, start/end times, and associated test results
**And** it handles invalid Launch IDs with a clear error message.

### Story 5.3: Delete Launch

As an AI Agent,
I want to delete or archive obsolete launches,
So that the launch history remains focused and manageable.

**Acceptance Criteria:**

**Given** an existing Launch ID
**When** I call `delete_launch`
**Then** the launch is removed or archived from Allure TestOps
**And** the tool returns a confirmation of the deletion.

### Story 5.4: Close/Finalize & Reopen Launch

As an AI Agent,
I want to finalize a launch and mark it as complete, or reopen a closed launch,
So that I can control the launch lifecycle and make corrections when needed.

**Acceptance Criteria:**

**Given** an open Launch ID
**When** I call `close_launch`
**Then** the launch status is updated to "Closed" or "Finalized"
**And** Allure TestOps triggers report generation for that launch
**And** subsequent attempts to add results to the closed launch are prevented with a clear error
**And** when I call `reopen_launch` on a closed launch
**Then** the launch status is updated to "Open" and I can add additional test results.

## Epic 6: Advanced Organization & Discovery

Enable Agents to manage complex test hierarchies (Trees, Suites) and perform advanced search operations, facilitating management of large-scale test repositories.

### Story 6.1: Test Hierarchy Management

As an AI Agent,
I want to create and manage test suites and tree structures,
So that I can organize tests into logical hierarchies for large repositories.

**Acceptance Criteria:**

**Given** a Project ID
**When** I call `create_test_suite` with a name and parent suite (if nested)
**Then** a new test suite is created in Allure TestOps
**And** I can assign test cases to the suite
**And** when I call `list_test_suites`, it returns the hierarchical structure of all suites.

### Story 6.2: Advanced Search with AQL

As an AI Agent,
I want to perform complex searches using Allure's query language (AQL),
So that I can find test cases using sophisticated filtering patterns.

**Acceptance Criteria:**

**Given** a complex search query (e.g., "status:failed AND tag:regression")
**When** I call `advanced_search` with the AQL query
**Then** the server returns all matching test cases
**And** it supports operators like AND, OR, NOT, and field-specific filters
**And** it provides clear error messages for invalid AQL syntax.

## Epic 7: Test Planning & Governance

Enable Agents to manage high-level Test Plans and Defects, supporting full lifecycle quality assurance and governance workflows.

### Story 7.1: Test Plan Management

As an AI Agent,
I want to create and manage Test Plans using manual selection or filters/AQL queries,
So that I can organize testing efforts around specific releases or milestones efficiently.

**Acceptance Criteria:**

**Given** a Project ID
**When** I call `create_test_plan` with a name and either a list of test case IDs OR an AQL filter query
**Then** a new Test Plan is created in Allure TestOps with the selected test cases
**And** when using AQL filters (e.g., "tag:smoke AND layer:api"), the system automatically selects all matching test cases
**And** when I call `edit_test_plan`, I can modify the plan name, description, or update the test case selection
**And** I can add or remove test cases from the plan after creation
**And** when I call `list_test_plans`, it returns all plans with their current status.

### Story 7.2: Defect Lifecycle Management with Automation Rules

As an AI Agent,
I want to create, update, and track defects with automation rules,
So that test results can be automatically associated with defects based on error patterns.

**Acceptance Criteria:**

**Given** a failed test result
**When** I call `create_defect` with details (title, description, severity, linked test case)
**Then** a new defect is created in Allure TestOps
**And** when I call `add_automation_rule` with regex patterns for error messages or stack traces
**Then** the defect is automatically linked to future test results matching those patterns
**And** when I call `update_defect`, I can change its status (Open, In Progress, Resolved, Closed) and modify automation rules
**And** when I call `get_defect`, it returns full defect details including linked test cases, automation rules, and resolution history.

## Epic 8: Enterprise Security & Intelligence

Implement advanced security protocols (OAuth, TLS) and higher-order "Agent Skills" for autonomous repository maintenance and complex reasoning workflows.

### Story 8.1: MCP Server Authentication (OAuth/OIDC via NGINX Ingress)

As a DevOps Engineer,
I want to secure the MCP server with OAuth 2.0/OIDC authentication at the infrastructure level,
So that only authorized clients can access the lucius-mcp tools and resources.

**Acceptance Criteria:**

**Given** an MCP server deployed behind NGINX Ingress
**When** OAuth2 Proxy is configured with an OIDC provider (e.g., Auth0, Okta, Keycloak)
**Then** all requests to the MCP server require valid OAuth tokens
**And** unauthenticated requests are redirected to the OAuth login flow
**And** the NGINX Ingress configuration supports both Authorization Code and Client Credentials flows
**And** token validation and refresh are handled by OAuth2 Proxy before reaching the application.

### Story 8.2: MCP Transport Security (TLS/mTLS)

As a Security Engineer,
I want to encrypt the MCP protocol transport using TLS and optionally mutual TLS,
So that communication is secure and client identity can be verified via certificates.

**Acceptance Criteria:**

**Given** an MCP server deployment
**When** TLS is configured with valid certificates
**Then** all client-server communication is encrypted
**And** when mutual TLS (mTLS) is enabled, clients must present valid certificates
**And** certificate rotation is supported without service interruption.

### Story 8.3: Agent Skill Definitions (MCP Prompts)

As a QA Engineer or SDET,
I want to provide AI agents with documented multi-step workflows (skills) via MCP prompts,
So that agents can autonomously execute complex test management tasks.

**Acceptance Criteria:**

**Given** the MCP server with skill prompt resources defined
**When** an QA Engineer or SDET has access to the MCP server code repository
**Then** it can view skills like "Auto-Generate Test Cases from PR"
**And** each skill provides a step-by-step workflow guide:
  - Example: Fetch Jira acceptance criteria → Extract GitHub PR description → Analyze code changes → Design test cases → Create in TestOps
**And** the prompt includes context, required tools, and expected outcomes
**And** QA teams can add new skill definitions by creating MCP prompt resource files.

### Story 8.4: Security Hardening & Audit

As a Compliance Officer,
I want comprehensive security controls and audit logging for the MCP server,
So that we meet enterprise security standards and can investigate incidents.

**Acceptance Criteria:**

**Given** a production MCP server deployment
**When** the Helm chart is configured with security policies
**Then** rate limiting is enforced at the NGINX Ingress level (e.g., max 100 requests/minute per client IP)
**And** IP allowlisting restricts access to approved networks via Ingress annotations
**And** all authenticated requests are logged by the application with structured audit trails (user, timestamp, tool invoked, result)
**And** audit logs are written in JSON format and exportable for SIEM integration
**And** the Helm chart provides configurable values for rate limits, allowed IPs, and log retention.


## Epic 9: Documentation & Knowledge Base & CLI

Provide comprehensive documentation and developer tools for lucius-mcp, including CLI access for direct tool invocation without MCP client runtime.

### Story 9.1: Comprehensive Project Documentation

As a Developer or QA Engineer,
I want comprehensive documentation covering architecture, installation, configuration, and usage,
So that I can quickly understand and onboard to the lucius-mcp project.

**Acceptance Criteria:**

**Given** a properly structured project
**When** developers access the repository documentation
**Then** all critical aspects are documented:
  - Architecture overview with diagrams
  - Installation and setup instructions
  - Configuration guide (environment variables, MCP client setup)
  - Tool API reference with examples
  - Testing guidelines and standards
  - Troubleshooting common issues
**And** documentation is kept up-to-date with code changes
**And** code examples are tested and verified
**And** diagrams reflect the actual system architecture

### Story 9.2: FastMCP CLI Integration

As a Developer or QA Engineer,
I want a universal CLI entry point `lucius` with subcommands that provide type-safe access to all MCP tools,
so that I can execute lucius-mcp functionality directly from the command line without requiring an MCP client runtime.

**CLI Design Principles (Course Correction):**

1. **No MCP/Python Logs in Output**
   - CLI should never display MCP server logs or Python tracebacks
   - Only user-facing error messages shown
   - All exceptions caught and formatted as clear error messages

2. **Guiding Error Messages**
   - Tool call errors provide guiding messages explaining what went wrong
   - Validation errors show meaningful hints (same as MCP server behavior)
   - Error messages include suggestions for fixes

3. **Use MCP Tools, Don't Reimplement**
   - CLI uses MCP server tools directly
   - CLI does NOT reimplement business logic or API calls
   - CLI is thin wrapper around MCP tools for command-line access
   - Exception: CLI-specific functionality like --version, --help

4. **Individual Tool Help**
   - Every tool has its own `--help` command
   - `lucius call <tool_name> --help` shows isolated tool documentation
   - Help includes: tool description, parameters, types, formats, examples
   - Help generated from MCP tool schema (not duplicated)

5. **Multiple Output Formats**
   - Every command supports: JSON, table, plain
   - JSON is the DEFAULT output format
   - Flag: `--format json|table|plain` or `-f json|table|plain`
   - Consistent output formatting across all commands

6. **Lazy Client Initialization**
   - `lucius list` uses static info built at build time
   - No MCP client initialization for `lucius list`
   - MCP client initialized ONLY when `lucius call <tool>` invoked
   - ONLY called tool loaded (eager imports removed from CLI entry point)
   - Fast startup (~< 1s) for help/version/list commands

7. **No HTTP Server in CLI**
   - HTTP server never imported or used in CLI
   - CLI uses stdio transport only
   - No Starlette, uvicorn, or HTTP-related imports in CLI code
   - Compiled binary must NOT include HTTP server components

**Acceptance Criteria:**

**Given** a lucius-mcp installation
**When** I run CLI commands
**Then** the following commands are available and work correctly:

**P0 (Must-Have):**

1. **CLI Entry Point**: Universal CLI entry point `lucius` with subcommands following pattern `lucius <command> [options]`

2. **Single Binary Distribution**: Compile CLI to standalone binaries using nuitka for:
   - Linux (ARM64, x86_64)
   - macOS (ARM64, x86_64)
   - Windows (ARM64, x86_64)

3. **Type-Safe Interface**: Implement type-safe CLI commands using cyclopts framework, leveraging JSON schemas from MCP tool definitions

4. **Core Commands**:
   - `lucius list [--format json|table|plain]` - List available tools using build-time static data (no MCP client)
   - `lucius call <tool_name> --args <json> [--format json|table|plain]` - Execute MCP tools via CLI
   - `lucius call <tool_name> --help` - Show isolated tool documentation from static schema
   - `lucius --help` - Display help and usage information
   - `lucius --version` - Display version information

5. **Clean Error Output**:
   - No MCP server logs in CLI output
   - No Python tracebacks in CLI output
   - Only user-facing error messages with guidance displayed
   - Tool call errors provide guiding messages
   - Validation errors show meaningful hints

6. **Tool Help Isolation**: Every tool has isolated `--help` generated from MCP schema including description, parameters, types, formats, examples

7. **Output Format Support**: All commands support JSON (default), table, and plain output formats

8. **Lazy Initialization**:
   - CLI starts fast (~< 1s) for help/version/list commands
   - MCP client initialized only on `lucius call <tool>` invocation
   - Only called tool loaded (no eager imports)
   - `lucius list` uses build-time static info

**P1 (Should-Have):**

9. **Tab Completion**: Support shell completion for commands and tool names

10. **E2E Test Coverage**: Implement E2E tests covering all CLI commands and tool invocations

11. **Packaging Tests**: Add packaging tests for all 6 target platforms to verify binary functionality

12. **No HTTP Dependencies**: Verify HTTP server components (Starlette, uvicorn) not imported or bundled in compiled binary

13. **Error Handling**: Provide clear, helpful error messages with guiding hints for invalid arguments or API errors

14. **Use MCP Tools**: Verify CLI uses MCP tools directly, no reimplemented business logic

**P2 (Nice-to-Have):**

15. **Documentation**: Comprehensive CLI documentation including installation, usage, building, troubleshooting

16. **Docker Integration**: Support running the CLI in Docker containers for consistent environments

17. **CI/CD Pipeline**: Automated build and test pipeline for all platform binaries

### Story 9.5: Nuitka Onefile Caching for CLI Startup

As a Release Engineer,
I want onefile CLI binaries to use persistent extraction caching,
so that repeated command startup is fast without significantly increasing binary size.

**Acceptance Criteria:**

**Given** the current onefile build configuration and benchmark variants
**When** we compare startup time and artifact size
**Then** Variant 2 (`onefile` + persistent `onefile-tempdir-spec` + `onefile-cache-mode=cached`) is selected as default
**And** Variant 3 (`--onefile-no-compression`) is not selected as default due to large artifact growth.

**Given** all currently supported OS targets (Linux, macOS, Windows; arm64/x86_64)
**When** binaries run with onefile cache enabled
**Then** extraction cache uses native OS cache roots
**And** cache paths are version-scoped and stable
**And** cache from older binary version is not reused after version increase.

**Given** benchmark documentation and packaging tests
**When** maintainers validate startup behavior
**Then** first-run (cold) and subsequent-run (warm) behavior is reproducible
**And** warm-start performance improvement over current configuration is verified.

### Story 9.6: Tool-to-CLI Output Contract (Tools JSON Default, CLI Table/CSV Rendering)

As a Developer or QA Engineer,
I want CLI to ingest and display data returned by tools through a consistent output contract,
so that tool output is machine-friendly by default while CLI still supports human-friendly table/csv views.

**Acceptance Criteria:**

**Given** any tool returning a payload
**When** output format is not explicitly requested
**Then** tool output defaults to `json`
**And** tools support `plain|json` output modes only
**And** this default change is treated as a breaking change.

**Given** CLI execution (`lucius <entity> <action>`)
**When** output is rendered
**Then** CLI supports `plain|json|table|csv`
**And** `table` and `csv` are CLI-only renderers (not tool output modes).

**Given** CLI invokes mapped tools
**When** tools return `json` (default) or `plain`
**Then** CLI ingests tool output and renders requested format deterministically
**And** no traceback/internal logs are printed for normal format handling.

**Given** plain text payloads containing escaped newline sequences (`\n`)
**When** plain output is displayed
**Then** `\n` is rendered as a line break (not literal backslash+n).

**Given** Story 9.6 implementation
**When** integration tests run
**Then** tests verify AC behavior and tool->CLI data flow for:
**And** tool default `json`
**And** tool `plain`
**And** CLI rendering `plain|json|table|csv`
**And** newline normalization
**And** deterministic table/csv columns for multi-record results.

**Given** Story 9.6 implementation
**When** documentation is updated
**Then** `specs/prd.md` and `specs/architecture.md` document:
**And** tool output contract (`plain|json`, default `json`)
**And** CLI-only renderer contract (`table|csv`)
**And** end-to-end data flow from tools to CLI.

**Given** Story 9.6 introduces a breaking output-contract change
**When** implementation changes are committed
**Then** commit message follows Conventional Commits with breaking marker `!` (for example `feat(cli)!: ...`)
**And** commit body includes `BREAKING CHANGE:` details.

**Given** the full set of exposed tools/routes
**When** output is produced and consumed by CLI
**Then** every tool follows `plain|json` output contract with default `json`
**And** CLI returns tool `plain`/`json` outputs without content changes
**And** CLI applies output rendering transformations only for `table|csv`.

### Story 9.7: CLI Auth Command with Persistent Configuration

As a Developer or QA Engineer,
I want `lucius auth` to prompt for my Allure TestOps URL, API token, and default project,
so that subsequent CLI launches can reuse those credentials without requiring environment variables every time.

**Acceptance Criteria:**

**Given** I run `lucius auth`
**When** no non-interactive values are supplied
**Then** the CLI prompts for Allure TestOps base URL, API token, and project ID
**And** token input is masked and never echoed.

**Given** URL, token, and project ID are entered
**When** the command validates the credentials
**Then** it authenticates through the existing Allure client token exchange
**And** it verifies the configured project is accessible before saving.

**Given** validation succeeds
**When** credentials are saved
**Then** the config file is stored under the native user config directory using `platformdirs.user_config_path("lucius", appauthor=False, ensure_exists=True) / "auth.json"`
**And** Linux/Unix, macOS, and Windows resolve to their OS-specific user config roots.

**Given** a saved auth config exists
**When** I run a subsequent CLI command
**Then** the CLI uses saved URL, token, and project values when matching environment variables are absent
**And** explicit tool args and real environment variables retain precedence over saved config.

**Given** this story is implemented
**When** help, docs, and tests are updated
**Then** `lucius auth --help`, `lucius auth status`, CLI docs, setup docs, and cross-platform config tests cover the behavior
**And** shell completion generation includes `auth` and auth-specific subcommands/options for bash, zsh, fish, and PowerShell
**And** the raw token is never printed, logged, or shown in status output
**And** source-invoked CLI E2E tests run the command via `uv run lucius ...` rather than a built binary.

### Story 9.8: CLI List Command Tool Table

As a Developer or QA Engineer,
I want `lucius list` to display the same available-tools discovery table as running `lucius` without arguments,
so that I can explicitly list supported CLI capabilities without relying on an empty invocation.

**Acceptance Criteria:**

**Given** I run `lucius list`
**When** the CLI starts
**Then** it exits successfully
**And** it prints the same discovery table content as `lucius` with no arguments.

**Given** I run `lucius list --help`
**When** help is requested
**Then** the CLI describes `list` as a local discovery command
**And** it does not require `--args` or TestOps credentials.

**Given** the `list` command is used
**When** output is generated
**Then** it uses build-time static metadata from `src/cli/data/tool_schemas.json` and `src/cli/route_matrix.py`
**And** it does not import `src.tools`, `src.main`, FastMCP, Starlette, or any HTTP server components.

**Given** existing entity/action commands
**When** `lucius list` is added
**Then** `lucius call ...` remains rejected as legacy command style
**And** `list` is not added to the canonical TestOps route matrix as a fake entity or action.

**Given** shell completions are generated
**When** users request top-level command completion for `lucius`
**Then** `list` is offered alongside `help`, `version`, and entity tokens in bash, zsh, fish, and PowerShell completions
**And** completion scripts are regenerated from `deployment/scripts/generate_completions.py`.

**Given** automated tests run
**When** CLI tests execute
**Then** they verify `lucius list` success, content parity with no-argument output, `lucius list --help`, shell completion exposure, legacy `call` rejection, and no Python tracebacks/internal logs
**And** process-level CLI E2E coverage invokes `uv run lucius list ...` from source, not via a built binary.

### Story 9.9: CLI Pretty JSON Output Flag

As a Developer or QA Engineer,
I want an optional `--pretty` flag for commands that assume JSON output,
so that JSON responses are easy to read with line breaks and indentation while compact output remains the default.

**Acceptance Criteria:**

**Given** I run `lucius <entity> <action>` with `--pretty` and no explicit `--format`
**When** the command executes successfully
**Then** CLI still requests tool `output_format=json`
**And** CLI renders the JSON result in pretty (multi-line indented) form.

**Given** I run `lucius <entity> <action> --format json --pretty`
**When** output is produced
**Then** CLI renders pretty JSON deterministically
**And** no traceback/internal logs are shown.

**Given** I run commands without `--pretty`
**When** outputs are rendered
**Then** existing behavior remains unchanged for `json|plain|table|csv`.

**Given** I pass `--pretty` with `--format plain`, `--format table`, or `--format csv`
**When** argument validation runs
**Then** CLI returns a clear guided error indicating `--pretty` is valid only for JSON output.

**Given** help/docs/completions are updated for this feature
**When** users inspect CLI help and shell completion
**Then** action usage includes `--pretty`
**And** docs clarify JSON-only applicability
**And** generated bash/zsh/fish/PowerShell completion scripts include `--pretty` for action options
**And** source-invoked CLI E2E tests validate `--pretty` behavior via `uv run lucius ...`.

### Story 9.10: CLI Install Completions Command

As a Developer or QA Engineer,
I want `lucius install-completions` to detect my shell and install the matching completion script from the binary,
so that standalone CLI users can enable tab completion without locating repository files or manually copying generated scripts.

**Acceptance Criteria:**

**Given** I run `lucius install-completions`
**When** the shell can be detected from an explicit `--shell` option or the current process environment
**Then** the CLI installs the matching completion script for bash, zsh, fish, or PowerShell
**And** it reports the installed path and any shell-specific reload/source instruction.

**Given** I run `lucius install-completions --shell bash|zsh|fish|powershell`
**When** the command executes
**Then** the explicit shell value overrides auto-detection
**And** unsupported shell values fail with a clean `CLIError` and a hint listing supported shells.

**Given** the CLI is running as a Nuitka standalone or onefile binary
**When** `install-completions` installs scripts
**Then** the completion script content comes from code/data embedded in the binary
**And** the command does not read `deployment/shell-completions/*`, `deployment/scripts/generate_completions.py`, the source checkout, or network resources at runtime.

**Given** completion scripts are generated or installed
**When** users request top-level command completion for `lucius`
**Then** `install-completions` is offered alongside existing top-level commands and entity tokens in bash, zsh, fish, and PowerShell completions
**And** the command itself supports completion/help for `--shell`, `--path`, `--force`, `--print`, `--help`, and `-h`.

**Given** completion installation would overwrite an existing script or shell startup hook
**When** the target already exists
**Then** the command preserves existing files unless `--force` is supplied
**And** any startup-file edits are idempotent, marker-delimited, and never duplicate prior Lucius blocks.

**Given** automated tests run
**Then** they verify shell detection, explicit shell override, per-shell install paths, embedded-content behavior without repository completion files, completion exposure for `install-completions`, clean errors/no tracebacks, and docs coverage
**And** process-level CLI E2E coverage invokes `uv run lucius install-completions ...` from source, not via a built binary.

### Story 9.11: CLI Human-Readable Table Dates with Local Timezone Fallback

As a Developer or QA Engineer,
I want `lucius ... --format table` to render date/time values in a human-readable form using my local timezone when possible,
so that operational data is easier to read without manual timestamp conversion.

**Acceptance Criteria:**

**Given** CLI table rendering receives JSON payload values that represent datetimes (for example epoch seconds/milliseconds or ISO-8601 strings)
**When** output is rendered with `--format table`
**Then** datetime values are shown in a human-readable datetime format
**And** non-datetime values remain unchanged.

**Given** local timezone can be resolved from the runtime environment
**When** datetime values are rendered in table output
**Then** values are converted to local timezone consistently for the command output
**And** the rendered table explicitly states which timezone was used.

**Given** local timezone cannot be resolved or conversion fails
**When** table output includes datetime values
**Then** CLI falls back to UTC conversion
**And** the rendered output explicitly states timezone as `UTC`
**And** command execution still succeeds without traceback/internal logs.

**Given** other output modes are requested
**When** output is rendered as `json`, `plain`, or `csv`
**Then** existing output-contract behavior remains unchanged.

**Given** automated tests run
**When** formatter and CLI tests execute
**Then** they verify local-timezone rendering, UTC fallback, explicit timezone labeling, deterministic formatting, and unchanged behavior for non-table formats
**And** source-invoked CLI E2E tests validate table rendering behavior via `uv run lucius ...`.

### Story 9.12: CLI Short Entity Aliases

As a Developer or QA Engineer,
I want short aliases for common CLI entities such as `tc` for `test_case`,
so that frequent `lucius <entity> <action>` commands are faster to type while preserving the canonical entity/action model.

**Acceptance Criteria:**

**Given** the canonical CLI entity/action matrix
**When** short entity aliases are configured
**Then** each alias resolves to exactly one canonical entity
**And** aliases are defined in the existing route-matrix alias source, not in a parallel parser or duplicate route table.

**Given** I use a supported short entity alias such as `tc`
**When** I run entity discovery or an action command
**Then** the CLI behaves exactly as if I used the canonical entity name
**And** examples such as `lucius tc`, `lucius tc list --help`, and `lucius tc list --args '{}'` resolve to `test_case`.

**Given** short aliases are exposed to users
**When** I run root help, entity help, or shell completion generation
**Then** short aliases are discoverable alongside existing canonical, plural, and dash-form aliases
**And** generated bash, zsh, fish, and PowerShell completions include the short aliases.

**Given** alias input contains uppercase letters, leading/trailing spaces, or dash/underscore variants where applicable
**When** the CLI normalizes the token
**Then** aliases resolve consistently using the existing `normalize_token()` behavior
**And** invalid or ambiguous aliases produce clean guided errors without Python tracebacks.

**Given** automated tests run
**When** CLI alias and completion tests execute
**Then** they verify short alias resolution, no canonical route duplication, root-help visibility, completion exposure, and unchanged behavior for existing canonical/plural/dash aliases
**And** process-level CLI E2E coverage exercises representative short aliases via `uv run lucius ...`.

### Story 9.13: CLI Comprehensive E2E Coverage via uv run lucius

As a Developer or QA Engineer,
I want comprehensive CLI command E2E coverage executed from source with `uv run lucius`,
so that CLI behavior is verified end-to-end without depending on built binaries and regressions in local commands or high-priority entity flows are caught early.

**Acceptance Criteria:**

**Given** the CLI E2E suite is executed
**When** command processes are launched
**Then** commands are invoked from source via `uv run lucius ...`
**And** the suite does not require building a Nuitka or wheel binary to validate CLI behavior.

**Given** CLI commands that do not call a TestOps tool directly
**When** process-level E2E tests run
**Then** coverage includes `lucius`, `lucius --help`, `lucius --version`, `lucius <entity>`, `lucius <entity> <action> --help`, and each CLI-local command introduced in Epic 9 such as `list`, `auth`, `auth status`, and `install-completions`
**And** those tests verify clean exit codes, no tracebacks/internal logs, and expected discovery/help text.

**Given** high-priority `test_case` command flows
**When** source-invoked CLI E2E tests run
**Then** they cover representative discovery, help, and execution paths for `test_case`
**And** they verify default JSON routing plus CLI rendering for `plain`, `table`, and `csv`
**And** they continue to validate escaped-newline handling in plain output.

**Given** high-priority `launch` command flows
**When** source-invoked CLI E2E tests run
**Then** they cover representative discovery, help, and execution paths for `launch`
**And** they validate at least one list/read flow and at least one state-transition flow relevant to launch lifecycle behavior.

**Given** high-priority custom-field flows
**When** source-invoked CLI E2E tests run
**Then** they cover representative discovery, help, and execution paths for `custom_field` and `custom_field_value`
**And** they validate behavior for both entity-level operations and value-level CRUD-style flows.

**Given** staged CLI features such as pretty JSON, local-timezone table rendering, and short aliases
**When** those features are implemented
**Then** the source-invoked E2E suite contains representative process tests for them
**And** aliases such as `tc`, `ln`, `cf`, or `cfv` are covered where the corresponding story makes them available.

**Given** future CLI-local commands or CLI-only rendering behaviors are added
**When** a story is prepared for development
**Then** its acceptance criteria explicitly require extending the shared `uv run lucius` CLI E2E suite
**And** story tasks identify the concrete test file(s) to update.


## Epic 10: Quality of Life and API Coverage

Goal: Improve day-to-day agent usability and close API coverage gaps without changing the service-first architecture or existing output contracts.

### Story 10.1: Include TestOps Entity URLs in Tool Responses

As an AI Agent,
I want tool responses that mention TestOps entity IDs to also include browser URLs for those entities,
so that I can navigate users directly to the relevant TestOps objects without manually reconstructing links.

**Acceptance Criteria:**

**Given** a tool response includes a stable TestOps entity ID
**When** the tool returns either `plain` or `json`
**Then** it includes the existing ID field unchanged
**And** it includes a corresponding `url` field or plain-text `URL:` line for that same entity
**And** existing output-format support remains limited to `plain|json`.

**Given** a tool uses an optional `project_id` override or runtime auth project context
**When** a URL is generated
**Then** the URL uses the resolved `AllureClient.get_base_url()` and `AllureClient.get_project()` values
**And** it does not use `settings.ALLURE_PROJECT_ID` directly after a client context has been resolved.

**Given** a response contains multiple entity references, such as a defect linked to a test case
**When** the JSON payload is rendered
**Then** every referenced entity with a known stable browser URL includes a type-specific URL field
**And** field names are unambiguous, for example `defect_url`, `test_case_url`, `launch_url`, or nested item `url`.

**Given** entity list tools return paginated or collection payloads
**When** each item contains an entity ID
**Then** each item includes its own `url`
**And** the plain output includes URLs without breaking the existing ID/name/status lines that tests and agents already parse.

**Given** an entity type does not have a verified stable browser URL pattern
**When** implementation reaches that type
**Then** the developer must either verify the URL against a sandbox TestOps instance and add tests
**Or** omit the URL for that entity and document why it is intentionally unsupported
**And** the implementation must not invent unverified links for settings-only or non-navigable API records.

**Given** automated tests run
**When** unit, integration, and selected e2e tests execute
**Then** they verify URL generation for test cases, launches, defects, test plans, and shared steps
**And** they verify output remains backward compatible for existing ID parsing and CLI formatting.
