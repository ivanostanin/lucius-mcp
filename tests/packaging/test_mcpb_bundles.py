import json
import re
import zipfile
from pathlib import Path

import pytest

# Logic adapted from deployment/scripts/verify_mcpb_bundles.py


def get_project_version() -> str:
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


@pytest.fixture(scope="module")
def bundle_paths():
    version = get_project_version()
    dist_dir = Path("dist")
    return {
        "uv": dist_dir / f"lucius-mcp-{version}-uv.mcpb",
        "python": dist_dir / f"lucius-mcp-{version}-python.mcpb",
        "version": version,
    }


def verify_manifest(manifest, expected_type, expected_version):
    assert manifest.get("name") == "lucius-mcp"
    assert manifest.get("version") == expected_version

    server = manifest.get("server")
    assert isinstance(server, dict)
    assert server.get("type") == expected_type
    assert server.get("entry_point") == "src.main:start"

    mcp_config = server.get("mcp_config")
    assert isinstance(mcp_config, dict)

    if expected_type == "python":
        assert mcp_config.get("command") == "python"
        assert mcp_config.get("args") == ["-m", "src.main"]
        env = mcp_config.get("env")
        assert isinstance(env, dict)
        assert env.get("MCP_MODE") == "stdio"
        assert "${__dirname}" in env.get("PYTHONPATH", "")
        assert "server/lib" in env.get("PYTHONPATH", "")
    else:
        assert mcp_config.get("command") == "uv"
        assert mcp_config.get("args") == ["run", "start"]


def test_uv_bundle_contents(bundle_paths):
    path = bundle_paths["uv"]
    assert path.exists(), "UV bundle not found. Run mcpb build tests first."

    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        assert "manifest.json" in names
        assert "src/main.py" in names
        assert "pyproject.toml" in names

        manifest = json.loads(zf.read("manifest.json"))
        verify_manifest(manifest, "uv", bundle_paths["version"])


def test_python_bundle_contents(bundle_paths):
    path = bundle_paths["python"]
    assert path.exists(), "Python bundle not found. Run mcpb build tests first."

    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        assert "manifest.json" in names
        assert "src/main.py" in names

        # Python bundle should have vendored dependencies
        has_server_lib = any(name.startswith("server/lib/") for name in names)
        assert has_server_lib, "Python bundle missing server/lib/"

        manifest = json.loads(zf.read("manifest.json"))
        verify_manifest(manifest, "python", bundle_paths["version"])
