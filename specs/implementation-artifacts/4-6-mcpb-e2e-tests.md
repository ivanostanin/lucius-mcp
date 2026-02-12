# Story 4.6: mcpb-e2e-tests

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer,
I want to add E2E tests that verify the specific `mcpb` lifecycle (manifests, bundles, execution),
so that I can ensure the packaging and distribution pipeline is robust and that generated bundles actually work.

## Acceptance Criteria

1.  **Verify Manifests**: Test must validate `mcpb` manifests against the schema (reuse logic from `deployment/scripts/validate_mcpb.py`).
2.  **Build Bundles**: Test must successfully build a bundle from the manifests (reuse or call `deployment/scripts/build-mcpb.sh`).
3.  **Verify Bundle Contents**: Test must inspect the generated bundle (zip/archive) and verify key files exist (reuse `verify_manifest` and `verify_python_bundle_contents` logic from `deployment/scripts/verify_mcpb_bundles.py`).
4.  **Unpack and Run**: Test must unpack the bundle and attempt to start the server from the unpacked content.
5.  **Server Startup Verification**: Verify that the server from the unpacked bundle starts up correctly and responds to initialization or health checks.

## Tasks / Subtasks

- [ ] Task 1: Create E2E Test Suite for mcpb (AC: 1, 2, 3)
    - [ ] Subtask 1.1: Implement test to validate `mcpb.yaml` / manifests, reusing logic from `validate_mcpb.py`.
    - [ ] Subtask 1.2: Implement test to build the bundle, either by calling `build-mcpb.sh` or porting its logic to Python.
    - [ ] Subtask 1.3: Implement verification of the output bundle structure, porting/reusing logic from `verify_mcpb_bundles.py`.
- [x] Task 2: Runtime Verification (AC: 4, 5)
    - [x] Subtask 2.1: Implement logic to unpack the bundle to a temporary location.
    - [x] Subtask 2.2: Implement execution test that runs the server (e.g., using `subprocess` or `uv run`) from the unpacked location and performs a connection handshake/ping.

### Review Follow-ups (AI)

- [x] [AI-Review][High] AC4 is not implemented: no E2E test unpacks a generated `.mcpb` and runs server from unpacked bundle [tests/e2e/test_mcp_server_lifecycle.py:17]
- [x] [AI-Review][High] AC5 is not implemented via bundle flow: startup/handshake checks run against `src.main` directly, not unpacked bundle runtime [tests/e2e/test_mcp_server_lifecycle.py:121]
- [ ] [AI-Review][Medium] Story File List is empty while repository has undocumented changes (`.agent/`, `src/client/.DS_Store`) [specs/implementation-artifacts/4-6-mcpb-e2e-tests.md:59]
- [x] [AI-Review][Medium] Story status was `ready-for-dev` during review execution; workflow expectation is reviewable story status [specs/implementation-artifacts/sprint-status.yaml:34]
- [x] [AI-Review][Low] E2E runtime tests are not marked with `@pytest.mark.e2e` despite story guidance for slow lifecycle checks [tests/e2e/test_mcp_server_lifecycle.py:112]

## Dev Notes

- **Existing Scripts**: 
  - `deployment/scripts/validate_mcpb.py`: Manifest validation and entry point checking.
  - `deployment/scripts/verify_mcpb_bundles.py`: Bundle content verification.
  - `deployment/scripts/build-mcpb.sh`: Build process (vendor dependencies, pack).
- **Environment**: These tests might take longer to run; ensure they are marked appropriately (e.g., `@pytest.mark.e2e`).
- **Isolation**: Use `tempfile` for unpacking and building to avoid polluting the workspace.

### Project Structure Notes

- Tests should go in `tests/e2e/`.

### References

- `mcpb` documentation/readme.
- Existing CI/CD scripts.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

- Added bundle-runtime E2E coverage that unpacks generated `.mcpb` and runs server from unpacked content.
- Added unpacked-runtime MCP handshake validation (`initialize` + `list_tools`) to close AC4/AC5 gaps.
- Marked lifecycle runtime tests with `@pytest.mark.e2e` and registered the `e2e` marker in pytest config.
- Verified with targeted lifecycle tests and packaging build/bundle tests.

### File List

- [tests/e2e/test_mcp_server_lifecycle.py](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/tests/e2e/test_mcp_server_lifecycle.py)
- [pyproject.toml](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/pyproject.toml)
- [specs/implementation-artifacts/4-6-mcpb-e2e-tests.md](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/specs/implementation-artifacts/4-6-mcpb-e2e-tests.md)
- [specs/implementation-artifacts/sprint-status.yaml](file:///Users/anmaro/Code/personal/github.com/ivanostanin/lucius-mcp/specs/implementation-artifacts/sprint-status.yaml)

## Senior Developer Review (AI)

- **Outcome**: Changes Requested
- **Story Status Warning**: Review executed while story was `ready-for-dev`; proceeding per explicit user direction.
- **Git vs Story Discrepancies**:
  - Story File List had no implementation entries.
  - Git reported undocumented working tree changes: `.agent/` and `src/client/.DS_Store`.
- **AC Validation Summary**:
  - AC1 **Implemented**: manifest validation present in `tests/packaging/test_mcpb_manifests.py:11` and `deployment/scripts/validate_mcpb.py:7`.
  - AC2 **Implemented**: bundle build covered by `tests/packaging/test_mcpb_build.py:12` and `deployment/scripts/build-mcpb.sh:25`.
  - AC3 **Implemented**: bundle content checks covered by `tests/packaging/test_mcpb_bundles.py:56` and `deployment/scripts/verify_mcpb_bundles.py:74`.
  - AC4 **Missing**: no E2E unpack-and-run from generated bundle (`tests/e2e/test_mcp_server_lifecycle.py:17`).
  - AC5 **Partial/Missing**: startup verification exists only for source-run server, not unpacked bundle runtime (`tests/e2e/test_mcp_server_lifecycle.py:121`).
- **Severity Totals**: 2 High, 2 Medium, 1 Low

### Change Log

#### 2026-02-11: Implementation follow-up for review issues
- Added `test_http_lifecycle_from_unpacked_python_bundle` to verify unpack-and-run flow from generated `.mcpb`.
- Added/registered `@pytest.mark.e2e` for lifecycle runtime tests.
- Ran validations:
  - `uv run --env-file .env.test pytest tests/e2e/test_mcp_server_lifecycle.py -m e2e`
  - `uv run --env-file .env.test pytest tests/packaging/test_mcpb_build.py tests/packaging/test_mcpb_bundles.py`
- Updated story status to `review` and synced sprint status.

#### 2026-02-11: Senior Developer Review (AI)
- Executed adversarial review for Story 4.6 and recorded AC evidence with file:line references.
- Added `Review Follow-ups (AI)` action items for unresolved HIGH/MEDIUM/LOW findings.
- Updated story status to `in-progress` because HIGH issues remain.
