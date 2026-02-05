---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
inputDocuments:
  - 'lucius-mcp/specs/analysis/product-brief-lucius-mcp-2025-12-25.md'
  - 'lucius-mcp/brief.md'
documentCounts:
  briefs: 2
  research: 0
  brainstorming: 0
  projectDocs: 0
workflowType: 'prd'
lastStep: 11
project_name: 'lucius-mcp'
user_name: 'Ivan Ostanin'
date: '2025-12-26'
---

# Product Requirements Document - lucius-mcp

**Author:** Ivan Ostanin
**Date:** 2025-12-26

## Executive Summary

The Allure TestOps MCP Server (`lucius-mcp`) is a specialized Model Context Protocol (MCP) server designed to bridge Large Language Models (LLMs) with the Allure TestOps platform. It enables AI agents to seamlessly manage test cases, launches, and defects through a type-safe, documented, and reliable interface. By exposing TestOps capabilities directly to agents, it facilitates autonomous test management and quality assurance workflows.

### What Makes This Special

Unlike generic API wrappers, **lucius-mcp** is built with an **LLM-First Design**, ensuring all tools and prompts are thoroughly documented for machine understanding. It leverages **Spec-Driven Reliability** by generating the Python client directly from the OpenAPI 3.1 spec, which is then structured into a **categorized Model Facade** to simplify entity discovery for agents. With a focus on **High Assurance** (>85% test coverage), it eliminates the guesswork for agents, preventing hallucinations and ensuring reliable test repository maintenance.

## Project Classification

**Technical Type:** api_backend (MCP Server)
**Domain:** Software Quality Assurance
**Complexity:** Medium (High Reliability Requirements)
**Project Context:** Greenfield - new project

## Success Criteria

### User Success

*   **Autonomous Agent:** Can successfully utilize tools to map user intent to valid TestOps entities without hallucinating parameters, achieving a >95% success rate on first attempt.
*   **SDET:** Shifts from "data entry" to "reviewer," reducing time spent syncing code-to-docs by significant margins (aiming for near-instant updates via agents).
*   **Manual QA:** Achieves both **speed** (creating bulk test cases from scenarios instantly) and **consistency** (all cases follow the same high-quality format and structure) by leveraging the agent interface.

### Business Success

*   **Automation Adoption:** Increased percentage of test repository managed by AI agents vs. manual input.
*   **Maintenance Efficiency:** Reduction in "test debt"—test documentation stays in sync with code releases automatically.
*   **Quality Velocity:** Faster turnaround from "feature spec" to "documented test cases ready for execution."

### Technical Success

*   **Reliability:** The server handles invalid inputs gracefully with descriptive errors, preventing agent loops.
*   **Code Quality:** Maintained >85% test coverage and strict type-safety (Pydantic models generated from OpenAPI).
*   **Maintainability:** Client code regeneration pipeline is robust, using an internal `models/_generated.py` backed by a human-and-agent-friendly `models/` facade.
*   **Testability:** All functions are thoroughly documented to be understandable by llms. End-to-end tests are implemented involving verification of tool execution results in sandbox TestOps instance or project.

### Measurable Outcomes

*   **Test Creation:** < 10s per test case via agent.
*   **Agent Reliability:** > 95% tool execution success rate.
*   **API Coverage:** 100% coverage of MVP requirements (Test Case + Shared Steps).

## Product Scope

### MVP - Minimum Viable Product

*   **Core Resources:** CRUD operations for Test Cases (Name, Description, Precondition, Steps, Checks, Tags, Custom Fields, Attachments).
*   **Shared Steps:** Full CRUD support for Shared Steps and ability to use them within Test Cases (critical for maintainability).
*   **Retrieval:** Basic lookup of existing test cases to enable updates.
*   **Foundation:** Python client generated from OpenAPI 3.1 spec.
*   **Interface:** MCP over `stdio` (and potentially `streamable http`), with traversable Auth config.
*   **Documentation:** Comprehensive inline tool documentation optimized for LLMs.

### Growth Features (Post-MVP)

*   **Discovery:** Rich Test Search and Hierarchy navigation.
*   **Execution:** Launches CRUD.
*   **Ops:** Docker containerization, Helm charts, and GitHub CI/CD workflows.

### Vision (Future)

*   **Full Lifecycle:** Test Plans and Defects CRUD.
*   **Enterprise Security:** TLS termination, OAuth flows, and granular API Key management.
*   **Advanced Capabilities:** Agent Skills and complex reasoning workflows.

## User Journeys

