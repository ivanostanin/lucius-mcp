import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT_PATH = Path("deployment/scripts/update_mcpb_hashes.py")


def _load_script_module():
    spec = importlib.util.spec_from_file_location("update_mcpb_hashes", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def test_update_mcpb_hashes_updates_all_mcpb_packages(tmp_path: Path) -> None:
    module = _load_script_module()
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    uv_content = b"uv bundle"
    python_content = b"python bundle"
    (dist_dir / "lucius-mcp-1.2.3-uv.mcpb").write_bytes(uv_content)
    (dist_dir / "lucius-mcp-1.2.3-python.mcpb").write_bytes(python_content)

    server_json = tmp_path / "server.json"
    server_json.write_text(
        json.dumps(
            {
                "packages": [
                    {
                        "registryType": "pypi",
                        "identifier": "lucius-mcp",
                    },
                    {
                        "registryType": "mcpb",
                        "identifier": "https://github.com/ivanostanin/lucius-mcp/releases/download/v1.2.3/lucius-mcp-1.2.3-uv.mcpb",
                        "fileSha256": "old",
                    },
                    {
                        "registryType": "mcpb",
                        "identifier": "lucius-mcp-1.2.3-python.mcpb",
                    },
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    updated = module.update_mcpb_hashes(server_json, dist_dir)

    assert updated == 2
    server = json.loads(server_json.read_text(encoding="utf-8"))
    assert server["packages"][1]["fileSha256"] == _sha256(uv_content)
    assert server["packages"][2]["fileSha256"] == _sha256(python_content)
    assert "fileSha256" not in server["packages"][0]


def test_update_mcpb_hashes_fails_when_bundle_is_missing(tmp_path: Path) -> None:
    module = _load_script_module()
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    server_json = tmp_path / "server.json"
    server_json.write_text(
        json.dumps(
            {
                "packages": [
                    {
                        "registryType": "mcpb",
                        "identifier": "https://github.com/ivanostanin/lucius-mcp/releases/download/v1.2.3/lucius-mcp-1.2.3-uv.mcpb",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match="Missing MCPB artifact"):
        module.update_mcpb_hashes(server_json, dist_dir)
