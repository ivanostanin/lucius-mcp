"""Cleanup tools for permanently removing archived entities."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.custom_field_service import CustomFieldService
from src.services.shared_step_service import SharedStepService
from src.services.test_case_service import TestCaseService

DESTRUCTIVE_CONFIRMATION_MESSAGE = "⚠️ Destructive operation. Pass confirm=True to proceed."


async def delete_archived_test_cases(
    confirm: Annotated[bool, Field(description="Must be set to True to proceed.")] = False,
    project_id: Annotated[int | None, Field(description="Optional Allure TestOps project ID override.")] = None,
) -> str:
    """Permanently delete all archived/deleted test cases in the current project."""
    if not confirm:
        return DESTRUCTIVE_CONFIRMATION_MESSAGE

    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client=client)
        deleted_count = await service.cleanup_archived()
        return f"Deleted {deleted_count} archived test case(s)."


async def delete_archived_shared_steps(
    confirm: Annotated[bool, Field(description="Must be set to True to proceed.")] = False,
    project_id: Annotated[int | None, Field(description="Optional Allure TestOps project ID override.")] = None,
) -> str:
    """Permanently delete all archived shared steps in the current project."""
    if not confirm:
        return DESTRUCTIVE_CONFIRMATION_MESSAGE

    async with AllureClient.from_env(project=project_id) as client:
        service = SharedStepService(client=client)
        deleted_count = await service.cleanup_archived()
        return f"Deleted {deleted_count} archived shared step(s)."


async def delete_unused_custom_fields(
    confirm: Annotated[bool, Field(description="Must be set to True to proceed.")] = False,
    project_id: Annotated[int | None, Field(description="Optional Allure TestOps project ID override.")] = None,
) -> str:
    """Delete custom fields that are unused by any test case in the current project."""
    if not confirm:
        return DESTRUCTIVE_CONFIRMATION_MESSAGE

    async with AllureClient.from_env(project=project_id) as client:
        service = CustomFieldService(client=client)
        deleted_count = await service.cleanup_unused()
        return f"Deleted {deleted_count} unused custom field(s)."
