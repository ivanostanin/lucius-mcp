from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.client import AllureClient
from src.client.generated.models import (
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
    aql = "status = 'active'"

    created_plan = TestPlanDto(id=2, name=name)
    updated_plan = TestPlanDto(id=2, name=name, base_rql=aql)

    with patch("src.services.plan_service.TestPlanControllerApi") as mock_controller:
        mock_api = mock_controller.return_value
        mock_api.create7.return_value = "create_coro"
        mock_api.patch7.return_value = "patch_coro"
        mock_api.find_one6.return_value = "find_coro"

        # Same sequence as manual creation
        mock_client._call_api.side_effect = [created_plan, created_plan, "patch_res", updated_plan, updated_plan]

        result = await service.create_plan(name, aql_filter=aql)

        assert result.base_rql == aql

        # Verify Patch call
        patch_dto = mock_api.patch7.call_args.kwargs["test_plan_patch_dto"]
        assert patch_dto.base_rql == aql


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
