"""Service for managing Integrations in Allure TestOps."""

import logging

from src.client import AllureClient
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError
from src.client.generated.models.integration_dto import IntegrationDto

logger = logging.getLogger(__name__)


class IntegrationService:
    """Service for managing Integrations in Allure TestOps.

    Integrations are external issue trackers (Jira, GitHub, etc.) that are configured
    at the instance level. This service provides methods to discover available integrations
    and resolve integration IDs for use in issue linking.
    """

    def __init__(self, client: AllureClient) -> None:
        """Initialize IntegrationService.

        Args:
            client: AllureClient instance
        """
        self._client = client

    async def list_integrations(self) -> list[IntegrationDto]:
        """List all available integrations.

        Returns:
            List of IntegrationDto objects

        Raises:
            AllureAPIError: If the API request fails
        """
        return await self._client.get_integrations()

    async def get_integration_by_id(self, integration_id: int) -> IntegrationDto:
        """Get an integration by its ID.

        Args:
            integration_id: The unique ID of the integration

        Returns:
            The IntegrationDto

        Raises:
            AllureNotFoundError: If integration doesn't exist
            AllureValidationError: If the ID is invalid
            AllureAPIError: If the API request fails
        """
        if integration_id <= 0:
            raise AllureValidationError("Integration ID must be a positive integer")

        integrations = await self.list_integrations()
        for integration in integrations:
            if integration.id == integration_id:
                return integration

        raise AllureNotFoundError(
            f"Integration with ID {integration_id} not found. "
            f"Available integrations: {self._format_integration_list(integrations)}"
        )

    async def get_integration_by_name(self, name: str) -> IntegrationDto:
        """Get an integration by its exact name (case-sensitive).

        Args:
            name: The exact name of the integration

        Returns:
            The IntegrationDto

        Raises:
            AllureNotFoundError: If integration doesn't exist
            AllureValidationError: If the name is empty
            AllureAPIError: If the API request fails
        """
        if not name or not name.strip():
            raise AllureValidationError("Integration name is required")

        integrations = await self.list_integrations()
        for integration in integrations:
            if integration.name == name:
                return integration

        raise AllureNotFoundError(
            f"Integration '{name}' not found. Available integrations: {self._format_integration_list(integrations)}"
        )

    async def resolve_integration(
        self,
        integration_id: int | None = None,
        integration_name: str | None = None,
    ) -> IntegrationDto | None:
        """Resolve an integration from either ID or name.

        This method handles mutual exclusivity validation and resolution.

        Args:
            integration_id: Optional integration ID
            integration_name: Optional integration name

        Returns:
            The resolved IntegrationDto if either parameter is provided, None otherwise

        Raises:
            AllureValidationError: If both parameters are provided (mutual exclusivity)
            AllureNotFoundError: If the specified integration doesn't exist
            AllureAPIError: If the API request fails
        """
        # 1. Mutual exclusivity check
        if integration_id is not None and integration_name is not None:
            raise AllureValidationError(
                "Cannot specify both 'integration_id' and 'integration_name'. "
                "Use only one parameter to identify the integration."
            )

        # 2. Resolve by ID
        if integration_id is not None:
            return await self.get_integration_by_id(integration_id)

        # 3. Resolve by Name
        if integration_name is not None:
            return await self.get_integration_by_name(integration_name)

        # 4. Neither provided
        return None

    async def resolve_integration_for_issues(
        self,
        integration_id: int | None = None,
        integration_name: str | None = None,
    ) -> int:
        """Resolve integration ID for issue linking with strict behavior.

        This method enforces AC#6 and AC#7:
        - Single integration: Auto-select
        - Multiple integrations: Error if no selection provided

        Args:
            integration_id: Optional integration ID to use
            integration_name: Optional integration name to use

        Returns:
            The resolved integration ID

        Raises:
            AllureValidationError: If multiple integrations exist and none specified,
                                  or if both parameters are provided
            AllureNotFoundError: If the specified integration doesn't exist
            AllureAPIError: If the API request fails or no integrations configured
        """
        # First check if explicit integration is provided
        resolved = await self.resolve_integration(integration_id, integration_name)
        if resolved:
            if resolved.id is None:
                raise AllureAPIError("Resolved integration has no ID")
            return resolved.id

        # No explicit selection - check available integrations
        integrations = await self.list_integrations()

        if not integrations:
            raise AllureAPIError(
                "No integrations configured in Allure TestOps. "
                "Please configure an integration (Jira, GitHub, etc.) before linking issues."
            )

        if len(integrations) == 1:
            # AC#6: Single integration - auto-select
            if integrations[0].id is None:
                raise AllureAPIError("Integration has no ID")
            return integrations[0].id

        # AC#7: Multiple integrations - require explicit selection
        raise AllureValidationError(
            f"Multiple integrations found. Please specify which integration to use.\n"
            f"Available integrations:\n{self._format_integration_list(integrations)}\n\n"
            "Hint: Use 'integration_id' or 'integration_name' parameter to specify the integration."
        )

    def _format_integration_list(self, integrations: list[IntegrationDto]) -> str:
        """Format a list of integrations for display in error messages.

        Args:
            integrations: List of IntegrationDto objects

        Returns:
            Formatted string with integration names and IDs
        """
        if not integrations:
            return "(none configured)"

        lines: list[str] = []
        for integration in integrations:
            name = integration.name or "(unnamed)"
            int_id = integration.id or "N/A"
            info_type = ""
            if integration.info and hasattr(integration.info, "type") and integration.info.type:
                info_type = f" [{integration.info.type}]"
            lines.append(f"- {name} (ID: {int_id}){info_type}")

        return "\n".join(lines)
