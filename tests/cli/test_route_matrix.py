"""
Canonical route-matrix coverage tests for CLI entity/action model.
"""

from __future__ import annotations

import pytest

from src.cli import cli_entry
from src.cli.cli_entry import run_cli
from src.cli.route_matrix import CANONICAL_ROUTE_MATRIX, all_canonical_routes
from src.cli.routing import build_command_registry
from src.cli.schema_loader import load_tool_schemas


class TestCLIRouteMatrix:
    """Guarantee canonical route coverage and representation."""

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
