import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def build_artifacts():
    # Setup: Run uv build
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    uv_path = shutil.which("uv") or "uv"
    result = subprocess.run([uv_path, "build"], capture_output=True, text=True)  # noqa: S603
    assert result.returncode == 0, f"uv build failed: {result.stderr}"

    # Get version from pyproject.toml
    version = ""
    with open("pyproject.toml") as f:
        for line in f:
            if line.startswith("version = "):
                version = line.split("=")[1].strip().strip('"')
                break
    assert version, "Could not find version in pyproject.toml"

    wheel_file = dist_dir / f"lucius_mcp-{version}-py3-none-any.whl"
    sdist_file = dist_dir / f"lucius_mcp-{version}.tar.gz"

    return {"wheel": wheel_file, "sdist": sdist_file, "version": version}


def test_uv_build_success(build_artifacts):
    assert build_artifacts["wheel"].exists()
    assert build_artifacts["sdist"].exists()


def test_wheel_contents(build_artifacts):
    wheel_path = build_artifacts["wheel"]
    with zipfile.ZipFile(wheel_path, "r") as z:
        names = z.namelist()
        # Check for essential files
        # Hatchling puts code in the package directory
        assert any(name.startswith("src/") for name in names)
        assert any(name.endswith("METADATA") for name in names)


def test_sdist_contents(build_artifacts):
    sdist_path = build_artifacts["sdist"]
    version = build_artifacts["version"]
    with tarfile.open(sdist_path, "r:gz") as t:
        names = t.getnames()
        root = f"lucius_mcp-{version}"
        assert f"{root}/pyproject.toml" in names
        assert f"{root}/README.md" in names
        assert any(name.startswith(f"{root}/src/") for name in names)
