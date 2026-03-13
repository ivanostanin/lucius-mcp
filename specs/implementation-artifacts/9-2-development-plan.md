# Development Plan - Story 9.2: FastMCP CLI Integration

**Story:** 9-2-fastmcp-cli-integration.md
**Status:** Development (Course Correction Phase)
**Created:** 2025-03-12
**Updated:** 2025-03-12 (Course Correction)
**Branch:** feature/fastmcp-cli-story-9-1 (git branch retains original name for continuity)

---

## Phase 1: Story Analysis

### 1.1 Understanding of Requirements

**Primary Goal:**
Build a universal CLI entry point `lucius` that provides type-safe access to all MCP tools from the command line, distributed as standalone binaries for multiple platforms.

**Key Requirements Breakdown:**

**Core Functional Requirements:**
1. CLI entry point named `lucius` with subcommands (P0)
2. Single binary distribution for 6 platforms: Linux (ARM64/x86_64), macOS (ARM64/x86_64), Windows (ARM64/x86_64) (P0)
3. Type-safe CLI commands derived from MCP tool JSON schemas (P0)
4. Core commands: `list`, `call [--help]`, `--version`, `--help` (P0)
5. Multiple output formats: JSON (default), table, plain (P0)
6. No MCP/Python logs in output (only user-facing errors) (P0)
7. Tool call errors provide guiding messages (P0)
8. Validation errors show meaningful hints (P0)
9. Individual tool help: `lucius call <tool> --help` (P0)
10. Lazy initialization: fast startup, MCP client only on `call`, only called tool loaded (P0)
11. No HTTP server: CLI does not import or use HTTP components (P0)
12. Shell completion for commands and tool names (P1)
13. E2E test coverage (P1)
14. Packaging tests for all 6 platforms (P1)
15. Verify HTTP components not bundled (P1)
16. Comprehensive documentation (P2)
17. Docker integration support (P2)
18. CI/CD pipeline for automated builds (P2)

**Architecture Pattern:**
- **Thin CLI / Fat Service**: CLI layer is minimal wrapper, uses MCP server tools directly
- **No Reimplementation**: CLI calls MCP tools, does not reimplement business logic
- **Lazy Loading**: Fast startup, delayed MCP client initialization
- **Clean Separation**: CLI module has no HTTP server imports

### 1.2 Key Challenges

**Challenge 1: Lazy Client Initialization (HIGH - Course Correction)**
- Refactor CLI entry point to remove eager `from src.main import mcp`
- Implement build-time static tool list generation for `lucius list`
- Ensure MCP client initialized only when `lucius call` invoked
- Load only called tool (lazy imports in MCP server invocation)
- Achieve < 1s startup for help/version/list commands

**Challenge 2: Multi-Platform Binary Compilation (HIGH)**
- Nuitka configuration complexity across 6 different platforms
- Platform-specific dependencies (GCC, Xcode, VS Build Tools)
- Binary size optimization while maintaining functionality
- Excluding HTTP server components from binary bundle
- Python 3.13 vs 3.14 compatibility (Nuitka experimental support issue)

**Challenge 3: Clean Error Output Medium-HIGH)**
- Catch and suppress all MCP and Python logs/tracebacks
- Format exceptions as user-facing guiding messages
- Extract and display validation hints from MCP server responses
- Consistent error message format across all CLI commands

**Challenge 4: Type-Safe Interface (MEDIUM-HIGH)**
- Extracting JSON schemas from MCP tool definitions
- Implementing individual tool help generation from schemas
- Robust argument parsing and validation for `lucius call`
- Type conversion between CLI arguments and tool parameters
- Support for 3 output formats (JSON, table, plain)

**Challenge 5: Build-Time Tool List Generation (MEDIUM)**
- Extract tool schemas from MCP server at build time
- Store static tool list as JSON data embedded in binary
- Verify CLI can display tool info without MCP client initialization
- Handle schema updates and regeneration

**Challenge 6: CI/CD Pipeline (MEDIUM)**
- GitHub Actions matrix builds for 6 platforms
- Cross-platform testing automation
- Artifact management and release automation
- Build time optimization
- Verify HTTP components not in binary (size test, import test)

