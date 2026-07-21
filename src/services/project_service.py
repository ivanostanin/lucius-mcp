"""Service for discovering Allure TestOps projects."""

from src.client import AllureClient
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError
from src.client.generated.exceptions import ApiException
from src.client.generated.models.project_dto import ProjectDto


class ProjectService:
    """Retrieve projects available to the authenticated TestOps user."""

    def __init__(self, client: AllureClient) -> None:
        """Initialize the project service.

        Args:
            client: Authenticated Allure TestOps client.
        """
        self._client = client

    async def list_projects(self) -> list[ProjectDto]:
        """List every project available to the authenticated user.

        Returns:
            Project records sorted by name.

        Raises:
            AllureAPIError: If the Project API is unavailable or the request fails.
        """
        api = self._client._project_api
        if api is None:
            raise AllureAPIError("Project API is not initialized")

        projects: list[ProjectDto] = []
        page_number = 0
        try:
            while True:
                page = await api.find_all21(page=page_number, size=100, sort=["name,asc"])
                projects.extend(page.content or [])
                total_pages = page.total_pages or 0
                if page_number + 1 >= total_pages:
                    return projects
                page_number += 1
        except ApiException as exc:
            self._client._handle_api_exception(exc)
            raise
        except (AllureAPIError, AllureNotFoundError, AllureValidationError):
            raise
        except Exception as exc:
            raise AllureAPIError(f"Failed to list projects: {exc}") from exc

    async def get_project_by_name(self, name: str) -> ProjectDto:
        """Resolve a project from an exact or unambiguous partial name.

        Exact matches are case-insensitive and always win over partial matches.

        Args:
            name: Project name or a unique portion of its name.

        Returns:
            The resolved project.

        Raises:
            AllureValidationError: If the name is blank or matches multiple projects.
            AllureNotFoundError: If no accessible project matches the name.
        """
        if not name or not name.strip():
            raise AllureValidationError("Project name is required")

        requested_name = name.strip()
        normalized_name = requested_name.casefold()
        projects = await self.list_projects()
        exact_matches = [project for project in projects if (project.name or "").casefold() == normalized_name]
        if len(exact_matches) == 1:
            return exact_matches[0]

        partial_matches = [project for project in projects if normalized_name in (project.name or "").casefold()]
        if len(partial_matches) == 1:
            return partial_matches[0]
        if len(partial_matches) > 1 or len(exact_matches) > 1:
            candidates = ", ".join(
                f"{project.name or '(unnamed)'} (ID: {project.id if project.id is not None else 'unknown'})"
                for project in (exact_matches or partial_matches)
            )
            raise AllureValidationError(
                f"Multiple projects match '{requested_name}': {candidates}. Use an exact project name."
            )

        raise AllureNotFoundError(
            f"Project '{requested_name}' not found. Use get_project() to list projects available to this account."
        )
