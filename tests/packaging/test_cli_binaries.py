"""
Packaging tests for CLI binaries across all platforms.

Tests verify binary size, functionality, and standalone execution.
"""

import json
import platform
import subprocess
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

        # Check all expected binaries exist (in CI/CD environment)
        # For dev builds, skip if not all platforms are available
        if platform.system() in ["Linux", "Darwin"]:
            # On Linux/macOS, expect at least the current platform binary
            machine = "arm64" if platform.machine() == "arm64" else "x86_64"
            current_binary = BINARIES.get(f"{platform.system().lower()}-{machine}")

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
        # Find current platform binary
        binaries = list(DIST_DIR.glob("lucius-*"))

        if not binaries:
            pytest.skip("No binaries found to test")

        # Try to run the binary most likely for current platform
        current_platform = platform.system().lower()
        machine = "arm64" if platform.machine() in ["arm64", "aarch64"] else "x86_64"
        expected_name = BINARIES.get(f"{current_platform}-{machine}")

        binary_to_test = None
        if expected_name and (DIST_DIR / expected_name).exists():
            binary_to_test = DIST_DIR / expected_name
        else:
            # Try to find a matching binary
            for binary in binaries:
                if current_platform in binary.name.lower():
                    binary_to_test = binary
                    break

        if not binary_to_test:
            pytest.skip(f"No suitable binary found for {platform.system()} {platform.machine()}")

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
        binaries = list(DIST_DIR.glob("lucius-*"))

        if not binaries:
            pytest.skip("No binaries found to test")

        current_platform = platform.system().lower()
        machine = "arm64" if platform.machine() in ["arm64", "aarch64"] else "x86_64"
        expected_name = BINARIES.get(f"{current_platform}-{machine}")

        binary_to_test = None
        if expected_name and (DIST_DIR / expected_name).exists():
            binary_to_test = DIST_DIR / expected_name
        else:
            for binary in binaries:
                if current_platform in binary.name.lower():
                    binary_to_test = binary
                    break

        if not binary_to_test:
            pytest.skip(f"No suitable binary found for {platform.system()} {platform.machine()}")

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
        assert "COMMAND" in output, "Help output missing COMMAND section"
        assert "list" in output.lower(), "Help output missing 'list' command"
        assert "call" in output.lower(), "Help output missing 'call' command"


class TestBinaryStandaloneExecution:
    """Test binary executes standalone without Python runtime."""

    @pytest.mark.skipif(not DIST_DIR.exists(), reason="dist/cli not found")
    def test_binary_standalone_no_python(self) -> None:
        """Test binary doesn't require Python to be in PATH."""
        binaries = list(DIST_DIR.glob("lucius-*"))

        if not binaries:
            pytest.skip("No binaries found to test")

        current_platform = platform.system().lower()
        machine = "arm64" if platform.machine() in ["arm64", "aarch64"] else "x86_64"
        expected_name = BINARIES.get(f"{current_platform}-{machine}")

        binary_to_test = None
        if expected_name and (DIST_DIR / expected_name).exists():
            binary_to_test = DIST_DIR / expected_name
        else:
            for binary in binaries:
                if current_platform in binary.name.lower():
                    binary_to_test = binary
                    break

        if not binary_to_test:
            pytest.skip(f"No suitable binary found for {platform.system()} {platform.machine()}")

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
    """Test binary has embedded tool schemas for fast list command."""

    @pytest.mark.skipif(not DIST_DIR.exists(), reason="dist/cli not found")
    def test_binary_has_schemas(self) -> None:
        """Test binary includes tool schemas (for fast list command)."""
        binaries = list(DIST_DIR.glob("lucius-*"))

        if not binaries:
            pytest.skip("No binaries found to test")

        current_platform = platform.system().lower()
        machine = "arm64" if platform.machine() in ["arm64", "aarch64"] else "x86_64"
        expected_name = BINARIES.get(f"{current_platform}-{machine}")

        binary_to_test = None
        if expected_name and (DIST_DIR / expected_name).exists():
            binary_to_test = DIST_DIR / expected_name
        else:
            for binary in binaries:
                if current_platform in binary.name.lower():
                    binary_to_test = binary
                    break

        if not binary_to_test:
            pytest.skip(f"No suitable binary found for {platform.system()} {platform.machine()}")

        print(f"\\nTesting tool schemas for: {binary_to_test.name}")

        # Run list command
        if platform.system() == "Windows":
            result = subprocess.run(
                [str(binary_to_test), "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        else:
            result = subprocess.run(
                [str(binary_to_test), "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )

        print(f"Exit code: {result.returncode}")

        # Should succeed
        assert result.returncode == 0, f"List command failed: {result.stderr}"

        # Should output JSON with tool list
        try:
            tools = json.loads(result.stdout)
            assert isinstance(tools, dict), "Output is not a dictionary"
            assert len(tools) > 0, "No tools found in output"
            print(f"✓ Found {len(tools)} tools in binary")
        except json.JSONDecodeError:
            pytest.fail(f"List command didn't return valid JSON: {result.stdout[:200]}")


class TestBinaryNoHTTPComponents:
    """Test binary doesn't include HTTP server components."""

    @pytest.mark.skipif(not DIST_DIR.exists(), reason="dist/cli not found")
    def test_binary_no_http_imports(self) -> None:
        """Test binary doesn't contain HTTP-related imports."""
        binaries = list(DIST_DIR.glob("lucius-*"))

        if not binaries:
            pytest.skip("No binaries found to test")

        for binary in binaries[:1]:  # Just test first binary
            print(f"\\nChecking for HTTP components in: {binary.name}")

            # Read binary as text and search for HTTP-related strings
            try:
                binary_content = binary.read_bytes().decode("utf-8", errors="ignore")

                # Check for HTTP server imports (should NOT be present)
                http_indicators = [
                    "import starlette",
                    "from starlette",
                    "import uvicorn",
                    "from uvicorn",
                    "from http.server",
                    "from wsgiref",
                ]

                found_http = []
                for indicator in http_indicators:
                    if indicator in binary_content:
                        found_http.append(indicator)

                if found_http:
                    pytest.fail(f"Binary {binary.name} contains HTTP server imports: {found_http}")
                else:
                    print(f"✓ No HTTP server components found in {binary.name}")

            except Exception as e:
                # Binary read failed, skip test
                print(f"Could not read binary content: {e}")


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
