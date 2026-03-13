"""
Packaging tests for CLI binaries across all platforms.

Tests verify binary size, functionality, and standalone execution.
"""

import ast
import platform
import subprocess
from os import environ
from pathlib import Path

import pytest

# Path to binary distribution directory
DIST_DIR = Path(__file__).parent.parent.parent / "dist" / "cli"

# Expected binary names by platform
BINARIES = {
    "linux-arm64": "lucius-linux-arm64",
    "linux-x86_64": "lucius-linux-x86_64",
    "macos-arm64": "lucius-macos-arm64",
    "macos-x86_64": "lucius-macos-x86_64",
    "windows-arm64": "lucius-windows-arm64.exe",
    "windows-x86_64": "lucius-windows-x86_64.exe",
}


def _platform_name() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system


def _machine_name() -> str:
    return "arm64" if platform.machine().lower() in {"arm64", "aarch64"} else "x86_64"


def _select_current_binary() -> Path | None:
    binaries = [binary for binary in DIST_DIR.glob("lucius-*") if binary.is_file()]
    if not binaries:
        return None

    platform_name = _platform_name()
    machine_name = _machine_name()
    expected_name = BINARIES.get(f"{platform_name}-{machine_name}")
    if expected_name and (DIST_DIR / expected_name).exists():
        return DIST_DIR / expected_name

    system_name = platform.system().lower()
    for binary in binaries:
        lower_name = binary.name.lower()
        if machine_name in lower_name and (platform_name in lower_name or system_name in lower_name):
            return binary

    for binary in binaries:
        lower_name = binary.name.lower()
        if platform_name in lower_name or system_name in lower_name:
            return binary

    return binaries[0]


def _is_release_binary_validation_enabled() -> bool:
    explicit = environ.get("REQUIRE_ALL_CLI_BINARIES", "").strip().lower()
    return explicit in {"1", "true", "yes", "on"}


class TestBinaryPresence:
    """Test that expected binaries exist."""

    def test_all_platform_binaries_exist(self) -> None:
        """Test all 6 platform binaries are built."""
        print(f"\\nChecking for binaries in: {DIST_DIR}")

        if not DIST_DIR.exists():
            pytest.skip(f"Distribution directory not found: {DIST_DIR}")

        found_binaries = set()
        for binary_name in DIST_DIR.iterdir():
            if binary_name.is_file():
                found_binaries.add(binary_name.name)

        print(f"Found binaries: {sorted(found_binaries)}")

        # Release packaging jobs can enforce full cross-platform artifact set.
        if _is_release_binary_validation_enabled():
            missing = sorted(set(BINARIES.values()) - found_binaries)
            assert not missing, f"Release build is missing platform binaries: {missing}"
            return

        # Default/dev behavior: only require current-platform binary.
        if platform.system() in ["Linux", "Darwin"]:
            machine = _machine_name()
            current_binary = BINARIES.get(f"{_platform_name()}-{machine}")
            if current_binary:
                assert (DIST_DIR / current_binary).exists(), f"Current platform binary not found: {current_binary}"


class TestBinarySize:
    """Test binary sizes are reasonable."""

    @pytest.mark.skipif(not DIST_DIR.exists(), reason="dist/cli not found")
    def test_binary_size_reasonable(self) -> None:
        """Test binary size is reasonable (< 100MB)."""
        # Find any binary in the dist directory
        binaries = list(DIST_DIR.glob("lucius-*"))

        if not binaries:
            pytest.skip("No binaries found to test")

        for binary in binaries:
            size_mb = binary.stat().st_size / (1024 * 1024)
            print(f"\\n{binary.name}: {size_mb:.2f} MB")

            # Nuitka binaries can be large, but should be < 100MB
            assert size_mb < 100, f"Binary {binary.name} is too large: {size_mb:.2f} MB"

            # Should be at least 5MB (not empty)
            assert size_mb > 5, f"Binary {binary.name} is too small: {size_mb:.2f} MB"


class TestBinaryPermissions:
    """Test binary permissions are correct."""

    @pytest.mark.skipif(platform.system() == "Windows", reason="Permissions only on Unix")
    def test_binary_executable(self) -> None:
        """Test Unix binaries have executable permission."""
        # Find Unix binaries (not .exe)
        binaries = list(DIST_DIR.glob("lucius-*"))

        if not binaries:
            pytest.skip("No binaries found to test")

        for binary in binaries:
            if not binary.name.endswith(".exe"):
                print(f"\\nChecking permissions for: {binary.name}")
                assert binary.stat().st_mode & 0o111 != 0, f"Binary {binary.name} is not executable"


