# Lucius CLI

## Command Model

Lucius uses an entity/action grammar:

```bash
lucius auth [--url <url>] [--token <token>] [--project <id>]
lucius auth status
lucius auth clear
lucius list
lucius list --help
lucius install-completions [--shell <shell>] [--path <file>] [--force] [--print]
lucius <entity>
lucius <entity> <action> --args '<json>' [--format json|table|plain|csv] [--pretty]
lucius <entity> <action> --help
```

`json` is the default output format.

## Examples

```bash
# Save CLI auth once for later commands
lucius auth
lucius auth --url https://example.testops.cloud --token <your_api_token> --project 123
lucius auth status
lucius auth clear

# Discover actions
lucius
lucius list
lucius list --help
lucius test_case
lucius integrations

# Install or print embedded shell completions
lucius install-completions
lucius install-completions --shell zsh
lucius install-completions --shell bash --print
lucius install-completions --shell fish --path ~/.config/fish/completions/lucius.fish --force

# Get action help
lucius test_case get --help
lucius launch close --help

# Execute actions
lucius test_case get --args '{"test_case_id": 1234}'
lucius test_case create --args '{"name": "Smoke login"}'
lucius test_case get --args '{"test_case_id": 1234}' --pretty
lucius launch close --args '{"launch_id": 123}' --format table
lucius defect list --args '{}' --format plain
```

## CLI Auth

`lucius auth` stores Allure credentials for later CLI launches. It validates the
URL, token, and project access before writing anything to disk.

Interactive mode:

```bash
lucius auth
```

Non-interactive mode:

```bash
lucius auth --url https://example.testops.cloud --token <your_api_token> --project 123
```

Status:

```bash
lucius auth status
```

Clear saved CLI auth:

```bash
lucius auth clear
```

Stored config path:

- Linux/Unix: `$XDG_CONFIG_HOME/lucius/auth.json` or `~/.config/lucius/auth.json`
- macOS: `~/Library/Application Support/lucius/auth.json` unless XDG overrides are explicitly set
- Windows: `%LOCALAPPDATA%\lucius\auth.json`

Precedence during tool execution:

1. Explicit tool args such as `api_token` or `project_id`
2. Environment variables: `ALLURE_ENDPOINT`, `ALLURE_API_TOKEN`, `ALLURE_PROJECT_ID`
3. Saved CLI auth config from `lucius auth`
4. Built-in defaults

The saved file contains URL, token, project ID, and timestamps. The token is never
shown by `lucius auth status`.

## Canonical Entities

- `test_case`
- `custom_field`
- `custom_field_value`
- `launch`
- `integration`
- `shared_step`
- `test_layer`
- `test_layer_schema`
- `test_suite`
- `test_plan`
- `defect`
- `defect_matcher`

## Entity Aliases

- `integrations` -> `integration`
- `test_cases` -> `test_case`
- `launches` -> `launch`
- `shared_steps` -> `shared_step`
- `test_layers` -> `test_layer`
- `test_layer_schemas` -> `test_layer_schema`
- `test_suites` -> `test_suite`
- `test_plans` -> `test_plan`
- `defects` -> `defect`
- `defect_matchers` -> `defect_matcher`
- `custom_fields` -> `custom_field`
- `custom_field_values` -> `custom_field_value`

## Output Formats

- `--format json`
- `--format table`
- `--format plain`
- `--format csv`
- `--pretty` for JSON output only

Examples:

```bash
lucius test_case list --args '{}' --format json
lucius test_case list --args '{}' --format json --pretty
lucius test_case get --args '{"test_case_id": 1234}' --pretty
lucius test_case list --args '{}' --format table
lucius test_case list --args '{}' --format plain
lucius test_case list --args '{}' --format csv
```

`--pretty` re-renders valid JSON output with deterministic indentation. It can be
used with the default JSON output or with `--format json`; it is rejected with
`plain`, `table`, or `csv`.

