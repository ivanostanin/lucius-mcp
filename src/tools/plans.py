from typing import Annotated

from src.client import AllureClient
from src.services.plan_service import PlanService


async def create_test_plan(
    name: Annotated[str, "Name of the test plan"],
    test_case_ids: Annotated[list[int] | None, "List of Test Case IDs to include"] = None,
    aql_filter: Annotated[str | None, "AQL query to select test cases"] = None,
) -> str:
    """Create a new Test Plan in Allure TestOps.

    This tool allows creating a Test Plan, which is a collection of Test Cases
    to be executed. You can define the content of the plan either by:
    1. Explicitly listing Test Case IDs (`test_case_ids`).
    2. Providing an AQL (Allure Query Language) filter (`aql_filter`).
    3. Both (explicit selection + dynamic filter).

    Args:
        name: The display name for the new Test Plan.
        test_case_ids: Optional list of numeric Test Case IDs to include initially.
        aql_filter: Optional AQL query string to dynamically select test cases
            (e.g., 'tag in ["smoke", "regression"]').

    Returns:
        A success message containing the ID and Name of the created plan.
    """
    async with AllureClient.from_env() as client:
        service = PlanService(client)
        plan = await service.create_plan(
            name=name,
            test_case_ids=test_case_ids,
            aql_filter=aql_filter,
        )
        return f"Created Test Plan {plan.id}: '{plan.name}'"


async def update_test_plan(
    plan_id: Annotated[int, "ID of the test plan"],
    name: Annotated[str | None, "New name"] = None,
) -> str:
    """Update the metadata of an existing Test Plan.

    Currently, supports updating the name of the plan.

    Args:
        plan_id: The numeric ID of the Test Plan to update.
        name: The new name for the Test Plan.

    Returns:
        A success message confirming the update with the Plan ID and new Name.
    """
    async with AllureClient.from_env() as client:
        service = PlanService(client)
        plan = await service.update_plan(plan_id=plan_id, name=name)
        return f"Updated Test Plan {plan.id}: '{plan.name}'"


async def manage_test_plan_content(
    plan_id: Annotated[int, "ID of the test plan"],
    add_test_case_ids: Annotated[list[int] | None, "List of Test Case IDs to add"] = None,
    remove_test_case_ids: Annotated[list[int] | None, "List of Test Case IDs to remove"] = None,
    update_aql_filter: Annotated[str | None, "Update the AQL filter string"] = None,
) -> str:
    """Modify the content (Test Cases) of an existing Test Plan.

    Allows adding or removing specific Test Cases by ID, or updating the
    underlying AQL filter query.

    Args:
        plan_id: The numeric ID of the Test Plan to modify.
        add_test_case_ids: List of Test Case IDs to add to the plan.
        remove_test_case_ids: List of Test Case IDs to remove from the plan.
        update_aql_filter: New AQL query string to replace the existing one.
            Use this to change the dynamic criteria for test case selection.

    Returns:
        A success message confirming the content update.
    """
    async with AllureClient.from_env() as client:
        service = PlanService(client)
        await service.update_plan_content(
            plan_id=plan_id,
            test_case_ids_add=add_test_case_ids,
            test_case_ids_remove=remove_test_case_ids,
            aql_filter=update_aql_filter,
        )
        return f"Updated content for Test Plan {plan_id}"


async def list_test_plans(
    page: Annotated[int, "Page number (0-based)"] = 0,
    size: Annotated[int, "Page size"] = 100,
) -> str:
    """List Test Plans for the current project.

    Retrieves a paginated list of Test Plans, showing their IDs, names,
    and the number of test cases they contain.

    Args:
        page: The page number to retrieve (0-based index). Defaults to 0.
        size: The number of items per page. Defaults to 100.

    Returns:
        A formatted string listing the Test Plans found, or a message indicating
        no plans were found.
    """
    async with AllureClient.from_env() as client:
        service = PlanService(client)
        plans = await service.list_plans(page=page, size=size)

        if not plans:
            return "No test plans found."

        result = []
        for p in plans:
            # Note: test_cases_count field might be None
            count = p.test_cases_count or 0
            result.append(f"[{p.id}] {p.name} ({count} cases)")

        return "\n".join(result)


async def delete_test_plan(
    plan_id: Annotated[int, "ID of the test plan to delete"],
    confirm: Annotated[bool, "Must be set to True to proceed with deletion. Safety measure."] = False,
) -> str:
    """Delete a Test Plan.
    ⚠️ CAUTION: Destructive.

    Permanently removes the Test Plan from Allure TestOps.
    The operation is idempotent: if the plan does not exist, it returns success.

    Args:
        plan_id: The numeric ID of the Test Plan to delete.
        confirm: Must be set to True to proceed with deletion.

    Returns:
        A formatted success message or a warning if confirmation is missing.
    """
    if not confirm:
        return (
            "⚠️ Deletion requires confirmation.\n\n"
            "This action permanently deletes the Test Plan. "
            f"Please call again with confirm=True to proceed with deleting test plan {plan_id}."
        )

    async with AllureClient.from_env() as client:
        service = PlanService(client)
        await service.delete_plan(plan_id=plan_id)
        return f"Successfully deleted Test Plan {plan_id}."
