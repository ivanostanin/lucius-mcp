# Nuitka CI Cache Reuse Plan

## Objective

Make the Nuitka compilation cache created while building the CLI available to
subsequent release-tag pipelines. The solution must retain platform,
architecture, Python, compiler, and Nuitka compatibility boundaries while
avoiding artifacts from one tag becoming the only reusable cache source.

## Current state and root cause

`_cli_build_test.yml` sets `NUITKA_CACHE_DIR` to
`${{ github.workspace }}/.nuitka-cache` and persists it through
`actions/cache`. The cache key is already independent of the release tag:

```text
nuitka-${os}-${arch}-py${python}-${uv-lock-and-build-script-hash}
```

However, GitHub Actions caches are scoped to the ref that created them:

- A pull-request run writes to its merge ref and cannot seed `main`.
- A run for `refs/tags/v0.12.2` cannot restore a cache written by
  `refs/tags/v0.12.1`.
- A tag run *can* restore a matching cache created on the default branch.

Today `cli-build.yml` runs on pull requests and manual dispatch only; the
release workflow calls the reusable workflow from a tag. There is therefore no
default-branch producer for the tag workflow to restore. Each tag build starts
with no accessible cache and writes a cache only that same tag can use.

## Target design

Use `main` as the trusted, shared cache producer:

```text
PR build                 main cache-warm build                 release tag
refs/pull/.../merge  ->  refs/heads/main                   ->  refs/tags/vX.Y.Z
private PR cache          shared cache scope                    restores main cache
```

The cache-warm build runs after a relevant change reaches `main`. It produces a
cache for every supported OS/architecture pair. A release tag at that same
commit uses the normal build workflow and restores the cache from `main`.
Release runs remain self-contained: if no main cache is available, they still
build successfully and simply run cold.

## Implementation steps

### 1. Add a cache-warming trigger on `main`

Update `.github/workflows/cli-build.yml` to run for relevant pushes to `main`.
Keep its existing pull-request and manual-dispatch triggers.

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'scripts/build_tool_schema.py'
      - 'deployment/scripts/build_cli_unix.sh'
      - 'deployment/scripts/build_cli_windows.bat'
      - '.github/actions/setup-python/**'
      - '.github/actions/resolve-cli-artifact-name/**'
      - '.github/workflows/cli-build.yml'
      - '.github/workflows/_cli_build_test.yml'
      - 'pyproject.toml'
      - 'uv.lock'
  pull_request:
    # Retain the same paths as push.
  workflow_dispatch:
```

The `push` event is a trusted trigger and can write caches in the default-branch
scope. A tag built immediately after the main workflow completes will find the
exact cache key in that scope.

### 2. Add a cache-warm-only reusable-workflow input

Extend the `workflow_call.inputs` section in
`.github/workflows/_cli_build_test.yml`:

```yaml
cache-warm-only:
  description: 'Populate the Nuitka cache without publishing or testing binaries'
  type: boolean
  default: false
```

Call the reusable workflow from `cli-build.yml` with
`cache-warm-only: true` for `push` runs. Pull-request and manual runs should
retain `false` so their current artifact and test behavior remains unchanged.

In the reusable workflow:

- Keep all six build matrix jobs; each cache is platform- and
  architecture-specific.
- Add `if: ${{ !inputs.cache-warm-only }}` to the artifact-upload step.
- Add `if: ${{ !inputs.cache-warm-only }}` to the `test-cli` job.
- Do **not** skip schema generation, dependency installation, cache restore, or
  the Nuitka build in cache-warm mode.

This avoids retaining redundant artifacts and running binary tests solely to
refresh the cache, while still warming every cache a release can use.

### 3. Replace the cache key with an explicit cache format and build-input hash

Actions caches are immutable. An unchanged exact key means a successful build
will not save newly produced C-compiler objects back to the existing archive.
The key must therefore change when compilation inputs change, while its prefix
must remain stable enough to restore the prior cache first.

Replace the cache step with this shape (the expression may be formatted onto one
line if required by YAML tooling):

```yaml
- name: Restore and save Nuitka build cache
  uses: actions/cache@v6.1.0
  with:
    path: ${{ env.NUITKA_CACHE_DIR }}
    key: >-
      nuitka-v2-${{ runner.os }}-${{ matrix.arch }}-py${{ env.CLI_BUILD_PYTHON_VERSION }}-
      ${{ hashFiles(
        'pyproject.toml',
        'uv.lock',
        'src/**',
        'scripts/build_tool_schema.py',
        'deployment/scripts/build_cli_unix.sh',
        'deployment/scripts/build_cli_windows.bat'
      ) }}
    restore-keys: |
      nuitka-v2-${{ runner.os }}-${{ matrix.arch }}-py${{ env.CLI_BUILD_PYTHON_VERSION }}-
