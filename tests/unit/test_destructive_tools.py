"""Unit tests for destructive tools confirmation logic."""

import pytest

from src.tools.delete_custom_field_value import delete_custom_field_value
from src.tools.delete_test_layer import delete_test_layer
from src.tools.delete_test_layer_schema import delete_test_layer_schema
from src.tools.link_shared_step import link_shared_step
from src.tools.shared_steps import delete_shared_step, update_shared_step
from src.tools.unlink_shared_step import unlink_shared_step
from src.tools.update_custom_field_value import update_custom_field_value
from src.tools.update_test_case import update_test_case
from src.tools.update_test_layer import update_test_layer
from src.tools.update_test_layer_schema import update_test_layer_schema


@pytest.mark.asyncio
async def test_update_shared_step_confirmation() -> None:
    result = await update_shared_step(step_id=123, confirm=False)
    assert "⚠️ Update requires confirmation" in result
    assert "Changes propagate to ALL test cases" in result
    assert "123" in result


@pytest.mark.asyncio
async def test_delete_shared_step_confirmation() -> None:
    result = await delete_shared_step(step_id=123, confirm=False)
    assert "⚠️ Deletion requires confirmation" in result
    assert "breaking those references" in result
    assert "123" in result


@pytest.mark.asyncio
async def test_update_test_case_confirmation() -> None:
    result = await update_test_case(test_case_id=456, confirm=False)
    assert "⚠️ Update requires confirmation" in result
    assert "modify test case properties" in result
    assert "456" in result


@pytest.mark.asyncio
async def test_link_shared_step_confirmation() -> None:
    result = await link_shared_step(test_case_id=456, shared_step_id=123, confirm=False)
    assert "⚠️ Linking requires confirmation" in result
    assert "add a shared step" in result
    assert "123" in result
    assert "456" in result


@pytest.mark.asyncio
async def test_unlink_shared_step_confirmation() -> None:
    result = await unlink_shared_step(test_case_id=456, shared_step_id=123, confirm=False)
    assert "⚠️ Unlinking requires confirmation" in result
    assert "remove a shared step" in result
    assert "123" in result
    assert "456" in result


@pytest.mark.asyncio
async def test_delete_test_layer_confirmation() -> None:
    result = await delete_test_layer(layer_id=789, confirm=False)
    assert "⚠️ Deletion requires confirmation" in result
    assert "affect test case categorization" in result
    assert "789" in result


@pytest.mark.asyncio
async def test_update_test_layer_confirmation() -> None:
    result = await update_test_layer(layer_id=789, name="New Name", confirm=False)
    assert "⚠️ Update requires confirmation" in result
    assert "Renaming a test layer" in result
    assert "789" in result


@pytest.mark.asyncio
async def test_delete_test_layer_schema_confirmation() -> None:
    result = await delete_test_layer_schema(schema_id=111, confirm=False)
    assert "⚠️ Deletion requires confirmation" in result
    assert "removes the mapping" in result
    assert "111" in result


@pytest.mark.asyncio
async def test_update_test_layer_schema_confirmation() -> None:
    result = await update_test_layer_schema(schema_id=111, confirm=False)
    assert "⚠️ Update requires confirmation" in result
    assert "affects how test layers are automatically assigned" in result
    assert "111" in result


@pytest.mark.asyncio
async def test_delete_custom_field_value_confirmation() -> None:
    result = await delete_custom_field_value(cfv_id=222, confirm=False)
    assert "⚠️ Deletion requires confirmation" in result
    assert "currently in use" in result
    assert "222" in result


@pytest.mark.asyncio
async def test_update_custom_field_value_confirmation() -> None:
    result = await update_custom_field_value(cfv_id=222, name="New Value", confirm=False)
    assert "⚠️ Update requires confirmation" in result
    assert "affects all test cases using it" in result
    assert "222" in result
