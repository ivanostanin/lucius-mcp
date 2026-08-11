#!/usr/bin/env python3
"""Regenerate MCPB Python runtime declarations from package metadata."""

from __future__ import annotations

import json
import re
from pathlib import Path

_REQUIRES_PYTHON = re.compile(r'^requires-python\s*=\s*"(?P<range>[^"]+)"\s*$', re.MULTILINE)


def read_requires_python(pyproject_path: Path) -> str:
    """Read the literal project-level ``requires-python`` declaration."""
    match = _REQUIRES_PYTHON.search(pyproject_path.read_text(encoding="utf-8"))
    if match is None or not (runtime_range := match.group("range").strip()):
        raise RuntimeError("Could not resolve requires-python from pyproject.toml")
    return runtime_range


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
