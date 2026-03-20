"""Cleanup tools for permanently removing archived entities."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.custom_field_service import CustomFieldService
from src.services.shared_step_service import SharedStepService
from src.services.test_case_service import TestCaseService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, render_output

DESTRUCTIVE_CONFIRMATION_MESSAGE = "⚠️ Destructive operation. Pass confirm=True to proceed."


async def delete_archived_test_cases(
    confirm: Annotated[bool, Field(description="Must be set to True to proceed.")] = False,
    project_id: Annotated[int | None, Field(description="Optional Allure TestOps project ID override.")] = None,
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """Permanently delete all archived/deleted test cases in the current project.

    Args:
        confirm: Must be set to True to proceed.
        project_id: Optional Allure TestOps project ID override.
        output_format: Output format: plain (default) or json.
    """
    if not confirm:
        return render_output(
            plain=DESTRUCTIVE_CONFIRMATION_MESSAGE,
            json_payload={
                "requires_confirmation": True,
                "action": "delete_archived_test_cases",
            },
            output_format=output_format,
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client=client)
        deleted_count = await service.cleanup_archived()
        return render_output(
            plain=f"Deleted {deleted_count} archived test case(s).",
            json_payload={"deleted_count": deleted_count},
            output_format=output_format,
        )


async def delete_archived_shared_steps(
    confirm: Annotated[bool, Field(description="Must be set to True to proceed.")] = False,
    project_id: Annotated[int | None, Field(description="Optional Allure TestOps project ID override.")] = None,
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """Permanently delete all archived shared steps in the current project.

    Args:
        confirm: Must be set to True to proceed.
        project_id: Optional Allure TestOps project ID override.
        output_format: Output format: plain (default) or json.
    """
    if not confirm:
        return render_output(
            plain=DESTRUCTIVE_CONFIRMATION_MESSAGE,
            json_payload={
                "requires_confirmation": True,
                "action": "delete_archived_shared_steps",
            },
            output_format=output_format,
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = SharedStepService(client=client)
        deleted_count = await service.cleanup_archived()
        return render_output(
            plain=f"Deleted {deleted_count} archived shared step(s).",
            json_payload={"deleted_count": deleted_count},
            output_format=output_format,
        )


async def delete_unused_custom_fields(
    confirm: Annotated[bool, Field(description="Must be set to True to proceed.")] = False,
    project_id: Annotated[int | None, Field(description="Optional Allure TestOps project ID override.")] = None,
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """Delete custom fields that are unused by any test case in the current project.

    Args:
        confirm: Must be set to True to proceed.
        project_id: Optional Allure TestOps project ID override.
        output_format: Output format: plain (default) or json.
    """
    if not confirm:
        return render_output(
            plain=DESTRUCTIVE_CONFIRMATION_MESSAGE,
            json_payload={
                "requires_confirmation": True,
                "action": "delete_unused_custom_fields",
            },
            output_format=output_format,
        )

    async with AllureClient.from_env(project=project_id) as client:
        service = CustomFieldService(client=client)
        deleted_count = await service.cleanup_unused()
        return render_output(
            plain=f"Deleted {deleted_count} unused custom field(s).",
            json_payload={"deleted_count": deleted_count},
            output_format=output_format,
        )
