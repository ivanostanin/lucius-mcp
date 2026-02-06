"""E2E tests for test layer CRUD operations."""

import pytest

from src.client import AllureClient
from src.services.test_layer_service import TestLayerService
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
from tests.e2e.helpers.cleanup import CleanupTracker


async def test_e2e_test_layer_full_lifecycle(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E-TL-1: Test Layer Full Lifecycle.
    Create, list, update, and delete a test layer using real Allure TestOps instance.
    """
    service = TestLayerService(client=allure_client)

    # Step 1: Create a test layer
    layer_name = "E2E-Test-Layer"
    created_layer = await service.create_test_layer(name=layer_name)

    assert created_layer.id is not None
    cleanup_tracker.track_test_layer(created_layer.id)
    assert created_layer.name == layer_name
    layer_id = created_layer.id

    # Step 2: Verify it appears in list
    layers = await service.list_test_layers(page=0, size=100)
    layer_ids = [layer.id for layer in layers]
    assert layer_id in layer_ids

    # Step 3: Update the layer name
    new_name = "E2E-Test-Layer-Updated"
    updated_layer, changed = await service.update_test_layer(layer_id=layer_id, name=new_name)

    assert changed is True
    assert updated_layer.name == new_name

    # Step 4: Verify idempotent update (same name)
    same_layer, changed = await service.update_test_layer(layer_id=layer_id, name=new_name)
    assert changed is False
    assert same_layer.name == new_name

    # Step 5: Delete the layer
    await service.delete_test_layer(layer_id=layer_id)

    # Step 6: Verify idempotent delete (already deleted)
    await service.delete_test_layer(layer_id=layer_id)  # Should not raise


async def test_e2e_test_layer_schema_full_lifecycle(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E-TL-2: Test Layer Schema Full Lifecycle.
    Create test layer and schema, verify, update, and delete.
    """
    service = TestLayerService(client=allure_client)

    # Step 1: Create a test layer first
    layer_name = "E2E-Schema-Layer"
    created_layer = await service.create_test_layer(name=layer_name)
    layer_id = created_layer.id
    assert layer_id is not None
    cleanup_tracker.track_test_layer(created_layer.id)

    try:
        # Step 2: Create a test layer schema
        schema_key = "e2e_test_layer"
        created_schema = await service.create_test_layer_schema(
            project_id=project_id,
            test_layer_id=layer_id,
            key=schema_key,
        )

        assert created_schema.id is not None
        assert created_schema.key == schema_key
        assert created_schema.test_layer.id == layer_id
        schema_id = created_schema.id

        # Step 3: Verify it appears in list
        schemas = await service.list_test_layer_schemas(project_id=project_id, page=0, size=100)
        schema_ids = [schema.id for schema in schemas]
        assert schema_id in schema_ids

        # Step 4: Update the schema key
        new_key = "e2e_updated_layer"
        updated_schema, changed = await service.update_test_layer_schema(
            schema_id=schema_id,
            key=new_key,
        )

        assert changed is True
        assert updated_schema.key == new_key

        # Step 5: Verify idempotent update
        _same_schema, changed = await service.update_test_layer_schema(
            schema_id=schema_id,
            key=new_key,
        )
        assert changed is False

        # Step 6: Delete the schema
        await service.delete_test_layer_schema(schema_id=schema_id)

        # Step 7: Verify idempotent delete
        await service.delete_test_layer_schema(schema_id=schema_id)  # Should not raise

    finally:
        # Cleanup: Delete the test layer
        await service.delete_test_layer(layer_id=layer_id)


async def test_e2e_list_test_layers_tool(
    project_id: int,
) -> None:
    """
    E2E-TL-3: List Test Layers Tool.
    Verify that the list_test_layers tool works against real API.
    """
    output = await list_test_layers(page=0, size=10)

    # Should return successful output
    assert isinstance(output, str)
    assert "test layer" in output.lower() or "no test layers found" in output.lower()


async def test_e2e_create_and_delete_test_layer_tools(
    project_id: int,
    allure_client: AllureClient,
) -> None:
    """
    E2E-TL-4: Create and Delete Test Layer Tools.
    Verify create and delete tools work together.
    """
    # Create via tool
    import uuid

    layer_name = f"E2E-Tool-Layer-{uuid.uuid4().hex[:8]}"
    create_output = await create_test_layer(name=layer_name, project_id=project_id)

    assert "✅" in create_output
    assert "created successfully" in create_output
    assert layer_name in create_output

    # Extract ID from output
    import re

    match = re.search(r"ID: (\d+)", create_output)
    assert match, "Could not extract ID from create output"
    layer_id = int(match.group(1))

    try:
        # Verify it exists
        service = TestLayerService(client=allure_client)
        layer = await service.get_test_layer(layer_id=layer_id)
        assert layer.name == layer_name

    finally:
        # Delete via tool
        delete_output = await delete_test_layer(layer_id=layer_id, project_id=project_id, confirm=True)
        assert "✅" in delete_output
        assert "deleted successfully" in delete_output


async def test_e2e_update_test_layer_tool(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E-TL-5: Update Test Layer Tool.
    Create, update via tool, and verify.
    """
    service = TestLayerService(client=allure_client)

    # Create a layer
    layer_name = "E2E-Update-Layer"
    created_layer = await service.create_test_layer(name=layer_name)
    layer_id = created_layer.id
    assert layer_id is not None
    cleanup_tracker.track_test_layer(created_layer.id)

    try:
        # Update via tool
        new_name = "E2E-Update-Layer-Modified"
        update_output = await update_test_layer(layer_id=layer_id, name=new_name, project_id=project_id, confirm=True)

        assert "✅" in update_output or "[INFO]" in update_output
        assert str(layer_id) in update_output

        # Verify the update
        updated_layer = await service.get_test_layer(layer_id=layer_id)
        assert updated_layer.name == new_name

    finally:
        # Cleanup
        await service.delete_test_layer(layer_id=layer_id)


async def test_e2e_test_layer_schema_tools(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E-TL-6: Test Layer Schema Tools.
    Test create, list, update, delete schema tools.
    """
    service = TestLayerService(client=allure_client)

    # Create a test layer first
    layer_name = "E2E-Schema-Tools-Layer"
    created_layer = await service.create_test_layer(name=layer_name)
    layer_id = created_layer.id
    assert layer_id is not None
    cleanup_tracker.track_test_layer(created_layer.id)

    try:
        # Create schema via tool
        schema_key = "e2e_schema_tool"
        create_output = await create_test_layer_schema(
            key=schema_key,
            test_layer_id=layer_id,
            project_id=project_id,
        )

        assert "✅" in create_output
        assert "created successfully" in create_output
        assert schema_key in create_output

        # Extract schema ID
        import re

        match = re.search(r"ID: (\d+)", create_output)
        assert match
        schema_id = int(match.group(1))

        # List schemas via tool
        list_output = await list_test_layer_schemas(project_id=project_id)
        assert str(schema_id) in list_output or "test layer schema" in list_output.lower()

        # Update schema via tool
        new_key = "e2e_schema_tool_updated"
        update_output = await update_test_layer_schema(
            schema_id=schema_id,
            key=new_key,
            project_id=project_id,
            confirm=True,
        )
        assert "✅" in update_output or "[INFO]" in update_output

        # Delete schema via tool
        delete_output = await delete_test_layer_schema(schema_id=schema_id, project_id=project_id, confirm=True)
        assert "✅" in delete_output
        assert "deleted successfully" in delete_output

    finally:
        # Cleanup layer
        await service.delete_test_layer(layer_id=layer_id)


async def test_e2e_validation_errors(
    project_id: int,
    allure_client: AllureClient,
) -> None:
    """
    E2E-TL-7: Validation Errors.
    Verify that validation errors are properly raised.
    """
    from src.client.exceptions import AllureValidationError

    service = TestLayerService(client=allure_client)

    # Test empty name validation
    with pytest.raises(AllureValidationError, match="Name is required"):
        await service.create_test_layer(name="")

    # Test long name validation
    long_name = "a" * 256
    with pytest.raises(AllureValidationError, match="Name too long"):
        await service.create_test_layer(name=long_name)

    # Test invalid project ID
    with pytest.raises(AllureValidationError, match="Project ID must be a positive integer"):
        await service.create_test_layer_schema(project_id=-1, test_layer_id=1, key="test")


async def test_e2e_multiple_schemas_same_project(
    project_id: int,
    allure_client: AllureClient,
) -> None:
    """
    E2E-TL-8: Multiple Schemas in Same Project.
    Verify multiple schemas can exist in the same project.
    """
    service = TestLayerService(client=allure_client)

    # Create two test layers
    layer1 = await service.create_test_layer(name="E2E-Multi-Layer-1")
    layer2 = await service.create_test_layer(name="E2E-Multi-Layer-2")

    layer1_id = layer1.id
    layer2_id = layer2.id
    assert layer1_id is not None
    assert layer2_id is not None

    try:
        # Create two schemas for the same project
        schema1 = await service.create_test_layer_schema(
            project_id=project_id,
            test_layer_id=layer1_id,
            key="e2e_multi_schema_1",
        )
        schema2 = await service.create_test_layer_schema(
            project_id=project_id,
            test_layer_id=layer2_id,
            key="e2e_multi_schema_2",
        )

        schema1_id = schema1.id
        schema2_id = schema2.id
        assert schema1_id is not None
        assert schema2_id is not None

        # List schemas and verify both exist
        schemas = await service.list_test_layer_schemas(project_id=project_id)
        schema_ids = [s.id for s in schemas]
        assert schema1_id in schema_ids
        assert schema2_id in schema_ids

        # Delete both schemas
        await service.delete_test_layer_schema(schema_id=schema1_id)
        await service.delete_test_layer_schema(schema_id=schema2_id)

    finally:
        # Cleanup layers
        await service.delete_test_layer(layer_id=layer1_id)
        await service.delete_test_layer(layer_id=layer2_id)
