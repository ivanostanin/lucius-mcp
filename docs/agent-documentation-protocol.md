# AI Agent Documentation Protocol

To ensure the documentation stays in sync with the evolving codebase, AI agents should follow this protocol when
implementing new features or modifying existing tools.

## 🔄 Documentation Update Scenario

When you are tasked with adding a new MCP tool or a new feature to Lucius:

### 1. Discovery

- Review `docs/tools.md` to see where the new tool fits into the taxonomy.
- Review `docs/architecture.md` to ensure your implementation aligns with core patterns.

### 2. Implementation

- Implement the service and the thin tool as per the [Development Guide](development.md).

### 3. Documentation Update (MANDATORY)

- **Tool Reference**: Add the new tool to the appropriate table in `docs/tools.md`. Include a brief description and key
  parameters.
- **Root README**: If the tool is a major feature, check if the "Supported Tools" table in the root `README.md` needs an
  update.
- **Architecture**: If you introduced a new pattern or utility, update `docs/architecture.md`.
- **Changelog**: Update `CHANGELOG.md` following the [Changelog Update Protocol](../scripts/update-changelog.md).

### 4. Verification

- Verify that all internal links in the `docs/` folder are still valid.
- Ensure the descriptions are clear and follow the "Agent Hint" philosophy.

## 📝 Writing Style

- **AI-Focused**: Write descriptions that help an agent understand *when* and *how* to use a tool.
- **Concise**: Keep tables and summaries brief. Link to detailed implementation artifacts if necessary.
- **Markdown-First**: Use standard GitHub Flavored Markdown.
