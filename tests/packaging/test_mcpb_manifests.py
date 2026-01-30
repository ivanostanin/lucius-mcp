import json
from pathlib import Path

import pytest


def get_manifest_path(server_type: str) -> Path:
    return Path("deployment/mcpb") / f"manifest.{server_type}.json"


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


def test_manifest_tools_match_code():
    # Import mcp instance from src.main to list registered tools
    import importlib.util

    spec = importlib.util.find_spec("src.main")
    if spec is None or spec.loader is None:
        pytest.skip("Could not find src.main")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "mcp"):
        pytest.skip("mcp instance not found in src.main")

    mcp_instance = module.mcp
    code_tools = set(mcp_instance._tool_manager._tools.keys())

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
