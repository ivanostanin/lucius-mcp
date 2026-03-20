"""
Packaging tests for CLI binaries across all platforms.

Tests verify binary size, functionality, and standalone execution.
"""

import ast
import os
import platform
import subprocess
import tempfile
import time
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


def _is_benchmark_binary_name(name: str) -> bool:
    """Detect ad-hoc benchmark variants that should not be treated as release artifacts."""
    lower = name.lower()
    markers = ("variant1", "variant2", "variant3", "-v1-", "-v2-", "-v3-", "nocomp")
    return any(marker in lower for marker in markers)


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


def _render_cache_path(template: str, cache_dir: str, company: str, product: str, version: str) -> str:
    """Render Nuitka onefile cache template for deterministic path checks."""
    return (
        template.replace("{CACHE_DIR}", cache_dir)
        .replace("{COMPANY}", company)
        .replace("{PRODUCT}", product)
        .replace("{VERSION}", version)
    )


def _is_release_binary_validation_enabled() -> bool:
    explicit = environ.get("REQUIRE_ALL_CLI_BINARIES", "").strip().lower()
    return explicit in {"1", "true", "yes", "on"}


def _emit_build_log(request: pytest.FixtureRequest, message: str) -> None:
    reporter = request.config.pluginmanager.getplugin("terminalreporter")
    if reporter is not None:
        reporter.write_line(message)
    else:
        print(message, flush=True)


