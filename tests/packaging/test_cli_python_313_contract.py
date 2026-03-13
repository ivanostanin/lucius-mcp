"""Regression checks for Python 3.13 compatibility contract in CLI build flow."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "cli-build.yml"
BUILD_ALL_SCRIPT = PROJECT_ROOT / "deployment" / "scripts" / "build_all_cli.sh"
CLI_BUILD_SCRIPTS = [
    PROJECT_ROOT / "deployment" / "scripts" / "build_cli_unix.sh",
    PROJECT_ROOT / "deployment" / "scripts" / "build_cli_windows.bat",
]


def test_packaging_metadata_and_tooling_targets_python_313() -> None:
    with PYPROJECT_PATH.open("rb") as fh:
        pyproject = tomllib.load(fh)

    project = pyproject["project"]
    assert project["requires-python"] == ">=3.13"

    classifiers = set(project["classifiers"])
    assert "Programming Language :: Python :: 3.13" in classifiers
    assert "Programming Language :: Python :: 3.14" in classifiers

    assert pyproject["tool"]["ruff"]["target-version"] == "py313"
    assert pyproject["tool"]["mypy"]["python_version"] == "3.13"


def test_cli_build_workflow_remains_pinned_to_python_313() -> None:
    content = WORKFLOW_PATH.read_text(encoding="utf-8")
    python_version_lines = re.findall(r"python-version:\s*'([^']+)'", content)
    assert python_version_lines
    assert set(python_version_lines) == {"${{ env.CLI_BUILD_PYTHON_VERSION }}"}
    assert "CLI_BUILD_PYTHON_VERSION: '3.13'" in content
    assert "path: dist/cli/${{ matrix.artifact_name }}" in content
    for artifact_name in {
        "lucius-linux-arm64",
        "lucius-linux-x86_64",
        "lucius-macos-arm64",
        "lucius-macos-x86_64",
        "lucius-windows-arm64.exe",
        "lucius-windows-x86_64.exe",
    }:
        assert f"artifact_name: {artifact_name}" in content


def test_cli_build_scripts_require_python_313() -> None:
    missing_version_pin: list[str] = []

    for script_path in CLI_BUILD_SCRIPTS:
        content = script_path.read_text(encoding="utf-8")
        if "--python 3.13" not in content:
            missing_version_pin.append(script_path.name)

    assert not missing_version_pin, f"Missing --python 3.13 pin in: {missing_version_pin}"


def test_master_build_script_enforces_python_313_requirement() -> None:
    content = BUILD_ALL_SCRIPT.read_text(encoding="utf-8")
    assert "uv python find 3.13" in content
    assert "Python 3.13 is required" in content
    # Current implementation may orchestrate either canonical cross-platform scripts
    # or explicit per-platform build scripts.
    assert (
        "build_cli_unix.sh" in content
        or "build_cli_linux_arm64.sh" in content
        or "build_cli_linux_x86_64.sh" in content
    )
    assert (
        "build_cli_windows.bat" in content
        or "build_cli_windows_arm64.bat" in content
        or "build_cli_windows_x86_64.bat" in content
    )


def test_build_scripts_preserve_existing_cli_binaries_by_default() -> None:
    for script_path in CLI_BUILD_SCRIPTS:
        content = script_path.read_text(encoding="utf-8")
        assert not re.search(r"^\s*rm -rf dist/cli\s*$", content, flags=re.MULTILINE)
        assert not re.search(r"^\s*rmdir /s /q dist\\cli\s*$", content, flags=re.MULTILINE)

    master_content = BUILD_ALL_SCRIPT.read_text(encoding="utf-8")
    assert "CLEAN_CLI_DIST" in master_content
    assert "dist/cli" in master_content
