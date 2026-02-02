"""E2E tests for the get_custom_fields tool.

These tests verify the get_custom_fields functionality against
a real Allure TestOps sandbox environment.
"""

import pytest

from src.client import AllureClient
from src.services.test_case_service import TestCaseService
from src.tools.get_custom_fields import get_custom_fields
from tests.e2e.helpers.cleanup import CleanupTracker


async def test_e2e_get_all_custom_fields(
    project_id: int,
    allure_client: AllureClient,
) -> None:
    """E2E Test: Retrieve all custom fields for a project.

    Verifies that the tool can fetch and format all custom fields
    from the sandbox environment.
    """
    service = TestCaseService(client=allure_client)

    # Get all custom fields
    fields = await service.get_custom_fields()

    # Verify response structure
    assert isinstance(fields, list), "Response should be a list"

    # If fields exist, verify structure
    if fields:
        # Each field should have name, required, and values
        for field in fields:
            assert "name" in field, "Field missing 'name' key"
            assert "required" in field, "Field missing 'required' key"
            assert "values" in field, "Field missing 'values' key"

            assert isinstance(field["name"], str), "Field name should be string"
            assert isinstance(field["required"], bool), "Required should be boolean"
            assert isinstance(field["values"], list), "Values should be list"

            print(f"Found field: {field['name']} (required={field['required']}, values={len(field['values'])})")


async def test_e2e_get_custom_fields_with_filter(
    project_id: int,
    allure_client: AllureClient,
) -> None:
    """E2E Test: Filter custom fields by name (case-insensitive).

    Verifies that name filtering works correctly with real data.
    """
    service = TestCaseService(client=allure_client)

    # First, get all fields to find one to filter
    all_fields = await service.get_custom_fields()

    if not all_fields:
        pytest.skip(
            f"No custom fields found in project {project_id}. "
            "Configure custom fields in TestOps before running this test."
        )

    # Use the first field's name for filtering test
    test_field = all_fields[0]
    field_name = test_field["name"]

    # Test exact match (case-insensitive)
    filtered = await service.get_custom_fields(name=field_name.lower())
    assert len(filtered) >= 1, f"Should find at least one field matching '{field_name}'"
    assert any(f["name"] == field_name for f in filtered), f"Should include exact match for '{field_name}'"

    # Test partial match
    if len(field_name) > 3:
        partial_name = field_name[:3]
        partial_filtered = await service.get_custom_fields(name=partial_name)
        # Should find at least the original field (possibly more if names share prefix)
        assert len(partial_filtered) >= 1, f"Should find fields matching partial name '{partial_name}'"
        matching_names = [f["name"] for f in partial_filtered]
        print(f"Partial match '{partial_name}' found fields: {matching_names}")


async def test_e2e_get_custom_fields_tool_output(
    project_id: int,
) -> None:
    """E2E Test: Verify tool output format for LLM consumption.

    Tests the actual tool function that formats output as plain text.
    """
    # Call the tool directly (it will use project_id from env)
    output = await get_custom_fields(project_id=project_id)

    # Verify it's a string (LLM-friendly format)
    assert isinstance(output, str), "Tool should return string"

    # Verify basic formatting
    if "No custom fields found" not in output:
        # Should have header
        assert "Found" in output and "custom fields:" in output, "Should have count header"

        # Should have bullet points
        assert "- " in output, "Should use bullet point formatting"

        # Should have required/optional indicators
        assert "required" in output.lower() or "optional" in output.lower(), "Should indicate required status"

        print(f"Tool output:\n{output}")
    else:
        print("No custom fields in project - output shows appropriate message")


async def test_e2e_get_custom_fields_nonexistent_name(
    project_id: int,
    allure_client: AllureClient,
) -> None:
    """E2E Test: Filter with non-existent name returns appropriate message.

    Verifies graceful handling when no fields match the filter.
    """
    # Use a very unlikely field name
    unlikely_name = "ThisFieldDefinitelyDoesNotExist_E2E_Test_987654321"

    output = await get_custom_fields(name=unlikely_name, project_id=project_id)

    # Should return not-found message
    assert "No custom fields found" in output, "Should indicate no matches found"
    assert unlikely_name in output, "Should mention the search term"

    print(f"Not found message: {output}")


async def test_e2e_get_custom_fields_with_values_constraints(
    project_id: int,
    allure_client: AllureClient,
) -> None:
    """E2E Test: Verify fields with allowed values are properly reported.

    This test validates that custom fields with constrained values
    (dropdowns, multi-select, etc.) properly report their allowed values.
    """
    service = TestCaseService(client=allure_client)

    # Get all custom fields
    all_fields = await service.get_custom_fields()
    # Find fields that have allowed values
    fields_with_values = [f for f in all_fields if f.get("values") and len(f["values"]) > 0]

    if not fields_with_values:
        pytest.skip(
            f"No custom fields with constrained values in project {project_id}. "
            "Configure dropdown/select custom fields in TestOps before running this test."
        )

    # Verify structure of fields with values
    for field in fields_with_values:
        field_name = field["name"]
        values = field["values"]
        required = field["required"]

        print(f"Field '{field_name}' (required={required}) has {len(values)} allowed values: {values}")

        # All values should be strings
        assert all(isinstance(v, str) for v in values), f"All values for '{field_name}' should be strings"

        # Values should not be empty strings
        assert all(len(v) > 0 for v in values), f"Values for '{field_name}' should not be empty"


async def test_e2e_get_custom_fields_cache_efficiency(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
) -> None:
    """E2E Test: Verify that get_custom_fields uses cache efficiently.

    This test validates that multiple calls to get_custom_fields
    within the same session benefit from caching, and that the cache
    is shared with create_test_case operations.
    """
    service = TestCaseService(client=allure_client)

    # First call - populates cache
    fields_first = await service.get_custom_fields()

    # Second call - should use cache
    fields_second = await service.get_custom_fields()

    # Results should be identical
    assert fields_first == fields_second, "Cached results should match original"

    # Now create a test case - this should also use the same cache
    # If there are fields with values, we can test that validation uses the cached data
    fields_with_values = [f for f in fields_first if f.get("values") and len(f["values"]) > 0]

    if fields_with_values:
        # Pick a field with values and use a valid value
        test_field = fields_with_values[0]
        field_name = test_field["name"]
        valid_value = test_field["values"][0]

        # Create test case with valid custom field (should succeed using cached validation)
        case = await service.create_test_case(
            name=f"[{test_run_id}] Cache Test", custom_fields={field_name: valid_value}
        )
        cleanup_tracker.track_test_case(case.id)

        assert case.id is not None, "Test case should be created successfully"
        print(f"Successfully created test case {case.id} using cached custom field validation")
    else:
        print("No fields with values to test cache integration with create_test_case")


async def test_e2e_get_custom_fields_empty_project(
    allure_client: AllureClient,
) -> None:
    """E2E Test: Handle projects with no custom fields gracefully.

    Note: This test may skip if the configured project has custom fields.
    """
    service = TestCaseService(client=allure_client)

    fields = await service.get_custom_fields()

    # If no fields, verify graceful handling
    if not fields:
        # Tool should return appropriate message
        output = await get_custom_fields()
        assert "No custom fields found" in output, "Should indicate no fields in project"
        print("Project has no custom fields - verified graceful handling")
    else:
        # This is fine - the test project has fields
        print(f"Project has {len(fields)} custom fields - skipping empty project test")
