"""List hierarchy suites from an Allure TestOps project tree.

This tool returns an LLM-friendly hierarchical view of suites. By default it
includes empty suites; set `include_empty=False` to show only branches with
nested suites.

This operation is read-only and non-destructive.
"""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_hierarchy_service import SuiteNode, TestHierarchyService


def _format_suite_lines(nodes: list[SuiteNode], indent: int = 0) -> list[str]:
    """Render suite hierarchy into text lines."""
    lines: list[str] = []
    prefix = "  " * indent
    for node in nodes:
        lines.append(f"{prefix}- ID: {node.id}, Name: {node.name}")
        lines.extend(_format_suite_lines(node.children, indent + 1))
    return lines


async def list_test_suites(
    project_id: Annotated[int | None, Field(description="Allure TestOps project ID.")] = None,
    tree_id: Annotated[
        int | None, Field(description="Target hierarchy tree ID. If omitted, default project tree is used.")
    ] = None,
    include_empty: Annotated[
        bool,
        Field(description="Whether to include suites that have no nested child suites. Default is True."),
    ] = True,
) -> str:
    """List hierarchy suites for a project tree.

    Args:
        project_id: Optional project override. If omitted, use default project from environment.
        tree_id: Optional hierarchy tree ID. If omitted, the default project tree is used.
        include_empty: Whether to include suites without nested child suites.

    Returns:
        Hierarchical text output with tree info and suite nodes.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestHierarchyService(client)
        tree, suites = await service.list_test_suites(tree_id=tree_id, include_empty=include_empty)

    tree_name = tree.name or "Unnamed tree"
    tree_id_value = tree.id if tree.id is not None else "N/A"

    if not suites:
        return f"Tree '{tree_name}' (ID: {tree_id_value}) has no suites."

    lines = [
        f"Tree: {tree_name} (ID: {tree_id_value})",
        f"Found {len(suites)} top-level suites:",
    ]
    lines.extend(_format_suite_lines(suites))
    return "\n".join(lines)
