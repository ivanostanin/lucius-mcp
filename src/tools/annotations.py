from collections.abc import Set
from typing import Final

from mcp.types import ToolAnnotations

_TITLE_TOKEN_OVERRIDES: Final[dict[str, str]] = {
    "aql": "AQL",
    "api": "API",
    "cfv": "CFV",
    "id": "ID",
    "ids": "IDs",
    "mcp": "MCP",
}

READ_ONLY_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "get_custom_fields",
        "get_defect",
        "get_launch",
        "get_test_case_custom_fields",
        "get_test_case_details",
        "list_custom_field_values",
        "list_defect_matchers",
        "list_defect_test_cases",
        "list_defects",
        "list_integrations",
        "list_launches",
        "list_shared_steps",
        "list_test_cases",
        "list_test_layer_schemas",
        "list_test_layers",
        "list_test_plans",
        "list_test_suites",
        "search_test_cases",
    }
)

ADDITIVE_NON_IDEMPOTENT_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "create_custom_field_value",
        "create_defect",
        "create_defect_matcher",
        "create_launch",
        "create_shared_step",
        "create_test_case",
        "create_test_layer",
        "create_test_layer_schema",
        "create_test_plan",
        "create_test_suite",
        "link_shared_step",
    }
)

ADDITIVE_IDEMPOTENT_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "link_defect_to_test_case",
    }
)

DESTRUCTIVE_IDEMPOTENT_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "assign_test_cases_to_suite",
        "close_launch",
        "delete_archived_shared_steps",
        "delete_archived_test_cases",
        "delete_custom_field_value",
        "delete_defect",
        "delete_defect_matcher",
        "delete_launch",
        "delete_shared_step",
        "delete_test_case",
        "delete_test_layer",
        "delete_test_layer_schema",
        "delete_test_plan",
        "delete_test_suite",
        "delete_unused_custom_fields",
        "manage_test_plan_content",
        "reopen_launch",
        "unlink_shared_step",
        "update_custom_field_value",
        "update_defect",
        "update_defect_matcher",
        "update_shared_step",
        "update_test_case",
        "update_test_layer",
        "update_test_layer_schema",
        "update_test_plan",
    }
)


def _build_hint_policy() -> dict[str, dict[str, bool]]:
    policy: dict[str, dict[str, bool]] = {}

    for tool_name in READ_ONLY_TOOLS:
        policy[tool_name] = {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
        }

    for tool_name in ADDITIVE_NON_IDEMPOTENT_TOOLS:
        policy[tool_name] = {
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
        }

    for tool_name in ADDITIVE_IDEMPOTENT_TOOLS:
        policy[tool_name] = {
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
        }

    for tool_name in DESTRUCTIVE_IDEMPOTENT_TOOLS:
        policy[tool_name] = {
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
        }

    return policy


TOOL_HINT_POLICY: Final[dict[str, dict[str, bool]]] = _build_hint_policy()

