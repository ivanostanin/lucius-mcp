from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client import (
    AllureClient,
    PageSharedStepDto,
    SharedStepAttachmentRowDto,
    SharedStepDto,
)
from src.client.exceptions import AllureValidationError
from src.services.shared_step_service import SharedStepService


@pytest.fixture
def mock_client():
    client = MagicMock(spec=AllureClient)
    client.create_shared_step = AsyncMock()
    client.create_shared_step_scenario_step = AsyncMock()
    client.patch_shared_step_scenario_step = AsyncMock()
    client.list_shared_steps = AsyncMock()
    client.upload_shared_step_attachment = AsyncMock()
    client.get_project.return_value = 1
    return client


@pytest.fixture
def service(mock_client):
    return SharedStepService(client=mock_client)


@pytest.mark.asyncio
async def test_create_shared_step_success(service, mock_client):
    """Test creating a shared step with steps and attachments."""
    mock_client.create_shared_step.return_value = SharedStepDto(id=100, name="Shared Step", project_id=1)
    # Use generic objects for step response to avoid oneOf validation issues during test
    action_mock = MagicMock()
    action_mock.created_step_id = 201

    expected_mock = MagicMock()
    expected_mock.created_step_id = 202

    att_mock = MagicMock()
    att_mock.created_step_id = 203

    mock_client.create_shared_step_scenario_step.side_effect = [
        action_mock,  # Action
        expected_mock,  # Expected
        att_mock,  # Attachment step
    ]
    mock_client.upload_shared_step_attachment.return_value = [SharedStepAttachmentRowDto(id=500, name="file.txt")]

    steps = [
        {
            "action": "Do something",
            "expected": "Something happens",
            "attachments": [{"name": "file.txt", "content": "Zm9vYmFy"}],
        }
    ]

    result = await service.create_shared_step(name="Shared Step", steps=steps)

    assert result.id == 100
    mock_client.create_shared_step.assert_called_once_with(1, "Shared Step")

    # Check step creation calls
    assert mock_client.create_shared_step_scenario_step.call_count == 3
    mock_client.patch_shared_step_scenario_step.assert_called_once()

    # 1. Action
    action_call = mock_client.create_shared_step_scenario_step.call_args_list[0]
    assert action_call[0][0].body == "Do something"
    assert action_call[0][0].shared_step_id == 100

    # Patch expected result on action step
    patch_call = mock_client.patch_shared_step_scenario_step.call_args
    assert patch_call.kwargs["step_id"] == 201
    assert patch_call.kwargs["patch"].body == "Do something"
    assert patch_call.kwargs["patch"].expected_result == "Something happens"

    # 2. Expected
    expected_call = mock_client.create_shared_step_scenario_step.call_args_list[1]
    assert expected_call[0][0].body == "Something happens"
    assert expected_call[0][0].parent_id == 201

    # 3. Attachment
    att_call = mock_client.create_shared_step_scenario_step.call_args_list[2]
    assert att_call[0][0].attachment_id == 500
    assert att_call[0][0].parent_id == 201


@pytest.mark.asyncio
async def test_list_shared_steps_success(service, mock_client):
    """Test listing shared steps."""
    mock_page = PageSharedStepDto(
        content=[
            SharedStepDto(id=1, name="Step 1", steps_count=5),
            SharedStepDto(id=2, name="Step 2", steps_count=3),
        ],
        total_elements=2,
    )
    mock_client.list_shared_steps.return_value = mock_page

    result = await service.list_shared_steps(search="Step")

    assert len(result) == 2
    assert result[0].name == "Step 1"
    mock_client.list_shared_steps.assert_called_once_with(project_id=1, page=0, size=100, search="Step", archived=None)


@pytest.mark.asyncio
async def test_create_shared_step_fail_validation(service):
    """Test validation errors."""
    service._project_id = -1
    with pytest.raises(AllureValidationError):
        await service.create_shared_step(name="Valid")

    service._project_id = 1
    with pytest.raises(AllureValidationError):
        await service.create_shared_step(name="")