**Challenge 7: Testing Strategy (MEDIUM)**
- Mocking API responses for reliable CLI testing
- Platform-specific binary verification tests
- Testing lazy initialization (verify fast startup)
- Testing error message formatting (no Python tracebacks)
- Verify HTTP components not imported in CLI module

### 1.3 Complexity Assessment

**Overall Complexity: Medium-High (7/10)** (increased due to course correction)

**Breakdown by Component:**
- **Lazy Client Initialization**: 8/10 (highest complexity - refactoring required)
- **Multi-Platform Binary Compilation**: 7.5/10 (excluding HTTP components)
- **Clean Error Output**: 7/10
- **Type-Safe Interface**: 6.5/10
- **Build-Time Tool List Generation**: 6/10
- **CI/CD Pipeline**: 5/10
- **E2E Testing**: 5/10
- **CLI Entry Point (cyclopts)**: 4/10
- **Documentation**: 2/10

**Rationale:**
- Lazy initialization requires significant refactoring of CLI entry point
- Removing HTTP components from binary adds complexity to build system
- Clean error output requires comprehensive exception handling
- Multi-platform compilation remains complex with Python version compatibility

---

## Phase 2: Implementation Planning

### 2.1 Implementation Strategy

**High-Level Approach:**
1. **Phase 1: CLI Core Implementation** (Task 1-3) - Build the basic CLI functionality using FastMCP native integration
2. **Phase 2: Build System** (Task 4) - Set up Nuitka compilation for all 6 platforms
3. **Phase 3: Testing** (Task 5-6) - Implement E2E and packaging tests
4. **Phase 4: CI/CD** (Task 7) - Automate builds and releases
5. **Phase 5: Quality & Documentation** (Task 8-9) - Ensure quality and comprehensive docs

**Key Design Decisions:**

**Decision 1: Leverage FastMCP Native CLI**
- **Rationale:** FastMCP v3.0+ provides CLI integration out of the box
- **Benefit:** Aligns perfectly with MCP protocol, minimal wrapper code required
- **Trade-off:** Less flexibility than custom CLI framework, but sufficient for requirements

**Decision 2: Nuitka for Binary Compilation**
- **Rationale:** Better performance, smaller binaries, true standalone execution
- **Benefit:** No Python runtime needed on target machines
- **Trade-off:** More complex build configuration than PyInstaller

**Decision 3: Separate Binaries per Platform**
- **Rationale:** Optimize download size and compatibility
- **Benefit:** Users only download what they need
- **Trade-off:** More build configurations to maintain

### 2.2 Dependency Planning

**New Dependencies:**
```toml
dependencies = [
    # ... existing dependencies
    "nuitka>=2.0",  # Binary compilation
]

[project.optional-dependencies]
dev = [
    # ... existing dev dependencies
    "click>=8.0",  # Optional: for advanced CLI features if needed
]
```

**Build Dependencies (Platform-Specific):**
- **Linux**: GCC, python3-dev, libc6-dev
- **macOS**: Xcode command line tools
- **Windows**: Visual Studio C++ Build Tools, Python header files

### 2.3 Implementation Phases

**Phase 1: CLI Core (Days 1-3)**
- Implement basic CLI entry point using FastMCP native integration
- Add core commands: list, call, help, version
- Implement type-safe argument parsing
- Add basic error handling

**Phase 2: Build System (Days 4-6)**
- Set up Nuitka configurations
- Create platform-specific build scripts
- Test manual builds on available platforms
- Optimize binary sizes

**Phase 3: Testing (Days 7-9)**
- Implement E2E tests for CLI commands
- Create packaging verification tests
- Mock API responses for reliable testing
- Ensure comprehensive coverage

**Phase 4: CI/CD (Days 10-12)**
- Set up GitHub Actions workflow
- Configure matrix builds for all 6 platforms
- Add automated testing
- Configure artifact uploads

**Phase 5: Quality & Documentation (Days 13-14)**
- Run linting (ruff) and type checking (mypy --strict)
- Comprehensive CLI documentation
- Update README
- Final verification

**Total Estimated Effort:** 14 days

### 2.4 Risk Management

