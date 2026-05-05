#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse


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


def update_mcpb_hashes(server_json_path: Path, dist_dir: Path) -> int:
    server = json.loads(server_json_path.read_text(encoding="utf-8"))
    packages = server.get("packages")
    if not isinstance(packages, list):
        raise ValueError("server.json must contain a packages array")

    updated = 0
    for package in packages:
        if not isinstance(package, dict) or package.get("registryType") != "mcpb":
            continue

        identifier = package.get("identifier")
        if not isinstance(identifier, str):
            raise ValueError("MCPB package must contain a string identifier")

        bundle_path = dist_dir / bundle_name_from_identifier(identifier)
        if not bundle_path.exists():
            raise FileNotFoundError(f"Missing MCPB artifact for {identifier}: {bundle_path}")

        package["fileSha256"] = sha256_file(bundle_path)
        updated += 1

    if updated == 0:
        raise ValueError("No MCPB packages found in server.json")

    server_json_path.write_text(json.dumps(server, indent=2) + "\n", encoding="utf-8")
    return updated


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Update MCPB fileSha256 values in server.json from local dist artifacts."
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    updated = update_mcpb_hashes(args.server_json, args.dist_dir)
    print(f"Updated {updated} MCPB package hash(es) in {args.server_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
