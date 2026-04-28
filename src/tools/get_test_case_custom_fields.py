from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_case_service import TestCaseService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output


async def get_test_case_custom_fields(
    test_case_id: Annotated[int, Field(description="The ID of the test case to retrieve custom fields for")],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Retrieve custom field values for a specific test case.

    Args:
        test_case_id: The ID of the test case.
        project_id: Optional project ID override.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        A dictionary where keys are custom field names and values are
        either a single string value or a list of string values.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = TestCaseService(client=client)
        cf_values = await service.get_test_case_custom_fields_values(test_case_id)

        if not cf_values:
            return render_output(
                plain=f"Test Case {test_case_id} has no custom field values set.",
                json_payload={"test_case_id": test_case_id, "custom_fields": {}},
                output_format=output_format,
            )

        lines = [f"Custom Fields for Test Case {test_case_id}:"]
        for name, value in cf_values.items():
            val_str = ", ".join(value) if isinstance(value, list) else str(value)
            lines.append(f"- {name}: {val_str}")
        return render_output(
            plain="\n".join(lines),
            json_payload={"test_case_id": test_case_id, "custom_fields": cf_values},
            output_format=output_format,
        )
