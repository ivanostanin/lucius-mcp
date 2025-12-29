---
stepsCompleted: [1, 2, 3, 4, 5]
inputDocuments: 
  - 'lucius-mcp/brief.md'
workflowType: 'product-brief'
lastStep: 5
project_name: 'lucius-mcp'
user_name: 'Ivan Ostanin'
date: '2025-12-25'
author: 'Ivan Ostanin'
---

# Product Brief: lucius-mcp

<!-- Content will be appended sequentially through collaborative workflow steps -->

## Executive Summary

The Allure TestOps MCP Server is a specialized Model Context Protocol (MCP) server designed to bridge Large Language Models (LLMs) with the Allure TestOps platform. It enables AI agents to seamlessly manage test cases, launches, and defects through a type-safe, documented, and reliable interface. By exposing TestOps capabilities—starting with Test Case CRUD operations—directly to agents, it facilitates autonomous test management and quality assurance workflows.

---

## Core Vision

### Problem Statement

Integrating AI agents with robust test management tools like Allure TestOps is currently hindered by the lack of a standardized, machine-consumable interface. LLMs struggle to correctly invoke complex APIs without clear documentation, typing, and safety rails, leading to hallucinations or invalid operations when attempting to manage test artifacts.

### Problem Impact

This disconnect limits the potential of AI in QA automation, preventing agents from autonomously creating test cases, updating results, or analyzing defects. Teams cannot fully leverage AI for maintaining their Allure TestOps repository efficiently.

### Why Existing Solutions Fall Short

Direct API usage often creates friction for agents, requiring them to "guess" complex endpoints or payloads. Generic API wrappers may lack the specific metadata, rich typing, and "LLM-friendly" documentation required for reliable, autonomous agentic performance.

### Proposed Solution

A robust MCP server built with Python, `uv`, and `starlette`, featuring Pydantic models generated directly from the Allure TestOps OpenAPI 3.1 spec. It provides a clean, typed toolset for Agents to perform CRUD on test cases (including steps, tags, attachments), manage associated metadata, and eventually handle launches and defects, all via standard IO communication.

### Key Differentiators

*   **LLM-First Design**: All functions and prompts are thoroughly documented specifically to be understandable by LLMs.
*   **Spec-Driven Reliability**: Python code for accessing the API is generated from the OpenAPI spec, ensuring accuracy and type safety.
*   **High Assurance**: >85% test coverage, fully typed codebase, and CI/CD integration.
*   **Seamless Integration**: supports `stdio` and `streamable http` (future), with traverse-able auth parameters (token, project ID).

## Target Users

### Primary Users

#### 1. The Autonomous QA Agent (Digital User)
*   **Role:** AI/LLM operating as a testing assistant.
*   **Context:** Running in a standardized MCP environment (e.g., Claude Desktop, custom agent runtime).
*   **Needs:**
    *   Unambiguous, typed tool definitions.
    *   Structured error handling (no "guessing" why a request failed).
    *   Context-rich prompts to understand TestOps entities.
    *   Fast IO (`stdio`) for latency-sensitive interactions.
*   **Goal:** To autonomously maintain the test repository without human intervention.

#### 2. The SDET / Automation Engineer (Human User)
*   **Role:** Technical Owner of the TestOps infrastructure.
*   **Context:** Maintaining a large suite of tests; overwhelmed by manual test case updates and "flaky" test categorization.
*   **Pain Point:** Spending too much time manually syncing code changes to TestOps case descriptions/steps.
*   **Success Vision:** "I just tell my agent to 'update the login tests based on the new PR', and it's done correctly in Allure."

#### 3. The Manual QA Engineer (Human User)
*   **Role:** Quality Assurance Specialist focused on functional/exploratory testing.
*   **Context:** Often tasked with documenting hundreds of test cases which is time-consuming and repetitive.
*   **Pain Point:** "I have to write out the same 'Login to application' steps 50 times. It takes forever to get test cases into the system."
*   **Needs:** Bulk creation of test cases from brief descriptions; using AI to expand one-liners into full test steps in Allure.
*   **Success Vision:** They write a high-level list of scenarios, and the Agent (via `lucius-mcp`) populates Allure with detailed, formatted test cases instantly.