### Journey 1: Unit 734 - The First Autonomous "Shift-Left"
Unit 734 is an autonomous coding agent assigned to refactor a legacy payment module. In the past, it would write code but struggle to document the test changes in the external TestOps system, leading to drift. Today, it has access to `lucius-mcp`.

After generating the Python refactor, 734 decides to update the test repository. It calls `list_test_cases` to find the existing "Payment Validation" test. It reads the current steps, realizes they are outdated, and calls `update_test_case` with the new logic. It encounters a need for a reusable step "Authorize Payment", checks for its existence via `list_shared_steps`, finds it, and links it by ID. Finally, it creates a new negative test case for "Expired Card" using `create_test_case`. 

The operation succeeds on the first try because the tool definitions provided strict typing for the `TestCase` schema. Unit 734 marks the task complete, having modified the codebase AND the test documentation simultaneously without human help.

### Journey 2: Sarah - From Data Entry to Architect
Sarah, a Senior SDET, is dreading the "Documentation Sprint." Her team has released 5 new features, and Allure TestOps is completely behind. Usually, she spends 3 days copying Gherkin scenarios into the UI.

This time, she opens her agent workspace and types: "Read the `features/` directory and sync all scenarios to Allure TestOps." She watches as the agent uses `lucius-mcp` to iterate through the files. She sees a stream of "Created Test Case [ID]" logs. 

Ten minutes later, she logs into Allure TestOps. 50 new test cases are there, perfectly tagged with "Automated" and linked to the correct Jira tickets. Instead of typing for 3 days, she spends 30 minutes reviewing the agent's work, spots one minor tag issue, tells the agent to fix it (which it does via `update_test_case`), and closes her laptop early.

### Journey 3: Mike - The Consistency Breakthrough
Mike, a Manual QA Lead, manages a team of juniors who document bugs and tests. The problem is consistency—everyone writes steps differently. Searching for "Login" yields 5 different variations.

Mike decides to use the agent as a gatekeeper. He writes a sloppy bulleted list of 20 edge cases for the new Search UI and pastes it into his agent: "Standardize these and add them to Allure."

The agent uses `lucius-mcp` to create the cases. It automatically applies the team's standard tagging convention (`Component: Search`, `Type: Manual`) and formats every step as "Action -> Expected Result" because the MCP server's JSON schema enforces that structure. Mike checks Allure and sees 20 beautifully uniform test cases. He realizes he can scale his team's output without sacrificing quality.

### Journey 4: David - The One-Shot Integration
David is building a custom "DevOps Assistant" agent for his company. He needs it to be able to talk to their testing infrastructure. He discovers `lucius-mcp`.

He's worried about the complexity of the Allure API. He installs `lucius-mcp` via `uv` and points his agent at it. He opens the MCP Inspector to test it. He runs `list_tools` and sees comprehensive documentation for every parameter—not just `project_id (string)`, but `project_id (string): The unique ID of the project, found in the URL after /project/`.

He tries to make his agent create a test case with a missing required field. The server responds not with a 500 error, but with a clear validation message: "Field 'steps' is required." David's agent catches this error and self-corrects. Within an hour, David has a working integration, purely because the "Developer Experience" of the MCP server (docs + error handling) was treated as a first-class feature.

### Journey Requirements Summary

