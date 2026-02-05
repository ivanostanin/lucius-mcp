from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.custom_field_value_service import CustomFieldValueService


async def list_custom_field_values(
    custom_field_id: Annotated[
        int | None, Field(description="Project-scoped custom field ID to list values for.")
    ] = None,
    custom_field_name: Annotated[
        str | None,
        Field(description="Custom field name to resolve when custom_field_id is not provided."),
    ] = None,
    query: Annotated[str | None, Field(description="Optional search query to filter values.")] = None,
    var_global: Annotated[bool | None, Field(description="Optional filter for global values.")] = None,
    test_case_search: Annotated[
        str | None,
        Field(description="Optional test case search filter to match values in test cases."),
    ] = None,
    page: Annotated[int | None, Field(description="Zero-based page index.")] = None,
    size: Annotated[int | None, Field(description="Number of items per page.")] = None,
    sort: Annotated[
        list[str] | None,
        Field(description="Optional sort criteria, e.g. ['name,asc', 'id,desc']"),
    ] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
) -> str:
    """List available values for a custom field.

    Args:
        custom_field_id: Project-scoped custom field ID to list values for.
        custom_field_name: Custom field name to resolve when custom_field_id is not provided.
        query: Optional search query to filter values.
        var_global: Optional filter for global values.
        test_case_search: Optional test case search filter to match values in test cases.
        page: Zero-based page index.
        size: Number of items per page.
        sort: Optional sort criteria, e.g. ["name,asc", "id,desc"].
        project_id: Optional override for the default Project ID.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = CustomFieldValueService(client=client)
        result = await service.list_custom_field_values(
            project_id=project_id,
            custom_field_id=custom_field_id,
            custom_field_name=custom_field_name,
            query=query,
            var_global=var_global,
            test_case_search=test_case_search,
            page=page,
            size=size,
            sort=sort,
        )

        values = result.content or []
        if not values:
            return "No custom field values found."

        total = result.total_elements if result.total_elements is not None else len(values)
        header = f"Found {total} custom field values:"
        if result.number is not None and result.total_pages is not None:
            header = f"Found {total} custom field values (page {result.number + 1}/{result.total_pages}):"

        lines = [header]
        for value in values:
            count = value.test_cases_count if value.test_cases_count is not None else 0
            lines.append(f"- ID: {value.id}, Name: {value.name}, Test cases: {count}")

        return "\n".join(lines)
