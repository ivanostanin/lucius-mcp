# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), but with `v` prefix in the version header,
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added
- Added a standalone `lucius` CLI with packaged binaries, route mapping, and shell completion support for direct tool execution outside MCP clients (#85).

### Changed
- Unified output formats across CLI commands and MCP tools (`json`, `table`, `csv`, `plain`) for consistent machine- and human-readable responses (#97).
- Enabled XDG-based CLI caching to improve startup performance and artifact reuse in builds (#96).
- Improved quick-start and CLI documentation for clearer setup and usage guidance (#94, #95).
- Added a release workflow feature flag to control CLI artifact publishing behavior in CI/CD (#126).

### Fixed
- Fixed CI/release packaging so CLI binaries are included in release assets with correct versioned artifact naming (#100, #102).
- Fixed CLI E2E subprocess handling to use a dynamic Python version instead of a hardcoded interpreter path (#99).
- Improved CLI build pipeline reliability and optimization in CI checks (#88).

## [v0.8.2] - 2026-04-13

### Added
- Added a Pages workflow for publishing tool registry from CI (#98).
- Added a CI workflow to combine Dependabot pull requests into consolidated dependency updates (#116).

### Changed
- Expanded Python 3.13 support across CI, packaging checks, and release workflows (#87, #101).
- Updated runtime, tooling, and workflow dependencies, including `cryptography`, `softprops/action-gh-release`, and lockfile refreshes (#129, #130, #131, #140).

## [v0.8.1] - 2026-04-08

### Changed
- Updated runtime, tooling, and workflow dependencies across the release window, including FastMCP, Uvicorn, Cyclopts, Ruff, Pytest-Cov, Starlette, `softprops/action-gh-release`, `docker/login-action`, and lockfile dependency refreshes (#89, #90, #91, #93, #103, #104, #105, #117, #124).

### Fixed
- Hardened telemetry identity handling using installation-scoped HMAC protection with transparent telemetry configuration and documentation improvements (#125).

## [v0.8.0] - 2026-03-09

### Added
- Added MCP manifest documentation for tool exposure and usage guidance (#74).
- Added tool registry documentation updates for MCP clients (#79).

### Changed
- Updated GitHub Actions dependencies for artifact handling and Docker build support (`actions/upload-artifact`, `actions/download-artifact`, `docker/setup-qemu-action`, `docker/setup-buildx-action`) (#75, #76, #77, #78).

## [v0.7.2] - 2026-03-09

### Changed
- Updated project security policy documentation in `SECURITY.md` (#71).

### Security
- Tightened GitHub Actions workflow permissions to enforce least-privilege defaults (#72).

## [v0.7.1] - 2026-03-08

### Changed
- Upgraded core and development dependencies, including FastMCP 3, Uvicorn 0.41.0, Pydantic Settings 2.13.1, Rich 14.3.3, Faker 40.8.0, Ruff 0.15.5, and OpenAPI Generator CLI 7.20.0 (#57, #64, #65, #66, #67, #68, #69).
- Updated GitHub Actions dependencies used in CI and release workflows (`actions/setup-node`, `actions/checkout`, `docker/login-action`, `docker/build-push-action`, `softprops/action-gh-release`) (#59, #60, #61, #62, #63).
- Refined Dependabot automation configuration for dependency maintenance (#58).

### Fixed
- Corrected a README documentation issue (#56).

## [v0.7.0] - 2026-03-08

### Added
- `delete_test_case` support for archived test case cleanup workflows (#52).
- `delete_test_suite` tool to remove obsolete hierarchy suites (#53).
- Anonymous telemetry collection for MCP tool usage and runtime metadata (#49).

### Changed
- Tool schemas now include richer annotation hints to improve client-side guidance (#54).

### Fixed
- Integration selection logic for linked issues in test case workflows (#50).
- Flaky E2E coverage for test-layer update scenarios was stabilized (#51).

## [v0.6.1] - 2026-02-16

### Changed
- Changelog update protocol now enforces Keep a Changelog 1.1.0 sections and release-link rules (#XX).
- Release preparation instructions now include concrete `v0.6.1` branch/tag and version bump examples (#XX).

## [v0.6.0] - 2026-02-15

### Added
- Test plan management tools for creating, listing, and updating test plans (#37).
- `delete_test_plan` tool to remove obsolete test plans with idempotent behavior (#38).
- Test hierarchy management tools for organizing and maintaining test trees (#39).
- Defect lifecycle management tools for creating, updating, and retrieving defects (#40).
- Defect-to-test-case linking support in defect and test case workflows (#42).

### Fixed
- Launch result uploads now handle entity cleanup more reliably in E2E and integration coverage (#43).

## [v0.5.0] - 2026-02-12

### Added
- `delete_launch` tool to archive obsolete launches with idempotent outcomes (Story 5.3) (#34).
- `close_launch` and `reopen_launch` tools to manage launch lifecycle transitions and surface launch status details (Story 5.4) (#33).
- Bundle-runtime E2E lifecycle coverage that unpacks generated `.mcpb` artifacts and validates MCP startup/handshake from unpacked content (Story 4.6) (#35).
- `e2e` pytest marker registration and `scripts/full-test-suite.sh` to standardize full validation execution (#35).

### Changed
- Launch tool manifest definitions updated to expose lifecycle operations in MCP bundles (`deployment/mcpb/manifest.python.json`, `deployment/mcpb/manifest.uv.json`) (#33, #34).
- Release preparation protocol updated with explicit environment/branch setup and manual PR creation guidance (#32).
- Story and sprint tracking artifacts updated to mark Story 4.6 as completed (#35).

### Fixed
- Attachment discriminator parsing in `AllureClient` now normalizes DTO entity names for scenario step attachment deserialization (#32).
- `create_test_case` tool documentation updated to include `test_layer_id` argument guidance (#32).
- Re-enabled unit coverage for scenario-step attachment parsing regression (`tests/unit/test_client.py`) (#32).

## [v0.4.1] - 2026-02-09

### Added
- Pull request template for standardized contributions (#29).
- Security policy documentation (SECURITY.md) (#28).
- GitHub issue templates for bug reports and feature requests (#27).
- Code of conduct documentation (CODE_OF_CONDUCT.md) (#26).

### Fixed
- Test case step creation now correctly uses step with expected result instead of sub-steps for expected results (#30).

## [v0.4.0] - 2026-02-06

### Added
- CRUD support for project-level custom field values (#18).
- Issue linking and unlinking support for test cases (Story 3-12) (#17).
- Integration filtering by project for issue linking (#22).
- Support for test case steps with explicit expected results (#13).
- `get_launch` tool to retrieve detailed execution statistics (#12).
- Verification instructions for MCP tools (#11).

### Changed
- Mandatory confirmation and safety warnings for destructive tools (#23).
- Support for test layers by name in `update_test_case` (#15).
- Release pipeline restricted to the `main` branch (#10).
- Standardized specification cleanup (#19).

### Fixed
- Idempotent deletion messages for better feedback (#16).
- Logic for unlinking shared steps from test cases (#20).
- Exposure of the `get_launch` tool on the MCP server (#21).

## [v0.3.0] - 2026-02-03

### Added
- Launch management tools, including create and list launch operations.
- New tool entries in manifests for expanded tool coverage.
- Test layer support across test case CRUD and related tools.

### Changed
- Search test cases documentation and tests refined.
- E2E test execution supports parallel mode.

### Fixed
- Custom fields handling in test case operations.
- Test layer handling in tools and update_test_case support.
- Tag casing is preserved in search_test_cases results.

## [v0.2.2] - 2026-01-30

### Fixed
- Docker image build.

## [v0.2.1] - 2026-01-30

### Fixed
- Deployment workflows: release description now includes the changelog, and PyPI publishing steps are corrected.

## [v0.2.0] - 2026-01-30

### Added
- `get_custom_fields` tool to fetch custom fields and their allowed values (Story 3.6).
- New example payloads for the `create_test_case` tool to guide usage.
- Client generation for project and custom field controllers.
- Initial `CHANGELOG.md` and `LICENSE` documentation.

### Changed
- Default run mode changed to `stdio` for easier integration with MCP clients.
- Improved guidance for `create_test_case` tool, providing extended hints when non-existing custom fields are used (Story 3.5).
- Updated package metadata and versions.

## [v0.1.0] - 2026-01-28

### Added
- Initial release

[Unreleased]: https://github.com/ivanostanin/lucius-mcp/compare/v0.8.2...HEAD
[v0.8.2]: https://github.com/ivanostanin/lucius-mcp/compare/v0.8.1...v0.8.2
[v0.8.1]: https://github.com/ivanostanin/lucius-mcp/compare/v0.8.0...v0.8.1
[v0.8.0]: https://github.com/ivanostanin/lucius-mcp/compare/v0.7.2...v0.8.0
[v0.7.2]: https://github.com/ivanostanin/lucius-mcp/compare/v0.7.1...v0.7.2
[v0.7.1]: https://github.com/ivanostanin/lucius-mcp/compare/v0.7.0...v0.7.1
[v0.7.0]: https://github.com/ivanostanin/lucius-mcp/compare/v0.6.1...v0.7.0
[v0.6.1]: https://github.com/ivanostanin/lucius-mcp/compare/v0.6.0...v0.6.1
[v0.6.0]: https://github.com/ivanostanin/lucius-mcp/compare/v0.5.0...v0.6.0
[v0.5.0]: https://github.com/ivanostanin/lucius-mcp/compare/v0.4.1...v0.5.0
[v0.4.1]: https://github.com/ivanostanin/lucius-mcp/compare/v0.4.0...v0.4.1
[v0.4.0]: https://github.com/ivanostanin/lucius-mcp/compare/v0.3.0...v0.4.0
[v0.3.0]: https://github.com/ivanostanin/lucius-mcp/compare/v0.2.2...v0.3.0
[v0.2.2]: https://github.com/ivanostanin/lucius-mcp/compare/v0.2.1...v0.2.2
[v0.2.1]: https://github.com/ivanostanin/lucius-mcp/compare/v0.2.0...v0.2.1
[v0.2.0]: https://github.com/ivanostanin/lucius-mcp/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/ivanostanin/lucius-mcp/releases/tag/v0.1.0
