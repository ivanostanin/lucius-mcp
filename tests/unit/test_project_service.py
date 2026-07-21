"""Unit tests for project discovery."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError
from src.client.generated.models.page_project_dto import PageProjectDto
from src.client.generated.models.project_dto import ProjectDto
from src.services.project_service import ProjectService


@pytest.fixture
def project_api() -> MagicMock:
    api = MagicMock()
    api.find_all21 = AsyncMock(
        return_value=PageProjectDto(
            content=[
                ProjectDto(id=1, name="Lucius MCP", description="Primary project"),
                ProjectDto(id=2, name="Lucius MCP Demo"),
            ],
            total_pages=1,
        )
    )
    return api


@pytest.fixture
def service(project_api: MagicMock) -> ProjectService:
    client = MagicMock()
    client._project_api = project_api
    client._handle_api_exception = MagicMock()
    return ProjectService(client)


async def test_list_projects_returns_all_available_projects(service: ProjectService, project_api: MagicMock) -> None:
    projects = await service.list_projects()

    assert [project.id for project in projects] == [1, 2]
    project_api.find_all21.assert_awaited_once_with(page=0, size=100, sort=["name,asc"])


async def test_list_projects_fetches_every_page(service: ProjectService, project_api: MagicMock) -> None:
    project_api.find_all21.side_effect = [
        PageProjectDto(content=[ProjectDto(id=1, name="Alpha")], total_pages=2),
        PageProjectDto(content=[ProjectDto(id=2, name="Beta")], total_pages=2),
    ]

    projects = await service.list_projects()

    assert [project.id for project in projects] == [1, 2]
    assert project_api.find_all21.await_count == 2


async def test_list_projects_requires_initialized_project_api() -> None:
    client = MagicMock()
    client._project_api = None

    with pytest.raises(AllureAPIError, match="Project API is not initialized"):
        await ProjectService(client).list_projects()


async def test_list_projects_wraps_unexpected_api_errors(service: ProjectService, project_api: MagicMock) -> None:
    project_api.find_all21.side_effect = RuntimeError("network unavailable")

    with pytest.raises(AllureAPIError, match="Failed to list projects: network unavailable"):
        await service.list_projects()


async def test_list_projects_preserves_allure_errors(service: ProjectService, project_api: MagicMock) -> None:
    project_api.find_all21.side_effect = AllureAPIError("Project endpoint unavailable")

    with pytest.raises(AllureAPIError, match="Project endpoint unavailable"):
        await service.list_projects()


async def test_get_project_by_name_matches_case_insensitively(service: ProjectService) -> None:
    project = await service.get_project_by_name("lucius mcp")

    assert project.id == 1
    assert project.name == "Lucius MCP"


async def test_get_project_by_name_prefers_exact_match_over_partial_match(service: ProjectService) -> None:
    project = await service.get_project_by_name("LuciUs McP")

    assert project.id == 1


async def test_get_project_by_name_accepts_an_unambiguous_partial_match(
    service: ProjectService, project_api: MagicMock
) -> None:
    project_api.find_all21.return_value = PageProjectDto(content=[ProjectDto(id=1, name="Lucius MCP")], total_pages=1)

    project = await service.get_project_by_name("lucius")

    assert project.id == 1


async def test_get_project_by_name_reports_ambiguous_partial_matches(
    service: ProjectService, project_api: MagicMock
) -> None:
    project_api.find_all21.return_value = PageProjectDto(
        content=[ProjectDto(id=1, name="Lucius Alpha"), ProjectDto(id=2, name="Lucius Beta")], total_pages=1
    )

    with pytest.raises(AllureValidationError, match="Multiple projects match 'lucius'"):
        await service.get_project_by_name("lucius")


async def test_get_project_by_name_reports_not_found(service: ProjectService) -> None:
    with pytest.raises(AllureNotFoundError, match="Project 'missing' not found"):
        await service.get_project_by_name("missing")


async def test_get_project_by_name_requires_non_blank_name(service: ProjectService) -> None:
    with pytest.raises(AllureValidationError, match="Project name is required"):
        await service.get_project_by_name("  ")
