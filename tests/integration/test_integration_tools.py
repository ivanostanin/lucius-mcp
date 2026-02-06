"""Integration tests for integration-related tools."""

import importlib
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.client import AllureClient
from src.client.generated.models.integration_dto import IntegrationDto
from src.client.generated.models.integration_info_dto import IntegrationInfoDto
from src.client.generated.models.integration_type_dto import IntegrationTypeDto
from src.tools.create_test_case import create_test_case
from src.tools.list_integrations import list_integrations
from src.tools.update_test_case import update_test_case

# Modules for patching
create_test_case_module = importlib.import_module("src.tools.create_test_case")
update_test_case_module = importlib.import_module("src.tools.update_test_case")


@pytest.mark.asyncio
@patch("src.client.AllureClient.from_env")
async def test_list_integrations_tool_output(mock_from_env):
    """Test the output formatting of list_integrations tool."""
    mock_client = AsyncMock()
    mock_from_env.return_value.__aenter__.return_value = mock_client

    mock_client.get_integrations.return_value = [
        IntegrationDto(id=1, name="Jira Instance", info=IntegrationInfoDto(type=IntegrationTypeDto.JIRA)),
        IntegrationDto(id=2, name="GitHub Repo", info=IntegrationInfoDto(type=IntegrationTypeDto.GITHUB)),
    ]

    result = await list_integrations()

    assert "Available Integrations" in result
    assert "2 found" in result
    assert "Jira Instance" in result
    assert "ID: 1" in result
    assert "[jira]" in result
    assert "GitHub Repo" in result
    assert "ID: 2" in result
    assert "[github]" in result
    # Fixed assertion to match bold Hint and complete text
    assert "**Hint:** Use `integration_id` or `integration_name`" in result


@pytest.mark.asyncio
@patch("src.client.AllureClient.from_env")
async def test_list_integrations_tool_empty(mock_from_env):
    """Test list_integrations tool when no integrations are found."""
    mock_client = AsyncMock()
    mock_from_env.return_value.__aenter__.return_value = mock_client
    mock_client.get_integrations.return_value = []

    result = await list_integrations()
    assert "No integrations configured" in result


@pytest.mark.asyncio
async def test_create_test_case_tool_passes_integration_params(monkeypatch):
    """Test that create_test_case tool correctly passes integration parameters to service."""
    service = AsyncMock()

    async def mock_create(*args, **kwargs):
        return Mock(id=1, name="Test")

    service.create_test_case.side_effect = mock_create

    class DummyClient:
        async def __aenter__(self):
            return AsyncMock()

        async def __aexit__(self, exc_type, exc, tb):
            return None

    monkeypatch.setattr(AllureClient, "from_env", Mock(return_value=DummyClient()))
    monkeypatch.setattr(create_test_case_module, "TestCaseService", Mock(return_value=service))

    await create_test_case(name="Test TC", issues=["PROJ-123"], integration_id=5)

    service.create_test_case.assert_called_once()
    kwargs = service.create_test_case.call_args.kwargs
    assert kwargs["issues"] == ["PROJ-123"]
    assert kwargs["integration_id"] == 5
    assert kwargs["integration_name"] is None


@pytest.mark.asyncio
async def test_update_test_case_tool_passes_integration_params(monkeypatch):
    """Test that update_test_case tool correctly passes integration parameters to service."""
    service = AsyncMock()

    async def mock_update(*args, **kwargs):
        return Mock(id=1, name="Test")

    service.update_test_case.side_effect = mock_update
    service.get_test_case.return_value = Mock(id=123, project_id=1, issues=[])

    class DummyClient:
        async def __aenter__(self):
            return AsyncMock()

        async def __aexit__(self, exc_type, exc, tb):
            return None

    monkeypatch.setattr(AllureClient, "from_env", Mock(return_value=DummyClient()))
    monkeypatch.setattr(update_test_case_module, "TestCaseService", Mock(return_value=service))

    await update_test_case(test_case_id=123, issues=["PROJ-456"], integration_name="Jira")

    service.update_test_case.assert_called_once()
    data = service.update_test_case.call_args[0][1]
    assert data.issues == ["PROJ-456"]
    assert data.integration_name == "Jira"
    assert data.integration_id is None
