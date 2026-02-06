"""Integration tests for test layer tools."""

from unittest.mock import AsyncMock, patch

import pytest

from src.tools.test_layers import (
    create_test_layer,
    create_test_layer_schema,
    delete_test_layer,
    delete_test_layer_schema,
    list_test_layer_schemas,
    list_test_layers,
    update_test_layer,
    update_test_layer_schema,
)


@pytest.mark.asyncio
async def test_list_test_layers_output_format() -> None:
    """Test list_test_layers output text formatting."""
    mock_layers = [
        {"id": 1, "name": "Unit"},
        {"id": 2, "name": "Integration"},
    ]

    with patch("src.tools.list_test_layers.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.list_test_layers.TestLayerService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.list_test_layers = AsyncMock(
                return_value=[type("TestLayerDto", (), layer) for layer in mock_layers]
            )

            output = await list_test_layers(page=0, size=50)

            assert "Found 2 test layers:" in output
            assert "ID: 1, Name: Unit" in output
            assert "ID: 2, Name: Integration" in output
            mock_service.list_test_layers.assert_called_once_with(page=0, size=50)


@pytest.mark.asyncio
async def test_list_test_layers_empty() -> None:
    """Test list_test_layers when no layers exist."""
    with patch("src.tools.list_test_layers.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.list_test_layers.TestLayerService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.list_test_layers = AsyncMock(return_value=[])

            output = await list_test_layers()

            assert "No test layers found." in output


@pytest.mark.asyncio
async def test_create_test_layer_output_format() -> None:
    """Test create_test_layer output formatting."""
    with patch("src.tools.create_test_layer.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.create_test_layer.TestLayerService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_layer = type("TestLayerDto", (), {"id": 10, "name": "E2E"})
            mock_service.create_test_layer = AsyncMock(return_value=mock_layer)

            output = await create_test_layer(name="E2E")

            assert "✅ Test layer created successfully!" in output
            assert "ID: 10" in output
            assert "Name: E2E" in output


@pytest.mark.asyncio
async def test_update_test_layer_changed() -> None:
    """Test update_test_layer output when changes are made."""
    with patch("src.tools.update_test_layer.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.update_test_layer.TestLayerService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            updated_layer = type("TestLayerDto", (), {"id": 5, "name": "New Name"})
            mock_service.update_test_layer = AsyncMock(return_value=(updated_layer, True))

            output = await update_test_layer(layer_id=5, name="New Name", confirm=True)

            assert "✅ Test layer 5 updated successfully!" in output
            assert "New name: New Name" in output


@pytest.mark.asyncio
async def test_update_test_layer_no_change() -> None:
    """Test update_test_layer output when no changes are made (idempotent)."""
    with patch("src.tools.update_test_layer.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.update_test_layer.TestLayerService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            unchanged_layer = type("TestLayerDto", (), {"id": 5, "name": "Same Name"})
            mock_service.update_test_layer = AsyncMock(return_value=(unchanged_layer, False))

            output = await update_test_layer(layer_id=5, name="Same Name", confirm=True)

            assert "[INFO]" in output
            assert "no changes made" in output


@pytest.mark.asyncio
async def test_delete_test_layer_output() -> None:
    """Test delete_test_layer output formatting."""
    with patch("src.tools.delete_test_layer.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.delete_test_layer.TestLayerService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.delete_test_layer = AsyncMock()

            output = await delete_test_layer(layer_id=7, confirm=True)

            assert "✅ Test layer 7 deleted successfully!" in output


@pytest.mark.asyncio
async def test_list_test_layer_schemas_output_format() -> None:
    """Test list_test_layer_schemas output formatting."""
    mock_schemas = [
        {"id": 1, "key": "layer", "test_layer": type("TestLayerDto", (), {"id": 10, "name": "Unit"})},
        {"id": 2, "key": "test_level", "test_layer": type("TestLayerDto", (), {"id": 11, "name": "E2E"})},
    ]

    with patch("src.tools.list_test_layer_schemas.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.list_test_layer_schemas.TestLayerService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.list_test_layer_schemas = AsyncMock(
                return_value=[type("TestLayerSchemaDto", (), schema) for schema in mock_schemas]
            )

            output = await list_test_layer_schemas(project_id=1)

            assert "Found 2 test layer schemas:" in output
            assert "ID: 1, Key: layer, Layer: Unit" in output
            assert "ID: 2, Key: test_level, Layer: E2E" in output


@pytest.mark.asyncio
async def test_create_test_layer_schema_output() -> None:
    """Test create_test_layer_schema output formatting."""
    with patch("src.tools.create_test_layer_schema.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.create_test_layer_schema.TestLayerService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_schema = type(
                "TestLayerSchemaDto",
                (),
                {"id": 100, "key": "layer", "test_layer": type("TestLayerDto", (), {"id": 5, "name": "Integration"})},
            )
            mock_service.create_test_layer_schema = AsyncMock(return_value=mock_schema)

            output = await create_test_layer_schema(key="layer", test_layer_id=5, project_id=1)

            assert "✅ Test layer schema created successfully!" in output
            assert "ID: 100" in output
            assert "Key: layer" in output
            assert "Layer: Integration" in output


@pytest.mark.asyncio
async def test_update_test_layer_schema_changed() -> None:
    """Test update_test_layer_schema output when changes are made."""
    with patch("src.tools.update_test_layer_schema.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.update_test_layer_schema.TestLayerService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            updated_schema = type(
                "TestLayerSchemaDto",
                (),
                {"id": 30, "key": "new_key", "test_layer": type("TestLayerDto", (), {"id": 2, "name": "Integration"})},
            )
            mock_service.update_test_layer_schema = AsyncMock(return_value=(updated_schema, True))

            output = await update_test_layer_schema(schema_id=30, key="new_key", confirm=True)

            assert "✅ Test layer schema 30 updated successfully!" in output
            assert "Key: new_key" in output


@pytest.mark.asyncio
async def test_delete_test_layer_schema_output() -> None:
    """Test delete_test_layer_schema output formatting."""
    with patch("src.tools.delete_test_layer_schema.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.delete_test_layer_schema.TestLayerService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.delete_test_layer_schema = AsyncMock()

            output = await delete_test_layer_schema(schema_id=40, confirm=True)

            assert "✅ Test layer schema 40 deleted successfully!" in output
