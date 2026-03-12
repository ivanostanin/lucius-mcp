# Lucius CLI Documentation

## Installation

### Download Pre-built Binaries

Download the binary for your platform from the [latest release](https://github.com/ivanostanin/lucius-mcp/releases):

- **Linux ARM64**: `lucius-linux-arm64`
- **Linux x86_64**: `lucius-linux-x86_64`
- **macOS ARM64 (Apple Silicon)**: `lucius-macos-arm64`
- **macOS x86_64 (Intel)**: `lucius-macos-x86_64`
- **Windows ARM64**: `lucius-windows-arm64.exe`
- **Windows x86_64**: `lucius-windows-x86_64.exe`

### Installation Steps

#### Linux / macOS

```bash
# Download the binary
wget https://github.com/ivanostanin/lucius-mcp/releases/latest/download/lucius-linux-x86_64

# Make it executable
chmod +x lucius-linux-x86_64

# Optionally move to PATH
sudo mv lucius-linux-x86_64 /usr/local/bin/lucius

# Verify installation
lucius --version
```

#### Windows

```powershell
# Download the binary
Invoke-WebRequest -Uri "https://github.com/ivanostanin/lucius-mcp/releases/latest/download/lucius-windows-x86_64.exe" -OutFile "lucius.exe"

# Add to PATH (PowerShell)
$env:PATH += ";C:\path\to\directory"

# Verify installation
.\lucius.exe --version
```

### Build from Source

```bash
# Clone the repository
git clone https://github.com/ivanostanin/lucius-mcp.git
cd lucius-mcp

# Build for current platform (Linux x86_64 example)
./deployment/scripts/build_cli_linux_x86_64.sh

# The binary will be in: dist/cli/lucius-linux-x86_64
```

## Usage

### List Available Tools

```bash
# List all tools (JSON format - default)
lucius list

# List tools in table format
lucius list --format table

# List tools in plain text format
lucius list --format plain
```

### Call a Tool

```bash
# Call tool with JSON arguments (JSON output - default)
lucius call get_test_case_details --args '{"test_case_id": 1234}'

# Call tool with table output
lucius call get_test_case_details --args '{"test_case_id": 1234}' --format table

# Call tool with plain text output
lucius call get_test_case_details --args '{"test_case_id": 1234}' -f plain

# Short flag for format
lucius call list_test_cases --args '{}' -f table
```

### Show Help for a Tool

```bash
# Show detailed help for a specific tool
lucius call get_test_case_details --show-help

# Show general CLI help
lucius --help

# Show help for list command
lucius list --help

# Show help for call command
lucius call --help
```

### Display Version

```bash
# Show CLI version
lucius --version

# Alternative
lucius version
```

## Output Formats

All commands support three output formats:

### JSON Format (Default)

Machine-readable structured output.

```bash
lucius list                          # JSON is default
lucius list --format json            # Explicit JSON
lucius call list_projects --args '{}' -f json
```

### Table Format

Human-readable tabular output.

```bash
lucius list --format table
lucius call list_projects --args '{}' --format table
```

### Plain Format

Plain text, human-friendly output.

```bash
lucius list --format plain
lucius call list_projects --args '{}' -f plain
```

## Configuration

The lucius CLI uses the same configuration as the MCP server:

### Environment Variables

- `ALLURE_API_URL`: Allure TestOps API endpoint URL
- `ALLURE_API_TOKEN`: API authentication token
- `ALLURE_PROJECT_ID`: Default project ID (optional, can be overridden per request)
- `LOG_LEVEL`: Logging level (e.g., `INFO`, `DEBUG`, `ERROR`)

Example `.env` file:

```bash
ALLURE_API_URL=https://your-allure-instance.com
ALLURE_API_TOKEN=your-api-token-here
ALLURE_PROJECT_ID=1
LOG_LEVEL=INFO
```

### Configuration File

You can also use a `.env` file in the current directory or set environment variables in your shell profile.

## Examples

### Common Workflows

#### Get Test Case Details

```bash
lucius call get_test_case_details --args '{"test_case_id": 1234}'
```

#### List Test Cases in a Project

```bash
lucius call list_test_cases --args '{"project_id": 1}' -f table
```

#### Create a New Test Case

```bash
lucius call create_test_case --args '{
  "name": "Login test",
  "description": "Test user login functionality",
  "steps": [
    {"action": "Navigate to login page", "expected": "Login form displayed"},
    {"action": "Enter credentials", "expected": "Credentials entered"},
    {"action": "Click login button", "expected": "Redirected to dashboard"}
  ],
  "tags": ["smoke", "auth"]
}'
```

#### Search Test Cases

```bash
lucius call search_test_cases --args '{
  "query": "login",
  "project_id": 1
}'
```

#### Create a Launch

```bash
lucius call create_launch --args '{
  "name": "Nightly Regression",
  "project_id": 1,
  "launch_type": 1
}'
```

## Troubleshooting

### Binary Won't Execute

**Problem**: `Permission denied` when running the binary

**Solution**:
```bash
chmod +x lucius-*
```

**Problem**: `command not found` after installation

**Solution**: Add the binary to your PATH or move to `/usr/local/bin/`

### Tool Execution Failed

**Problem**: Error when calling a tool

**Solutions**:

1. **Check API credentials**:
   ```bash
   echo $ALLURE_API_URL
   echo $ALLURE_API_TOKEN
   ```

2. **Check network connectivity**:
   ```bash
   curl -I $ALLURE_API_URL
   ```

3. **Verify tool name**:
   ```bash
   lucius list | grep tool_name
   ```

4. **Verify arguments**:
   ```bash
   lucius call <tool> --show-help
   ```

### Invalid JSON Arguments

**Problem**: `Invalid JSON in --args` error

**Solution**: Ensure JSON is properly formatted:
- Use single quotes around the JSON string
- Use double quotes for JSON keys and string values
- Escape any double quotes inside the JSON

```bash
# Correct
lucius call get_test_case --args '{"id": 1234}'

# Incorrect - missing quotes
lucius call get_test_case --args '{id: 1234}'

# Incorrect - wrong quote order
lucius call get_test_case --args "{'id': 1234}"
```

### Unknown Tool Error

**Problem**: `Tool 'xyz' not found` error

**Solution**: List available tools to find the correct name:
```bash
lucius list
```

### Permission Denied on File Writes

**Problem**: Binary can't write to directories

**Solution**: The CLI uses your environment configuration. Ensure:
- `.env` file is readable
- Environment variables are correctly set
- Current directory is writable if using local configuration files

## Design Principles

The lucius CLI follows these design principles:

1. **Lazy Initialization**: Fast startup (< 1s), MCP client only loaded when needed
2. **Clean Error Output**: No Python tracebacks, only user-facing error messages
3. **Individual Tool Help**: Every tool has isolated help with parameters and examples
4. **Type-Safe Arguments**: Validates arguments against tool schemas
5. **Multiple Output Formats**: JSON, table, and plain text formats
6. **Uses MCP Tools Directly**: Thin wrapper around MCP server, no business logic
7. **No HTTP Server**: CLI uses stdio transport only, no HTTP dependencies

## Shell Completion

Shell completion is automatically available through cyclopts for:

- Bash
- Zsh
- Fish
- PowerShell

To enable completion (bash example):

```bash
# Add to ~/.bashrc
eval "$(lucius --completion bash)"
```

## Building from Source

### Prerequisites

**Linux**:
```bash
sudo apt-get install gcc python3-dev
```

**macOS**:
```bash
xcode-select --install
```

**Windows**:
- Install [Visual Studio C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Install Python from [python.org](https://www.python.org/downloads/)

### Building

```bash
# Clone repository
git clone https://github.com/ivanostanin/lucius-mcp.git
cd lucius-mcp

# Install build dependencies
pip install -e ".[dev]"

# Build for your platform
./deployment/scripts/build_cli_linux_x86_64.sh  # Linux x86_64
./deployment/scripts/build_cli_linux_arm64.sh  # Linux ARM64
./deployment/scripts/build_cli_macos_arm64.sh  # macOS ARM64
./deployment/scripts/build_cli_macos_x86_64.sh # macOS x86_64
./deployment/scripts/build_cli_windows_x86_64.bat  # Windows x86_64
./deployment/scripts/build_cli_windows_arm64.bat  # Windows ARM64
```

Binaries will be in `dist/cli/`.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/ivanostanin/lucius-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ivanostanin/lucius-mcp/discussions)
- **Documentation**: [Project Docs](./)
