"""
CLI entity/action registry helpers.
"""

from __future__ import annotations

import typing

from src.cli.models import ActionSpec, CLIError
from src.cli.route_matrix import ACTION_ALIASES, CANONICAL_ROUTE_MATRIX, all_entities_with_aliases, normalize_token


def build_command_registry(schemas: dict[str, typing.Any]) -> dict[str, dict[str, ActionSpec]]:
    """Build {entity: {action: ActionSpec}} from canonical route matrix."""
    registry: dict[str, dict[str, ActionSpec]] = {}

    for entity, action_map in CANONICAL_ROUTE_MATRIX.items():
        by_action = registry.setdefault(entity, {})
        for action, tool_name in action_map.items():
            schema = schemas.get(tool_name)
            if not isinstance(schema, dict):
                missing = ", ".join(sorted(action_map.values()))
                raise CLIError(
                    f"Tool schema for '{tool_name}' is missing",
                    hint=f"Regenerate schemas. Expected tools for '{entity}': {missing}",
                    exit_code=2,
                )
            if action in by_action:
                existing = by_action[action].tool_name
                raise CLIError(
                    f"Ambiguous command mapping for '{entity} {action}'",
                    hint=f"Tools '{existing}' and '{tool_name}' map to the same command",
                    exit_code=2,
                )
            by_action[action] = ActionSpec(
                tool_name=tool_name,
                entity=entity,
                action=action,
                schema=typing.cast(dict[str, typing.Any], schema),
            )

    represented = {spec.tool_name for actions in registry.values() for spec in actions.values()}
    for tool_name in schemas:
        if tool_name not in represented:
            raise CLIError(
                f"Tool schema '{tool_name}' is not represented in canonical route matrix",
                hint="Update src/cli/route_matrix.py canonical routes to include this tool.",
                exit_code=2,
            )
    return registry


def resolve_entity_name(entity_input: str, registry: dict[str, dict[str, ActionSpec]]) -> str:
    """Resolve entity aliases defined in route matrix metadata."""
    normalized = normalize_token(entity_input)
    alias_map: dict[str, str] = {}
    for entity, aliases in all_entities_with_aliases().items():
        if entity not in registry:
            continue
        for alias in aliases:
            alias_map.setdefault(alias, entity)

    if normalized not in alias_map:
        canonical = ", ".join(sorted(registry.keys()))
        alias_names = ", ".join(
            sorted(alias for alias in alias_map if alias not in registry and "_" not in alias and "-" not in alias)
        )
        hint = f"Canonical entities: {canonical}"
        if alias_names:
            hint += f". Aliases: {alias_names}"
        raise CLIError(
            f"Unknown entity '{entity_input}'",
            hint=hint,
            exit_code=1,
        )
    return alias_map[normalized]


def resolve_action_name(entity: str, action_input: str, actions: dict[str, ActionSpec]) -> str:
    """Resolve action aliases (hyphen/underscore normalization)."""
    normalized = normalize_token(action_input)
    if normalized in actions:
        return normalized

    alias_map: dict[str, str] = {}
    for action_name in actions:
        aliases = {action_name, action_name.replace("_", "-")}
        canonical_aliases = ACTION_ALIASES.get(entity, {})
        for alias, canonical in canonical_aliases.items():
            if canonical == action_name:
                aliases.add(alias)
        for alias in aliases:
            alias_map.setdefault(alias, action_name)

    if normalized not in alias_map:
        available = ", ".join(sorted(actions.keys()))
        raise CLIError(
            f"Unknown action '{action_input}' for entity '{entity}'",
            hint=f"Available actions: {available}",
            exit_code=1,
        )

    return alias_map[normalized]