`table` format renders recognized date/time fields, such as `created_at`,
`updated_at`, `started_at`, `finished_at`, `*date`, `*timestamp`, and
start/end-style `*time` fields, as `YYYY-MM-DD HH:MM:SS`. Epoch seconds, epoch
milliseconds, and ISO-8601 strings with `Z` or explicit offsets are converted to
the local timezone when it can be resolved. Tables that render localized
datetimes include a caption such as `Timezone: Europe/Podgorica` so the display
timezone is explicit.

If the local timezone cannot be resolved, `table` format falls back to UTC and
labels the table with `Timezone: UTC`. Invalid date-like values remain unchanged,
and `json`, `plain`, and `csv` keep the original raw values.

`plain` format normalizes escaped newline markers (`\n`) into rendered line breaks.

## Shell Completions

`lucius install-completions` installs embedded completion scripts for bash, zsh,
fish, and PowerShell. It works from an installed wheel or standalone binary and
does not read repository completion files at runtime.

```bash
lucius install-completions
lucius install-completions --shell bash
lucius install-completions --shell zsh
lucius install-completions --shell fish
lucius install-completions --shell powershell
```

Options:

- `--shell <shell>` overrides shell detection. Supported values are `bash`, `zsh`, `fish`, and `powershell`; aliases such as `pwsh`, `powershell.exe`, and `/bin/zsh` are normalized.
- `--path <file>` writes the selected script to a custom file.
- `--force` overwrites an existing completion file.
- `--print` writes only the selected completion script to stdout and does not modify the filesystem.

Default install targets:

- bash: `${XDG_DATA_HOME:-~/.local/share}/bash-completion/completions/lucius`
- zsh: `${XDG_DATA_HOME:-~/.local/share}/zsh/site-functions/_lucius`
- fish: `${XDG_CONFIG_HOME:-~/.config}/fish/completions/lucius.fish`
- PowerShell: `%LOCALAPPDATA%/lucius/completions/lucius.ps1` on Windows, or `${XDG_DATA_HOME:-~/.local/share}/lucius/completions/lucius.ps1` elsewhere, plus an idempotent profile hook.

After installing, restart the shell. Bash users can also source the installed
file directly. Zsh users can activate the default install path in the current
session with `fpath=(${XDG_DATA_HOME:-~/.local/share}/zsh/site-functions $fpath); autoload -Uz compinit && compinit`.
PowerShell users can start a new session after the profile hook is written.

Repository completion artifacts are still generated for releases and stored in:

- `deployment/shell-completions/lucius.bash`
- `deployment/shell-completions/lucius.zsh`
- `deployment/shell-completions/lucius.fish`
- `deployment/shell-completions/lucius.ps1`

Regenerate them after route, alias, or CLI-local command changes:

```bash
python3 deployment/scripts/generate_completions.py
```

## Help and Validation

- `lucius` and `lucius list` print the same discovery table built from local static metadata.
- `lucius list --help` explains the explicit discovery command and does not require `--args`, saved credentials, or network access.
- `lucius <entity>` prints actions and short descriptions.
- `lucius <entity> <action> --help` prints description, parameters, required/optional markers, and examples.
- Unknown entities/actions and invalid JSON receive guided error hints.

## Onefile Startup Cache

Nuitka onefile CLI builds are configured to reuse extraction cache between runs:

- `--onefile-cache-mode=cached`
- `--onefile-tempdir-spec={CACHE_DIR}/{COMPANY}/{PRODUCT}/{VERSION}`

Operational behavior:

- First run after build/version change performs extraction (cold start).
- Subsequent runs reuse extracted payload (warm start).
- Cache path is version-scoped (`{VERSION}`), so a newer binary version does not reuse older cached extraction artifacts.
- `{CACHE_DIR}` maps to native OS cache roots:
  - Linux: XDG cache (`$XDG_CACHE_HOME` or `~/.cache`)
  - macOS: `~/Library/Caches`
  - Windows: `%LOCALAPPDATA%`

### Guardrails for Non-Writable Cache Roots

If startup fails with a cache extraction/write error, verify cache-root writability first.

Linux/macOS:

