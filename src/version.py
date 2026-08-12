from __future__ import annotations

import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[import-not-found, unused-ignore]


def read_project_version(pyproject_path: Path) -> str:
    """Read the non-empty ``project.version`` from a static pyproject file."""
    with pyproject_path.open("rb") as pyproject_file:
        project_data = tomllib.load(pyproject_file)
    project = project_data.get("project")
    project_version = project.get("version") if isinstance(project, dict) else None
    if not isinstance(project_version, str) or not project_version.strip():
        raise RuntimeError("Could not resolve project version from pyproject.toml")
    return project_version.strip()


try:
    __version__ = version("lucius-mcp")
except PackageNotFoundError:
    __version__ = read_project_version(Path(__file__).resolve().parent.parent / "pyproject.toml")
