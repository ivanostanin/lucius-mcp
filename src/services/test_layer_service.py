"""Service for managing Test Layers in Allure TestOps."""

import logging

from pydantic import ValidationError as PydanticValidationError

from src.client import AllureClient
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError
from src.client.generated.exceptions import ApiException
from src.client.generated.models.page_test_layer_dto import PageTestLayerDto
from src.client.generated.models.page_test_layer_schema_dto import PageTestLayerSchemaDto
from src.client.generated.models.test_layer_create_dto import TestLayerCreateDto
from src.client.generated.models.test_layer_dto import TestLayerDto
from src.client.generated.models.test_layer_patch_dto import TestLayerPatchDto
from src.client.generated.models.test_layer_schema_create_dto import TestLayerSchemaCreateDto
from src.client.generated.models.test_layer_schema_dto import TestLayerSchemaDto
from src.client.generated.models.test_layer_schema_patch_dto import TestLayerSchemaPatchDto
from src.utils.schema_hint import generate_schema_hint

logger = logging.getLogger(__name__)

# Constants - from Allure TestOps API constraints
# These limits match the database schema VARCHAR field lengths for test layer names and schema keys
MAX_NAME_LENGTH = 255
MAX_KEY_LENGTH = 255


class TestLayerService:
    """Service for managing Test Layers and their Schemas in Allure TestOps."""

    def __init__(self, client: AllureClient) -> None:
        """Initialize TestLayerService.

        Args:
            client: AllureClient instance
        """
        self._client = client
        self._project_id = client.get_project()

    # ==========================================
    # Test Layer CRUD Operations
    # ==========================================

    async def list_test_layers(
        self,
        page: int = 0,
        size: int = 100,
    ) -> list[TestLayerDto]:
        """List all test layers.

        Args:
            page: Page number (0-based)
            size: Page size

        Returns:
            List of TestLayerDto

        Raises:
            AllureAPIError: If the API request fails
        """
        if not self._client._test_layer_api:
            raise AllureAPIError("Test Layer API is not initialized")

        try:
            page_dto: PageTestLayerDto = await self._client._test_layer_api.find_all7(
                page=page,
                size=size,
            )
            return page_dto.content or []
        except Exception as e:
            raise AllureAPIError(f"Failed to list test layers: {e}") from e

    async def create_test_layer(self, name: str) -> TestLayerDto:
        """Create a new test layer.

        Args:
            name: Name of the test layer

        Returns:
            The created TestLayerDto

        Raises:
            AllureValidationError: If validation fails
            AllureAPIError: If the API request fails
        """
        self._validate_name(name)

        if not self._client._test_layer_api:
            raise AllureAPIError("Test Layer API is not initialized")

        try:
            create_dto = TestLayerCreateDto(name=name)
        except PydanticValidationError as e:
            hint = generate_schema_hint(TestLayerCreateDto)
            raise AllureValidationError(f"Invalid test layer data: {e}", suggestions=[hint]) from e

        try:
            return await self._client._test_layer_api.create9(test_layer_create_dto=create_dto)
        except Exception as e:
            raise AllureAPIError(
                f"Failed to create test layer '{name}': {e}. "
                "Ensure the name is unique and you have project permissions."
            ) from e

    async def get_test_layer(self, layer_id: int) -> TestLayerDto:
        """Get a test layer by ID.

        Args:
            layer_id: The test layer ID

        Returns:
            The TestLayerDto

        Raises:
            AllureNotFoundError: If test layer doesn't exist
            AllureAPIError: If the API request fails
        """
        if not self._client._test_layer_api:
            raise AllureAPIError("Test Layer API is not initialized")

        try:
            return await self._client._test_layer_api.find_one8(id=layer_id)
        except ApiException as e:
            self._client._handle_api_exception(e)
            raise
        except (AllureNotFoundError, AllureValidationError, AllureAPIError):
            raise
        except Exception as e:
            raise AllureAPIError(f"Failed to get test layer {layer_id}: {e}") from e

    async def update_test_layer(
        self,
        layer_id: int,
        name: str,
    ) -> tuple[TestLayerDto, bool]:
        """Update an existing test layer with idempotency support.

        Args:
            layer_id: The test layer ID to update
            name: New name for the test layer

        Returns:
            Tuple of (updated_test_layer, changed) where changed is True if update was applied

        Raises:
            AllureNotFoundError: If test layer doesn't exist
            AllureValidationError: If validation fails
            AllureAPIError: If the API request fails
        """
        self._validate_name(name)

        # Get current state
        current = await self.get_test_layer(layer_id)

        # Check idempotency
        if current.name == name:
            return current, False

        if not self._client._test_layer_api:
            raise AllureAPIError("Test Layer API is not initialized")

        # Build patch DTO and update
        try:
            patch_data = TestLayerPatchDto(name=name)
        except PydanticValidationError as e:
            hint = generate_schema_hint(TestLayerPatchDto)
            raise AllureValidationError(f"Invalid patch data: {e}", suggestions=[hint]) from e

        try:
            updated = await self._client._test_layer_api.patch9(id=layer_id, test_layer_patch_dto=patch_data)
            return updated, True
        except Exception as e:
            raise AllureAPIError(
                f"Failed to update test layer {layer_id}: {e}. "
                "Check that the layer exists and you have update permissions."
            ) from e

    async def delete_test_layer(self, layer_id: int) -> bool:
        """Delete a test layer with idempotent behavior.

        Args:
            layer_id: The test layer ID to delete

        Returns:
            True if the layer was deleted, False if it was already deleted/not found

        Raises:
            AllureAPIError: If the API request fails (other than 404)

        Note:
            This operation is idempotent. If already deleted (404), returns False.
        """
        if not self._client._test_layer_api:
            raise AllureAPIError("Test Layer API is not initialized")

        try:
            # Check existence first for accurate feedback
            await self.get_test_layer(layer_id)
            await self._client._test_layer_api.delete9(id=layer_id)
            return True
        except AllureNotFoundError:
            # Idempotent: if already deleted, this is fine
            logger.debug(f"Test layer {layer_id} already deleted or not found")
            return False

    # ==========================================
    # Test Layer Schema CRUD Operations
    # ==========================================

    async def list_test_layer_schemas(
        self,
        project_id: int | None = None,
        page: int = 0,
        size: int = 100,
    ) -> list[TestLayerSchemaDto]:
        """List all test layer schemas for a project.

        Args:
            project_id: Project ID (defaults to client's project)
            page: Page number (0-based)
            size: Page size

        Returns:
            List of TestLayerSchemaDto

        Raises:
            AllureAPIError: If the API request fails
        """
        target_project_id = project_id or self._project_id
        self._validate_project_id(target_project_id)

        if not self._client._test_layer_schema_api:
            raise AllureAPIError("Test Layer Schema API is not initialized")

        try:
            page_dto: PageTestLayerSchemaDto = await self._client._test_layer_schema_api.find_all6(
                project_id=target_project_id,
                page=page,
                size=size,
            )
            return page_dto.content or []
        except Exception as e:
            raise AllureAPIError(f"Failed to list test layer schemas: {e}") from e

    async def create_test_layer_schema(
        self,
        project_id: int,
        test_layer_id: int,
        key: str,
    ) -> TestLayerSchemaDto:
        """Create a new test layer schema.

        Args:
            project_id: The project ID
            test_layer_id: The test layer ID to link to
            key: The schema key

        Returns:
            The created TestLayerSchemaDto

        Raises:
            AllureValidationError: If validation fails
            AllureAPIError: If the API request fails
        """
        self._validate_project_id(project_id)
        self._validate_key(key)

        if not self._client._test_layer_schema_api:
            raise AllureAPIError("Test Layer Schema API is not initialized")

        try:
            create_dto = TestLayerSchemaCreateDto(
                project_id=project_id,
                test_layer_id=test_layer_id,
                key=key,
            )
        except PydanticValidationError as e:
            hint = generate_schema_hint(TestLayerSchemaCreateDto)
            raise AllureValidationError(f"Invalid test layer schema data: {e}", suggestions=[hint]) from e

        try:
            return await self._client._test_layer_schema_api.create8(test_layer_schema_create_dto=create_dto)
        except Exception as e:
            raise AllureAPIError(
                f"Failed to create test layer schema '{key}': {e}. "
                "Ensure the project_id and test_layer_id are valid, and the key is unique within the project."
            ) from e

    async def get_test_layer_schema(self, schema_id: int) -> TestLayerSchemaDto:
        """Get a test layer schema by ID.

        Args:
            schema_id: The test layer schema ID

        Returns:
            The TestLayerSchemaDto

        Raises:
            AllureNotFoundError: If test layer schema doesn't exist
            AllureAPIError: If the API request fails
        """
        if not self._client._test_layer_schema_api:
            raise AllureAPIError("Test Layer Schema API is not initialized")

        try:
            return await self._client._test_layer_schema_api.find_one7(id=schema_id)
        except ApiException as e:
            self._client._handle_api_exception(e)
            raise
        except (AllureNotFoundError, AllureValidationError, AllureAPIError):
            raise
        except Exception as e:
            raise AllureAPIError(f"Failed to get test layer schema {schema_id}: {e}") from e

    async def update_test_layer_schema(
        self,
        schema_id: int,
        test_layer_id: int | None = None,
        key: str | None = None,
    ) -> tuple[TestLayerSchemaDto, bool]:
        """Update an existing test layer schema with idempotency support.

        Args:
            schema_id: The test layer schema ID to update
            test_layer_id: New test layer ID (optional)
            key: New key (optional)

        Returns:
            Tuple of (updated_schema, changed) where changed is True if update was applied

        Raises:
            AllureNotFoundError: If test layer schema doesn't exist
            AllureValidationError: If validation fails
            AllureAPIError: If the API request fails
        """
        # Validation
        if key is not None:
            self._validate_key(key)

        # Get current state
        current = await self.get_test_layer_schema(schema_id)

        # Check idempotency
        needs_update = False
        if test_layer_id is not None and current.test_layer and current.test_layer.id != test_layer_id:
            needs_update = True
        if key is not None and current.key != key:
            needs_update = True

        # No changes needed
        if not needs_update:
            return current, False

        if not self._client._test_layer_schema_api:
            raise AllureAPIError("Test Layer Schema API is not initialized")

        # Build patch DTO and update
        try:
            patch_data = TestLayerSchemaPatchDto(
                test_layer_id=test_layer_id,
                key=key,
            )
        except PydanticValidationError as e:
            hint = generate_schema_hint(TestLayerSchemaPatchDto)
            raise AllureValidationError(f"Invalid patch data: {e}", suggestions=[hint]) from e

        try:
            updated = await self._client._test_layer_schema_api.patch8(
                id=schema_id, test_layer_schema_patch_dto=patch_data
            )
            return updated, True
        except Exception as e:
            raise AllureAPIError(
                f"Failed to update test layer schema {schema_id}: {e}. "
                "Check that the schema exists and the new values are valid."
            ) from e

    async def delete_test_layer_schema(self, schema_id: int) -> bool:
        """Delete a test layer schema with idempotent behavior.

        Args:
            schema_id: The test layer schema ID to delete

        Returns:
            True if the schema was deleted, False if it was already deleted/not found

        Raises:
            AllureAPIError: If the API request fails (other than 404)

        Note:
            This operation is idempotent. If already deleted (404), returns False.
        """
        if not self._client._test_layer_schema_api:
            raise AllureAPIError("Test Layer Schema API is not initialized")

        try:
            # Check existence first for accurate feedback
            await self.get_test_layer_schema(schema_id)
            await self._client._test_layer_schema_api.delete8(id=schema_id)
            return True
        except AllureNotFoundError:
            # Idempotent: if already deleted, this is fine
            logger.debug(f"Test layer schema {schema_id} already deleted or not found")
            return False

    # ==========================================
    # Validation Methods
    # ==========================================

    def _validate_project_id(self, project_id: int) -> None:
        """Validate project ID."""
        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")

    def _validate_name(self, name: str) -> None:
        """Validate test layer name."""
        if not name or not name.strip():
            raise AllureValidationError("Name is required")
        if len(name) > MAX_NAME_LENGTH:
            raise AllureValidationError(f"Name too long (max {MAX_NAME_LENGTH})")

    def _validate_key(self, key: str) -> None:
        """Validate test layer schema key."""
        if not key or not key.strip():
            raise AllureValidationError("Key is required")
        if len(key) > MAX_KEY_LENGTH:
            raise AllureValidationError(f"Key too long (max {MAX_KEY_LENGTH})")
