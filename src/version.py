from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Protocol

    class _TomlModule(Protocol):
        def load(self, file: object, /) -> dict[str, Any]: ...

    tomllib: _TomlModule
else:
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib


def read_project_version(pyproject_path: Path) -> str:
    """Read the non-empty ``project.version`` from a static pyproject file."""
    with pyproject_path.open("rb") as pyproject_file:
        project_data = tomllib.load(pyproject_file)
    project = project_data.get("project", {})
    project_version = project.get("version") if isinstance(project, dict) else None
    if not isinstance(project_version, str) or not project_version.strip():
        raise RuntimeError("Could not resolve project version from pyproject.toml")
    return project_version.strip()


def _version_from_pyproject() -> str:
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    return read_project_version(pyproject_path)


try:
    __version__ = version("lucius-mcp")
except PackageNotFoundError:
    __version__ = _version_from_pyproject()