**Risk 1: Build Failures on Some Platforms**
- **Mitigation 1:** Prioritize platforms available for local testing
- **Mitigation 2:** Use containerized builds where possible (Docker for Linux, macOS runners for macOS, Windows runners for Windows)
- **Mitigation 3:** Thoroughly test Nuitka configuration on each platform individually before CI integration
- **Fallback:** Document manual build process as backup

**Risk 2: Binary Size Too Large**
- **Mitigation 1:** Optimize Nuitka settings (exclude unused modules, enable optimizations)
- **Mitigation 2:** Use UPX compression if needed
- **Acceptance Criteria:** Target < 50MB per binary

**Risk 3: Type-Safe Interface Complexity**
- **Mitigation 1:** Start with FastMCP's native type-safe CLI (don't over-engineer)
- **Mitigation 2:** Simple validation initially, enhance if tests show issues
- **Mitigation 3:** Extensive test coverage for error cases

**Risk 4: Dependency on System Toolchains**
- **Mitigation 1:** Document build prerequisites clearly
- **Mitigation 2:** Use pre-built CI images with required toolchains
- **Mitigation 3:** Provide detailed troubleshooting guide

**Risk 5: Shell Completion Compatibility**
- **Mitigation 1:** Start with bash/zsh (most common)
- **Mitigation 2:** Defer fish/pwsh to P2 scope if time constrained
- **Fallback:** Document manual usage clearly

---

## Phase 3: Acceptance Criteria Validation

### 3.1 P0 (Must-Have) Criteria Validation

| Criteria | Validation Plan | Success Metric |
|----------|----------------|----------------|
| 1. CLI Entry Point with subcommands | Test `lucius <command>` pattern works | All subcommands execute |
| 2. Single binary for 6 platforms | Build and execute each binary | All 6 binaries run standalone |
| 3. Type-safe interface | Test type validation on command arguments | Invalid types rejected with clear errors |
| 4. Core commands (list, call, help, version) | Test each command with various inputs | All commands work correctly |

### 3.2 P1 (Should-Have) Criteria Validation

| Criteria | Validation Plan | Success Metric |
|----------|----------------|----------------|
| 5. Tab completion | Test completion in bash/zsh | Completion provides valid suggestions |
| 6. E2E test coverage | pytest tests/ coverage report | > 80% coverage on CLI code |
| 7. Packaging tests | pytest tests/packaging/ | All binary tests pass |
| 8. Error handling | Test with invalid inputs, API errors | Clear, actionable error messages |

### 3.3 P2 (Nice-to-Have) Criteria Validation

| Criteria | Validation Plan | Success Metric |
|----------|----------------|----------------|
| 9. Documentation | Complete CLI.md with all sections | Docs reviewed and approved |
| 10. Docker integration | Test CLI in Docker container | CLI works in Docker |
| 11. CI/CD pipeline | Run GitHub Actions workflow | All builds succeed |
| 12. Output formats | Test --json, --table flags | All formats produce valid output |

---

## Phase 4: Step-by-Step Implementation Plan

### Task 1: Design CLI Architecture (AC: #1, #3)

**Subtasks:**

1.1 Design lazy initialization architecture
- Remove eager `from src.main import mcp` from CLI entry point
- Design build-time tool schema extraction
- Design static tool list generation for `lucius list`
- Plan delayed MCP client loading for `lucius call`

1.2 Design clean error output system
- Configure logging to suppress MCP and Python logs
- Design exception catching and formatting
- Design error message templates (guiding messages + hints)
- Ensure no tracebacks in CLI output

1.3 Define JSON schema extraction and tool help
- Build-time: Extract tool schemas from MCP server
- Store as static JSON data embedded in binary
- Generate individual tool help from stored schemas
- Support: description, parameters, types, formats, examples

1.4 Design multi-format output system
- JSON format (default): Structured output
- Table format: Tabular output using rich tables
- Human format: Pretty-printed natural language
- Unified formatter interface for all commands

1.5 Plan shell completion integration
- Bash completion: Generate tool names from static list
- Zsh completion: Generate from bash completion
- Installation: Provide completion scripts in repo root

1.6 Verify HTTP exclusion
- Ensure CLI module has no HTTP imports
- Ensure FastMCP configured for stdio only
- Document HTTP server exclusion in build system
- Test binary to confirm HTTP components not present

