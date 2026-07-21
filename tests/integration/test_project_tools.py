"""Integration tests for the get_project MCP tool."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.client.generated.models.project_dto import ProjectDto
from src.tools.projects import get_project


@pytest.mark.asyncio
async def test_get_project_returns_named_project_details() -> None:
    with patch("src.tools.projects.AllureClient.from_env") as client_factory:
        client_factory.return_value.__aenter__.return_value = MagicMock()
        with patch("src.tools.projects.ProjectService") as service_class:
            service_class.return_value.get_project_by_name = AsyncMock(
                return_value=ProjectDto(id=7, name="Lucius MCP", description="Project details", abbr="LCP")
            )

            output = await get_project(name="lucius mcp", output_format="plain")

    assert "Project #7: Lucius MCP" in output
    assert "Description: Project details" in output
    assert "Abbreviation: LCP" in output
    client_factory.assert_called_once_with(require_project=False)
    service_class.return_value.get_project_by_name.assert_awaited_once_with("lucius mcp")


@pytest.mark.asyncio
async def test_get_project_without_name_lists_project_summaries() -> None:
    with patch("src.tools.projects.AllureClient.from_env") as client_factory:
        client_factory.return_value.__aenter__.return_value = MagicMock()
        with patch("src.tools.projects.ProjectService") as service_class:
            service_class.return_value.list_projects = AsyncMock(
                return_value=[ProjectDto(id=7, name="Lucius MCP"), ProjectDto(id=8, name="Demo")]
            )

            output = await get_project(output_format="plain")

    assert "Available Projects (2 found)" in output
    assert "Lucius MCP (ID: 7)" in output
    assert "Demo (ID: 8)" in output
    client_factory.assert_called_once_with(require_project=False)
