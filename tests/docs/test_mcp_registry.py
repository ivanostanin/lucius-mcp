import json
import re
import tomllib
from pathlib import Path

MCP_REGISTRY_NAME = "io.github.ivanostanin/lucius-mcp"
PYPI_PACKAGE = "lucius-mcp"
GITHUB_RELEASE_BASE_URL = "https://github.com/ivanostanin/lucius-mcp/releases/download"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_server_json() -> dict[str, object]:
    path = _project_root() / "server.json"
    assert path.exists(), "server.json is required for MCP Registry publishing"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "server.json must contain a JSON object"
    return data


def _load_pyproject() -> dict[str, object]:
    path = _project_root() / "pyproject.toml"
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _packages_by_type(packages: object, registry_type: str) -> list[dict[str, object]]:
    assert isinstance(packages, list)
    return [
        package for package in packages if isinstance(package, dict) and package.get("registryType") == registry_type
    ]


def test_server_json_matches_pypi_package_metadata() -> None:
    server = _load_server_json()
    pyproject = _load_pyproject()
    project = pyproject["project"]

    assert server["$schema"] == "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
    assert server["name"] == MCP_REGISTRY_NAME
    assert server["version"] == project["version"]
    assert project["name"] == PYPI_PACKAGE

    pypi_packages = _packages_by_type(server["packages"], "pypi")
    assert len(pypi_packages) == 1

    pypi_package = pypi_packages[0]
    assert pypi_package["identifier"] == PYPI_PACKAGE
    assert pypi_package["version"] == project["version"]
    assert pypi_package["transport"] == {"type": "stdio"}


def test_server_json_lists_all_supported_package_types() -> None:
    server = _load_server_json()
    package_types = [package["registryType"] for package in server["packages"] if isinstance(package, dict)]
    assert package_types.count("pypi") == 1
    assert package_types.count("oci") == 1
    assert package_types.count("mcpb") == 2


def test_server_json_docker_package_matches_registry_verification_label() -> None:
    server = _load_server_json()
    version = str(server["version"])
    oci_packages = _packages_by_type(server["packages"], "oci")
    assert len(oci_packages) == 1
    assert oci_packages[0]["identifier"] == f"ghcr.io/ivanostanin/lucius-mcp:{version}"
    assert oci_packages[0]["transport"] == {"type": "stdio"}

    dockerfile = (_project_root() / "deployment" / "Dockerfile").read_text(encoding="utf-8")
    assert f'LABEL io.modelcontextprotocol.server.name="{MCP_REGISTRY_NAME}"' in dockerfile


def test_server_json_mcpb_packages_point_to_release_assets_with_hashes() -> None:
    server = _load_server_json()
    version = str(server["version"])
    mcpb_packages = _packages_by_type(server["packages"], "mcpb")
    assert len(mcpb_packages) == 2

    expected_identifiers = {
        f"{GITHUB_RELEASE_BASE_URL}/v{version}/lucius-mcp-{version}-uv.mcpb",
        f"{GITHUB_RELEASE_BASE_URL}/v{version}/lucius-mcp-{version}-python.mcpb",
    }
    assert {str(package["identifier"]) for package in mcpb_packages} == expected_identifiers

    for package in mcpb_packages:
        assert package["transport"] == {"type": "stdio"}
        assert re.fullmatch(r"^[a-f0-9]{64}$", str(package["fileSha256"]))


def test_pypi_readme_contains_registry_ownership_marker() -> None:
    readme = (_project_root() / "README.md").read_text(encoding="utf-8")
    assert f"mcp-name: {MCP_REGISTRY_NAME}" in readme


def test_package_exposes_registry_friendly_server_entrypoint() -> None:
    pyproject = _load_pyproject()
    scripts = pyproject["project"]["scripts"]

    assert scripts["lucius-mcp"] == "src.main:start"
    assert scripts["start"] == "src.main:start"


def test_release_workflow_publishes_to_mcp_registry_after_pypi() -> None:
    workflow = (_project_root() / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "pypa/gh-action-pypi-publish" in workflow
    assert "needs: [pypi-publish, docker-build, github-release]" in workflow
    assert re.search(r"^\s+MCP_PUBLISHER_VERSION: v\d+\.\d+\.\d+\s*$", workflow, re.MULTILINE)
    assert "modelcontextprotocol/registry/releases/latest/download" not in workflow
    assert "modelcontextprotocol/registry/releases/download/${MCP_PUBLISHER_VERSION}/" in workflow
    assert "mcp-publisher login github-oidc" in workflow
    assert "mcp-publisher publish" in workflow

    pypi_index = workflow.index("pypa/gh-action-pypi-publish")
    registry_job_index = workflow.index("mcp-registry-publish:")
    login_index = workflow.index("mcp-publisher login github-oidc")
    publish_index = workflow.index("mcp-publisher publish")
    assert pypi_index < registry_job_index < login_index < publish_index


def test_server_json_description_stays_registry_friendly() -> None:
    server = _load_server_json()

    description = server["description"]
    assert isinstance(description, str)
    assert 1 <= len(description) <= 100
    assert re.fullmatch(r"^[a-zA-Z0-9.-]+/[a-zA-Z0-9._-]+$", str(server["name"]))