```bash
# Linux (XDG root or fallback)
CACHE_ROOT="${XDG_CACHE_HOME:-$HOME/.cache}"
test -d "$CACHE_ROOT" || mkdir -p "$CACHE_ROOT"
test -w "$CACHE_ROOT" || echo "Cache root is not writable: $CACHE_ROOT"

# macOS default root
test -d "$HOME/Library/Caches" || mkdir -p "$HOME/Library/Caches"
test -w "$HOME/Library/Caches" || echo "Cache root is not writable: $HOME/Library/Caches"
```

Windows PowerShell:

```powershell
$cacheRoot = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { Join-Path $env:USERPROFILE "AppData\Local" }
if (-not (Test-Path $cacheRoot)) { New-Item -ItemType Directory -Path $cacheRoot | Out-Null }
try {
  $probe = Join-Path $cacheRoot "lucius-write-probe.tmp"
  Set-Content -Path $probe -Value "ok" -ErrorAction Stop
  Remove-Item $probe -ErrorAction SilentlyContinue
} catch {
  Write-Host "Cache root is not writable: $cacheRoot"
}
```

Fallback guidance:

- Linux/macOS: set `XDG_CACHE_HOME` to a writable directory before running the binary.
- Windows: set `LOCALAPPDATA` to a writable directory before running the binary.

### Reproducible Benchmark Workflow

Build variants on the same host/arch, then run cold/warm timing checks for each.

Build commands (Unix):

```bash
case "$(uname -s)" in
  Linux) PLATFORM=linux ;;
  Darwin) PLATFORM=macos ;;
  *) echo "Unsupported platform"; exit 1 ;;
esac
case "$(uname -m)" in
  arm64|aarch64) ARCH=arm64 ;;
  x86_64|amd64) ARCH=x86_64 ;;
  *) echo "Unsupported arch"; exit 1 ;;
esac
BINARY="dist/cli/lucius-${PLATFORM}-${ARCH}"

# Variant 1: current onefile (no cache mode/tempdir spec)
bash deployment/scripts/build_cli_unix.sh --onefile-cache-mode off
cp "$BINARY" dist/cli/lucius-variant1

# Variant 2: cached tempdir spec + cached mode (default)
bash deployment/scripts/build_cli_unix.sh
cp "$BINARY" dist/cli/lucius-variant2

# Variant 3: variant 2 + no compression
bash deployment/scripts/build_cli_unix.sh --onefile-no-compression
cp "$BINARY" dist/cli/lucius-variant3
```

Build commands (Windows):

```bat
REM Variant 1
deployment\scripts\build_cli_windows.bat --onefile-cache-mode off
copy dist\cli\lucius-windows-x86_64.exe dist\cli\lucius-variant1.exe

REM Variant 2 (default)
deployment\scripts\build_cli_windows.bat
copy dist\cli\lucius-windows-x86_64.exe dist\cli\lucius-variant2.exe

REM Variant 3
deployment\scripts\build_cli_windows.bat --onefile-no-compression
copy dist\cli\lucius-windows-x86_64.exe dist\cli\lucius-variant3.exe
```

Timing commands:

```bash
hyperfine --warmup 0 --runs 1 ./dist/cli/lucius-variant1 --version
hyperfine --warmup 3 --runs 10 ./dist/cli/lucius-variant1 --version

hyperfine --warmup 0 --runs 1 ./dist/cli/lucius-variant2 --version
hyperfine --warmup 3 --runs 10 ./dist/cli/lucius-variant2 --version

hyperfine --warmup 0 --runs 1 ./dist/cli/lucius-variant3 --version
hyperfine --warmup 3 --runs 10 ./dist/cli/lucius-variant3 --version
```

Observed tradeoff (2026-03-20):

| Variant | Config | Cold Start | Warm Avg | Size |
|---|---|---:|---:|---:|
| v1_current | current onefile | 4.644s | 3.915s | 32,216,032 B |
| v2_cached | onefile + cached mode + persistent tempdir spec | 3.820s | 0.284s | 32,232,336 B |
| v3_cached_nocomp | v2 + no compression | 5.008s | 0.150s | 159,881,088 B |
