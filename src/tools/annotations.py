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


def validate_tool_annotation_coverage(tool_names: Set[str] | set[str]) -> None:
    policy_tool_names = set(TOOL_HINT_POLICY.keys())
    expected_tool_names = set(tool_names)

    missing_in_policy = expected_tool_names - policy_tool_names
    extra_in_policy = policy_tool_names - expected_tool_names

    if missing_in_policy or extra_in_policy:
        problems: list[str] = []
        if missing_in_policy:
            problems.append(f"missing in policy: {sorted(missing_in_policy)}")
        if extra_in_policy:
            problems.append(f"extra in policy: {sorted(extra_in_policy)}")
        raise ValueError("Tool annotation coverage mismatch: " + "; ".join(problems))


__all__ = [
    "ADDITIVE_IDEMPOTENT_TOOLS",
    "ADDITIVE_NON_IDEMPOTENT_TOOLS",
    "DESTRUCTIVE_IDEMPOTENT_TOOLS",
    "READ_ONLY_TOOLS",
    "TOOL_HINT_POLICY",
    "generate_tool_title",
    "get_tool_annotations",
    "validate_tool_annotation_coverage",
]
