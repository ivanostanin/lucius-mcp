import logging

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.generated.api.test_plan_controller_api import TestPlanControllerApi
from src.client.generated.models.test_plan_create_dto import TestPlanCreateDto
from src.client.generated.models.test_plan_dto import TestPlanDto
from src.client.generated.models.test_plan_patch_dto import TestPlanPatchDto
from src.client.generated.models.tree_selection_dto import TreeSelectionDto

logger = logging.getLogger(__name__)


class PlanService:
    """Service for managing Test Plans in Allure TestOps."""

    def __init__(self, client: AllureClient) -> None:
        self._client = client
        self._project_id = client.get_project()

    @property
    def _api(self) -> TestPlanControllerApi:
        return TestPlanControllerApi(self._client.api_client)

    async def create_plan(
        self,
        name: str,
        test_case_ids: list[int] | None = None,
        aql_filter: str | None = None,
    ) -> TestPlanDto:
        """Create a new test plan.

        Args:
            name: Plan name.
            test_case_ids: List of specific test case IDs to include.
            aql_filter: AQL query to select test cases.

        Returns:
            Created Test Plan DTO.
        """
        if not name:
            raise AllureValidationError("Test Plan name is required")

        if not test_case_ids and not aql_filter:
            # Allow empty plans, but log warning if neither provided?
            # Story doesn't strictly forbid empty plans, useful for setting up structure.
            pass

        create_dto = TestPlanCreateDto(
            name=name,
            project_id=self._project_id,
        )

        plan = await self._client._call_api(self._api.create7(test_plan_create_dto=create_dto))

        # Apply selection/filter if needed
        if test_case_ids or aql_filter:
            # Ensure plan has an ID
            if plan.id is None:
                raise AllureValidationError("Created plan returned no ID")

            await self.update_plan_content(plan_id=plan.id, test_case_ids_add=test_case_ids, aql_filter=aql_filter)
            # Re-fetch
            plan = await self.get_plan(plan.id)

        return plan

    async def get_plan(self, plan_id: int) -> TestPlanDto:
        """Get a test plan by ID."""
        return await self._client._call_api(self._api.find_one6(id=plan_id))

    async def update_plan(
        self,
        plan_id: int,
        name: str | None = None,
    ) -> TestPlanDto:
        """Update a test plan's metadata."""
        await self.get_plan(plan_id)

        # Build Patch DTO
        # Note: TestPlanPatchDto might not have all fields (e.g. description/tags might separate?)
        patch = TestPlanPatchDto(
            name=name,
        )

        # If patch has keys (ignoring None), call update
        if patch.to_dict():
            await self._client._call_api(self._api.patch7(id=plan_id, test_plan_patch_dto=patch))

        return await self.get_plan(plan_id)

    async def update_plan_content(
        self,
        plan_id: int,
        test_case_ids_add: list[int] | None = None,
        test_case_ids_remove: list[int] | None = None,
        aql_filter: str | None = None,
    ) -> TestPlanDto:
        """Update plan content (selection/filter)."""
        current = await self.get_plan(plan_id)

        current_selection = current.tree_selection or TreeSelectionDto()
        current_leafs_include = set(current_selection.leafs_include or [])
        current_leafs_exclude = set(current_selection.leafs_exclude or [])

        if test_case_ids_add:
            current_leafs_include.update(test_case_ids_add)
            # If added, ensure not in exclude
            current_leafs_exclude.difference_update(test_case_ids_add)

        if test_case_ids_remove:
            # If in include, remove
            current_leafs_include.difference_update(test_case_ids_remove)
            # If the plan has a base_rql, removing a case means adding to exclude.
            if current.base_rql or aql_filter:
                current_leafs_exclude.update(test_case_ids_remove)

        new_selection = TreeSelectionDto(
            leafs_include=list(current_leafs_include),
            leafs_exclude=list(current_leafs_exclude),
            groups_include=current_selection.groups_include,
            groups_exclude=current_selection.groups_exclude,
            inverted=current_selection.inverted,
            path=current_selection.path,
        )

        patch = TestPlanPatchDto(
            tree_selection=new_selection, base_rql=aql_filter if aql_filter is not None else current.base_rql
        )

        await self._client._call_api(self._api.patch7(id=plan_id, test_plan_patch_dto=patch))

        return await self.get_plan(plan_id)

    async def add_cases_to_plan(self, plan_id: int, test_case_ids: list[int]) -> None:
        """Add test cases to a plan."""
        await self.update_plan_content(plan_id, test_case_ids_add=test_case_ids)

    async def remove_cases_from_plan(self, plan_id: int, test_case_ids: list[int]) -> None:
        """Remove test cases from a plan."""
        await self.update_plan_content(plan_id, test_case_ids_remove=test_case_ids)

    async def list_plans(self, page: int = 0, size: int = 100) -> list[TestPlanDto]:
        """List test plans."""
        response = await self._client._call_api(
            self._api.find_all_by_project(project_id=self._project_id, page=page, size=size, sort=["id,desc"])
        )
        return response.content or []
