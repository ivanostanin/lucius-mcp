"""Integration tests for _get_resolved_custom_fields method.

These tests verify that the internal caching mechanism properly
fetches and stores custom field information including values.
"""

from unittest.mock import AsyncMock, patch

import pytest
from pydantic import SecretStr

from src.client import AllureClient
from src.client.generated.models import (
    CustomFieldDto,
    CustomFieldProjectDto,
    CustomFieldProjectWithValuesDto,
    CustomFieldValueDto,
)
from src.services.test_case_service import TestCaseService


@pytest.mark.asyncio
async def test_get_resolved_custom_fields_returns_values() -> None:
    """Test that _get_resolved_custom_fields returns custom field values.

    This test verifies the fix for the bug where _get_resolved_custom_fields
    was always returning empty values lists.
    """
    project_id = 1

    # Create mock response with values
    mock_cf = CustomFieldProjectWithValuesDto(
        custom_field=CustomFieldProjectDto(
            custom_field=CustomFieldDto(name="Layer", id=123),
            required=True,
        ),
        values=[
            CustomFieldValueDto(name="UI", id=1),
            CustomFieldValueDto(name="API", id=2),
            CustomFieldValueDto(name="DB", id=3),
        ],
    )

    # Patch token validation to avoid real API calls
    with patch("src.client.client.AllureClient._ensure_valid_token", new_callable=AsyncMock):
        async with AllureClient("http://localhost", SecretStr("token"), project_id) as client:
            # Mock the client method
            client.get_custom_fields_with_values = AsyncMock(return_value=[mock_cf])

            service = TestCaseService(client=client)

            # Call the method
            result = await service._get_resolved_custom_fields(project_id)

            # Verify values are populated
            assert "Layer" in result, "Field 'Layer' should be in result"
            assert result["Layer"]["values"] == ["UI", "API", "DB"], "Values should be populated, not empty"
            assert result["Layer"]["id"] == 123, "Field ID should be correct"
            assert result["Layer"]["required"] is True, "Required flag should be set"


@pytest.mark.asyncio
async def test_get_resolved_custom_fields_caches_results() -> None:
    """Test that _get_resolved_custom_fields caches results.

    Verifies that subsequent calls return cached data without making
    additional API calls.
    """
    project_id = 1

    mock_cf = CustomFieldProjectWithValuesDto(
        custom_field=CustomFieldProjectDto(
            custom_field=CustomFieldDto(name="Priority", id=456),
            required=False,
        ),
        values=[CustomFieldValueDto(name="High"), CustomFieldValueDto(name="Low")],
    )

    with patch("src.client.client.AllureClient._ensure_valid_token", new_callable=AsyncMock):
        async with AllureClient("http://localhost", SecretStr("token"), project_id) as client:
            client.get_custom_fields_with_values = AsyncMock(return_value=[mock_cf])

            service = TestCaseService(client=client)

            # First call - should make API call
            result1 = await service._get_resolved_custom_fields(project_id)

            # Second call - should use cache
            result2 = await service._get_resolved_custom_fields(project_id)

            # Results should be identical
            assert result1 == result2, "Cached result should match original"

            # Client method should only be called once
            client.get_custom_fields_with_values.assert_called_once_with(project_id)


@pytest.mark.asyncio
async def test_get_resolved_custom_fields_handles_empty_values() -> None:
    """Test that _get_resolved_custom_fields handles fields with no allowed values.

    Some custom fields ( like text fields) don't have constrained values.
    """
    project_id = 1

    # Field with no values (free text field)
    mock_cf = CustomFieldProjectWithValuesDto(
        custom_field=CustomFieldProjectDto(
            custom_field=CustomFieldDto(name="Description", id=789),
            required=False,
        ),
        values=None,  # No constrained values
    )

    with patch("src.client.client.AllureClient._ensure_valid_token", new_callable=AsyncMock):
        async with AllureClient("http://localhost", SecretStr("token"), project_id) as client:
            client.get_custom_fields_with_values = AsyncMock(return_value=[mock_cf])

            service = TestCaseService(client=client)
            result = await service._get_resolved_custom_fields(project_id)

            # Should handle None values gracefully
            assert "Description" in result
            assert result["Description"]["values"] == [], "Should return empty list for fields without constraints"
            assert result["Description"]["id"] == 789


@pytest.mark.asyncio
async def test_get_resolved_custom_fields_filters_null_names() -> None:
    """Test that _get_resolved_custom_fields filters out values with null names."""
    project_id = 1

    mock_cf = CustomFieldProjectWithValuesDto(
        custom_field=CustomFieldProjectDto(
            custom_field=CustomFieldDto(name="Status", id=999),
            required=True,
        ),
        values=[
            CustomFieldValueDto(name="Active", id=1),
            CustomFieldValueDto(name=None, id=2),  # Null name - should be filtered
            CustomFieldValueDto(name="Inactive", id=3),
            CustomFieldValueDto(name="", id=4),  # Empty string - will be included but filtered
        ],
    )

    with patch("src.client.client.AllureClient._ensure_valid_token", new_callable=AsyncMock):
        async with AllureClient("http://localhost", SecretStr("token"), project_id) as client:
            client.get_custom_fields_with_values = AsyncMock(return_value=[mock_cf])

            service = TestCaseService(client=client)
            result = await service._get_resolved_custom_fields(project_id)

            # Only valid names should be included
            assert result["Status"]["values"] == ["Active", "Inactive"], "Should filter out None names"


@pytest.mark.asyncio
async def test_get_resolved_custom_fields_multiple_fields() -> None:
    """Test _get_resolved_custom_fields with multiple custom fields."""
    project_id = 1

    mock_cfs = [
        CustomFieldProjectWithValuesDto(
            custom_field=CustomFieldProjectDto(
                custom_field=CustomFieldDto(name="Layer", id=1),
                required=True,
            ),
            values=[CustomFieldValueDto(name="UI"), CustomFieldValueDto(name="API")],
        ),
        CustomFieldProjectWithValuesDto(
            custom_field=CustomFieldProjectDto(
                custom_field=CustomFieldDto(name="Priority", id=2),
                required=False,
            ),
            values=[
                CustomFieldValueDto(name="High"),
                CustomFieldValueDto(name="Medium"),
                CustomFieldValueDto(name="Low"),
            ],
        ),
        CustomFieldProjectWithValuesDto(
            custom_field=CustomFieldProjectDto(
                custom_field=CustomFieldDto(name="Component", id=3),
                required=False,
            ),
            values=[CustomFieldValueDto(name="Auth")],
        ),
    ]

    with patch("src.client.client.AllureClient._ensure_valid_token", new_callable=AsyncMock):
        async with AllureClient("http://localhost", SecretStr("token"), project_id) as client:
            client.get_custom_fields_with_values = AsyncMock(return_value=mock_cfs)

            service = TestCaseService(client=client)
            result = await service._get_resolved_custom_fields(project_id)

            # All fields should be in result
            assert len(result) == 3, "Should have all 3 fields"
            assert "Layer" in result
            assert "Priority" in result
            assert "Component" in result

            # Verify each field's values
            assert result["Layer"]["values"] == ["UI", "API"]
            assert result["Priority"]["values"] == ["High", "Medium", "Low"]
            assert result["Component"]["values"] == ["Auth"]

            # Verify metadata
            assert result["Layer"]["required"] is True
            assert result["Priority"]["required"] is False
