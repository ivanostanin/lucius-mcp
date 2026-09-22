from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.client.generated.models import (
    LaunchDto,
    TestPlanDto,
    TreeSelectionDto,
)
from src.services.plan_service import PlanService


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock(spec=AllureClient)
    client.api_client = Mock()
    client.get_project.return_value = 1
    return client


@pytest.fixture
def service(mock_client: AsyncMock) -> PlanService:
    return PlanService(mock_client)


@pytest.mark.asyncio
async def test_create_plan_manual(service: PlanService, mock_client: AsyncMock) -> None:
    """Test creating a plan with manual test case selection."""
    name = "Manual Plan"
    ids = [100, 101]

    # Mock create response
    created_plan = TestPlanDto(id=1, name=name, project_id=1)
    # Mock get response (after update)
    updated_plan = TestPlanDto(id=1, name=name, project_id=1, tree_selection=TreeSelectionDto(leafs_include=ids))

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value
        mock_api.create7.return_value = "create_coro"
        mock_api.patch7.return_value = "patch_coro"
        mock_api.find_one6.return_value = "find_coro"

        # Sequence:
        # 1. create7 -> created_plan
        # 2. update_plan_content -> get_plan -> created_plan (as current)
        # 3. update_plan_content -> patch
        # 4. update_plan_content -> get_plan -> updated_plan
        # 5. create_plan -> get_plan -> updated_plan
        mock_client._call_api.side_effect = [created_plan, created_plan, "patch_res", updated_plan, updated_plan]

        result = await service.create_plan(name, test_case_ids=ids)

        assert result == updated_plan

        # Verify Create called
        mock_api.create7.assert_called_once()
        create_dto = mock_api.create7.call_args.kwargs["test_plan_create_dto"]
        assert create_dto.name == name

        # Verify Patch called (for content)
        mock_api.patch7.assert_called_once()
        patch_dto = mock_api.patch7.call_args.kwargs["test_plan_patch_dto"]
        assert set(patch_dto.tree_selection.leafs_include) == set(ids)


@pytest.mark.asyncio
async def test_create_plan_filter(service: PlanService, mock_client: AsyncMock) -> None:
    """Test creating a plan with AQL filter."""
    name = "Filter Plan"
    aql = 'status="active"'

    created_plan = TestPlanDto(id=2, name=name)
    updated_plan = TestPlanDto(id=2, name=name, base_rql='status = "active"')

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value
        mock_api.create7.return_value = "create_coro"
        mock_api.patch7.return_value = "patch_coro"
        mock_api.find_one6.return_value = "find_coro"

        # Same sequence as manual creation
        mock_client._call_api.side_effect = [created_plan, created_plan, "patch_res", updated_plan, updated_plan]

        result = await service.create_plan(name, aql_filter=aql)

        assert result.base_rql == 'status = "active"'

        # Verify Patch call
        patch_dto = mock_api.patch7.call_args.kwargs["test_plan_patch_dto"]
        assert patch_dto.base_rql == 'status = "active"'


@pytest.mark.asyncio
async def test_update_plan_content_normalizes_tag_shorthand_aql(service: PlanService, mock_client: AsyncMock) -> None:
    plan_id = 1
    current_plan = TestPlanDto(id=plan_id, tree_selection=TreeSelectionDto(leafs_include=[]))
    updated_plan = TestPlanDto(id=plan_id, base_rql='tag = "smoke" and tag = "regression"')

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value
        mock_api.find_one6.return_value = "find_coro"
        mock_api.patch7.return_value = "patch_coro"

        mock_client._call_api.side_effect = [current_plan, "patch_res", updated_plan]

        result = await service.update_plan_content(plan_id=plan_id, aql_filter="tag:smoke tag:regression")

        assert result.base_rql == 'tag = "smoke" and tag = "regression"'
        patch_dto = mock_api.patch7.call_args.kwargs["test_plan_patch_dto"]
        assert patch_dto.base_rql == 'tag = "smoke" and tag = "regression"'


@pytest.mark.asyncio
async def test_create_plan_rejects_blank_aql_filter(service: PlanService) -> None:
    with pytest.raises(Exception, match="AQL filter must be a non-empty string when provided"):
        await service.create_plan("Blank Filter Plan", aql_filter="   ")


@pytest.mark.asyncio
async def test_update_plan_content_rejects_blank_aql_filter(service: PlanService) -> None:
    with pytest.raises(Exception, match="AQL filter must be a non-empty string when provided"):
        await service.update_plan_content(plan_id=1, aql_filter="   ")


