# Changelog Update Protocol for AI Agents

To maintain a clear and consistent history of the project, AI agents must update the `CHANGELOG.md` file whenever a task or story is completed.

## 📝 Format: Added-Changed-Fixed

We follow a structured format for each version entry. Use the following categories:

- **### Added**: For new features, tools, or capabilities.
- **### Changed**: For changes in existing functionality, refactors, or documentation updates.
- **### Fixed**: For any bug fixes or error corrections.

## 🔄 How to Update

1. **Summarize Changes**: Gather all changes made since the last version tag (`vX.Y.Z`).
2. **Identify Category**: Group each change into `Added`, `Changed`, or `Fixed`.
3. **Write Entries**:
    - Use clear, professional, and human-readable language (avoid excessive jargon).
    - Use bullet points.
    - Reference Stories or Issues if applicable (e.g., `(Story 9.1)`).
4. **Update Version**:
    - If you are preparing a new release, add a new version header: `## [vX.Y.Z] - YYYY-MM-DD`.
    - If you are updating an "Unreleased" or current working version, add your entries to the top section.

## 💡 Examples

```markdown
### Added
- New `get_launch` tool to retrieve detailed execution statistics.
- Automated link verification test for documentation.

### Changed
- Refactored root `README.md` to be more human-centric and concise.
- Updated `docs/setup.md` with Claude Code installation instructions.

### Fixed
- Broken relative links in `docs/tools.md`.
- Incorrect environment variable mapping in `deployment/mcpb/manifest.uv.json`.
```

## ⚠️ Important Rules
- **Do not** add generic messages like "Updated files".
- **Do not** repeat the same information across categories.
- **Always** keep the newest version at the top.
