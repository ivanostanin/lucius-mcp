#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tomllib
from pathlib import Path
from urllib.parse import urlparse, urlunparse

MCPB_BUNDLE_NAME_PATTERN = re.compile(
    r"^(?P<prefix>.+-)(?P<version>\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)-(?P<variant>.+\.mcpb)$"
)
VERSION_PATH_SEGMENT_PATTERN = re.compile(r"^v?\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bundle_name_from_identifier(identifier: str) -> str:
    parsed = urlparse(identifier)
    name = Path(parsed.path).name if parsed.scheme else Path(identifier).name
    if not name.endswith(".mcpb"):
        raise ValueError(f"MCPB identifier does not point to a .mcpb artifact: {identifier}")
    return name


def read_project_version(pyproject_path: Path) -> str:
    project = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))["project"]
    version = project["version"]
    if not isinstance(version, str):
        raise ValueError("pyproject.toml project.version must be a string")
    return version


def bundle_name_for_version(identifier: str, version: str) -> str:
    name = bundle_name_from_identifier(identifier)
    match = MCPB_BUNDLE_NAME_PATTERN.fullmatch(name)
    if match is None:
        raise ValueError(f"MCPB artifact name does not contain a replaceable semver version: {name}")
    return f"{match.group('prefix')}{version}-{match.group('variant')}"


def path_segment_for_version(segment: str, version: str) -> str:
    if VERSION_PATH_SEGMENT_PATTERN.fullmatch(segment) is None:
        return segment
    return f"v{version}" if segment.startswith("v") else version


def mcpb_identifier_for_version(identifier: str, version: str) -> str:
    parsed = urlparse(identifier)
    name = bundle_name_for_version(identifier, version)
    if not parsed.scheme:
        return name

    path_parts = parsed.path.split("/")
    path_parts = [path_segment_for_version(part, version) for part in path_parts]
    path = str(Path("/".join(path_parts)).with_name(name))
    return urlunparse(parsed._replace(path=path))


def oci_identifier_for_version(identifier: str, version: str) -> str:
    last_path_part = identifier.rsplit("/", maxsplit=1)[-1]
    if ":" not in last_path_part:
        raise ValueError(f"OCI identifier does not contain a tag to replace: {identifier}")
    image_without_tag = identifier.rsplit(":", maxsplit=1)[0]
    return f"{image_without_tag}:{version}"


def update_package_metadata(package: dict[str, object], dist_dir: Path, version: str) -> int:
    registry_type = package.get("registryType")
    if registry_type == "pypi":
        package["version"] = version
        return 0

    identifier = package.get("identifier")
    if registry_type == "oci":
        if not isinstance(identifier, str):
            raise ValueError("OCI package must contain a string identifier")
        package["identifier"] = oci_identifier_for_version(identifier, version)
        return 0

    if registry_type != "mcpb":
        return 0

    if not isinstance(identifier, str):
        raise ValueError("MCPB package must contain a string identifier")

    package["identifier"] = mcpb_identifier_for_version(identifier, version)
    bundle_path = dist_dir / bundle_name_from_identifier(package["identifier"])
    if not bundle_path.exists():
        raise FileNotFoundError(f"Missing MCPB artifact for {package['identifier']}: {bundle_path}")

    package["fileSha256"] = sha256_file(bundle_path)
    return 1


def update_mcp_registry_metadata(server_json_path: Path, dist_dir: Path, version: str) -> int:
    server = json.loads(server_json_path.read_text(encoding="utf-8"))
    packages = server.get("packages")
    if not isinstance(packages, list):
        raise ValueError("server.json must contain a packages array")

    server["version"] = version

    updated = 0
    for package in packages:
        if not isinstance(package, dict):
            continue
        updated += update_package_metadata(package, dist_dir, version)

    if updated == 0:
        raise ValueError("No MCPB packages found in server.json")

    server_json_path.write_text(json.dumps(server, indent=2) + "\n", encoding="utf-8")
    return updated


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Update server.json release metadata and MCPB fileSha256 values from local release artifacts."
    )
    parser.add_argument(
        "--server-json",
        type=Path,
        default=repo_root / "server.json",
        help="Path to server.json. Defaults to the repository root server.json.",
    )
    parser.add_argument(
        "--dist-dir",
        type=Path,
        default=repo_root / "dist",
        help="Directory containing built .mcpb artifacts. Defaults to the repository root dist directory.",
    )
    parser.add_argument(
        "--pyproject",
        type=Path,
        default=repo_root / "pyproject.toml",
        help="Path to pyproject.toml. Defaults to the repository root pyproject.toml.",
    )
    parser.add_argument(
        "--version",
        help="Release version to write. Defaults to project.version from pyproject.toml.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    version = args.version or read_project_version(args.pyproject)
    updated = update_mcp_registry_metadata(args.server_json, args.dist_dir, version)
    print(f"Updated {args.server_json} to version {version} with {updated} MCPB package hash(es)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
