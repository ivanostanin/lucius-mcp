"""Unit tests for TestLayerService."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
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

    # Mock test layer API
    client._test_layer_api = MagicMock()
    client._test_layer_api.find_all7 = AsyncMock()
    client._test_layer_api.create9 = AsyncMock()
    client._test_layer_api.find_one8 = AsyncMock()
    client._test_layer_api.patch9 = AsyncMock()
    client._test_layer_api.delete9 = AsyncMock()

    # Mock test layer schema API
    client._test_layer_schema_api = MagicMock()
    client._test_layer_schema_api.find_all6 = AsyncMock()
    client._test_layer_schema_api.create8 = AsyncMock()
    client._test_layer_schema_api.find_one7 = AsyncMock()
    client._test_layer_schema_api.patch8 = AsyncMock()
    client._test_layer_schema_api.delete8 = AsyncMock()

    return client


@pytest.fixture
def service(mock_client):
    """Create a TestLayerService instance with mock client."""
    return TestLayerService(client=mock_client)


# ==========================================
# Test Layer CRUD Tests
# ==========================================


@pytest.mark.asyncio
async def test_list_test_layers_success(service, mock_client):
    """Test listing test layers."""
    mock_page = PageTestLayerDto(
        content=[
            TestLayerDto(id=1, name="Unit"),
            TestLayerDto(id=2, name="Integration"),
        ],
        total_elements=2,
    )
    mock_client._test_layer_api.find_all7.return_value = mock_page

    result = await service.list_test_layers(page=0, size=50)

    assert len(result) == 2
    assert result[0].name == "Unit"
    assert result[1].name == "Integration"
    mock_client._test_layer_api.find_all7.assert_called_once_with(page=0, size=50)


@pytest.mark.asyncio
async def test_list_test_layers_empty(service, mock_client):
    """Test listing when no test layers exist."""
    mock_page = PageTestLayerDto(content=[], total_elements=0)
    mock_client._test_layer_api.find_all7.return_value = mock_page

    result = await service.list_test_layers()

    assert len(result) == 0


@pytest.mark.asyncio
async def test_create_test_layer_success(service, mock_client):
    """Test creating a test layer."""
    created_layer = TestLayerDto(id=10, name="E2E")
    mock_client._test_layer_api.create9.return_value = created_layer

    result = await service.create_test_layer(name="E2E")

    assert result.id == 10
    assert result.name == "E2E"
    mock_client._test_layer_api.create9.assert_called_once()


@pytest.mark.asyncio
async def test_create_test_layer_validation_empty_name(service):
    """Test validation fails for empty name."""
    with pytest.raises(AllureValidationError, match="Name is required"):
        await service.create_test_layer(name="")


@pytest.mark.asyncio
async def test_create_test_layer_validation_long_name(service):
    """Test validation fails for name exceeding max length."""
    long_name = "a" * 256
    with pytest.raises(AllureValidationError, match="Name too long"):
        await service.create_test_layer(name=long_name)


@pytest.mark.asyncio
async def test_get_test_layer_success(service, mock_client):
    """Test getting a test layer by ID."""
    layer = TestLayerDto(id=5, name="API")
    mock_client._test_layer_api.find_one8.return_value = layer

    result = await service.get_test_layer(layer_id=5)

    assert result.id == 5
    assert result.name == "API"
    mock_client._test_layer_api.find_one8.assert_called_once_with(id=5)


@pytest.mark.asyncio
async def test_update_test_layer_success(service, mock_client):
    """Test updating a test layer with name change."""
    current_layer = TestLayerDto(id=3, name="Old Name")
    updated_layer = TestLayerDto(id=3, name="New Name")

    mock_client._test_layer_api.find_one8.return_value = current_layer
    mock_client._test_layer_api.patch9.return_value = updated_layer

    result, changed = await service.update_test_layer(layer_id=3, name="New Name")

    assert result.name == "New Name"
    assert changed is True
    mock_client._test_layer_api.patch9.assert_called_once()


@pytest.mark.asyncio
async def test_update_test_layer_idempotent(service, mock_client):
    """Test update is idempotent when name matches current state."""
    current_layer = TestLayerDto(id=3, name="Same Name")

    mock_client._test_layer_api.find_one8.return_value = current_layer

    result, changed = await service.update_test_layer(layer_id=3, name="Same Name")

    assert result.name == "Same Name"
    assert changed is False
    mock_client._test_layer_api.patch9.assert_not_called()


@pytest.mark.asyncio
async def test_delete_test_layer_success(service, mock_client):
    """Test deleting a test layer."""
    layer = TestLayerDto(id=7, name="API")
    mock_client._test_layer_api.find_one8.return_value = layer
    mock_client._test_layer_api.delete9.return_value = None

    result = await service.delete_test_layer(layer_id=7)

    assert result is True
    mock_client._test_layer_api.find_one8.assert_called_once_with(id=7)
    mock_client._test_layer_api.delete9.assert_called_once_with(id=7)


@pytest.mark.asyncio
async def test_delete_test_layer_idempotent(service, mock_client):
    """Test delete is idempotent - handles already deleted layer gracefully."""
    mock_client._test_layer_api.find_one8.side_effect = AllureNotFoundError("Not found", 404, "{}")

    # Should not raise, just return False
    result = await service.delete_test_layer(layer_id=7)

    assert result is False
    mock_client._test_layer_api.find_one8.assert_called_once_with(id=7)
    mock_client._test_layer_api.delete9.assert_not_called()


# ==========================================
# Test Layer Schema CRUD Tests
# ==========================================


@pytest.mark.asyncio
async def test_list_test_layer_schemas_success(service, mock_client):
    """Test listing test layer schemas for a project."""
    mock_page = PageTestLayerSchemaDto(
        content=[
            TestLayerSchemaDto(id=1, key="layer", project_id=1, test_layer=TestLayerDto(id=10, name="Unit")),
            TestLayerSchemaDto(id=2, key="test_level", project_id=1, test_layer=TestLayerDto(id=11, name="E2E")),
        ],
        total_elements=2,
    )
    mock_client._test_layer_schema_api.find_all6.return_value = mock_page

    result = await service.list_test_layer_schemas(project_id=1, page=0, size=50)

    assert len(result) == 2
    assert result[0].key == "layer"
    assert result[1].key == "test_level"
    mock_client._test_layer_schema_api.find_all6.assert_called_once_with(project_id=1, page=0, size=50)


@pytest.mark.asyncio
async def test_create_test_layer_schema_success(service, mock_client):
    """Test creating a test layer schema."""
    created_schema = TestLayerSchemaDto(
        id=100,
        key="test_layer",
        project_id=1,
        test_layer=TestLayerDto(id=5, name="Integration"),
    )
    mock_client._test_layer_schema_api.create8.return_value = created_schema

    result = await service.create_test_layer_schema(project_id=1, test_layer_id=5, key="test_layer")

    assert result.id == 100
    assert result.key == "test_layer"
    assert result.test_layer.id == 5
    mock_client._test_layer_schema_api.create8.assert_called_once()


@pytest.mark.asyncio
async def test_create_test_layer_schema_validation(service):
    """Test validation for test layer schema creation."""
    with pytest.raises(AllureValidationError, match="Key is required"):
        await service.create_test_layer_schema(project_id=1, test_layer_id=5, key="")

    with pytest.raises(AllureValidationError, match="Project ID must be a positive integer"):
        await service.create_test_layer_schema(project_id=-1, test_layer_id=5, key="layer")


@pytest.mark.asyncio
async def test_get_test_layer_schema_success(service, mock_client):
    """Test getting a test layer schema by ID."""
    schema = TestLayerSchemaDto(
        id=20,
        key="layer",
        project_id=1,
        test_layer=TestLayerDto(id=5, name="API"),
    )
    mock_client._test_layer_schema_api.find_one7.return_value = schema

    result = await service.get_test_layer_schema(schema_id=20)

    assert result.id == 20
    assert result.key == "layer"
    mock_client._test_layer_schema_api.find_one7.assert_called_once_with(id=20)


@pytest.mark.asyncio
async def test_update_test_layer_schema_success(service, mock_client):
    """Test updating a test layer schema."""
    current_schema = TestLayerSchemaDto(
        id=30,
        key="old_key",
        project_id=1,
        test_layer=TestLayerDto(id=1, name="Unit"),
    )
    updated_schema = TestLayerSchemaDto(
        id=30,
        key="new_key",
        project_id=1,
        test_layer=TestLayerDto(id=2, name="Integration"),
    )

    mock_client._test_layer_schema_api.find_one7.return_value = current_schema
    mock_client._test_layer_schema_api.patch8.return_value = updated_schema

    result, changed = await service.update_test_layer_schema(schema_id=30, key="new_key", test_layer_id=2)

    assert result.key == "new_key"
    assert result.test_layer.id == 2
    assert changed is True
    mock_client._test_layer_schema_api.patch8.assert_called_once()


@pytest.mark.asyncio
async def test_update_test_layer_schema_idempotent(service, mock_client):
    """Test update is idempotent when values match current state."""
    current_schema = TestLayerSchemaDto(
        id=30,
        key="same_key",
        project_id=1,
        test_layer=TestLayerDto(id=5, name="API"),
    )

    mock_client._test_layer_schema_api.find_one7.return_value = current_schema

    _result, changed = await service.update_test_layer_schema(schema_id=30, key="same_key", test_layer_id=5)

    assert changed is False
    mock_client._test_layer_schema_api.patch8.assert_not_called()


@pytest.mark.asyncio
async def test_delete_test_layer_schema_success(service, mock_client):
    """Test deleting a test layer schema."""
    schema = TestLayerSchemaDto(id=40, key="layer", project_id=1, test_layer=TestLayerDto(id=10, name="Unit"))
    mock_client._test_layer_schema_api.find_one7.return_value = schema
    mock_client._test_layer_schema_api.delete8.return_value = None

    result = await service.delete_test_layer_schema(schema_id=40)

    assert result is True
    mock_client._test_layer_schema_api.find_one7.assert_called_once_with(id=40)
    mock_client._test_layer_schema_api.delete8.assert_called_once_with(id=40)


@pytest.mark.asyncio
async def test_delete_test_layer_schema_idempotent(service, mock_client):
    """Test delete is idempotent - handles already deleted schema gracefully."""
    mock_client._test_layer_schema_api.find_one7.side_effect = AllureNotFoundError("Not found", 404, "{}")

    # Should not raise, just return False
    result = await service.delete_test_layer_schema(schema_id=40)

    assert result is False
    mock_client._test_layer_schema_api.find_one7.assert_called_once_with(id=40)
    mock_client._test_layer_schema_api.delete8.assert_not_called()