**Deliverables:**
- Architecture design documented in code comments
- No code changes in this task (planning only)

### Task 2: Implement Core CLI Entry Point (AC: #1, #3, #4, #5, #6, #7, #8)

**Subtasks:**

2.1 Create `src/cli/__init__.py`
```python
"""
CLI module for lucius-mcp command-line interface.

Note: No HTTP server imports allowed in CLI module.
"""
from .cli_entry import main

__all__ = ["main"]
```

2.2 Create `src/cli/cli_entry.py` - Lazy CLI entry point with cyclopts
- Use cyclopts for CLI command parsing
- NO eager imports of `src.main.mcp` (lazy import only)
- Implement fast startup for `--help`, `--version`, `list`
- Implement clean error catching (suppress Python tracebacks)

2.3 Create `src/cli/build_tool_schema.py` - Build-time schema generator
- Import MCP server temporarily to extract tool schemas
- Export schemas as JSON: `src/cli/data/tool_schemas.json`
- Include: name, description, parameters (with types, formats, required)
- Run during build process

2.4 Implement `lucius list [--format json|table|plain]` command
- Load tool schemas from static JSON file (no MCP client)
- Format output based on `--format` flag
- JSON is default format
- Display tool metadata: name, description, parameters

2.5 Implement `lucius call <tool_name> --help` command
- Load tool schema from static JSON
- Generate isolated tool help documentation
- Display: description, all parameters, types, formats, examples
- No MCP client initialization (static only)

2.6 Implement `lucius call <tool_name> --args <json> [--format json|table|plain]` command
- Lazy import: Initialize MCP client only here
- Load only the called tool (lazy imports in tool modules)
- Parse and validate `--args <json>` against tool schema
- Execute tool through MCP (do NOT reimplement)
- Format output based on `--format` flag
- Catch all exceptions, format as guiding error messages

2.7 Add `--help` and `--version` flags
- `--help`: Use FastMCP's built-in help
- `--version`: Display version from src/version.py

2.6 Configure error handling
- Wrap tool execution in try-catch
- Convert Pydantic validation errors to user-friendly messages
- Provide actionable suggestions for common errors

**Deliverables:**
- `src/cli/__init__.py`
- `src/cli/lucius_cli.py`
- Basic CLI functional locally

### Task 3: Type-Safe Interface Implementation (AC: #3)

**Subtasks:**

3.1 Extract JSON schemas from tool definitions
- Use FastMCP's `get_tool_schemas()` method
- Store schemas for argument validation
- Cache for performance

3.2 Implement argument validation using Pydantic
- Create dynamic Pydantic models from schemas
- Parse `--args <json>` input
- Validate against tool schema
- Return structured errors for invalid input

3.3 Add type conversion for CLI arguments
- Convert CLI strings to appropriate types (int, float, bool, etc.)
- Handle nested JSON structures
- Validate required vs optional parameters

3.4 Implement structured output formatting
- JSON output: Use `--json` flag
- Human-readable: Default format with nice formatting
- Table: Use `--table` flag (P2, defer if needed)

**Deliverables:**
- Updated `src/cli/lucius_cli.py` with type-safe interface
- Helper functions for schema extraction and validation

### Task 4: Build System with Nuitka (AC: #2)

**Subtasks:**

4.1 Create base Nuitka configuration
- File: `nuitka.cfg` in project root
- Configure standalone mode
- Set optimization level
- Exclude unused modules

4.2-4.7 Create platform-specific build scripts

**Linux ARM64 (4.2):** `deployment/scripts/build_cli_linux_arm64.sh`
```bash
#!/bin/bash
set -e
python -m nuitka \
    --standalone \
    --onefile \
    --output-dir=dist \
    --output-filename=lucius-linux-arm64 \
    --enable-plugin=numpy \  # if needed
    --follow-imports \
    src/cli/lucius_cli.py
```

**Linux x86_64 (4.3):** `deployment/scripts/build_cli_linux_x86_64.sh` (similar)

**macOS ARM64 (4.4):** `deployment/scripts/build_cli_macos_arm64.sh`
- Target: arm64-apple-darwin
- Codesign with ad-hoc signature