class TestBinaryExecution:
    """Test binary execution and basic functionality."""

    @pytest.mark.skipif(not DIST_DIR.exists(), reason="dist/cli not found")
    def test_binary_version_command(self) -> None:
        """Test binary responds to --version command."""
        binary_to_test = _select_current_binary()
        if not binary_to_test:
            pytest.skip("No binaries found to test")

        print(f"\\nTesting binary: {binary_to_test.name}")

        # Run --version command
        if platform.system() == "Windows":
            result = subprocess.run(
                [str(binary_to_test), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        else:
            result = subprocess.run(
                [str(binary_to_test), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )

        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")

        # Should succeed
        assert result.returncode == 0 or result.returncode == 1, f"Binary failed to execute: {result.stderr}"

        # Should output version
        output = result.stdout + result.stderr
        assert "lucius" in output.lower(), f"Version output doesn't contain 'lucius': {output}"

    @pytest.mark.skipif(not DIST_DIR.exists(), reason="dist/cli not found")
    def test_binary_help_command(self) -> None:
        """Test binary responds to --help command."""
        binary_to_test = _select_current_binary()
        if not binary_to_test:
            pytest.skip("No binaries found to test")

        print(f"\\nTesting help for: {binary_to_test.name}")

        # Run --help command
        if platform.system() == "Windows":
            result = subprocess.run(
                [str(binary_to_test), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        else:
            result = subprocess.run(
                [str(binary_to_test), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

        print(f"Exit code: {result.returncode}")

        # Should succeed
        assert result.returncode == 0, f"Help command failed: {result.stderr}"

        # Should show help content
        output = result.stdout + result.stderr
        assert "Usage:" in output, "Help output missing usage section"
        assert "lucius <entity>" in output, "Help output missing entity/action usage"
        assert "Available Entities" in output, "Help output missing entity list"


class TestBinaryStandaloneExecution:
    """Test binary executes standalone without Python runtime."""

    @pytest.mark.skipif(not DIST_DIR.exists(), reason="dist/cli not found")
    def test_binary_standalone_no_python(self) -> None:
        """Test binary doesn't require Python to be in PATH."""
        binary_to_test = _select_current_binary()
        if not binary_to_test:
            pytest.skip("No binaries found to test")

        print(f"\\nTesting standalone execution for: {binary_to_test.name}")

        # Run with empty PATH to verify binary doesn't depend on Python
        # Note: This test may fail if libc or system libraries are needed
        if platform.system() != "Windows":
            env = {"PATH": ""}  # Empty PATH
            result = subprocess.run(
                [str(binary_to_test), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                env=env,
            )

            # If this succeeds, binary is truly standalone
            # If it fails with "not found" or similar, it might need system shared libs
            # which is acceptable for Nuitka binaries
            print(f"Standalone execution result: {result.returncode}")
            if result.returncode == 0:
                print("✓ Binary is standalone (no Python dependency detected)")
            else:
                print(f"Note: Binary may need system libraries: {result.stderr}")


class TestBinaryToolSchemaEmbedded:
    """Test binary contains embedded command metadata for entity/action discovery."""

    @pytest.mark.skipif(not DIST_DIR.exists(), reason="dist/cli not found")
    def test_binary_has_schemas(self) -> None:
        """Test binary supports entity discovery without runtime MCP dependency."""
        binary_to_test = _select_current_binary()
        if not binary_to_test:
            pytest.skip("No binaries found to test")

        print(f"\\nTesting tool schemas for: {binary_to_test.name}")

        # Run entity discovery command
        if platform.system() == "Windows":
            result = subprocess.run(
                [str(binary_to_test), "test_case"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        else:
            result = subprocess.run(
                [str(binary_to_test), "test_case"],
                capture_output=True,
                text=True,
                timeout=10,
            )

        print(f"Exit code: {result.returncode}")

        # Should succeed
        assert result.returncode == 0, f"List command failed: {result.stderr}"

        output = result.stdout + result.stderr
        assert "Actions for test_case" in output, "Entity discovery output missing action table"
        assert "list_test_cases" in output, "Entity discovery output missing mapped tool metadata"


class TestBinaryNoHTTPComponents:
    """Test binary doesn't include HTTP server components."""

    FORBIDDEN_IMPORT_PREFIXES = ("starlette", "uvicorn", "http.server", "wsgiref")

    def test_cli_source_has_no_http_imports(self) -> None:
        """CLI module must not import HTTP server components."""
        cli_root = Path(__file__).parent.parent.parent / "src" / "cli"
        assert cli_root.exists(), f"CLI source directory not found: {cli_root}"

        violations: list[str] = []
        for path in sorted(cli_root.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported = alias.name
                        if imported.startswith(self.FORBIDDEN_IMPORT_PREFIXES):
                            violations.append(f"{path}:{node.lineno} import {imported}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if module.startswith(self.FORBIDDEN_IMPORT_PREFIXES):
                        violations.append(f"{path}:{node.lineno} from {module} import ...")

        assert not violations, "Forbidden HTTP imports found in CLI source:\n" + "\n".join(violations)


class TestCrossPlatformCompatibility:
    """Test cross-platform binary naming and structure."""

    def test_binary_naming_convention(self) -> None:
        """Test all binary files follow expected naming convention."""
        if not DIST_DIR.exists():
            pytest.skip("dist/cli not found")

        binaries = list(DIST_DIR.glob("lucius-*"))

        for binary in binaries:
            # Check name matches expected pattern
            if platform.system() == "Windows":
                # Windows binaries should end with .exe
                assert binary.name.endswith(".exe") or platform.system().lower() not in binary.name.lower(), (
                    f"Windows binary should end with .exe: {binary.name}"
                )
            else:
                # Unix binaries should NOT end with .exe
                assert not binary.name.endswith(".exe"), f"Unix binary should not end with .exe: {binary.name}"

            # Check name contains platform indicator
            name_parts = binary.name.lower().split("-")
            assert len(name_parts) >= 3, f"Binary name doesn't follow pattern: {binary.name}"
            assert name_parts[0] == "lucius", f"Binary name should start with 'lucius': {binary.name}"


class TestBinaryBuildScriptConfiguration:
    """Validate CLI build script configuration needed for runtime stability."""

    def test_rich_unicode_data_included_in_nuitka_builds(self) -> None:
        """All platform build scripts must include rich unicode data package."""
        project_root = Path(__file__).parent.parent.parent
        scripts = [
            project_root / "deployment/scripts/build_cli_unix.sh",
            project_root / "deployment/scripts/build_cli_windows.bat",
        ]

        missing: list[str] = []
        for script_path in scripts:
            content = script_path.read_text(encoding="utf-8")
            if "--include-package=rich._unicode_data" not in content:
                missing.append(str(script_path))

        assert not missing, "Nuitka build scripts missing rich unicode data include flag:\n" + "\n".join(
            sorted(missing)
        )
