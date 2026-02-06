"""Unit tests for IntegrationService."""

from unittest.mock import AsyncMock

import pytest

from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError
from src.client.generated.models.integration_dto import IntegrationDto
from src.client.generated.models.integration_info_dto import IntegrationInfoDto
from src.services.integration_service import IntegrationService


@pytest.fixture
def mock_client():
    return AsyncMock()


@pytest.fixture
def service(mock_client):
    return IntegrationService(mock_client)


@pytest.fixture
def integrations():
    return [
        IntegrationDto(id=1, name="Jira", info=IntegrationInfoDto(type="jira")),
        IntegrationDto(id=2, name="GitHub", info=IntegrationInfoDto(type="github")),
    ]


@pytest.mark.asyncio
async def test_list_integrations(service, mock_client, integrations):
    mock_client.get_integrations.return_value = integrations
    result = await service.list_integrations()
    assert result == integrations
    mock_client.get_integrations.assert_called_once()


@pytest.mark.asyncio
async def test_get_integration_by_id_success(service, mock_client, integrations):
    mock_client.get_integrations.return_value = integrations
    result = await service.get_integration_by_id(1)
    assert result.id == 1
    assert result.name == "Jira"


@pytest.mark.asyncio
async def test_get_integration_by_id_not_found(service, mock_client, integrations):
    mock_client.get_integrations.return_value = integrations
    with pytest.raises(AllureNotFoundError, match="Integration with ID 999 not found"):
        await service.get_integration_by_id(999)


@pytest.mark.asyncio
async def test_get_integration_by_id_invalid(service):
    with pytest.raises(AllureValidationError, match="Integration ID must be a positive integer"):
        await service.get_integration_by_id(0)


@pytest.mark.asyncio
async def test_get_integration_by_name_success(service, mock_client, integrations):
    mock_client.get_integrations.return_value = integrations
    result = await service.get_integration_by_name("GitHub")
    assert result.id == 2
    assert result.info.type == "github"


@pytest.mark.asyncio
async def test_get_integration_by_name_not_found(service, mock_client, integrations):
    mock_client.get_integrations.return_value = integrations
    with pytest.raises(AllureNotFoundError, match="Integration 'GitLab' not found"):
        await service.get_integration_by_name("GitLab")


@pytest.mark.asyncio
async def test_resolve_integration_mutual_exclusivity(service):
    with pytest.raises(AllureValidationError, match="Cannot specify both 'integration_id' and 'integration_name'"):
        await service.resolve_integration(integration_id=1, integration_name="Jira")


@pytest.mark.asyncio
async def test_resolve_integration_by_id(service, mock_client, integrations):
    mock_client.get_integrations.return_value = integrations
    result = await service.resolve_integration(integration_id=2)
    assert result.id == 2


@pytest.mark.asyncio
async def test_resolve_integration_by_name(service, mock_client, integrations):
    mock_client.get_integrations.return_value = integrations
    result = await service.resolve_integration(integration_name="Jira")
    assert result.id == 1


@pytest.mark.asyncio
async def test_resolve_integration_none(service):
    result = await service.resolve_integration()
    assert result is None


@pytest.mark.asyncio
async def test_resolve_integration_for_issues_single(service, mock_client):
    integrations = [IntegrationDto(id=1, name="Jira")]
    mock_client.get_integrations.return_value = integrations
    result = await service.resolve_integration_for_issues()
    assert result == 1


@pytest.mark.asyncio
async def test_resolve_integration_for_issues_multiple_error(service, mock_client, integrations):
    mock_client.get_integrations.return_value = integrations
    with pytest.raises(AllureValidationError, match="Multiple integrations found"):
        await service.resolve_integration_for_issues()


@pytest.mark.asyncio
async def test_resolve_integration_for_issues_explicit_override(service, mock_client, integrations):
    mock_client.get_integrations.return_value = integrations
    result = await service.resolve_integration_for_issues(integration_name="GitHub")
    assert result == 2


@pytest.mark.asyncio
async def test_resolve_integration_for_issues_no_integrations(service, mock_client):
    mock_client.get_integrations.return_value = []
    with pytest.raises(AllureAPIError, match="No integrations configured in Allure TestOps"):
        await service.resolve_integration_for_issues()