**macOS x86_64 (4.5):** `deployment/scripts/build_cli_macos_x86_64.sh`
- Target: x86_64-apple-darwin

**Windows ARM64 (4.6):** `deployment/scripts/build_cli_windows_arm64.bat`
- Use python.exe -m nuitka
- Target: win_arm64

**Windows x86_64 (4.7):** `deployment/scripts/build_cli_windows_x86_64.bat`
- Target: win_amd64

4.8 Create master build script: `scripts/build_all_cli.sh`
- Build all 6 platforms sequentially
- Report success/failure for each
- Create checksums for binaries

**Deliverables:**
- `nuitka.cfg` configuration
- 7 build scripts (6 platform-specific + 1 master)
- Successfully built binaries (test on Linux at minimum)

### Task 5: E2E Test Suite (AC: #6)

**Subtasks:**

5.1 Create `tests/cli/conftest.py`
- Fixture for CLI subprocess execution
- Mock Allure API client responses
- Test data fixtures for tool calls

5.2 Create `tests/cli/test_cli_basics.py`
```python
def test_cli_help():
    """Test lucius --help displays help"""
    result = run_cli(["--help"])
    assert result.returncode == 0
    assert "lucius" in result.stdout

def test_cli_version():
    """Test lucius --version displays version"""
    result = run_cli(["--version"])
    assert result.returncode == 0
    assert __version__ in result.stdout

def test_cli_list_tools():
    """Test lucius list --json lists all tools"""
    result = run_cli(["list", "--json"])
    assert result.returncode == 0
    tools = json.loads(result.stdout)
    assert len(tools) > 0
```

5.3 Create `tests/cli/test_cli_tools.py`
```python
@pytest.mark.respx
def test_cli_call_tool(respx_mock):
    """Test lucius call executes a tool"""
    # Mock API response
    # Call tool
    # Assert result
```

5.4 Add error handling tests
- Invalid tool name
- Malformed JSON args
- Missing required parameters
- API errors

5.5 Mock API responses
- Use respx to mock httpx requests
- Return predictable test data
- Cover success and error cases

**Deliverables:**
- `tests/cli/conftest.py`
- `tests/cli/test_cli_basics.py`
- `tests/cli/test_cli_tools.py`
- All tests passing

### Task 6: Packaging Tests (AC: #7)

**Subtasks:**

6.1 Create `tests/packaging/test_cli_binaries.py`
```python
import stat
import subprocess

def test_binary_permissions():
    """Test binaries are executable"""
    for binary in get_binaries():
        st = os.stat(binary)
        assert st.st_mode & stat.S_IXUSR

def test_binary_execution():
    """Test binaries execute standalone"""
    for binary in get_binaries():
        result = subprocess.run([binary, "--version"])
        assert result.returncode == 0

def test_binary_size():
    """Test binaries are within size limits"""
    for binary in get_binaries():
        size = os.path.getsize(binary)
        assert size < 50 * 1024 * 1024  # < 50MB

def test_no_runtime_dependencies():
    """Test binaries run without Python installed"""
    # This is hard to test automatically, but we can:
    # - Check ldd output on Linux for Python references
    # - Check file type is executable binary, not script
    pass
```

6.2-6.5: Implement tests as outlined
- Binary size verification
- Permission checks
- Standalone execution verification
- Sample tool calls

**Deliverables:**
- `tests/packaging/test_cli_binaries.py`
- All packaging tests passing

### Task 7: CI/CD Pipeline (AC: #11)

**Subtasks:**

7.1 Create `.github/workflows/cli-build.yml`
```yaml
name: Build CLI Binaries

on:
  push:
    tags: ['v*']
  pull_request:
    paths:
      - 'src/cli/**'
      - '.github/workflows/cli-build.yml'

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            arch: x86_64
          - os: macos-14
            arch: arm64
          - os: macos-13
            arch: x86_64
          - os: windows-latest
            arch: x86_64
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Set up uv
        uses: astral-sh/setup-uv@v4
      - name: Build binary
        run: ./deployment/scripts/build_cli_${{ matrix.os }}_${{ matrix.arch }}.sh
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: lucius-${{ matrix.os }}-${{ matrix.arch }}
          path: dist/lucius-*
```

