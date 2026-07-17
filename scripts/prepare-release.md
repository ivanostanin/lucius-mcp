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
- Create or refresh the repo-local virtual environment and reinstall the git hooks for this checkout.
```bash
uv sync --all-extras
uv run pre-commit install --install-hooks --hook-type pre-commit --hook-type pre-push
```

### 1. Version Bump
- Update the `version` field in `pyproject.toml`.
- Follow Semantic Versioning (SemVer) principles.

### 2. Dependency Sync
- Update project lockfiles and synchronized environments if anything changed after the initial bootstrap.
```bash
uv sync --all-extras
```

### 3. Regenerate MCP Documentation Manifest
- Regenerate `docs/mcp_manifest.json` after the version bump and dependency sync so the published MCP Registry documentation reflects the release version and current tool metadata.
```bash
uv run --locked fastmcp inspect src/main.py --format mcp -o docs/mcp_manifest.json
uv run --locked pytest tests/docs/test_mcp_manifest.py -q
```

### 4. Changelog Update
- Update `CHANGELOG.md` following the [Changelog Update Protocol](update-changelog.md).
- Ensure all major changes, fixes, and additions are categorized correctly.

### 5. Build MCPB Bundles Locally
- Build local MCPB artifacts for the release version.
```bash
./deployment/scripts/build-mcpb.sh
```

### 6. Update MCP Registry Metadata in `server.json`
- Update release version metadata and `fileSha256` values for all MCPB packages in `server.json` from the local `dist/*.mcpb` artifacts.
```bash
uv run python deployment/scripts/update_mcp_registry_metadata.py
```

### 7. Commit and Pull Request
- Commit changes with a descriptive message (e.g., `chore: prepare release v0.x.x`).
- Push to the release branch.
- Create a PR to `main` with `gh` CLI. The PR title MUST use Conventional Commit format (e.g., `chore: prepare release v0.x.x`).
```bash
gh pr create \
  --base main \
  --head release/v0.x.x \
  --title "chore: prepare release v0.x.x" \
  --body "Prepare release v0.x.x."
```
- Wait for CI/CD checks to pass on the PR.

### 8. Tagging (Manual/Triggered)
- Once the PR is merged to `main`, a git tag MUST be created for the new version.
- Tag name must match the version (e.g., `v0.x.x`).
- Push the tag to trigger deployment workflows.
