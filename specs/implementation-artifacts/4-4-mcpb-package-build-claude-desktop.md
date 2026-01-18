# Story 4.4: mcpb package build for Claude Desktop

Status: ready-for-dev
Story Key: 4-4-mcpb-package-build-claude-desktop

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a DevOps engineer,
I want a reproducible build and release of our **Python MCP server** packaged as a `.mcpb` bundle for Claude Desktop,
so that Claude Desktop users can install and update it reliably via published releases without needing a local Python setup.

## Acceptance Criteria

1. **Bundle creation (Python MCP):** Given the repo with the Python MCP server, when we build dependencies into the bundle (e.g., vendored `server/lib/` or `server/venv/`, or UV runtime) and run `mcpb pack`, then a versioned `.mcpb` is produced with filename including the current app version.
2. **Manifest correctness:** The `manifest.json` uses `server.type = "python"` (or `uv`), sets `server.entry_point` to the MCP server module/cli, and configures `env` (e.g., `PYTHONPATH` to include bundled libs) so Claude Desktop can run without an external Python install.
3. **Release publishing:** Given a git tag/release matching the project version, when the release pipeline runs, then it uploads the `.mcpb` bundle as a GitHub Release asset. If we also publish to PyPI (optional), the version matches the tag.
4. **PR quality gate:** Given a pull request, when CI runs, then it executes lint, tests, build, and `mcpb pack`, failing on errors and surfacing the packed artifact (or its path) for verification without publishing.
5. **Desktop installability:** Given the produced `.mcpb` bundle, when opened in Claude Desktop (macOS/Windows), then the install dialog appears and installation succeeds; instructions for this flow are documented.
6. **Version control and safety:** The pipeline fails if the git tag and project version mismatch, and no secrets or tokens are hardcoded in build scripts; pinned Python version and reproducible lock are enforced in CI.

## Tasks / Subtasks

- [ ] Add a build script for the Python MCP server that vendors deps (e.g., `server/lib/` or `server/venv/`, or uses UV runtime) and runs `mcpb pack`, emitting a versioned `.mcpb` artifact.
- [ ] Ensure `manifest.json` is correct for Python/UV: `server.type`, `server.entry_point`, `env` (e.g., `PYTHONPATH`), and platform notes; wire it into the build script.
- [ ] Add CI workflow(s): PR path (lint/test/pack, artifact exposure) and release path (tag-triggered pack + upload `.mcpb` to GitHub Release, version/tag validation). Optional: PyPI publish aligned to the same version.
- [ ] Document installation steps for Claude Desktop consumers and contributor steps for local pack/test (README or docs section).
- [ ] Manually verify bundle install in Claude Desktop (macOS/Windows) using the produced artifact and record the result.

## Dev Notes

- **Languages/Tooling:** Python MCP server packaged via `mcpb`. Manifest uses `server.type = "python"` (or `uv`), sets `server.entry_point`, and configures `env` (e.g., `PYTHONPATH` to bundled libs). `mcpb` CLI (latest observed v2.1.2) produces `.mcpb` bundles.
- **Build commands:** `uv pip compile` / `uv pip install -r requirements.txt --target server/lib` (or `python -m venv server/venv && pip install -r requirements.txt`), then `mcpb pack`. Ensure the bundle includes deps and pins Python version (or uses UV runtime for user-Python-free installs).
- **Release flow:** Tag-driven workflow validates version, runs pack, and uploads `.mcpb` to GitHub Release. Optional: publish to PyPI with the same version. Fail fast on version/tag mismatches and missing artifacts.
- **Desktop install:** End-users open the `.mcpb` file in Claude Desktop to trigger installation; keep filename aligned to version (e.g., `lucius-mcp-<version>.mcpb`).

### Project Structure Notes

- CI workflows live in `.github/workflows/`.
- Build/publish scripts should reside under `deployment/scripts/` (per architecture doc separation of infra) and be invoked from CI/package scripts.
- Keep repo root clean; avoid scattering ad-hoc scripts outside `deployment/` or package scripts.

### References

- Architecture decisions (deployment separation, patterns): `specs/architecture.md`
- PRD context (LLM-first reliability, release discipline): `specs/prd.md`
- Project rules: `specs/project-context.md`
- mcpb upstream guidance (Python packaging & manifest expectations): https://github.com/modelcontextprotocol/mcpb

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
