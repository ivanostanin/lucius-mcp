@echo off
REM Build CLI binary for Windows ARM64

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
for %%I in ("%SCRIPT_DIR%..\..") do set PROJECT_ROOT=%%~fI
cd /d "%PROJECT_ROOT%"

echo Building lucius CLI for Windows ARM64...

REM Clean previous builds
if exist dist\cli rmdir /s /q dist\cli

REM Generate tool schemas for fast startup (build-time static data)
echo Generating tool schemas...
uv --quiet run python scripts\build_tool_schema.py

if not exist "src\cli\data\tool_schemas.json" (
    echo Error: tool_schemas.json not found after generation
    exit /b 1
)

REM Use uv to run nuitka
REM Excluding HTTP components - CLI uses stdio transport only
REM Including static tool schemas for fast startup
REM Destination path: data/tool_schemas.json (relative to module location)
uv run nuitka ^
    --standalone ^
    --onefile ^
    --assume-yes-for-downloads ^
    --output-dir=dist\cli ^
    --output-filename=lucius-windows-arm64.exe ^
    --include-data-files=src/cli/data/tool_schemas.json=data/tool_schemas.json ^
    src\cli\cli_entry.py

echo Built: dist\cli\lucius-windows-arm64.exe
echo Windows ARM64 build complete