TOOL_TAGS: Final[dict[str, frozenset[str]]] = {
    "assign_test_cases_to_suite": frozenset({"test-case", "test-suite"}),
    "close_launch": frozenset({"launch"}),
    "create_custom_field_value": frozenset({"custom-field", "custom-field-value"}),
    "create_defect": frozenset({"defect"}),
    "create_defect_matcher": frozenset({"defect", "defect-matcher"}),
    "create_launch": frozenset({"launch"}),
    "create_shared_step": frozenset({"shared-step"}),
    "create_test_case": frozenset({"test-case"}),
    "create_test_layer": frozenset({"test-layer"}),
    "create_test_layer_schema": frozenset({"test-layer", "test-layer-schema"}),
    "create_test_plan": frozenset({"test-plan"}),
    "create_test_suite": frozenset({"test-suite"}),
    "delete_archived_shared_steps": frozenset({"shared-step"}),
    "delete_archived_test_cases": frozenset({"test-case"}),
    "delete_custom_field_value": frozenset({"custom-field", "custom-field-value"}),
    "delete_defect": frozenset({"defect"}),
    "delete_defect_matcher": frozenset({"defect", "defect-matcher"}),
    "delete_launch": frozenset({"launch"}),
    "delete_shared_step": frozenset({"shared-step"}),
    "delete_test_case": frozenset({"test-case"}),
    "delete_test_layer": frozenset({"test-layer"}),
    "delete_test_layer_schema": frozenset({"test-layer", "test-layer-schema"}),
    "delete_test_plan": frozenset({"test-plan"}),
    "delete_test_suite": frozenset({"test-suite"}),
    "delete_unused_custom_fields": frozenset({"custom-field", "test-case"}),
    "get_custom_fields": frozenset({"custom-field"}),
    "get_defect": frozenset({"defect"}),
    "get_launch": frozenset({"launch"}),
    "get_test_case_custom_fields": frozenset({"custom-field", "test-case"}),
    "get_test_case_details": frozenset({"test-case"}),
    "link_defect_to_test_case": frozenset({"defect", "integration", "test-case"}),
    "link_shared_step": frozenset({"shared-step", "test-case"}),
    "list_custom_field_values": frozenset({"custom-field", "custom-field-value"}),
    "list_defect_matchers": frozenset({"defect", "defect-matcher"}),
    "list_defect_test_cases": frozenset({"defect", "test-case"}),
    "list_defects": frozenset({"defect"}),
    "list_integrations": frozenset({"integration"}),
    "list_launches": frozenset({"launch"}),
    "list_shared_steps": frozenset({"shared-step"}),
    "list_test_cases": frozenset({"test-case"}),
    "list_test_layer_schemas": frozenset({"test-layer", "test-layer-schema"}),
    "list_test_layers": frozenset({"test-layer"}),
    "list_test_plans": frozenset({"test-plan"}),
    "list_test_suites": frozenset({"test-suite"}),
    "manage_test_plan_content": frozenset({"test-case", "test-plan"}),
    "reopen_launch": frozenset({"launch"}),
    "search_test_cases": frozenset({"test-case"}),
    "unlink_shared_step": frozenset({"shared-step", "test-case"}),
    "update_custom_field_value": frozenset({"custom-field", "custom-field-value"}),
    "update_defect": frozenset({"defect"}),
    "update_defect_matcher": frozenset({"defect", "defect-matcher"}),
    "update_shared_step": frozenset({"shared-step"}),
    "update_test_case": frozenset({"test-case"}),
    "update_test_layer": frozenset({"test-layer"}),
    "update_test_layer_schema": frozenset({"test-layer", "test-layer-schema"}),
    "update_test_plan": frozenset({"test-plan"}),
}


def generate_tool_title(tool_name: str) -> str:
    words = tool_name.split("_")
    rendered_words = [_TITLE_TOKEN_OVERRIDES.get(word, word.capitalize()) for word in words if word]
    return " ".join(rendered_words)


def get_tool_annotations(tool_name: str) -> ToolAnnotations:
    hints = TOOL_HINT_POLICY.get(tool_name)
    if hints is None:
        raise KeyError(f"No annotation policy defined for tool '{tool_name}'")

    return ToolAnnotations(
        title=generate_tool_title(tool_name),
        readOnlyHint=hints["readOnlyHint"],
        destructiveHint=hints["destructiveHint"],
        idempotentHint=hints["idempotentHint"],
    )


def get_tool_tags(tool_name: str) -> set[str]:
    tags = TOOL_TAGS.get(tool_name)
    if tags is None:
        raise KeyError(f"No tags defined for tool '{tool_name}'")
    return set(tags)


def validate_tool_annotation_coverage(tool_names: Set[str] | set[str]) -> None:
    expected_tool_names = set(tool_names)
    problems: list[str] = []

    for source_name, source_tool_names in (
        ("hint policy", set(TOOL_HINT_POLICY.keys())),
        ("tag policy", set(TOOL_TAGS.keys())),
    ):
        missing_in_source = expected_tool_names - source_tool_names
        extra_in_source = source_tool_names - expected_tool_names

        if missing_in_source:
            problems.append(f"missing in {source_name}: {sorted(missing_in_source)}")
        if extra_in_source:
            problems.append(f"extra in {source_name}: {sorted(extra_in_source)}")

    if problems:
        raise ValueError("Tool annotation coverage mismatch: " + "; ".join(problems))


__all__ = [
    "ADDITIVE_IDEMPOTENT_TOOLS",
    "ADDITIVE_NON_IDEMPOTENT_TOOLS",
    "DESTRUCTIVE_IDEMPOTENT_TOOLS",
    "READ_ONLY_TOOLS",
    "TOOL_HINT_POLICY",
    "TOOL_TAGS",
    "generate_tool_title",
    "get_tool_annotations",
    "get_tool_tags",
    "validate_tool_annotation_coverage",
]
