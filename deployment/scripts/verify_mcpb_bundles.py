#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile


def read_project_version(pyproject_path: Path) -> str:
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def verify_manifest(
    manifest: dict[str, object],
    expected_type: str,
    expected_version: str,
    errors: list[str],
) -> None:
    expect(manifest.get("name") == "lucius-mcp", "manifest.name must be lucius-mcp", errors)
    expect(manifest.get("version") == expected_version, "manifest.version does not match pyproject.toml", errors)

    server = manifest.get("server")
    if not isinstance(server, dict):
        errors.append("manifest.server must be an object")
        return

    expect(server.get("type") == expected_type, f"server.type must be {expected_type}", errors)
    expect(server.get("entry_point") == "src.main:start", "server.entry_point must be src.main:start", errors)

    mcp_config = server.get("mcp_config")
    if not isinstance(mcp_config, dict):
        errors.append("server.mcp_config must be an object")
        return

    if expected_type == "python":
        expect(mcp_config.get("command") == "python", "python mcp_config.command must be python", errors)
        expect(mcp_config.get("args") == ["-m", "src.main"], "python mcp_config.args must be [-m, src.main]", errors)
        env = mcp_config.get("env")
        if isinstance(env, dict):
            expect(env.get("MCP_MODE") == "stdio", "python MCP_MODE must be stdio", errors)
            pythonpath = env.get("PYTHONPATH")
            expect(
                isinstance(pythonpath, str)
                and "${__dirname}" in pythonpath
                and "server/lib" in pythonpath,
                "python PYTHONPATH must include ${__dirname} and server/lib",
                errors,
            )
        else:
            errors.append("python mcp_config.env must be an object")
    else:
        expect(mcp_config.get("command") == "uv", "uv mcp_config.command must be uv", errors)
        expect(mcp_config.get("args") == ["run", "lucius-mcp"], "uv mcp_config.args must be [run, lucius-mcp]", errors)


def verify_python_bundle_contents(names: set[str], errors: list[str]) -> None:
    expect("src/main.py" in names, "python bundle must include src/main.py", errors)
    has_server_lib = any(name.startswith("server/lib/") for name in names)
    expect(has_server_lib, "python bundle must include server/lib/", errors)
    has_uvicorn = any(name.startswith("server/lib/uvicorn/") for name in names) or any(
        name.startswith("server/lib/uvicorn-") for name in names
    )
    expect(has_uvicorn, "python bundle must include uvicorn in server/lib", errors)


def verify_bundle(bundle_path: Path, expected_type: str, expected_version: str) -> list[str]:
    errors: list[str] = []
    with ZipFile(bundle_path) as zf:
        names = set(zf.namelist())
        if "manifest.json" not in names:
            return ["bundle missing manifest.json"]
        manifest = json.loads(zf.read("manifest.json"))
        verify_manifest(manifest, expected_type, expected_version, errors)
        if expected_type == "python":
            verify_python_bundle_contents(names, errors)
    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    dist_dir = repo_root / "dist"
    pyproject_path = repo_root / "pyproject.toml"

    if not dist_dir.exists():
        print(f"dist directory not found: {dist_dir}")
        return 1

    version = read_project_version(pyproject_path)
    expected = {
        "uv": dist_dir / f"lucius-mcp-{version}-uv.mcpb",
        "python": dist_dir / f"lucius-mcp-{version}-python.mcpb",
    }

    exit_code = 0
    for server_type, bundle_path in expected.items():
        if not bundle_path.exists():
            print(f"❌ Missing bundle: {bundle_path}")
            exit_code = 1
            continue

        errors = verify_bundle(bundle_path, server_type, version)
        if errors:
            exit_code = 1
            print(f"❌ {bundle_path.name} failed validation:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"✅ {bundle_path.name} passed validation")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
