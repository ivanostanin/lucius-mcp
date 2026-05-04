"""
Canonical route-matrix coverage tests for CLI entity/action model.
"""

from __future__ import annotations

import pytest

from src.cli import cli_entry
from src.cli.cli_entry import run_cli
from src.cli.route_matrix import CANONICAL_ROUTE_MATRIX, ENTITY_ALIASES, all_canonical_routes, all_entities_with_aliases
from src.cli.routing import build_command_registry, resolve_entity_name
from src.cli.schema_loader import load_tool_schemas


class TestCLIRouteMatrix:
    """Guarantee canonical route coverage and representation."""

    def test_short_entity_aliases_resolve_to_canonical_entities(self) -> None:
        schemas = load_tool_schemas(cli_entry.TOOL_SCHEMAS_PATH, cli_entry.Path(cli_entry.__file__))
        registry = build_command_registry(schemas)

        expected_aliases = {
            "tc": "test_case",
            "cf": "custom_field",
            "cfv": "custom_field_value",
            "ln": "launch",
            "int": "integration",
            "ss": "shared_step",
            "tl": "test_layer",
            "tls": "test_layer_schema",
            "ts": "test_suite",
            "tp": "test_plan",
            "df": "defect",
            "dm": "defect_matcher",
        }

        for alias, canonical in expected_aliases.items():
            assert ENTITY_ALIASES[alias] == canonical
            assert resolve_entity_name(alias, registry) == canonical
            assert resolve_entity_name(alias.upper(), registry) == canonical

    def test_entity_aliases_have_no_conflicting_canonical_targets(self) -> None:
        alias_targets: dict[str, str] = {}
        for canonical, aliases in all_entities_with_aliases().items():
            for alias in aliases:
                existing = alias_targets.setdefault(alias, canonical)
                assert existing == canonical, f"{alias!r} maps to both {existing!r} and {canonical!r}"

    def test_registry_matches_canonical_route_matrix(self) -> None:
        schemas = load_tool_schemas(cli_entry.TOOL_SCHEMAS_PATH, cli_entry.Path(cli_entry.__file__))
        registry = build_command_registry(schemas)

        assert set(registry.keys()) == set(CANONICAL_ROUTE_MATRIX.keys())
        for entity, actions in CANONICAL_ROUTE_MATRIX.items():
            assert set(registry[entity].keys()) == set(actions.keys())
            for action, tool_name in actions.items():
                assert registry[entity][action].tool_name == tool_name

    @pytest.mark.parametrize("entity,action,tool_name", all_canonical_routes())
    def test_every_canonical_route_supports_help(
        self,
        entity: str,
        action: str,
        tool_name: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        run_cli([entity, action, "--help"])
        output = capsys.readouterr().out
        assert f"lucius {entity} {action}" in output
        assert f"Mapped tool: {tool_name}" in output
