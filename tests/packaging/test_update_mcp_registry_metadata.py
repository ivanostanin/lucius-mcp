import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT_PATH = Path("deployment/scripts/update_mcp_registry_metadata.py")


def _load_script_module():
    spec = importlib.util.spec_from_file_location("update_mcp_registry_metadata", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def test_update_mcp_registry_metadata_updates_versions_and_mcpb_hashes(tmp_path: Path) -> None:
    module = _load_script_module()
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    uv_content = b"uv bundle"
    python_content = b"python bundle"
    (dist_dir / "lucius-mcp-1.2.4-uv.mcpb").write_bytes(uv_content)
    (dist_dir / "lucius-mcp-1.2.4-python.mcpb").write_bytes(python_content)

    server_json = tmp_path / "server.json"
    server_json.write_text(
        json.dumps(
            {
                "version": "1.2.3",
                "packages": [
                    {
                        "registryType": "pypi",
                        "identifier": "lucius-mcp",
                        "version": "1.2.3",
                    },
                    {
                        "registryType": "oci",
                        "identifier": "ghcr.io/ivanostanin/lucius-mcp:1.2.3",
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
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    updated = module.update_mcp_registry_metadata(server_json, dist_dir, "1.2.4")

    assert updated == 2
    server = json.loads(server_json.read_text(encoding="utf-8"))
    assert server["version"] == "1.2.4"
    assert server["packages"][0]["version"] == "1.2.4"
    assert "fileSha256" not in server["packages"][0]
    assert server["packages"][1]["identifier"] == "ghcr.io/ivanostanin/lucius-mcp:1.2.4"
    assert server["packages"][2]["identifier"] == (
        "https://github.com/ivanostanin/lucius-mcp/releases/download/v1.2.4/lucius-mcp-1.2.4-uv.mcpb"
    )
    assert server["packages"][2]["fileSha256"] == _sha256(uv_content)
    assert server["packages"][3]["identifier"] == "lucius-mcp-1.2.4-python.mcpb"
    assert server["packages"][3]["fileSha256"] == _sha256(python_content)


def test_update_mcp_registry_metadata_updates_github_release_tag_in_mcpb_urls(tmp_path: Path) -> None:
    module = _load_script_module()
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    bundle_content = b"uv bundle"
    (dist_dir / "lucius-mcp-1.2.4-uv.mcpb").write_bytes(bundle_content)
    server_json = tmp_path / "server.json"
    server_json.write_text(
        json.dumps(
            {
                "version": "1.2.3",
                "packages": [
                    {
                        "registryType": "mcpb",
                        "identifier": "https://github.com/ivanostanin/lucius-mcp/releases/download/v1.2.3/lucius-mcp-1.2.3-uv.mcpb",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    module.update_mcp_registry_metadata(server_json, dist_dir, "1.2.4")

    server = json.loads(server_json.read_text(encoding="utf-8"))
    assert server["packages"][0]["identifier"] == (
        "https://github.com/ivanostanin/lucius-mcp/releases/download/v1.2.4/lucius-mcp-1.2.4-uv.mcpb"
    )


def test_update_mcp_registry_metadata_fails_when_bundle_is_missing(tmp_path: Path) -> None:
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
        module.update_mcp_registry_metadata(server_json, dist_dir, "1.2.3")
