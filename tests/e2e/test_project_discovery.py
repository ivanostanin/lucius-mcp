"""End-to-end coverage for project discovery."""

import pytest

from src.client import AllureClient
from src.services.project_service import ProjectService


async def test_e2e_list_projects_then_resolve_project_by_name(allure_client: AllureClient) -> None:
    """Authenticate, list projects, and resolve a listed project by name."""
    service = ProjectService(allure_client)
    projects = await service.list_projects()
    if not projects or not projects[0].name:
        pytest.skip("No named projects available to the authenticated TestOps user")

    expected = projects[0]
    resolved = await service.get_project_by_name(expected.name.swapcase())

    assert resolved.id == expected.id
