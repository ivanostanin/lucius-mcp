from collections.abc import Mapping

from src.main import mcp
from src.tools.annotations import (
    DESTRUCTIVE_IDEMPOTENT_TOOLS,
    TOOL_HINT_POLICY,
    generate_tool_title,
    validate_tool_annotation_coverage,
)


def _get_registered_tools() -> dict[str, object]:
    return dict(mcp._tool_manager._tools)


def _annotation_value(annotations: object, key: str) -> object:
    if isinstance(annotations, Mapping):
        return annotations.get(key)
    return getattr(annotations, key, None)


def test_annotation_policy_matches_registered_tools() -> None:
    registered_tool_names = set(_get_registered_tools().keys())
    policy_tool_names = set(TOOL_HINT_POLICY.keys())

    assert len(registered_tool_names) == 55
    assert registered_tool_names == policy_tool_names

    validate_tool_annotation_coverage(registered_tool_names)


def test_all_registered_tools_have_expected_annotations() -> None:
    tools = _get_registered_tools()

    for tool_name, tool in tools.items():
        annotations = getattr(tool, "annotations", None)
        expected = TOOL_HINT_POLICY[tool_name]

        assert annotations is not None, f"{tool_name} is missing annotations"
        assert _annotation_value(annotations, "title") == generate_tool_title(tool_name)
        assert _annotation_value(annotations, "readOnlyHint") == expected["readOnlyHint"]
        assert _annotation_value(annotations, "destructiveHint") == expected["destructiveHint"]
        assert _annotation_value(annotations, "idempotentHint") == expected["idempotentHint"]


def test_new_cleanup_and_suite_delete_tools_are_destructive_idempotent() -> None:
    newly_added_tools = {
        "delete_test_suite",
        "delete_archived_test_cases",
        "delete_archived_shared_steps",
        "delete_unused_custom_fields",
    }

    assert newly_added_tools.issubset(DESTRUCTIVE_IDEMPOTENT_TOOLS)

    for tool_name in newly_added_tools:
        hints = TOOL_HINT_POLICY[tool_name]
        assert hints["readOnlyHint"] is False
        assert hints["destructiveHint"] is True
        assert hints["idempotentHint"] is True
