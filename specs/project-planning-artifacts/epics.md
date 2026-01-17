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