# ==========================================
# Update Shared Step Tests (Story 2.2)
# ==========================================


@pytest.mark.asyncio
async def test_get_shared_step_success(service, mock_client):
    """Test getting a shared step."""
    expected_step = SharedStepDto(id=100, name="Test Step", project_id=1, steps_count=3)
    mock_client.get_shared_step = AsyncMock(return_value=expected_step)

    result = await service.get_shared_step(step_id=100)

    assert result.id == 100
    assert result.name == "Test Step"
    mock_client.get_shared_step.assert_called_once_with(100)


@pytest.mark.priority("P0")
@pytest.mark.asyncio
async def test_update_shared_step_success(service, mock_client):
    """
    Test updating a shared step with name changes.
    ID: 2.2-UNIT-001
    """
    current_step = SharedStepDto(id=100, name="Old Name", project_id=1)
    updated_step = SharedStepDto(id=100, name="New Name", project_id=1)

    mock_client.get_shared_step = AsyncMock(return_value=current_step)
    mock_client.update_shared_step = AsyncMock(return_value=updated_step)

    result, changed = await service.update_shared_step(step_id=100, name="New Name")

    assert result.name == "New Name"
    assert changed is True
    mock_client.get_shared_step.assert_called_once_with(100)
    mock_client.update_shared_step.assert_called_once()


@pytest.mark.priority("P2")
@pytest.mark.asyncio
async def test_update_shared_step_idempotent(service, mock_client):
    """
    Test idempotency - no update if data matches current state.
    ID: 2.2-UNIT-002
    """
    current_step = SharedStepDto(id=100, name="Same Name", project_id=1)

    mock_client.get_shared_step = AsyncMock(return_value=current_step)
    mock_client.update_shared_step = AsyncMock()

    result, changed = await service.update_shared_step(step_id=100, name="Same Name")

    assert result.name == "Same Name"
    assert changed is False
    mock_client.get_shared_step.assert_called_once_with(100)
    # Should NOT call update_shared_step
    mock_client.update_shared_step.assert_not_called()


@pytest.mark.priority("P2")
@pytest.mark.asyncio
async def test_update_shared_step_partial_update(service, mock_client):
    """
    Test partial update with only some fields provided.
    ID: 2.2-UNIT-003
    """
    current_step = SharedStepDto(id=100, name="Current Name", project_id=1, description="Old Desc")
    updated_step = SharedStepDto(id=100, name="Current Name", project_id=1, description="New Desc")

    mock_client.get_shared_step = AsyncMock(return_value=current_step)
    mock_client.update_shared_step = AsyncMock(return_value=updated_step)

    # Only update description, leave name unchanged
    result, changed = await service.update_shared_step(step_id=100, description="New Desc")

    assert result is not None
    assert changed is True
    mock_client.update_shared_step.assert_called_once()


# ==========================================
# Delete Shared Step Tests (Story 2.2)
# ==========================================


@pytest.mark.priority("P0")
@pytest.mark.asyncio
async def test_delete_shared_step_success(service, mock_client):
    """
    Test deleting a shared step successfully.
    ID: 2.2-UNIT-004
    """
    mock_client.delete_shared_step = AsyncMock()

    await service.delete_shared_step(step_id=100)

    mock_client.delete_shared_step.assert_called_once_with(100)


@pytest.mark.priority("P2")
@pytest.mark.asyncio
async def test_delete_shared_step_idempotent(service, mock_client):
    """
    Test delete is idempotent (soft delete pattern from Story 1.5).
    ID: 2.2-UNIT-005
    """
    from src.client.exceptions import AllureNotFoundError

    # First call succeeds
    mock_client.delete_shared_step = AsyncMock()

    await service.delete_shared_step(step_id=100)
    mock_client.delete_shared_step.assert_called_once()

    # Second call with already-deleted step - should handle gracefully
    mock_client.delete_shared_step = AsyncMock(side_effect=AllureNotFoundError("Not found", 404, "{}"))

    # Should not raise, just return gracefully
    await service.delete_shared_step(step_id=100)
