import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from deployment.scripts.update_mcpb_runtime import read_project_version, read_requires_python

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
VERIFY_BUNDLES_SCRIPT = PROJECT_ROOT / "deployment" / "scripts" / "verify_mcpb_bundles.py"


def get_project_version() -> str:
    return read_project_version(PYPROJECT_PATH)


@pytest.fixture(scope="module")
def bundle_paths():
    version = get_project_version()
    dist_dir = PROJECT_ROOT / "dist"
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
    assert manifest["compatibility"]["runtimes"]["python"] == read_requires_python(PYPROJECT_PATH)

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
    if not path.exists():
        pytest.skip("Python bundle not found in this environment.")

    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        assert "manifest.json" in names
        assert "src/main.py" in names

        # Python bundle should have vendored dependencies
        has_server_lib = any(name.startswith("server/lib/") for name in names)
        assert has_server_lib, "Python bundle missing server/lib/"

        manifest = json.loads(zf.read("manifest.json"))
        verify_manifest(manifest, "python", bundle_paths["version"])


def test_bundle_verifier_runs_outside_repository(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(VERIFY_BUNDLES_SCRIPT)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
