# AI Agent Protocol: Release Preparation

This protocol outlines the mandatory steps an AI agent must take when preparing a new release for Lucius MCP.

## 🏁 Prerequisite: Quality Assurance

Before initiating any release steps, run the full validation suite. A release MUST NOT proceed if any of these checks fail.

```bash
./scripts/full-test-suite.sh
```

## 🚀 Release Steps

### 0. Prepare Environment
- Checkout the `main` branch.
- Create a release branch from `main` with name `release/v0.x.x`.

### 1. Version Bump
- Update the `version` field in `pyproject.toml`.
- Follow Semantic Versioning (SemVer) principles.

### 2. Dependency Sync
- Update project lockfiles and synchronized environments.
```bash
uv sync --all-extras
```

### 3. Changelog Update
- Update `CHANGELOG.md` following the [Changelog Update Protocol](update-changelog.md).
- Ensure all major changes, fixes, and additions are categorized correctly.

### 4. Commit and Pull Request
- Commit changes with a descriptive message (e.g., `chore: prepare release v0.x.x`).
- Push to a release branch
- (Manually) Create a PR to `main`.
- Wait for CI/CD checks to pass on the PR.

### 5. Tagging (Manual/Triggered)
- Once the PR is merged to `main`, a git tag MUST be created for the new version.
- Tag name must match the version (e.g., `v0.x.x`).
- Push the tag to trigger deployment workflows.
