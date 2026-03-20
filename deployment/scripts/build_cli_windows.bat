@echo off
REM Build CLI binary for Windows architectures.

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
for %%I in ("%SCRIPT_DIR%..\..") do set PROJECT_ROOT=%%~fI
cd /d "%PROJECT_ROOT%"

set TARGET_ARCH=
set CLEAN=true
if "%ONEFILE_CACHE_TEMPDIR_SPEC%"=="" set ONEFILE_CACHE_TEMPDIR_SPEC={CACHE_DIR}/{COMPANY}/{PRODUCT}/{VERSION}
if "%ONEFILE_CACHE_MODE%"=="" set ONEFILE_CACHE_MODE=cached
set ONEFILE_NO_COMPRESSION=false

:parse_args
if "%~1"=="" goto args_done

if /I "%~1"=="--arch" (
    if "%~2"=="" (
        echo Error: --arch requires a value
        exit /b 1
    )
    set TARGET_ARCH=%~2
    shift
    shift
    goto parse_args
)

if /I "%~1"=="--no-clean" (
    set CLEAN=false
    shift
    goto parse_args
)

if /I "%~1"=="--onefile-cache-mode" (
    if "%~2"=="" (
        echo Error: --onefile-cache-mode requires a value
        exit /b 1
    )
    set ONEFILE_CACHE_MODE=%~2
    shift
    shift
    goto parse_args
)

if /I "%~1"=="--onefile-no-compression" (
    set ONEFILE_NO_COMPRESSION=true
    shift
    goto parse_args
)

if /I "%~1"=="--help" goto show_help
if /I "%~1"=="-h" goto show_help

echo Unknown option: %~1
exit /b 1

:args_done
if "%TARGET_ARCH%"=="" set TARGET_ARCH=x86_64
if /I "%TARGET_ARCH%"=="amd64" set TARGET_ARCH=x86_64
if /I "%TARGET_ARCH%"=="aarch64" set TARGET_ARCH=arm64

if /I not "%TARGET_ARCH%"=="x86_64" if /I not "%TARGET_ARCH%"=="arm64" (
    echo Error: Unsupported --arch "%TARGET_ARCH%". Use arm64 or x86_64.
    exit /b 1
)

if /I not "%ONEFILE_CACHE_MODE%"=="cached" if /I not "%ONEFILE_CACHE_MODE%"=="off" (
    echo Error: Unsupported --onefile-cache-mode "%ONEFILE_CACHE_MODE%". Use cached or off.
    exit /b 1
)

set OUTPUT_DIR=dist\cli
set OUTPUT_FILE=lucius-windows-%TARGET_ARCH%.exe

echo Building lucius CLI for Windows %TARGET_ARCH%...

if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%
if /I "%CLEAN%"=="true" (
    if exist %OUTPUT_DIR%\%OUTPUT_FILE% del /f /q %OUTPUT_DIR%\%OUTPUT_FILE%
)

echo Generating tool schemas...
uv --quiet run --python 3.13 --extra dev python scripts\build_tool_schema.py

if not exist "src\cli\data\tool_schemas.json" (
    echo Error: tool_schemas.json not found after generation
    exit /b 1
)

set CLI_VERSION=
for /f "usebackq delims=" %%V in (`uv --quiet run --python 3.13 --extra dev python -c "from src.version import __version__; print(__version__)"`) do set CLI_VERSION=%%V
if "%CLI_VERSION%"=="" (
    echo Error: failed to resolve CLI version for onefile metadata
    exit /b 1
)

set "NUITKA_CACHE_FLAGS="
if /I "%ONEFILE_CACHE_MODE%"=="cached" (
    set "NUITKA_CACHE_FLAGS=--onefile-tempdir-spec=%ONEFILE_CACHE_TEMPDIR_SPEC% --onefile-cache-mode=cached"
)

set "NUITKA_COMPRESSION_FLAGS="
if /I "%ONEFILE_NO_COMPRESSION%"=="true" (
    set "NUITKA_COMPRESSION_FLAGS=--onefile-no-compression"
)

uv run --python 3.13 --extra dev nuitka ^
    --standalone ^
    --onefile ^
    --assume-yes-for-downloads ^
    --output-dir=%OUTPUT_DIR% ^
    --output-filename=%OUTPUT_FILE% ^
    --company-name=lucius-mcp ^
    --product-name=lucius ^
    --file-version=%CLI_VERSION% ^
    --product-version=%CLI_VERSION% ^
    --include-package=rich._unicode_data ^
    --include-data-files=src/cli/data/tool_schemas.json=data/tool_schemas.json ^
    %NUITKA_CACHE_FLAGS% ^
    %NUITKA_COMPRESSION_FLAGS% ^
    src\cli\cli_entry.py

echo Built: %OUTPUT_DIR%\%OUTPUT_FILE%
echo Windows %TARGET_ARCH% build complete
exit /b 0

:show_help
echo Usage: deployment\scripts\build_cli_windows.bat [OPTIONS]
echo.
echo Options:
echo   --arch ^<arm64^|x86_64^>  Target architecture ^(default: x86_64^)
echo   --no-clean               Do not remove previous target artifact
echo   --onefile-cache-mode     Onefile cache strategy: cached ^(default^) or off
echo   --onefile-no-compression Enable Nuitka --onefile-no-compression
echo   --help, -h               Show help
exit /b 0
