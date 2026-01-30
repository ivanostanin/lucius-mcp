"""Unit tests for pagination in TestLayerService."""

from unittest.mock import MagicMock

import pytest

from src.client import AllureClient
from src.client.generated.models.page_test_layer_dto import PageTestLayerDto
from src.client.generated.models.page_test_layer_schema_dto import PageTestLayerSchemaDto
from src.client.generated.models.test_layer_dto import TestLayerDto
from src.client.generated.models.test_layer_schema_dto import TestLayerSchemaDto
from src.services.test_layer_service import TestLayerService


@pytest.fixture
def mock_client():
    """Create a mock AllureClient with required APIs."""
    client = MagicMock(spec=AllureClient)
    client.get_project.return_value = 1
    return client


@pytest.mark.asyncio
async def test_list_test_layers_pagination(mock_client):
    """Test listing test layers with pagination."""
    service = TestLayerService(client=mock_client)

    # Mock the test layer API
    from unittest.mock import AsyncMock

    mock_client._test_layer_api = MagicMock()
    mock_client._test_layer_api.find_all7 = AsyncMock()

    # Create mock responses for different pages
    page1_data = PageTestLayerDto(
        content=[
            TestLayerDto(id=1, name="Layer 1"),
            TestLayerDto(id=2, name="Layer 2"),
        ],
        total_elements=5,
    )
    page2_data = PageTestLayerDto(
        content=[
            TestLayerDto(id=3, name="Layer 3"),
            TestLayerDto(id=4, name="Layer 4"),
        ],
        total_elements=5,
    )

    # Configure mock to return different pages
    mock_client._test_layer_api.find_all7.side_effect = [page1_data, page2_data]

    # Get page 0
    result_page0 = await service.list_test_layers(page=0, size=2)
    assert len(result_page0) == 2
    assert result_page0[0].name == "Layer 1"

    # Get page 1
    result_page1 = await service.list_test_layers(page=1, size=2)
    assert len(result_page1) == 2
    assert result_page1[0].name == "Layer 3"

    # Verify calls with different page numbers
    calls = mock_client._test_layer_api.find_all7.call_args_list
    assert calls[0].kwargs["page"] == 0
    assert calls[1].kwargs["page"] == 1


@pytest.mark.asyncio
async def test_list_test_layer_schemas_pagination(mock_client):
    """Test listing test layer schemas with pagination."""
    service = TestLayerService(client=mock_client)

    # Mock the test layer schema API
    from unittest.mock import AsyncMock

    mock_client._test_layer_schema_api = MagicMock()
    mock_client._test_layer_schema_api.find_all6 = AsyncMock()

    # Create mock responses for different pages
    page1_data = PageTestLayerSchemaDto(
        content=[
            TestLayerSchemaDto(id=1, key="schema1", project_id=1, test_layer=TestLayerDto(id=10, name="Layer")),
            TestLayerSchemaDto(id=2, key="schema2", project_id=1, test_layer=TestLayerDto(id=10, name="Layer")),
        ],
        total_elements=5,
    )
    page2_data = PageTestLayerSchemaDto(
        content=[
            TestLayerSchemaDto(id=3, key="schema3", project_id=1, test_layer=TestLayerDto(id=10, name="Layer")),
        ],
        total_elements=5,
    )

    # Configure mock to return different pages
    mock_client._test_layer_schema_api.find_all6.side_effect = [page1_data, page2_data]

    # Get page 0
    result_page0 = await service.list_test_layer_schemas(project_id=1, page=0, size=2)
    assert len(result_page0) == 2
    assert result_page0[0].key == "schema1"

    # Get page 1
    result_page1 = await service.list_test_layer_schemas(project_id=1, page=1, size=2)
    assert len(result_page1) == 1
    assert result_page1[0].key == "schema3"

    # Verify calls with different page numbers
    calls = mock_client._test_layer_schema_api.find_all6.call_args_list
    assert calls[0].kwargs["page"] == 0
    assert calls[1].kwargs["page"] == 1