### Secondary Users

#### 1. DevOps / Platform Engineer
*   **Role:** Infrastructure maintainer.
*   **Needs:** Easy deployment (Docker, Helm), security (API Key/OAuth traversal), reliability (health checks, logging).
*   **Interaction:** Sets up the MCP server initially, ensures connectivity to Allure TestOps instance.

### User Journey

1.  **Setup (SDET):** The engineer installs `lucius-mcp` via `uv` or Docker, providing the Allure URL and Token.
2.  **Connection (SDET):** Configures their AI client (e.g., Claude Desktop or a custom Python agent) to use the MCP server.
3.  **Instruction (SDET -> Agent):** "Check the new payment flow code and create corresponding test cases in Allure from the spec."
4.  **Creation (Manual QA -> Agent):** "Here is a list of 20 edge cases for the Search feature. Add them to Allure."
5.  **Execution (Agent):**
    *   Agent calls `list_test_cases` to see what exists.
    *   Agent interprets the new code or list of scenarios.
    *   Agent calls `create_test_case` with rich steps and metadata.
    *   Server validates against Pydantic models and executes against Allure API.
6.  **Validation (Agent -> SDET/Manual QA):** Agent reports: "Created test cases with IDs [list] and updated existing ones."
7.  **Value Realization:** The test repository is populated and up-to-date with minimal manual effort.

## Success Metrics

### Business Objectives

*   **Automation Adoption:** Increase the percentage of test cases managed by AI agents vs. manual entry.
*   **Reduced Maintenance Time:** Drastically cut down the hours SDETs spend syncing code changes to Allure documentation.
*   **Quality Assurance Velocity:** Faster test creation cycles leading to quicker PR checks and release confidence.

### Key Performance Indicators

*   **Test Case Creation Velocity:** Average time to create a fully documented test case (Target: < 10 seconds via Agent vs. minutes manually).
*   **Agent Success Rate:** % of Agent attempts to create/update test cases that succeed without validation errors (Target: > 95%).
*   **Manual Effort Reduction:** Estimate of hours saved per sprint on test documentation.
*   **API Coverage:** % of Allure TestOps API endpoints successfully mapped and usable by the MCP server (Target: 100% of P0/P1 requirements).

## MVP Scope

### Core Features (v1.0 - P0)

*   **Test Case CRUD:** Create, Read, Update, Delete test cases with all metadata (Name, Description, Precondition, Steps, Checks, Tags, Attachments, Custom Fields).
*   **Shared Steps CRUD:** Create, update, and manage reusable Shared Steps to prevent duplication.
*   **Basic Test Search & List:** Filter by Project ID and Name to find existing cases for updates.
*   **Spec-Generated Client:** Python code for API access generated directly from Allure TestOps OpenAPI 3.1 spec.
*   **Agent-Friendly Interface:** `stdio` transport, traversable auth, and thorough inline documentation.
*   **Quality Gates:** >85% test coverage, full typing, end-to-end tests, CI/CD in GitHub.

### Out of Scope for MVP (P1/P2 deferred)

*   **P1 Deferred:** Launches CRUD (Execution reporting), Docker/Helm packaging (User setup manual for now), CI/CD in GitHub.
*   **P2 Deferred:** Test Plans, Defects, Advanced Search (RQL), TLS termination, OAuth flows, Skills.

### MVP Success Criteria

1.  **Functionality:** An Agent can create and update test cases (including Shared Steps) and find them via IDs or basic filtering.
2.  **Reliability:** The server handles invalid inputs gracefully.
3.  **Performance:** >85% code coverage.

### Future Vision

*   **Phase 2 (P1):** Enable Agents to execute tests and report results (Launches).
*   **Phase 3 (P2):** Full QA Automation lifecycle including Defect management and complex Test Plans.