7.2 Configure multi-platform builds
- Use matrix strategy for all 6 platforms
- Note: ARM64 platforms may require cross-compilation or self-hosted runners

7.3 Add automated testing
- Run CLI tests after build
- Verify binary execution
- Upload test results

7.4 Configure artifact uploads
- Upload binaries as artifacts
- Generate checksums
- Create release notes

7.5 Add release automation
```yaml
- name: Create Release
  if: startsWith(github.ref, 'refs/tags/')
  uses: softprops/action-gh-release@v2
  with:
    files: dist/*
```

**Deliverables:**
- `.github/workflows/cli-build.yml`
- CI/CD pipeline running successfully

### Task 8: Documentation (AC: #9)

**Subtasks:**

8.1 Create `docs/CLI.md`
```markdown
# Lucius CLI Documentation

## Installation

### Download Pre-built Binaries
[Download links to latest release]

### Build from Source
[Instructions]

## Usage

### List Available Tools
\`\`\`
lucius list --json
\`\`\`

### Call a Tool
## Usage

### List Available Tools
```bash
# List all tools (JSON format - default)
lucius list

# List tools in table format
lucius list --format table

# List tools in plain format
lucius list --format plain
```

### Call a Tool
```bash
# Call tool with JSON arguments (JSON output - default)
lucius call get_test_case --args '{"id": 1234}'

# Call tool with table output
lucius call get_test_case --args '{"id": 1234}' --format table

# Call tool with plain output
lucius call get_test_case --args '{"id": 1234}' --format plain

# Get help for a specific tool
lucius call get_test_case --help
```

### Help and Version
```bash
# Show CLI help
lucius --help

# Show CLI version
lucius --version

# Show help for a subcommand
lucius list --help
lucius call --help
```

## Output Formats

All commands support three output formats:

### JSON Format (Default)
Machine-readable structured output
```bash
lucius list  # JSON is default
lucius list -f json  # Explicit JSON format
```

### Table Format
Tabular output for easy scanning
```bash
lucius list --format table
lucius call list_projects --args '{}' -f table
```

### Human-Readable Format
Natural language, pretty-printed output
```bash
lucius list --format plain
lucius call list_projects --args '{}' -f plain
```

## Shell Completion

### Bash
\`\`\`bash
source <(lucius --completion bash)
\`\`\`

### Zsh
\`\`\`zsh
source <(lucius --completion zsh)
\`\`\`

## Building

### Prerequisites
[Platform-specific requirements]

### Building All Platforms
\`\`\`bash
./scripts/build_all_cli.sh
\`\`\`

### Building for Specific Platform
\`\`\`bash
./deployment/scripts/build_cli_linux_x86_64.sh
\`\`\`

## Troubleshooting

### Binary won't execute
- Check permissions: `chmod +x lucius-*`
- Verify binary integrity with SHA256 checksum
- Check platform compatibility

### Tool execution failed
- Verify API credentials are configured
- Check network connectivity
- Use `--debug` flag for detailed error messages
```

8.2-8.5: Complete documentation sections
- Installation instructions
- Building instructions for all platforms
- Usage examples and workflows
- Troubleshooting guide

8.6 Update `README.md`
- Add CLI section at top
- Link to full CLI.md documentation
- Add quick start examples

**Deliverables:**
- `docs/CLI.md` (comprehensive)
- Updated `README.md`

### Task 9: Quality Assurance (AC: #8, #5)

**Subtasks:**

9.1 Run ruff and fix issues
```bash
ruff check src/cli/
ruff check --fix src/cli/
```

9.2 Run mypy with strict mode
```bash
mypy --strict src/cli/
```
- Fix any type errors
- Add type hints where needed

9.3 Run all tests
```bash
pytest tests/cli/ tests/packaging/
pytest --cov=src/cli tests/
```

9.4 Test binary execution
- Build binary for current platform
- Execute `./lucius-* --version`
- Execute `./lucius-* list --json`
- Execute `./lucius-* call list_projects --args '{}'`

9.5 Verify shell completion
- Test bash completion
- Test zsh completion
- Verify suggestions are correct

**Deliverables:**
- Zero ruff errors
- Zero mypy errors
- All tests passing
- Binary tested end-to-end
- Shell completion verified

---

