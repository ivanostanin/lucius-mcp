import asyncio
import json
from pathlib import Path

import pytest

from deployment.scripts.update_mcpb_runtime import read_requires_python

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"


def get_manifest_path(server_type: str) -> Path:
    return PROJECT_ROOT / "deployment" / "mcpb" / f"manifest.{server_type}.json"


@pytest.mark.parametrize("server_type", ["uv", "python"])
def test_manifest_structure(server_type):
    manifest_path = get_manifest_path(server_type)
    assert manifest_path.exists(), f"{manifest_path} not found"

    with open(manifest_path) as f:
        manifest = json.load(f)

    required_fields = ["manifest_version", "name", "version", "server"]
    for field in required_fields:
        assert field in manifest, f"Missing required field: {field} in {server_type} manifest"

    assert manifest["name"] == "lucius-mcp"
    assert "entry_point" in manifest["server"]
    assert manifest["server"]["entry_point"] == "src.main:start"
    assert manifest["compatibility"]["runtimes"]["python"] == read_requires_python(PYPROJECT_PATH)


def test_manifest_tools_match_code():
    # Use the application's normal import path so its lazy imports are resolved
    # through Python's module cache before inspecting the registered tools.
    from src.main import mcp

    tools = asyncio.run(mcp.list_tools(run_middleware=False))
    code_tools = {tool.name for tool in tools}

    for server_type in ["uv", "python"]:
        manifest_path = get_manifest_path(server_type)
        with open(manifest_path) as f:
            manifest = json.load(f)

        manifest_tools = {t["name"] for t in manifest.get("tools", [])}

        missing_in_manifest = code_tools - manifest_tools
        missing_in_code = manifest_tools - code_tools

        assert not missing_in_code, f"Tools in {server_type} manifest but not in code: {missing_in_code}"
        assert not missing_in_manifest, f"Tools in code but not in {server_type} manifest: {missing_in_manifest}"


def test_uv_server_config():
    manifest_path = get_manifest_path("uv")
    with open(manifest_path) as f:
        manifest = json.load(f)

    server = manifest["server"]
    assert server["type"] == "uv"
    assert "mcp_config" in server
    assert server["mcp_config"]["command"] == "uv"
    assert server["mcp_config"]["args"] == ["run", "start"]


def test_python_server_config():
    manifest_path = get_manifest_path("python")
    with open(manifest_path) as f:
        manifest = json.load(f)

    server = manifest["server"]
    assert server["type"] == "python"
    assert "mcp_config" in server
    assert server["mcp_config"]["command"] == "python"
    assert server["mcp_config"]["args"] == ["-m", "src.main"]
    assert "env" in server["mcp_config"]
    assert server["mcp_config"]["env"]["MCP_MODE"] == "stdio"
