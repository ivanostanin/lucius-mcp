# Lucius MCP

Lucius is a specialized Model Context Protocol (MCP) server designed to bridge the gap between AI agents and Allure
TestOps.

## 🎯 Motivation

### Why we built Lucius

Managing tests manually through a complex API is frustrating for both humans and AI. Most REST APIs are built for
code-to-code communication, not for the conversational style of AI agents. When an agent hits an error, it often lacks
the context to recover without human help.

### How Lucius helps

Lucius acts as a translator between your AI assistant and Allure TestOps.

- **Tools that make sense**: Instead of navigating thousands of raw API endpoints, your AI gets a small set of
  high-level tools focused on getting things done.
- **Agent Hints**: This is our most important feature. When a tool fails (like if you forget a Project ID), Lucius
  returns a clear, text-based hint. This tells the AI exactly what happened and gives it a specific suggestion for how
  to fix the request.
- **Built for Developers**: We use a "Thin Tool" pattern to keep the logic in one place. This makes it easy for
  developers to add new features or test old ones without worrying about the underlying protocol.

## 🚀 Key Concepts

- **Agent Hints**: Instead of raw stack traces, Lucius returns human-readable (and agent-readable) suggestions when
  things go wrong.
- **Thin Tool / Fat Service**: Tool definitions are kept minimal, delegating all business logic to reusable services.
- **Spec-Fidelity**: The API client is generated directly from (filtered) Allure TestOps OpenAPI specs, ensuring
  correctness.

## 📂 Documentation Sections

- [Architecture & Design](architecture.md): Learn about the core patterns and philosophies.
- [Tool Reference](tools.md): Complete guide to all available MCP tools.
- [Configuration & Setup](setup.md): How to install and configure Lucius for your environment.
- [Development Guide](development.md): Instructions for contributors and developers.
- [AI Agent Documentation Protocol](agent-documentation-protocol.md): How AI agents should maintain this documentation.
