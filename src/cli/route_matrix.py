"""
Canonical CLI entity/action routing matrix and aliases.
"""

from __future__ import annotations

from collections.abc import Iterable

# Canonical entity/action -> existing tool function name.
CANONICAL_ROUTE_MATRIX: dict[str, dict[str, str]] = {
    "test_case": {
        "create": "create_test_case",
        "get": "get_test_case_details",
        "update": "update_test_case",
        "delete": "delete_test_case",
        "delete_archived": "delete_archived_test_cases",
        "list": "list_test_cases",
        "search": "search_test_cases",
        "get_custom_fields": "get_test_case_custom_fields",
    },
    "custom_field": {
        "get": "get_custom_fields",
        "delete_unused": "delete_unused_custom_fields",
    },
    "custom_field_value": {
        "list": "list_custom_field_values",
        "create": "create_custom_field_value",
        "update": "update_custom_field_value",
        "delete": "delete_custom_field_value",
    },
    "launch": {
        "create": "create_launch",
        "list": "list_launches",
        "get": "get_launch",
        "delete": "delete_launch",
        "close": "close_launch",
        "reopen": "reopen_launch",
    },
    "integration": {
        "list": "list_integrations",
    },
    "shared_step": {
        "create": "create_shared_step",
        "list": "list_shared_steps",
        "update": "update_shared_step",
        "delete": "delete_shared_step",
        "delete_archived": "delete_archived_shared_steps",
        "link_test_case": "link_shared_step",
        "unlink_test_case": "unlink_shared_step",
    },
    "test_layer": {
        "list": "list_test_layers",
        "create": "create_test_layer",
        "update": "update_test_layer",
        "delete": "delete_test_layer",
    },
    "test_layer_schema": {
        "list": "list_test_layer_schemas",
        "create": "create_test_layer_schema",
        "update": "update_test_layer_schema",
        "delete": "delete_test_layer_schema",
    },
    "test_suite": {
        "create": "create_test_suite",
        "list": "list_test_suites",
        "assign_test_cases": "assign_test_cases_to_suite",
        "delete": "delete_test_suite",
    },
    "test_plan": {
        "create": "create_test_plan",
        "update": "update_test_plan",
        "manage_content": "manage_test_plan_content",
        "list": "list_test_plans",
        "delete": "delete_test_plan",
    },
    "defect": {
        "create": "create_defect",
        "get": "get_defect",
        "update": "update_defect",
        "delete": "delete_defect",
        "list": "list_defects",
        "link_test_case": "link_defect_to_test_case",
        "list_test_cases": "list_defect_test_cases",
    },
    "defect_matcher": {
        "create": "create_defect_matcher",
        "update": "update_defect_matcher",
        "delete": "delete_defect_matcher",
        "list": "list_defect_matchers",
    },
}

# Spec-defined entity aliases.
ENTITY_ALIASES: dict[str, str] = {
    "integrations": "integration",
    "test_cases": "test_case",
    "launches": "launch",
    "shared_steps": "shared_step",
    "test_layers": "test_layer",
    "test_layer_schemas": "test_layer_schema",
    "test_suites": "test_suite",
    "test_plans": "test_plan",
    "defects": "defect",
    "defect_matchers": "defect_matcher",
    "custom_fields": "custom_field",
    "custom_field_values": "custom_field_value",
}

# Compatibility action aliases.
ACTION_ALIASES: dict[str, dict[str, str]] = {
    "custom_field": {"list": "get"},
}


def all_canonical_routes() -> list[tuple[str, str, str]]:
    """Return (entity, action, tool_name) for every canonical route."""
    rows: list[tuple[str, str, str]] = []
    for entity, actions in CANONICAL_ROUTE_MATRIX.items():
        for action, tool_name in actions.items():
            rows.append((entity, action, tool_name))
    return sorted(rows)


def all_route_tool_names() -> set[str]:
    """Return all unique tool names used in canonical matrix."""
    names: set[str] = set()
    for _entity, _action, tool_name in all_canonical_routes():
        names.add(tool_name)
    return names


def all_entities_with_aliases() -> dict[str, set[str]]:
    """Return canonical entities mapped to all accepted aliases."""
    alias_map: dict[str, set[str]] = {entity: {entity} for entity in CANONICAL_ROUTE_MATRIX}
    for alias, entity in ENTITY_ALIASES.items():
        alias_map.setdefault(entity, {entity}).add(alias)
    # Accept dash-form aliases too.
    for entity, aliases in alias_map.items():
        aliases.update({item.replace("_", "-") for item in list(aliases)})
        aliases.add(entity.replace("_", "-"))
    return alias_map


def normalize_token(value: str) -> str:
    """Normalize CLI token."""
    return value.strip().lower().replace("-", "_")


def iter_actions(entity: str) -> Iterable[str]:
    """Iterate canonical actions for one entity."""
    return CANONICAL_ROUTE_MATRIX[entity].keys()
