import base64
import logging
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from src.client import (
    AllureClient,
    PageSharedStepDto,
    ScenarioStepCreateDto,
    SharedStepAttachmentRowDto,
    SharedStepDto,
)
from src.client.exceptions import AllureAPIError, AllureValidationError
from src.services.attachment_service import AttachmentService
from src.utils.schema_hint import generate_schema_hint

logger = logging.getLogger(__name__)

# Constants
MAX_NAME_LENGTH = 255
MAX_BODY_LENGTH = 10000


class SharedStepService:
    """Service for managing Shared Steps in Allure TestOps."""

    def __init__(
        self,
        client: AllureClient,
        attachment_service: AttachmentService | None = None,
    ) -> None:
        self._client = client
        self._attachment_service = attachment_service or AttachmentService(client)

    async def create_shared_step(
        self,
        project_id: int,
        name: str,
        steps: list[dict[str, Any]] | None = None,
    ) -> SharedStepDto:
        """Create a new shared step with optional steps.

        Args:
            project_id: ID of the project.
            name: Name of the shared step.
            steps: Optional list of steps.

        Returns:
            The created SharedStepDto.
        """
        # 1. Validation
        self._validate_project_id(project_id)
        self._validate_name(name)
        self._validate_steps(steps)

        # 2. Create Shared Step container
        try:
            shared_step = await self._client.create_shared_step(project_id, name)
        except Exception as e:
            raise AllureAPIError(f"Failed to create shared step '{name}': {e}") from e

        if not shared_step.id:
            raise AllureAPIError("Created shared step has no ID")

        # 3. Add steps if provided
        if steps:
            try:
                await self._add_steps(shared_step.id, steps)
                # Refetch to get updated counts/metadata if needed,
                # but API returns DTO on create, maybe we just return that + local knowledge?
                # Actually, step counts might update async or on fetch.
                # For now, return the initial object, as explicit listing/get is separate.
            except Exception as e:
                # Rollback?
                # Shared steps don't have atomic rollbacks easily without delete.
                # We attempt to delete the shared step if step creation fails to avoid partial state.
                try:
                    logger.warning(f"Shared step creation failed during step addition: {e}. Attempting rollback...")
                    await self.delete_shared_step(shared_step.id)
                    logger.info(f"Rollback successful: Deleted incomplete shared step {shared_step.id}")
                except Exception as rollback_error:
                    logger.error(
                        f"Rollback failed: {rollback_error}. Shared step {shared_step.id} may be explicitly incomplete."
                    )
                raise AllureAPIError(f"Failed to add steps to shared step: {e}") from e

        return shared_step

    async def list_shared_steps(
        self,
        project_id: int,
        page: int = 0,
        size: int = 100,
        search: str | None = None,
        archived: bool | None = None,
    ) -> list[SharedStepDto]:
        """List shared steps for a project.

        Args:
            project_id: Project ID.
            page: Page number (0-based).
            size: Page size.
            search: Optional search query.
            archived: Optional archived status filter.

        Returns:
            List of SharedStepDto.
        """
        self._validate_project_id(project_id)

        page_dto: PageSharedStepDto = await self._client.list_shared_steps(
            project_id=project_id, page=page, size=size, search=search, archived=archived
        )

        return page_dto.content or []

    async def get_shared_step(self, step_id: int) -> SharedStepDto:
        """Retrieve a specific shared step by its ID.

        Args:
            step_id: The unique ID of the shared step.

        Returns:
            The shared step data.

        Raises:
            AllureNotFoundError: If shared step doesn't exist.
            AllureAPIError: If the server returns an error.
        """
        return await self._client.get_shared_step(step_id)

    async def update_shared_step(
        self,
        step_id: int,
        name: str | None = None,
        description: str | None = None,
    ) -> tuple[SharedStepDto, bool]:
        """Update an existing shared step with idempotency support.

        Only provided fields are updated. Repeated calls with same data are idempotent.

        Args:
            step_id: The shared step ID to update.
            name: New name for the shared step (optional).
            description: New description (optional).

        Returns:
            Tuple of (updated_shared_step, changed) where changed is True if update was applied.

        Raises:
            AllureNotFoundError: If shared step doesn't exist.
            AllureValidationError: If validation fails.
            AllureAPIError: If the server returns an error.
        """
        # Validation
        if name is not None:
            self._validate_name(name)

        # Get current state
        current = await self._client.get_shared_step(step_id)

        # Check idempotency (from Story 1.4 pattern)
        needs_update = False
        if name is not None and name != current.name:
            needs_update = True
        if description is not None and description != getattr(current, "description", None):
            needs_update = True

        # No changes needed
        if not needs_update:
            return current, False

        # Build patch DTO and update
        from src.client import SharedStepPatchDto

        patch_data = SharedStepPatchDto(name=name if name is not None else None)

        updated = await self._client.update_shared_step(step_id, patch_data)
        return updated, True

    async def delete_shared_step(self, step_id: int) -> None:
        """Delete (archive) a shared step with idempotent behavior.

        Args:
            step_id: The shared step ID to delete.

        Raises:
            AllureAPIError: If the API request fails (other than 404).

        Note:
            This operation is idempotent following Story 1.5 pattern.
            If already deleted (404), returns gracefully.
        """
        from src.client.exceptions import AllureNotFoundError

        try:
            await self._client.delete_shared_step(step_id)
        except AllureNotFoundError:
            # Idempotent: if already deleted, this is fine
            logger.debug(f"Shared step {step_id} already deleted or not found")
            pass

    # ==========================================
    # Helper Methods
    # ==========================================

    async def _add_steps(
        self,
        shared_step_id: int,
        steps: list[dict[str, Any]],
        parent_step_id: int | None = None,
    ) -> int | None:
        """Recursively add steps to a shared step."""
        last_step_id = None

        for s in steps:
            action = str(s.get("action", ""))
            expected = str(s.get("expected", ""))
            step_attachments: list[dict[str, str]] = s.get("attachments", [])

            current_parent_id: int | None = parent_step_id

            # 1. Action Step
            if action:
                step_dto = self._build_scenario_step_dto(
                    shared_step_id=shared_step_id, body=action, parent_id=current_parent_id
                )
                response = await self._client.create_shared_step_scenario_step(step_dto)
                current_parent_id = response.created_step_id

                # 2. Expected Result (child of action)
                if expected:
                    expected_dto = self._build_scenario_step_dto(
                        shared_step_id=shared_step_id, body=expected, parent_id=current_parent_id
                    )
                    await self._client.create_shared_step_scenario_step(expected_dto)

                # 3. Attachments (children of action)
                if step_attachments:
                    for att in step_attachments:
                        # Upload using shared step attachment API
                        # But wait, AttachmentService uses TestCaseAttachmentControllerApi?
                        # Or does it use AllureClient wrapper?
                        # AttachmentService.upload_attachment uses test_case_id.
                        # I can't use AttachmentService directly for shared steps if it requires test_case_id.
                        # I need to duplicate upload logic or enable AttachmentService to handle shared steps.
                        # Shared API: create21(shared_step_id, file)
                        # AttachmentService uses create16(test_case_id, file)
                        # I'll implement internal upload here or extend AttachmentService.
                        # Extending Service is better but for now internal helper is faster.

                        # Handle content/url logic similar to AttachmentService
                        # Simplified: assume content/name
                        row = await self._upload_attachment(shared_step_id, att)

                        att_step_dto = self._build_scenario_step_dto(
                            shared_step_id=shared_step_id, attachment_id=row.id, parent_id=current_parent_id
                        )
                        await self._client.create_shared_step_scenario_step(att_step_dto)

            # 4. Recursive Steps (sub-steps)
            # The tool definition allows nested steps?
            # "steps: list[Argument]" - usually recursive in our model.
            # If the dict has "steps", recurse.
            nested_steps = s.get("steps")
            if nested_steps and isinstance(nested_steps, list):
                await self._add_steps(shared_step_id, nested_steps, parent_step_id=current_parent_id)

            last_step_id = current_parent_id

        return last_step_id

    async def _upload_attachment(self, shared_step_id: int, att: dict[str, str]) -> SharedStepAttachmentRowDto:
        """Upload attachment for shared step."""
        content = att.get("content")
        name = att.get("name", "attachment")

        if not content:
            raise AllureValidationError("Attachment must have 'content'")

        try:
            decoded = base64.b64decode(content)
        except Exception as e:
            raise AllureValidationError(f"Invalid base64 content: {e}") from e

        # client.upload_shared_step_attachment returns List[Row]
        rows = await self._client.upload_shared_step_attachment(shared_step_id, [(name, decoded)])
        if not rows:
            raise AllureAPIError("No attachment rows returned after upload")
        return rows[0]

    def _build_scenario_step_dto(
        self,
        shared_step_id: int,
        body: str | None = None,
        attachment_id: int | None = None,
        parent_id: int | None = None,
    ) -> ScenarioStepCreateDto:
        """Build ScenarioStepCreateDto."""
        try:
            return ScenarioStepCreateDto(
                shared_step_id=shared_step_id, body=body, attachment_id=attachment_id, parent_id=parent_id
            )
        except PydanticValidationError as e:
            hint = generate_schema_hint(ScenarioStepCreateDto)
            raise AllureValidationError(f"Invalid step data: {e}", suggestions=[hint]) from e

    # ==========================================
    # Validation Methods
    # ==========================================

    def _validate_project_id(self, project_id: int) -> None:
        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")

    def _validate_name(self, name: str) -> None:
        if not name or not name.strip():
            raise AllureValidationError("Name is required")
        if len(name) > MAX_NAME_LENGTH:
            raise AllureValidationError(f"Name too long (max {MAX_NAME_LENGTH})")

    def _validate_steps(self, steps: list[dict[str, Any]] | None) -> None:
        if steps is None:
            return
        if not isinstance(steps, list):
            raise AllureValidationError("Steps must be a list")

        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                raise AllureValidationError(f"Step {i} must be a dictionary")
            # ... minimal validation, details handled by DTO
