from __future__ import annotations

import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _version_from_pyproject() -> str:
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as pyproject_file:
        project_data = tomllib.load(pyproject_file)
    project_version = project_data.get("project", {}).get("version")
    if not isinstance(project_version, str) or not project_version.strip():
        raise RuntimeError("Could not resolve project version from pyproject.toml")
    return project_version.strip()


try:
    __version__ = version("lucius-mcp")
except PackageNotFoundError:
    __version__ = _version_from_pyproject()
