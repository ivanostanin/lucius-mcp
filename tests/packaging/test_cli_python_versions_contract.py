"""Regression checks for the supported Python runtime and CLI build contract."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
CLI_BUILD_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "cli-build.yml"
RELEASE_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "release.yml"
CLI_REUSABLE_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "_cli_build_test.yml"
CLI_ARTIFACT_ACTION_PATH = PROJECT_ROOT / ".github" / "actions" / "resolve-cli-artifact-name" / "action.yml"
BUILD_ALL_SCRIPT = PROJECT_ROOT / "deployment" / "scripts" / "build_all_cli.sh"
CLI_BUILD_SCRIPTS = [
    PROJECT_ROOT / "deployment" / "scripts" / "build_cli_unix.sh",
    PROJECT_ROOT / "deployment" / "scripts" / "build_cli_windows.bat",
]


SUPPORTED_PYTHONS = ("3.10", "3.11", "3.12", "3.13", "3.14")


def test_packaging_metadata_and_tooling_targets_supported_runtime_range() -> None:
    pyproject = PYPROJECT_PATH.read_text(encoding="utf-8")

    assert 'requires-python = ">=3.10,<3.15"' in pyproject
    for python_version in SUPPORTED_PYTHONS:
        assert f'"Programming Language :: Python :: {python_version}"' in pyproject
    assert 'target-version = "py310"' in pyproject
    assert 'python_version = "3.10"' in pyproject


def test_cli_build_workflow_uses_the_caller_selected_python_version() -> None:
    reusable_content = CLI_REUSABLE_WORKFLOW_PATH.read_text(encoding="utf-8")
    cli_build_content = CLI_BUILD_WORKFLOW_PATH.read_text(encoding="utf-8")
    release_content = RELEASE_WORKFLOW_PATH.read_text(encoding="utf-8")
    artifact_action_content = CLI_ARTIFACT_ACTION_PATH.read_text(encoding="utf-8")

    assert "default: '3.14'" in reusable_content
    python_version_lines = re.findall(r"python-version:\s*'([^']+)'", reusable_content)
    assert python_version_lines
    assert set(python_version_lines) == {"${{ env.CLI_BUILD_PYTHON_VERSION }}"}
    assert "CLI_BUILD_PYTHON_VERSION: ${{ inputs.python-version }}" in reusable_content
    assert "uses: ./.github/actions/resolve-cli-artifact-name" in reusable_content
    assert "name: ${{ steps.artifact.outputs.artifact_name }}" in reusable_content
    assert "path: dist/cli/${{ steps.artifact.outputs.artifact_name }}" in reusable_content
    assert 'binary_ext: ".exe"' in reusable_content
    assert "binary-ext: '${{ matrix.binary_ext }}'" in reusable_content

    assert "uses: ./.github/workflows/_cli_build_test.yml" in cli_build_content
    assert "python-version: ${{ vars.PYTHON_VERSION }}" in cli_build_content
    assert ".github/actions/resolve-cli-artifact-name/**" in cli_build_content

    assert "uses: ./.github/workflows/_cli_build_test.yml" in release_content
    assert "python-version: ${{ vars.PYTHON_VERSION }}" in release_content

    assert "from src.version import __version__; print(__version__)" in artifact_action_content
    assert (
        'artifactName = "lucius-$cliVersion-${{ inputs.platform }}-${{ inputs.arch }}${{ inputs.binary-ext }}"'
        in artifact_action_content
    )


def test_cli_build_scripts_use_the_selected_python_version() -> None:
    for script_path in CLI_BUILD_SCRIPTS:
        content = script_path.read_text(encoding="utf-8")
        assert (
            'CLI_BUILD_PYTHON_VERSION="${CLI_BUILD_PYTHON_VERSION:-3.14}"' in content
            or "set CLI_BUILD_PYTHON_VERSION=3.14" in content
        )
        assert '--python "${CLI_BUILD_PYTHON_VERSION}"' in content or "--python %CLI_BUILD_PYTHON_VERSION%" in content


def test_master_build_script_accepts_a_selected_supported_python_version() -> None:
    content = BUILD_ALL_SCRIPT.read_text(encoding="utf-8")
    assert 'REQUIRED_PYTHON="${CLI_BUILD_PYTHON_VERSION:-3.14}"' in content
    assert 'uv python find "${REQUIRED_PYTHON}"' in content
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
    assert "dist/cli" in master_content
