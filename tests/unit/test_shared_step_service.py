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
    client.list_shared_steps = AsyncMock()
    client.upload_shared_step_attachment = AsyncMock()
    return client


@pytest.fixture
def service(mock_client):
    return SharedStepService(mock_client)


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

    result = await service.create_shared_step(project_id=1, name="Shared Step", steps=steps)

    assert result.id == 100
    mock_client.create_shared_step.assert_called_once_with(1, "Shared Step")

    # Check step creation calls
    assert mock_client.create_shared_step_scenario_step.call_count == 3
    # 1. Action
    action_call = mock_client.create_shared_step_scenario_step.call_args_list[0]
    assert action_call[0][0].body == "Do something"
    assert action_call[0][0].shared_step_id == 100

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

    result = await service.list_shared_steps(project_id=1, search="Step")

    assert len(result) == 2
    assert result[0].name == "Step 1"
    mock_client.list_shared_steps.assert_called_once_with(project_id=1, page=0, size=100, search="Step", archived=None)


@pytest.mark.asyncio
async def test_create_shared_step_fail_validation(service):
    """Test validation errors."""
    with pytest.raises(AllureValidationError):
        await service.create_shared_step(project_id=-1, name="Valid")

    with pytest.raises(AllureValidationError):
        await service.create_shared_step(project_id=1, name="")