@pytest.mark.asyncio
async def test_add_cases_to_plan(service: PlanService, mock_client: AsyncMock) -> None:
    """Test adding cases to an existing plan."""
    plan_id = 1
    existing_ids = [10]
    new_ids = [20]

    current_plan = TestPlanDto(id=plan_id, tree_selection=TreeSelectionDto(leafs_include=existing_ids))

    updated_plan_dto = TestPlanDto(id=plan_id, tree_selection=TreeSelectionDto(leafs_include=existing_ids + new_ids))

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value
        # Sequence: get_plan -> patch -> get_plan
        mock_api.find_one6.return_value = "find_coro"
        mock_api.patch7.return_value = "patch_coro"

        mock_client._call_api.side_effect = [current_plan, "patch_res", updated_plan_dto]

        await service.add_cases_to_plan(plan_id, new_ids)

        mock_api.patch7.assert_called_once()
        patch_dto = mock_api.patch7.call_args.kwargs["test_plan_patch_dto"]
        assert set(patch_dto.tree_selection.leafs_include) == {10, 20}
        # Explicit excluded should be empty if not set
        assert not patch_dto.tree_selection.leafs_exclude


@pytest.mark.asyncio
async def test_remove_cases_from_plan(service: PlanService, mock_client: AsyncMock) -> None:
    """Test removing cases from a manual plan."""
    plan_id = 1
    existing_ids = [10, 20]
    remove_ids = [20]

    current_plan = TestPlanDto(id=plan_id, tree_selection=TreeSelectionDto(leafs_include=existing_ids))

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value

        mock_client._call_api.side_effect = [current_plan, "patch_res", "final_plan"]

        await service.remove_cases_from_plan(plan_id, remove_ids)

        mock_api.patch7.assert_called_once()
        patch_dto = mock_api.patch7.call_args.kwargs["test_plan_patch_dto"]
        # Should contain only 10
        assert set(patch_dto.tree_selection.leafs_include) == {10}
        # 20 removed from include, usually not added to exclude unless it was filter based?
        # Logic says: difference_update on include.
        assert not patch_dto.tree_selection.leafs_exclude


@pytest.mark.asyncio
async def test_remove_cases_from_filter_plan(service: PlanService, mock_client: AsyncMock) -> None:
    """Test removing cases from a filter-based plan (should add to exclude)."""
    plan_id = 1
    remove_ids = [30]

    current_plan = TestPlanDto(
        id=plan_id, base_rql="some query", tree_selection=TreeSelectionDto(leafs_include=[], leafs_exclude=[5])
    )

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value

        mock_client._call_api.side_effect = [current_plan, "patch_res", "final_plan"]

        await service.remove_cases_from_plan(plan_id, remove_ids)

        mock_api.patch7.assert_called_once()
        patch_dto = mock_api.patch7.call_args.kwargs["test_plan_patch_dto"]
        # Should now have 5 and 30 in exclude
        assert set(patch_dto.tree_selection.leafs_exclude) == {5, 30}


@pytest.mark.asyncio
async def test_list_plans(service: PlanService, mock_client: AsyncMock) -> None:
    """Test listing plans."""

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value

        mock_response = Mock()
        mock_response.content = [TestPlanDto(id=1, name="P1")]
        mock_client._call_api.return_value = mock_response

        plans = await service.list_plans(page=0, size=10)

        assert len(plans) == 1
        assert plans[0].name == "P1"

        mock_api.find_all_by_project.assert_called_once_with(project_id=1, page=0, size=10, sort=["id,desc"])


@pytest.mark.asyncio
async def test_update_plan(service: PlanService, mock_client: AsyncMock) -> None:
    """Test updating plan metadata."""
    plan_id = 1
    name = "New Name"

    current_plan = TestPlanDto(id=plan_id, name="Old Name")
    updated_plan = TestPlanDto(id=plan_id, name=name)

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value
        mock_api.find_one6.return_value = "find_coro"
        mock_api.patch7.return_value = "patch_coro"

        mock_client._call_api.side_effect = [current_plan, "patch_res", updated_plan]

        result = await service.update_plan(plan_id, name=name)

        assert result == updated_plan

        mock_api.patch7.assert_called_once()
        patch_dto = mock_api.patch7.call_args.kwargs["test_plan_patch_dto"]
        assert patch_dto.name == name


@pytest.mark.asyncio
async def test_delete_plan(service: PlanService, mock_client: AsyncMock) -> None:
    """Test deleting a plan."""
    plan_id = 1

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value
        mock_api.delete7.return_value = "delete_coro"
        mock_client._call_api.return_value = None

        await service.delete_plan(plan_id)

        mock_api.delete7.assert_called_once_with(id=plan_id)


@pytest.mark.asyncio
async def test_delete_plan_not_found(service: PlanService, mock_client: AsyncMock) -> None:
    """Test deleting a non-existent plan (should be idempotent)."""
    plan_id = 1

    from src.client.exceptions import AllureNotFoundError

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value
        mock_api.delete7.return_value = "delete_coro"

        # Simulate 404
        mock_client._call_api.side_effect = AllureNotFoundError("Not found")

        # Should not raise exception
        await service.delete_plan(plan_id)

        mock_api.delete7.assert_called_once_with(id=plan_id)


