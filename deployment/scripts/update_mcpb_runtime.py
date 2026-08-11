#!/usr/bin/env python3
"""Regenerate MCPB Python runtime declarations from package metadata."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[import-not-found, unused-ignore]


def read_pyproject_metadata(pyproject_path: Path) -> dict[str, object]:
    """Read a parsed pyproject file."""
    with pyproject_path.open("rb") as pyproject_file:
        metadata = tomllib.load(pyproject_file)
    if not isinstance(metadata, dict):
        raise RuntimeError("pyproject.toml must contain a TOML table")
    return metadata


def read_project_metadata(pyproject_path: Path) -> dict[str, object]:
    """Read the parsed ``[project]`` table from a pyproject file."""
    metadata = read_pyproject_metadata(pyproject_path)
    project = metadata.get("project")
    if not isinstance(project, dict):
        raise RuntimeError("Could not resolve [project] metadata from pyproject.toml")
    return project


def _read_non_empty_project_string(pyproject_path: Path, field: str) -> str:
    value = read_project_metadata(pyproject_path).get(field)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Could not resolve project.{field} from pyproject.toml")
    return value.strip()


def read_requires_python(pyproject_path: Path) -> str:
    """Read the non-empty project-level ``requires-python`` declaration."""
    return _read_non_empty_project_string(pyproject_path, "requires-python")


def read_project_version(pyproject_path: Path) -> str:
    """Read the non-empty project-level version declaration."""
    return _read_non_empty_project_string(pyproject_path, "version")


def update_manifest_runtime(manifest_path: Path, runtime_range: str) -> None:
    """Update a generated MCPB manifest with the package runtime range."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    compatibility = manifest.get("compatibility")
    if not isinstance(compatibility, dict):
        raise RuntimeError(f"{manifest_path} must contain a compatibility object")
    runtimes = compatibility.get("runtimes")
    if not isinstance(runtimes, dict):
        raise RuntimeError(f"{manifest_path} compatibility must contain a runtimes object")
    runtimes["python"] = runtime_range
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    runtime_range = read_requires_python(repo_root / "pyproject.toml")
    for server_type in ("uv", "python"):
        manifest_path = repo_root / "deployment" / "mcpb" / f"manifest.{server_type}.json"
        update_manifest_runtime(manifest_path, runtime_range)
        print(f"Updated {manifest_path.relative_to(repo_root)}: {runtime_range}")


if __name__ == "__main__":
    main()
