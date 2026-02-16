# Changelog Update Protocol for AI Agents

Update `CHANGELOG.md` using the Keep a Changelog 1.1.0 format:
https://keepachangelog.com/en/1.1.0/, but with `v` prefix in the version header.

## Required File Structure

The changelog must keep this top-level structure:

```markdown
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [vX.Y.Z] - YYYY-MM-DD
```

## Allowed Change Sections

Inside each release (including `Unreleased`), use only these section headers:

- `### Added`
- `### Changed`
- `### Deprecated`
- `### Removed`
- `### Fixed`
- `### Security`

Only include sections that have entries.

## Entry Rules

1. Use concise, user-facing bullet points.
2. Group each entry under exactly one section.
3. Avoid noise like "updated files" or duplicate statements.
4. Keep newest releases at the top (right under `Unreleased`).
5. Keep dates in ISO format: `YYYY-MM-DD`.
6. Include PR number in format `... (#XX)`.

## Release Update Rules

1. Add ongoing work under `## [Unreleased]`.
2. When cutting a release:
   - Create `## [vX.Y.Z] - YYYY-MM-DD` (with `v` prefix in the header).
   - Move relevant entries from `Unreleased` into that release.
   - Leave an `Unreleased` section at the top for future work.
3. Update bottom reference links so comparisons resolve correctly.

## Required Reference Links

At the bottom of `CHANGELOG.md`, keep link references like:

```markdown
[Unreleased]: <compare-url>/vX.Y.Z...HEAD
[vX.Y.Z]: <release-or-compare-url>
```

Use the repository's existing URL pattern for version and compare links and keep all versions linkable.