@pytest.mark.asyncio
async def test_run_plan_starts_launch_from_plan(service: PlanService, mock_client: AsyncMock) -> None:
    """Test running a plan starts a launch via the run3 operation."""
    launch = LaunchDto(id=500, name="Nightly Run", project_id=1)

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value
        mock_api.run3.return_value = "run_coro"
        mock_client._call_api.return_value = launch

        result = await service.run_plan(plan_id=10, launch_name="Nightly Run")

        assert result == launch
        mock_api.run3.assert_called_once()
        call_kwargs = mock_api.run3.call_args.kwargs
        assert call_kwargs["id"] == 10
        request = call_kwargs["test_plan_run_request_dto"]
        assert request.launch_name == "Nightly Run"
        assert request.env_var_value_sets is None
        assert request.issues is None
        assert request.links is None
        assert request.tags is None


@pytest.mark.asyncio
async def test_run_plan_maps_simplified_enrichment_inputs(service: PlanService, mock_client: AsyncMock) -> None:
    """Test running a plan maps tags/links/issues like create_launch."""
    launch = LaunchDto(id=501, name="Enriched Run", project_id=1)

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value
        mock_api.run3.return_value = "run_coro"
        mock_client._call_api.return_value = launch

        await service.run_plan(
            plan_id=10,
            launch_name="Enriched Run",
            tags=["smoke", "regression"],
            links=[{"name": "Docs", "url": "https://example.com", "type": "issue"}],
            issues=[{"name": "ISSUE-1"}],
        )

        request = mock_api.run3.call_args.kwargs["test_plan_run_request_dto"]
        assert [tag.name for tag in (request.tags or [])] == ["smoke", "regression"]
        assert request.links is not None
        assert request.links[0].name == "Docs"
        assert request.links[0].url == "https://example.com"
        assert request.links[0].type == "issue"
        assert request.issues is not None
        assert request.issues[0].name == "ISSUE-1"
        assert request.env_var_value_sets is None


@pytest.mark.asyncio
async def test_run_plan_rejects_empty_launch_name(service: PlanService, mock_client: AsyncMock) -> None:
    """Test running a plan rejects an empty or whitespace launch name."""
    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        with pytest.raises(AllureValidationError, match="Launch name is required"):
            await service.run_plan(plan_id=1, launch_name="   ")
        mock_controller.return_value.run3.assert_not_called()
        mock_client._call_api.assert_not_called()


@pytest.mark.asyncio
async def test_run_plan_rejects_non_string_launch_name(service: PlanService) -> None:
    """Test running a plan rejects a non-string launch name."""
    with pytest.raises(AllureValidationError, match="Launch name must be a string"):
        await service.run_plan(plan_id=1, launch_name=None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_run_plan_rejects_overlong_launch_name(service: PlanService) -> None:
    """Test running a plan rejects a launch name longer than 255 characters."""
    with pytest.raises(AllureValidationError, match="255 characters or less"):
        await service.run_plan(plan_id=1, launch_name="x" * 256)


@pytest.mark.asyncio
async def test_run_plan_rejects_invalid_tags(service: PlanService) -> None:
    """Test running a plan rejects malformed tag entries."""
    with pytest.raises(AllureValidationError, match="Tag at index 1 must be a string"):
        await service.run_plan(plan_id=1, launch_name="Ok", tags=["smoke", 7])


@pytest.mark.asyncio
async def test_run_plan_rejects_invalid_links(service: PlanService) -> None:
    """Test running a plan rejects malformed link entries."""
    with pytest.raises(AllureValidationError, match="Link at index 0 'url' must be a string"):
        await service.run_plan(plan_id=1, launch_name="Ok", links=[{"url": 123}])


@pytest.mark.asyncio
async def test_run_plan_rejects_invalid_issues(service: PlanService) -> None:
    """Test running a plan rejects malformed issue entries."""
    with pytest.raises(AllureValidationError, match="Issue at index 0 must be a dictionary"):
        await service.run_plan(plan_id=1, launch_name="Ok", issues=["oops"])


@pytest.mark.asyncio
async def test_run_plan_dto_validation_failure_surfaces_schema_hint(service: PlanService) -> None:
    """Test running a plan surfaces a schema hint when the upstream DTO rejects input."""
    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        with pytest.raises(AllureValidationError, match="Invalid test plan run request") as exc_info:
            await service.run_plan(plan_id=1, launch_name="Ok", issues=[{"id": "not-an-int"}])
        suggestions = exc_info.value.suggestions or []
        assert any("launchName" in suggestion for suggestion in suggestions)
        mock_controller.return_value.run3.assert_not_called()


@pytest.mark.asyncio
async def test_run_plan_maps_unknown_plan_to_actionable_not_found(service: PlanService, mock_client: AsyncMock) -> None:
    """Test running an unknown plan maps upstream 404s to plan context."""
    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value
        mock_api.run3.return_value = "run_coro"
        mock_client._call_api.side_effect = AllureNotFoundError("Not found")

        with pytest.raises(AllureNotFoundError, match="Test plan ID 42 not found or is not runnable"):
            await service.run_plan(plan_id=42, launch_name="Nightly")
