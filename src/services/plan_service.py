import logging

from pydantic import ValidationError as PydanticValidationError

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.client.generated.api.test_plan_controller_api import TestPlanControllerApi
from src.client.generated.models.launch_dto import LaunchDto
from src.client.generated.models.test_plan_create_dto import TestPlanCreateDto
from src.client.generated.models.test_plan_dto import TestPlanDto
from src.client.generated.models.test_plan_patch_dto import TestPlanPatchDto
from src.client.generated.models.test_plan_run_request_dto import TestPlanRunRequestDto
from src.client.generated.models.tree_selection_dto import TreeSelectionDto
from src.services.launch_inputs import (
    build_issue_dtos,
    build_link_dtos,
    build_tag_dtos,
    validate_issues,
    validate_launch_name,
    validate_links,
    validate_tags,
)
from src.utils.aql import normalize_aql
from src.utils.schema_hint import generate_schema_hint

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
        if aql_filter is not None and not aql_filter.strip():
            raise AllureValidationError("AQL filter must be a non-empty string when provided")

        if not test_case_ids and not aql_filter:
            # Allow empty plans, but log warning if neither provided?
            # Story doesn't strictly forbid empty plans, useful for setting up structure.
            pass

        create_dto = TestPlanCreateDto(
            name=name,
            project_id=self._project_id,
        )
        normalized_aql = normalize_aql(aql_filter) if aql_filter else None

        plan = await self._client._call_api(self._api.create7(test_plan_create_dto=create_dto))

        # Apply selection/filter if needed
        if test_case_ids or normalized_aql:
            # Ensure plan has an ID
            if plan.id is None:
                raise AllureValidationError("Created plan returned no ID")

            await self.update_plan_content(plan_id=plan.id, test_case_ids_add=test_case_ids, aql_filter=normalized_aql)
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
        if aql_filter is not None and not aql_filter.strip():
            raise AllureValidationError("AQL filter must be a non-empty string when provided")

        current = await self.get_plan(plan_id)
        normalized_aql = normalize_aql(aql_filter) if aql_filter is not None else None

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
            if current.base_rql or normalized_aql:
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
            tree_selection=new_selection,
            base_rql=normalized_aql if normalized_aql is not None else current.base_rql,
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

    async def run_plan(
        self,
        plan_id: int,
        launch_name: str,
        issues: list[dict[str, object]] | None = None,
        links: list[dict[str, str]] | None = None,
        tags: list[str] | None = None,
    ) -> LaunchDto:
        """Start a launch from an existing test plan.

        Validates the simplified inputs locally, maps them onto the upstream
        run request, and returns the created launch without further hydration.

        Args:
            plan_id: ID of the test plan to run.
            launch_name: Name for the launch created from the plan (1-255 characters).
            issues: Optional list of issue dictionaries.
            links: Optional list of external link dictionaries.
            tags: Optional list of launch tags.

        Returns:
            The created launch.
        """
        validate_launch_name(launch_name)
        validate_tags(tags)
        validate_links(links)
        validate_issues(issues)

        try:
            run_request = TestPlanRunRequestDto(
                launch_name=launch_name,
                issues=build_issue_dtos(issues),
                links=build_link_dtos(links),
                tags=build_tag_dtos(tags),
            )
        except PydanticValidationError as e:
            hint = generate_schema_hint(TestPlanRunRequestDto)
            raise AllureValidationError(f"Invalid test plan run request: {e}", suggestions=[hint]) from e

        try:
            return await self._client._call_api(self._api.run3(id=plan_id, test_plan_run_request_dto=run_request))
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Test plan ID {plan_id} not found or is not runnable",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

    async def delete_plan(self, plan_id: int) -> None:
        """Delete a test plan."""
        try:
            await self._client._call_api(self._api.delete7(id=plan_id))
        except AllureNotFoundError:
            # Idempotent behavior: if plan is already gone, consider it success
            logger.info("Test plan %s not found during deletion (treated as success)", plan_id)