```

`v2` intentionally invalidates the old cache layout. The key isolates Python
minor versions, OS, and architecture. `uv.lock` also captures the Nuitka
version. The source and generator inputs ensure that a main build after a code
change restores the latest compatible cache by prefix, then saves an updated
cache under the new exact key after success.

Do not keep the existing fallback that omits the Python version. Reusing
compiler objects across Python versions is not a supported compatibility
boundary.

### 4. Ensure that Nuitka has a real C compilation cache

Nuitka uses `ccache` for GCC compilation reuse and automatically uses
`clcache` for MSVC/ClangCL. The current Linux setup installs `gcc` and
`python3-dev` but does not explicitly install `ccache`.

Update `.github/actions/setup-python/action.yml` in the Linux build-dependency
branch:

```bash
sudo apt-get install -y gcc python3-dev ccache
ccache --version
```

For macOS ARM64, add a check in the build prerequisites step:

```bash
if ! command -v ccache >/dev/null 2>&1; then
  brew install ccache
fi
ccache --version
```

Use this only for CLI build jobs (`install-build-deps: true`), not for every
Python quality-check job. Nuitka detects `ccache` from `PATH` and places its
objects under `NUITKA_CACHE_DIR`, so the existing cache path will persist them.

### 5. Add observable cache metrics

Add Linux/macOS diagnostic steps around the Nuitka build:

```yaml
- name: Reset C compiler cache statistics
  if: runner.os != 'Windows'
  run: ccache --zero-stats

# Build CLI binary step remains here.

- name: Report C compiler cache statistics
  if: always() && runner.os != 'Windows'
  run: ccache --show-stats
```

Also give the cache step an `id` and log its `cache-hit` output. A prefix restore
is intentionally not an exact hit, so `cache-hit: false` on a new input hash is
not a failure; `ccache` hit statistics are the authoritative signal that the
previous cache reduced compilation work.

For Windows, preserve Nuitka's automatic `clcache` behavior initially. Add
Windows-specific cache statistics only after confirming the available command
and output on the hosted ARM64 and x64 runners.

### 6. Keep caches alive when releases are infrequent

GitHub removes cache entries that have not been accessed for seven days. If
`main` builds or releases occur less often, create a small
`.github/workflows/nuitka-cache-keepalive.yml` workflow:

- Trigger it on a cron schedule every five days and allow manual dispatch.
- Run on the default branch only.
- Check out the repository and use the identical six-entry matrix and cache-key
  expression.
- Use `actions/cache/restore`, not `actions/cache`, and do not run Nuitka.

The restore-only job refreshes the last-access time without creating a new
cache. It should not be added unless repository activity is too infrequent to
keep the cache naturally warm, because restoring six cache archives has a
network and runner-time cost.

## Validation plan

1. Open a PR that changes a CLI source file and confirm normal PR builds and
   artifact tests still run.
2. Merge it to `main`; confirm the cache-warm run executes all six builds but
   uploads no release artifacts and skips `test-cli`.
3. Inspect each build's cache logs. First use of `nuitka-v2` may restore by
   prefix or start cold; after a successful job it must save a `v2` cache in
   `refs/heads/main` scope.
4. Confirm `ccache --show-stats` reports stored objects at the end of a Linux
   build.
5. Create a test tag at the same main commit. Confirm each release matrix job
   restores the matching cache from `main`; compare `ccache` hit/miss counters
   and wall time with the main warm build.
6. Create a second source-change PR, merge it, and tag the merge commit.
   Confirm the main build restores the previous cache by prefix, saves a new
   exact key, and the tag build restores that new key.
7. If keepalive is enabled, verify its cache list `last accessed` timestamps
   remain fresh without cache writes.

## Success criteria

- A release tag created from a successfully built `main` commit restores a
  default-branch Nuitka cache for every platform/architecture pair.
- The release does not depend on cache data written by a sibling tag.
- Linux builds show meaningful `ccache` hits on a warmed release build.
- Build correctness and release artifacts remain unchanged when a cache is
  absent, expired, or invalidated.
- Cache storage remains below the repository Actions-cache quota; monitor cache
  sizes after the first two release cycles.

## Rollback and safety

The cache is an optimization only. If a platform fails after rollout:

1. Disable the `push` cache-warm trigger or set `cache-warm-only` back to false
   to restore the original workflow behavior.
2. Bump `nuitka-v2` to `nuitka-v3` to invalidate suspect cached data without
   deleting unrelated caches.
3. Do not cache credentials, environment files, or release artifacts in
   `NUITKA_CACHE_DIR`.
4. Keep cache writes limited to trusted default-branch pushes; pull-request and
   tag workflows must treat restored cache files as untrusted build inputs.

## References

- GitHub Actions, [Dependency caching reference](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
- Nuitka, [User Manual: caching compilation results and cache locations](https://nuitka.net/user-documentation/user-manual.html)
