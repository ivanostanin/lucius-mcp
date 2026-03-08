import json
from pathlib import Path

import pytest

from src.tools import all_tools
from src.tools.annotations import TOOL_HINT_POLICY, TOOL_TAGS


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_manifest() -> dict[str, object]:
    manifest_path = _project_root() / "docs" / "mcp_manifest.json"
    assert manifest_path.exists(), f"Missing manifest: {manifest_path}"

    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert isinstance(raw, dict), "docs/mcp_manifest.json must be a JSON object"
    return raw


def _manifest_tools(manifest: dict[str, object]) -> list[dict[str, object]]:
    tools = manifest.get("tools")
    assert isinstance(tools, list), "manifest.tools must be a list"

    normalized: list[dict[str, object]] = []
    for index, tool in enumerate(tools):
        assert isinstance(tool, dict), f"manifest.tools[{index}] must be an object"
        normalized.append(tool)
    return normalized


def _validate_tool_identity(tool: dict[str, object], index: int) -> tuple[str | None, list[str]]:
    errors: list[str] = []

    tool_name = tool.get("name")
    if not isinstance(tool_name, str) or not tool_name.strip():
        errors.append(f"tools[{index}]: name must be a non-empty string")
        return None, errors

    title = tool.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append(f"{tool_name}: title must be a non-empty string")

    description = tool.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{tool_name}: description must be a non-empty string")

    return tool_name, errors


def _validate_tool_annotations(tool_name: str, tool: dict[str, object]) -> list[str]:
    errors: list[str] = []

    annotations = tool.get("annotations")
    if not isinstance(annotations, dict):
        return [f"{tool_name}: annotations must be an object"]

    annotation_title = annotations.get("title")
    if not isinstance(annotation_title, str) or not annotation_title.strip():
        errors.append(f"{tool_name}: annotations.title must be a non-empty string")

    read_only_hint = annotations.get("readOnlyHint")
    destructive_hint = annotations.get("destructiveHint")
    idempotent_hint = annotations.get("idempotentHint")
    if not isinstance(read_only_hint, bool):
        errors.append(f"{tool_name}: annotations.readOnlyHint must be bool")
    if not isinstance(destructive_hint, bool):
        errors.append(f"{tool_name}: annotations.destructiveHint must be bool")
    if not isinstance(idempotent_hint, bool):
        errors.append(f"{tool_name}: annotations.idempotentHint must be bool")

    expected_hints = TOOL_HINT_POLICY.get(tool_name)
    if expected_hints is None:
        errors.append(f"{tool_name}: missing hint policy entry")
        return errors

    if isinstance(read_only_hint, bool) and read_only_hint != expected_hints["readOnlyHint"]:
        errors.append(f"{tool_name}: readOnlyHint mismatch")
    if isinstance(destructive_hint, bool) and destructive_hint != expected_hints["destructiveHint"]:
        errors.append(f"{tool_name}: destructiveHint mismatch")
    if isinstance(idempotent_hint, bool) and idempotent_hint != expected_hints["idempotentHint"]:
        errors.append(f"{tool_name}: idempotentHint mismatch")

    return errors


def _validate_tool_tags(tool_name: str, tool: dict[str, object]) -> list[str]:
    errors: list[str] = []

    meta = tool.get("_meta")
    if not isinstance(meta, dict):
        return [f"{tool_name}: _meta must be an object"]

    fastmcp_meta = meta.get("fastmcp")
    if not isinstance(fastmcp_meta, dict):
        return [f"{tool_name}: _meta.fastmcp must be an object"]

    tags = fastmcp_meta.get("tags")
    if not isinstance(tags, list) or not tags:
        return [f"{tool_name}: _meta.fastmcp.tags must be a non-empty list"]

    if not all(isinstance(tag, str) and tag.strip() for tag in tags):
        errors.append(f"{tool_name}: _meta.fastmcp.tags must contain non-empty strings")

    expected_tags = TOOL_TAGS.get(tool_name)
    if expected_tags is None:
        errors.append(f"{tool_name}: missing tag policy entry")
        return errors

    parsed_tags = {tag for tag in tags if isinstance(tag, str) and tag.strip()}
    if parsed_tags != set(expected_tags):
        errors.append(f"{tool_name}: tags mismatch")

    return errors


def test_manifest_lists_all_registered_tools() -> None:
    manifest = _load_manifest()
    tools = _manifest_tools(manifest)

    manifest_tool_names = {tool["name"] for tool in tools if isinstance(tool.get("name"), str)}
    code_tool_names = {tool.__name__ for tool in all_tools}

    missing_in_manifest = sorted(code_tool_names - manifest_tool_names)
    extra_in_manifest = sorted(manifest_tool_names - code_tool_names)

    errors: list[str] = []
    if missing_in_manifest:
        errors.append(f"Missing tools in docs/mcp_manifest.json: {missing_in_manifest}")
    if extra_in_manifest:
        errors.append(f"Unknown tools in docs/mcp_manifest.json: {extra_in_manifest}")

    if errors:
        pytest.fail("Tool coverage mismatch:\n- " + "\n- ".join(errors))


def test_manifest_tools_have_title_description_annotations_and_tags() -> None:
    manifest = _load_manifest()
    tools = _manifest_tools(manifest)

    errors: list[str] = []

    for index, tool in enumerate(tools):
        tool_name, identity_errors = _validate_tool_identity(tool, index)
        errors.extend(identity_errors)
        if tool_name is None:
            continue

        errors.extend(_validate_tool_annotations(tool_name, tool))
        errors.extend(_validate_tool_tags(tool_name, tool))

    if errors:
        pytest.fail("Manifest metadata validation failed:\n- " + "\n- ".join(errors))
