# Changelog

## [Unreleased]

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

## [v0.2.0]

### Added
- `get_custom_fields` tool to fetch custom fields and their allowed values (Story 3.6).
- New example payloads for the `create_test_case` tool to guide usage.
- Client generation for project and custom field controllers.
- Initial `CHANGELOG.md` and `LICENSE` documentation.

### Changed
- Default run mode changed to `stdio` for easier integration with MCP clients.
- Improved guidance for `create_test_case` tool, providing extended hints when non-existing custom fields are used (Story 3.5).
- Updated package metadata and versions.

## [v0.1.0]

- Initial release
