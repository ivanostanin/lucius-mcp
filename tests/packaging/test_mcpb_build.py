import shutil
import subprocess
from pathlib import Path

import pytest


def is_mcpb_installed():
    return shutil.which("mcpb") is not None


@pytest.fixture(scope="module")
def mcpb_build_artifacts():
    if not is_mcpb_installed():
        pytest.skip("mcpb CLI not found")

    # Run deployment/scripts/build-mcpb.sh
    # It assumes it's run from repo root
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "deployment/scripts/build-mcpb.sh"

    # Clean dist before running
    dist_dir = repo_root / "dist"
    # Note: we might have artifacts from test_python_build.py, but build-mcpb.sh cleans dist/*.mcpb

    bash_path = shutil.which("bash") or "/bin/bash"
    result = subprocess.run([bash_path, str(script_path)], capture_output=True, text=True, cwd=str(repo_root))  # noqa: S603

    assert result.returncode == 0, f"build-mcpb.sh failed: {result.stdout}\n{result.stderr}"

    # Get version from pyproject.toml
    version = ""
    with open(repo_root / "pyproject.toml") as f:
        for line in f:
            if line.startswith("version = "):
                version = line.split("=")[1].strip().strip('"')
                break

    uv_bundle = dist_dir / f"lucius-mcp-{version}-uv.mcpb"
    python_bundle = dist_dir / f"lucius-mcp-{version}-python.mcpb"

    return {"uv": uv_bundle, "python": python_bundle, "version": version}


def test_mcpb_build_success(mcpb_build_artifacts):
    assert mcpb_build_artifacts["uv"].exists()
    assert mcpb_build_artifacts["python"].exists()


def test_mcpb_bundle_files(mcpb_build_artifacts):
    # Just check they are non-empty
    assert mcpb_build_artifacts["uv"].stat().st_size > 0
    assert mcpb_build_artifacts["python"].stat().st_size > 0