*   **Agent (Unit 734):** Strict JSON schemas, Type-safe CRUD, Shared Step lookup/linking.
*   **SDET (Sarah):** Bulk operation stability, Idempotency (don't create duplicates), Tagging support.
*   **Manual QA (Mike):** Enforced step structure, Standardized metadata fields.
*   **Developer (David):** Rich inline tool documentation (`docstrings`), Descriptive validation errors, Easy installation/setup.

## Innovation & Novel Patterns

### Detected Innovation Areas

*   **LLM-First Architecture:** Unlike traditional tools where documentation is for humans, `lucius-mcp` treats tool descriptions and docstrings as *runtime features*. The exhaustive documentation of every parameter is designed specifically to optimize the context window for Agents, maximizing their ability to reason about TestOps entities without hallucination.
*   **Autonomous TestOps:** Enabling a "Shift-Left" workflow where the *agent* is responsible for maintaining the test repository (CRUD + Linking) alongside the code, effectively automating the role of a "Test Librarian."
*   **Spec-Driven Agent Compliance:** Using `uv` and Pydantic to strictly enforce OpenAPI schemas ensures that agents cannot submit malformed data, bridging the gap between "stochastic" LLM output and "deterministic" TestOps APIs.

### Market Context & Competitive Landscape

*   **Current State:** Most TestOps integrations are CI/CD plugins (Jenkins, GitHub Actions) or manual UIs. API interaction is typically done via generic `requests` wrappers or Postman collections, which are hard for agents to navigate.
*   **Differentiation:** `lucius-mcp` is the first dedicated *Agent Interface* for Allure, positioning it as an infrastructure component for the AI-Native SDLC.

### Validation Approach

*   **Agent Zero-Shot Success Rate:** Measuring how often an un-tuned agent interacts correctly with the server purely based on tool definitions (Target: >90%).
*   **Self-Correction Velocity:** Mean number of turns required for an agent to fix a validation error based on server feedback (Target: < 1.5 turns).
*   **SDET Trust Score:** Percentage of agent-generated test cases accepted by human reviewers without modification (Change Acceptance Rate).
*   **Hallucination Rate:** Frequency of attempts to use non-existent API parameters or fields.

### Risk Mitigation

*   **Context Window Limits:** Exhaustive documentation consumes token limits. *Fallback:* Implement "fast" mode with simplified signatures for smaller models.
*   **API Drift:** If Allure TestOps API changes, the static client breaks. *Fallback:* Automated nightly build pipeline that regenerates the Pydantic client from the latest upstream OpenAPI spec.

## MCP Server (api_backend) Specific Requirements

### Project-Type Overview

`lucius-mcp` is a stateless Model Context Protocol (MCP) server exposing Allure TestOps functionality as typed tools. It acts as a translation layer between the infinite flexibility of an LLM and the rigid schema of the Allure API.

### Technical Architecture Considerations

*   **Statelessness:** The server must not maintain internal state between tool calls, relying entirely on the Allure TestOps API as the source of truth.
*   **Connection Resilience:** Must handle intermittent connectivity to the Allure instance gracefully.

### Endpoint Specification (Tools)

*   **Test Case Resources:**
    *   `create_test_case`: Create new case with steps, tags, attachments.
    *   `read_test_case`: Retrieve full details by ID.
    *   `update_test_case`: Modify existing fields (idempotent).
    *   `delete_test_case`: Soft/Hard delete support.
    *   `list_test_cases`: Search/Filter capabilities.
*   **Shared Step Resources:**
    *   `create_shared_step`: Define reusable steps.
    *   `read_shared_step`: Inspect shared logic.
    *   `update_shared_step`: Maintain shared library.
    *   `delete_shared_step`: Remove obsolete steps.
    *   `list_shared_steps`: Discovery for reuse.

### Authentication Model

*   **Token Exchange:** API tokens (`ALLURE_TOKEN`) are exchanged for JWT Bearer tokens via the `/api/uaa/oauth/token` endpoint at client initialization.
*   **Automatic Renewal:** JWT tokens (default TTL: 1 hour) are automatically refreshed 60 seconds before expiry to ensure uninterrupted operation.
*   **Primary:** Environment Variables (`ALLURE_ENDPOINT`, `ALLURE_TOKEN`) for zero-config startup.
*   **Traversable:** Optional `project_id` arguments in every tool to allow agents to switch contexts dynamically if authorized.

### Data Schemas & Formatting

*   **Input/Output:** Strict JSON following the MCP specification.
*   **Pydantic Models:** All schemas are auto-generated from the Allure TestOps OpenAPI 3.1 spec ensuring 1:1 fidelity.
*   **Attachments:** Handled via Base64 strings or external URL references (depending on Allure API limits).

### Error Handling & Rate Limits

*   **Agent-Optimized Errors:** 4xx errors must return descriptive messages *and* remediation hints (e.g., "Error: 'steps' missing. Hint: Use 'create_test_case' with a list of step objects").
*   **Rate Limiting:** Passthrough from Allure TestOps API headers.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

*   **MVP Approach:** **Platform MVP** - Focus on establishing a reliable, type-safe "bridge" for Test Authoring (Cases + Shared Steps).
*   **Resource Requirements:** 1 Senior Engineer (Python/MCP), 1 QA/Product Owner.

### MVP Feature Set (Phase 1 / P0)

**Core User Journeys Supported:**
*   **Journey 1 (Unit 734):** Refactoring code and updating tests.
*   **Journey 3 (Manual QA):** Bulk creation of standardized manual tests.

**Must-Have Capabilities:**
*   **Test Case CRUD:** Complete management (Steps, Checks, Tags, Attachments, Custom Fields).
*   **Shared Steps CRUD:** Full support for reusable steps (Essential for avoiding duplication).
*   **Core Architecture:** Python/Starlette server, Pydantic models from OpenAPI, Stdio transport.
*   **Auth:** Env Vars + Optional Runtime Traversal.
*   **End-to-End Tests:** Implemented involving verification of tool execution results in sandbox TestOps instance or project.

### Post-MVP Features

**Phase 2: Roll-out (Operations & DevOps - P1)**
*   **Execution Management:** Launches CRUD (Create/Close launches).
*   **Organization:** Test Hierarchy (Suites/Trees) and Test Search.
*   **Distribution:** Docker Images and Helm Charts.
*   **CI/CD:** GitHub Actions integration.

**Phase 3: Feature-proofing (Governance & Intelligence - P2)**
*   **Planning:** Test Plans CRUD.
*   **Defects:** Defect lifecycle management.
*   **Advanced Security:** TLS Termination, OAuth/API Key management.
*   **Agent Skills (Advanced Workflows):**
    *   **Automation:** End-to-end flow: `Get Jira AC` + `Get GitHub PR Code` + `Get App UI Graph` -> `Generate Allure Test Cases`.
    *   **Skills:** "Claude Code" skills for autonomously maintaining the test repository based on external triggers.

### Risk Mitigation Strategy

*   **Technical Risk (Schema Complexity):** Allure's model is complex. *Mitigation:* Focus MVP *only* on the "Test Case" entity and its direct dependencies (Steps), ignoring execution/results initially.
*   **Market Risk (Agent Adoption):** Agents might struggle with the API. *Mitigation:* The "Validation Approach" (Zero-shot metrics) defined in Step 6 is our primary de-risking tool.

## Functional Requirements

### Test Case Management

*   **FR1:** Agents can create new Test Cases with mandatory fields (Name) and optional metadata (Description, Preconditions).
*   **FR2:** Agents can define linear Test Steps (Action + Expected Result) to a Test Case.
*   **FR3:** Agents can attach shared/reusable steps to a Test Case by reference ID.
*   **FR4:** Agents can apply Tags, Custom Fields (e.g., Layer, Component), and Automation Status to Test Cases.
*   **FR5:** Agents can soft-delete Test Cases to archive them.
*   **FR6:** Agents can update existing Test Cases idempotently (partial updates supported).

### Shared Step Library

*   **FR7:** Agents can create reusable Shared Steps with a set of child steps.
*   **FR8:** Agents can modify existing Shared Steps, propagating changes to all linked Test Cases.
*   **FR9:** Agents can list available Shared Steps to discover reusable logic.

### Search & Discovery

*   **FR10:** Agents can list Test Cases filtered by Project ID.
*   **FR11:** Agents can retrieve the full details of a specific Test Case by its Allure ID.
*   **FR12:** Agents can search for Test Cases by Name or Tag (basic filtering).

### Security & Context

*   **FR13:** Agents can authenticate operations using Environment Variables by default.
*   **FR14:** Agents can override authentication context (Project ID) via tool arguments at runtime.
*   **FR15:** The system validates all inputs against strict schemas before sending to upstream API.
*   **FR16:** The system provides descriptive error hints when validation fails (e.g., "Missing field X").

## Non-Functional Requirements

### Performance (Latency & Throughput)
*   **NFR1:** Tool execution overhead (deserialization -> API call -> serialization) must be < 50ms.
*   **NFR2:** Server startup time must be < 2 seconds.

### Reliability & Robustness
*   **NFR3:** **Agent-Proofing:** The server must NEVER crash on invalid input; always return structured error hints.
*   **NFR4:** Schema fidelity must be 100% compliant with Allure Open API 3.1.

### Security
*   **NFR5:** API Tokens passed via environment variables must be masked in all logs.
*   **NFR6:** Input content is sanitized to prevent injection attacks.

### Quality & Maintainability
*   **NFR7:** Unit Test coverage > 85%.
*   **NFR8:** 100% `mypy` strict type checking compliance.
*   **NFR9:** Code style and strict linting enforced via `ruff`.
*   **NFR10:** LLM-optimized docstrings for all Tools.
*   **NFR11:** End-to-End Tests: Implemented involving verification of tool execution results in sandbox TestOps instance or project.

### Observability & Metrics
*   **NFR12:** **Structured Logging:** All events must be logged in structured JSON format (level, timestamp, logger, message, context).
*   **NFR13:** **Traffic Inspection:** Logs must capture Tool Input arguments and (truncated) Output results for debugging.
*   **NFR14:** **Correlation:** Every tool call should generate a Request ID.
*   **NFR15:** **Operational Metrics:** The server must expose metrics (via logs or generic endpoint) measuring:
    *   `mcp_tool_usage_count` (labeled by tool name)
    *   `mcp_tool_error_count` (labeled by error type)
    *   `mcp_tool_latency_ms` (histogram)