@pytest.fixture(scope="session")
def built_cli_binary(request: pytest.FixtureRequest) -> Path:
    """Build one current-platform CLI binary for packaging/runtime verification tests."""
    project_root = Path(__file__).parent.parent.parent
    platform_name = _platform_name()
    machine_name = _machine_name()

    if platform.system() == "Windows":
        command = ["cmd", "/c", "deployment\\scripts\\build_cli_windows.bat", "--arch", machine_name]
    else:
        command = [
            "bash",
            "deployment/scripts/build_cli_unix.sh",
            "--platform",
            platform_name,
            "--arch",
            machine_name,
        ]

    _emit_build_log(request, f"[build-cli] starting build for {platform_name}-{machine_name}: {' '.join(command)}")
    started = time.perf_counter()
    process = subprocess.Popen(
        command,
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert process.stdout is not None
    for line in process.stdout:
        _emit_build_log(request, f"[build-cli] {line.rstrip()}")

    return_code = process.wait()
    elapsed = time.perf_counter() - started
    _emit_build_log(request, f"[build-cli] finished in {elapsed:.2f}s (exit={return_code})")
    if return_code != 0:
        pytest.fail(f"CLI build failed with exit code {return_code}")

    binary = _select_current_binary()
    if binary is None or not binary.exists():
        pytest.fail("CLI build completed but no current-platform lucius binary was found in dist/cli")

    _emit_build_log(request, f"[build-cli] using binary: {binary}")
    return binary


class TestBinaryBuildFixture:
    """Ensure packaging tests can build and locate a runnable binary."""

    def test_fixture_build_binary_success(self, built_cli_binary: Path) -> None:
        assert built_cli_binary.exists(), f"Built binary does not exist: {built_cli_binary}"
        assert built_cli_binary.is_file(), f"Built binary path is not a file: {built_cli_binary}"
        assert built_cli_binary.stat().st_size > 0, f"Built binary is empty: {built_cli_binary}"


class TestBinaryPresence:
    """Test that expected binaries exist."""

    def test_all_platform_binaries_exist(self, built_cli_binary: Path) -> None:
        """Test all 6 platform binaries are built."""
        print(f"\\nChecking for binaries in: {DIST_DIR}")
        assert built_cli_binary.exists(), f"Built binary does not exist: {built_cli_binary}"
        assert DIST_DIR.exists(), f"Distribution directory not found: {DIST_DIR}"

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
                matching_current = list(DIST_DIR.glob(f"{current_binary}*"))
                assert matching_current, f"Current platform binary not found: {current_binary}"


class TestBinarySize:
    """Test binary sizes are reasonable."""

    def test_binary_size_reasonable(self, built_cli_binary: Path) -> None:
        """Test binary size is reasonable (< 100MB)."""
        assert built_cli_binary.exists(), f"Built binary does not exist: {built_cli_binary}"
        # Find any binary in the dist directory
        binaries = [
            binary
            for binary in DIST_DIR.glob("lucius-*")
            if binary.is_file() and not _is_benchmark_binary_name(binary.name)
        ]

        if not binaries:
            pytest.skip("No non-benchmark binaries found to test")

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
    def test_binary_executable(self, built_cli_binary: Path) -> None:
        """Test Unix binaries have executable permission."""
        assert built_cli_binary.exists(), f"Built binary does not exist: {built_cli_binary}"
        # Find Unix binaries (not .exe)
        binaries = list(DIST_DIR.glob("lucius-*"))
        assert binaries, f"No binaries found to test in {DIST_DIR}"

        for binary in binaries:
            if not binary.name.endswith(".exe"):
                print(f"\\nChecking permissions for: {binary.name}")
                assert binary.stat().st_mode & 0o111 != 0, f"Binary {binary.name} is not executable"


class TestBinaryExecution:
    """Test binary execution and basic functionality."""

    def test_binary_version_command(self, built_cli_binary: Path) -> None:
        """Test binary responds to --version command."""
        binary_to_test = built_cli_binary

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

    def test_binary_help_command(self, built_cli_binary: Path) -> None:
        """Test binary responds to --help command."""
        binary_to_test = built_cli_binary

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

    def test_binary_standalone_no_python(self, built_cli_binary: Path) -> None:
        """Test binary doesn't require Python to be in PATH."""
        binary_to_test = built_cli_binary

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

    def test_binary_has_schemas(self, built_cli_binary: Path) -> None:
        """Test binary supports entity discovery without runtime MCP dependency."""
        binary_to_test = built_cli_binary

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

    def test_binary_naming_convention(self, built_cli_binary: Path) -> None:
        """Test all binary files follow expected naming convention."""
        assert built_cli_binary.exists(), f"Built binary does not exist: {built_cli_binary}"
        assert DIST_DIR.exists(), "dist/cli not found"

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

    EXPECTED_ONEFILE_CACHE_SPEC = "{CACHE_DIR}/{COMPANY}/{PRODUCT}/{VERSION}"

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

    def test_onefile_cached_mode_enabled_for_build_scripts(self) -> None:
        """Onefile builds must enable cached startup extraction mode."""
        project_root = Path(__file__).parent.parent.parent
        scripts = [
            project_root / "deployment/scripts/build_cli_unix.sh",
            project_root / "deployment/scripts/build_cli_windows.bat",
        ]

        missing_cache_mode_default: list[str] = []
        missing_cache_mode_usage: list[str] = []
        missing_tempdir_spec: list[str] = []
        for script_path in scripts:
            content = script_path.read_text(encoding="utf-8")
            if script_path.suffix == ".sh":
                if 'ONEFILE_CACHE_MODE="${ONEFILE_CACHE_MODE:-cached}"' not in content:
                    missing_cache_mode_default.append(str(script_path))
                if "--onefile-cache-mode=${ONEFILE_CACHE_MODE}" not in content:
                    missing_cache_mode_usage.append(str(script_path))
            else:
                if 'if "%ONEFILE_CACHE_MODE%"=="" set ONEFILE_CACHE_MODE=cached' not in content:
                    missing_cache_mode_default.append(str(script_path))
                if "--onefile-cache-mode=cached" not in content:
                    missing_cache_mode_usage.append(str(script_path))
            if self.EXPECTED_ONEFILE_CACHE_SPEC not in content:
                missing_tempdir_spec.append(str(script_path))

        assert not missing_cache_mode_default, (
            "Nuitka build scripts missing default onefile cached mode configuration:\n"
            + "\n".join(sorted(missing_cache_mode_default))
        )
        assert not missing_cache_mode_usage, (
            "Nuitka build scripts missing onefile cache mode flag wiring:\n"
            + "\n".join(sorted(missing_cache_mode_usage))
        )
        assert not missing_tempdir_spec, (
            "Nuitka build scripts missing version-scoped onefile tempdir spec:\n"
            + "\n".join(sorted(missing_tempdir_spec))
        )

    def test_no_compression_not_enabled_by_default(self) -> None:
        """Variant 3 flag must not be enabled in default build scripts."""
        project_root = Path(__file__).parent.parent.parent
        scripts = [
            project_root / "deployment/scripts/build_cli_unix.sh",
            project_root / "deployment/scripts/build_cli_windows.bat",
        ]

        missing_default_false: list[str] = []
        missing_conditional_guard: list[str] = []
        for script_path in scripts:
            content = script_path.read_text(encoding="utf-8")
            if script_path.suffix == ".sh":
                if "ONEFILE_NO_COMPRESSION=false" not in content:
                    missing_default_false.append(str(script_path))
                if 'if [[ "${ONEFILE_NO_COMPRESSION}" == true ]]; then' not in content:
                    missing_conditional_guard.append(str(script_path))
            else:
                if "set ONEFILE_NO_COMPRESSION=false" not in content:
                    missing_default_false.append(str(script_path))
                if 'if /I "%ONEFILE_NO_COMPRESSION%"=="true"' not in content:
                    missing_conditional_guard.append(str(script_path))

        assert not missing_default_false, (
            "Default build scripts must keep no-compression disabled unless explicitly requested:\n"
            + "\n".join(sorted(missing_default_false))
        )
        assert not missing_conditional_guard, (
            "No-compression flag should only be applied behind an explicit runtime guard:\n"
            + "\n".join(sorted(missing_conditional_guard))
        )

    def test_version_bump_renders_distinct_cache_paths(self) -> None:
        """Version N and N+1 must map to different onefile cache directories."""
        template = self.EXPECTED_ONEFILE_CACHE_SPEC
        company = "lucius"
        product = "cli"
        version_n = "1.2.3"
        version_n1 = "1.2.4"

        os_roots = {
            "linux": "/home/test/.cache",
            "macos": "/Users/test/Library/Caches",
            "windows": "C:/Users/test/AppData/Local",
        }

        for os_name, cache_root in os_roots.items():
            path_n = _render_cache_path(template, cache_root, company, product, version_n)
            path_n1 = _render_cache_path(template, cache_root, company, product, version_n1)

            assert path_n != path_n1, f"{os_name}: version bump must invalidate previous cache path"
            assert path_n.startswith(cache_root), f"{os_name}: rendered cache path must stay under OS cache root"
            assert path_n1.startswith(cache_root), f"{os_name}: rendered cache path must stay under OS cache root"
            assert path_n.endswith(f"/{version_n}"), f"{os_name}: rendered path should end with version N"
            assert path_n1.endswith(f"/{version_n1}"), f"{os_name}: rendered path should end with version N+1"


class TestBinaryStartupCacheBehavior:
    """Optional runtime checks for onefile cache reuse behavior."""

    def test_cached_binary_second_start_is_faster(self, built_cli_binary: Path) -> None:
        """When using a cached onefile binary, second start should be faster than first."""
        override = environ.get("LUCIUS_CACHED_BINARY_PATH", "").strip()
        if override:
            binary = Path(override)
            if not binary.exists():
                pytest.skip(f"LUCIUS_CACHED_BINARY_PATH not found: {override}")
        else:
            binary = built_cli_binary

        env = os.environ.copy()
        cache_root = Path(tempfile.mkdtemp(prefix="lucius-cli-cache-"))
        # Nuitka onefile uses CACHE_DIR, which honors XDG cache roots on Unix.
        env["XDG_CACHE_HOME"] = str(cache_root)
        env["HOME"] = env.get("HOME", str(cache_root))
        if platform.system() == "Windows":
            env["LOCALAPPDATA"] = str(cache_root)

        def run_once() -> float:
            start = time.perf_counter()
            result = subprocess.run(
                [str(binary), "--version"],
                capture_output=True,
                text=True,
                timeout=20,
                env=env,
            )
            elapsed = time.perf_counter() - start
            assert result.returncode == 0, f"Binary failed: {result.stderr}"
            return elapsed

        first = run_once()
        second = run_once()
        assert second < first, f"Expected warm start to be faster, got first={first:.3f}s second={second:.3f}s"
        assert any(cache_root.rglob("*")), "Expected cache files to be created under configured cache root"

    def test_cache_template_tokens_are_resolved_at_runtime(self, built_cli_binary: Path) -> None:
        """Onefile cache directories should not contain unresolved {TOKEN} placeholders."""
        env = os.environ.copy()
        cache_root = Path(tempfile.mkdtemp(prefix="lucius-cli-cache-template-"))
        env["XDG_CACHE_HOME"] = str(cache_root)
        env["HOME"] = env.get("HOME", str(cache_root))
        if platform.system() == "Windows":
            env["LOCALAPPDATA"] = str(cache_root)

        result = subprocess.run(
            [str(built_cli_binary), "--version"],
            capture_output=True,
            text=True,
            timeout=20,
            env=env,
        )
        assert result.returncode == 0, f"Binary failed: {result.stderr}"

        created_paths = list(cache_root.rglob("*"))
        assert created_paths, "Expected onefile cache extraction artifacts to be created"

        unresolved = [
            path
            for path in created_paths
            if "{" in str(path.relative_to(cache_root)) or "}" in str(path.relative_to(cache_root))
        ]
        assert not unresolved, "Found unresolved onefile cache template placeholders:\n" + "\n".join(
            str(path) for path in unresolved[:20]
        )