## Phase 5: Success Criteria Checklist

### Functional Requirements
- [ ] All 6 platform binaries build successfully
- [ ] Binaries execute independently with no runtime dependencies
- [ ] Core commands work: `list --json`, `call <tool>`, `--help`, `--version`
- [ ] Type-safe interface validates arguments against schemas
- [ ] Error messages are clear and actionable

### Quality Requirements
- [ ] E2E tests cover all CLI commands and tool invocations
- [ ] Packaging tests verify binary correctness for all platforms
- [ ] Code passes `ruff check` with zero errors
- [ ] Code passes `mypy --strict` with zero errors
- [ ] Binary sizes are reasonable (< 50MB target)
- [ ] At least one platform tested manually end-to-end

### Documentation Requirements
- [ ] Comprehensive CLI.md documentation exists
- [ ] Installation instructions for all platforms
- [ ] Building instructions for all platforms
- [ ] Usage examples and workflows
- [ ] Troubleshooting guide
- [ ] README.md updated with CLI introduction

### CI/CD Requirements
- [ ] GitHub Actions workflow builds all 6 platforms
- [ ] Automated testing runs on all builds
- [ ] Artifacts uploaded for each platform
- [ ] Release automation configured

### Optional (P2) Requirements
- [ ] Docker image with CLI pre-installed
- [ ] Multiple output formats (JSON, plain, table)
- [ ] Shell completion for bash and zsh
- [ ] Fish and PowerShell completion (if time permits)

---

## Phase 6: Progress Tracking

### Task Completion Status
- [ ] Task 1: Design CLI Architecture
- [ ] Task 2: Implement Core CLI Entry Point
- [ ] Task 3: Type-Safe Interface Implementation
- [ ] Task 4: Build System with Nuitka
- [ ] Task 5: E2E Test Suite
- [ ] Task 6: Packaging Tests
- [ ] Task 7: CI/CD Pipeline
- [ ] Task 8: Documentation
- [ ] Task 9: Quality Assurance

### Blockers
- None identified

### Dependencies
- None - can proceed in parallel with other stories

### Next Steps
1. Begin implementation with Task 2 (CLI entry point)
2. Focus on getting basic CLI working before adding advanced features
3. Prioritize Linux x86_64 build first (most accessible platform)
4. Add other platforms after basic functionality is verified

---

## Appendix A: Technical References

### FastMCP CLI Documentation
- https://jlowin.github.io/fastmcp/cli/

### Nuitka Documentation
- https://nuitka.net/doc/user-manual.html
- Standalone mode: https://nuitka.net/doc/user-manual.html#stand-alone-mode
- Plugins: https://nuitka.net/doc/user-manual.html#plugins

### GitHub Actions Matrix Builds
- https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs
- https://docs.github.com/en/actions/using-github-hosted-runners/running-jobs-on-different-operating-systems

### Shell Completion
- Bash completion: https://www.gnu.org/software/bash/manual/html_node/Programmable-Completion.html
- Click completion: https://click.palletsprojects.com/en/8.1.x/shell-completion/

---

## Appendix B: Platform-Specific Build Notes

### Linux ARM64
- Build on native ARM64 system or use cross-compilation
- Requires: gcc, python3-dev, libc6-dev
- Test target: Raspberry Pi or cloud ARM64 instance

### Linux x86_64
- Most straightforward platform to build
- Requires: gcc, python3-dev, libc6-dev
- Test target: Any standard Linux distribution

### macOS ARM64
- Requires: Xcode command line tools
- Target: Apple Silicon Macs
- Codesigning: Use ad-hoc signature for distribution

### macOS x86_64
- Requires: Xcode command line tools
- Target: Intel Macs
- May build on x86_64 runner or cross-compile

### Windows ARM64
- Requires: Visual Studio C++ Build Tools
- Target: Surface Pro X, Windows Dev Kit 2023
- May need self-hosted runner for native ARM64 builds

### Windows x86_64
- Requires: Visual Studio C++ Build Tools
- Target: Standard Windows PCs
- Standard GitHub Actions windows-latest runner

---

**Document Status:** Complete
**Ready for Implementation:** Yes
**Next Action:** Begin Task 2 - Implement Core CLI Entry Point
