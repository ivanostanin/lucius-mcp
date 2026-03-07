"""Unit tests for cleanup service methods."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from src.client.exceptions import AllureNotFoundError
from src.services.custom_field_service import CustomFieldService
from src.services.shared_step_service import SharedStepService
from src.services.test_case_service import TestCaseService


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client.get_project.return_value = 1
    return client


@pytest.mark.asyncio
async def test_cleanup_archived_test_cases_force_deletes_archived_and_deleted(mock_client: MagicMock) -> None:
    service = TestCaseService(client=mock_client)
    mock_client.list_deleted_test_cases = AsyncMock(
        side_effect=[
            SimpleNamespace(
                content=[
                    SimpleNamespace(id=101, status=SimpleNamespace(name="Archived")),
                    SimpleNamespace(id=102, status=SimpleNamespace(name="Deleted")),
                ]
            ),
            SimpleNamespace(content=[SimpleNamespace(id=103, status=SimpleNamespace(name="Draft"))]),
        ]
    )
    mock_client.delete_test_case = AsyncMock()

    deleted_count = await service.cleanup_archived(page_size=2)

    assert deleted_count == 2
    assert mock_client.delete_test_case.await_args_list == [
        call(101, force=True),
        call(102, force=True),
    ]


@pytest.mark.asyncio
async def test_cleanup_archived_shared_steps_hard_deletes_archived_only(mock_client: MagicMock) -> None:
    service = SharedStepService(client=mock_client)
    mock_client.list_shared_steps = AsyncMock(
        side_effect=[
            SimpleNamespace(
                content=[
                    SimpleNamespace(id=11, archived=True),
                    SimpleNamespace(id=12, archived=False),
                    SimpleNamespace(id=13, archived=True),
                ]
            ),
            SimpleNamespace(content=[]),
        ]
    )
    mock_client.purge_shared_step = AsyncMock(side_effect=[None, AllureNotFoundError("not found")])

    deleted_count = await service.cleanup_archived(page_size=100)

    assert deleted_count == 1
    assert mock_client.purge_shared_step.await_args_list == [call(11), call(13)]


@pytest.mark.asyncio
async def test_cleanup_unused_custom_fields_removes_only_unused(mock_client: MagicMock) -> None:
    service = CustomFieldService(client=mock_client)
    mock_client.list_project_custom_fields = AsyncMock(
        side_effect=[
            [
                SimpleNamespace(custom_field=SimpleNamespace(id=201)),
                SimpleNamespace(custom_field=SimpleNamespace(id=202)),
                SimpleNamespace(custom_field=SimpleNamespace(id=202)),
            ],
            [],
        ]
    )
    mock_client.count_test_cases_in_projects = AsyncMock(
        side_effect=[
            [SimpleNamespace(id=1, test_case_count=3)],
            [SimpleNamespace(id=1, test_case_count=0)],
        ]
    )
    mock_client.remove_custom_field_from_project = AsyncMock()

    deleted_count = await service.cleanup_unused(page_size=100)

    assert deleted_count == 1
    assert mock_client.count_test_cases_in_projects.await_args_list == [
        call(project_ids=[1], custom_field_id=201, deleted=False),
        call(project_ids=[1], custom_field_id=202, deleted=False),
    ]
    mock_client.remove_custom_field_from_project.assert_awaited_once_with(custom_field_id=202, project_id=1)
