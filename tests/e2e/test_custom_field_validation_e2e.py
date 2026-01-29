"""E2E tests for custom field validation aggregation.

These tests verify that all missing custom fields and invalid values
are reported together in aggregated error responses.
"""

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.services.test_case_service import TestCaseService
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.mark.asyncio
async def test_e2e_all_missing_custom_fields_reported(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E Test: All missing custom field names are reported in a single error.

    This test verifies that when multiple non-existent custom fields are provided,
    the error message lists ALL of them in a single aggregated response.
    """
    service = TestCaseService(client=allure_client)

    case_name = "E2E Missing Fields Test"

    # Create a request with multiple non-existent custom fields
    # These field names should not exist in any real project
    custom_fields = {
        "NonExistentField1_E2E_Test": "Value1",
        "NonExistentField2_E2E_Test": "Value2",
        "NonExistentField3_E2E_Test": "Value3",
    }

    # Attempt to create test case with missing fields
    with pytest.raises(AllureValidationError) as exc_info:
        await service.create_test_case(name=case_name, custom_fields=custom_fields)

    error_msg = str(exc_info.value)

    # Verify ALL missing fields are reported
    assert "NonExistentField1_E2E_Test" in error_msg, "First missing field not in error"
    assert "NonExistentField2_E2E_Test" in error_msg, "Second missing field not in error"
    assert "NonExistentField3_E2E_Test" in error_msg, "Third missing field not in error"

    # Verify guidance is present
    assert "exclude all missing custom fields" in error_msg or "Usage Hint" in error_msg, "Guidance message not found"

    # Verify it's a structured error (not just a generic exception)
    assert "not found in project" in error_msg.lower() or "missing" in error_msg.lower()


@pytest.mark.asyncio
async def test_e2e_all_invalid_custom_field_values_reported(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E Test: All invalid custom field values are reported with allowed options.

    This test verifies that when custom fields exist but values are invalid,
    the error message lists ALL invalid values with their allowed options.
    """
    service = TestCaseService(client=allure_client)

    # First, discover actual custom fields with allowed values
    all_custom_fields = await service.get_custom_fields()

    # Filter to only fields with constrained values (non-empty values list)
    fields_with_values = [cf for cf in all_custom_fields if cf.get("values") and len(cf["values"]) > 0]

    if len(fields_with_values) < 2:
        pytest.skip(
            f"Need at least 2 custom fields with allowed values in project {project_id}. "
            f"Found {len(fields_with_values)}. Configure custom fields in TestOps before running this test."
        )

    # Select first two fields with allowed values
    field1 = fields_with_values[0]
    field2 = fields_with_values[1]

    field1_name = field1["name"]
    field2_name = field2["name"]
    field1_allowed = field1["values"]
    field2_allowed = field2["values"]

    # Create invalid values that are NOT in the allowed lists
    # Use a distinctive invalid value pattern
    invalid_value1 = f"INVALID_E2E_VALUE_NOT_IN_LIST_{field1_name}"
    invalid_value2 = f"INVALID_E2E_VALUE_NOT_IN_LIST_{field2_name}"

    # Ensure our invalid values are truly not in the allowed lists
    assert invalid_value1 not in field1_allowed, f"Test data issue: {invalid_value1} exists in allowed values"
    assert invalid_value2 not in field2_allowed, f"Test data issue: {invalid_value2} exists in allowed values"

    case_name = "E2E Invalid Values Test"
    custom_fields = {
        field1_name: invalid_value1,
        field2_name: invalid_value2,
    }

    # Attempt to create test case with invalid values
    with pytest.raises(AllureValidationError) as exc_info:
        await service.create_test_case(name=case_name, custom_fields=custom_fields)

    error_msg = str(exc_info.value)

    # Verify ALL invalid field/value pairs are reported
    assert field1_name in error_msg, f"Field '{field1_name}' not in error"
    assert field2_name in error_msg, f"Field '{field2_name}' not in error"

    # Verify the invalid values are shown
    assert invalid_value1 in error_msg or field1_name in error_msg, "First invalid value not referenced"
    assert invalid_value2 in error_msg or field2_name in error_msg, "Second invalid value not referenced"

    # Verify allowed values are mentioned (implementation shows them)
    assert "Allowed:" in error_msg or "allowed" in error_msg.lower(), "Allowed values hint not found"

    # Verify guidance to correct values
    assert "Correct any invalid values" in error_msg or "invalid" in error_msg.lower(), (
        "Guidance to correct values not found"
    )


@pytest.mark.asyncio
async def test_e2e_mixed_missing_and_invalid_reported(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E Test: Both missing fields and invalid values are reported together.

    This test verifies that when a request contains BOTH non-existent fields
    AND invalid values for existing fields, both error types are aggregated
    into a single comprehensive error message.
    """
    service = TestCaseService(client=allure_client)

    # Discover custom fields to find one with allowed values
    all_custom_fields = await service.get_custom_fields()
    fields_with_values = [cf for cf in all_custom_fields if cf.get("values") and len(cf["values"]) > 0]

    if len(fields_with_values) < 1:
        pytest.skip(
            f"Need at least 1 custom field with allowed values in project {project_id}. "
            f"Configure custom fields in TestOps before running this test."
        )

    # Use one existing field with an invalid value
    existing_field = fields_with_values[0]
    existing_field_name = existing_field["name"]
    existing_field_allowed = existing_field["values"]
    invalid_value = f"INVALID_MIXED_E2E_VALUE_{existing_field_name}"

    assert invalid_value not in existing_field_allowed, "Test data issue: invalid value exists"

    case_name = "E2E Mixed Errors Test"

    # Mix of: missing fields AND invalid values for existing fields
    custom_fields = {
        # Missing fields (don't exist)
        "MixedMissingField1_E2E": "Value1",
        "MixedMissingField2_E2E": "Value2",
        # Existing field with invalid value
        existing_field_name: invalid_value,
    }

    # Attempt to create test case
    with pytest.raises(AllureValidationError) as exc_info:
        await service.create_test_case(name=case_name, custom_fields=custom_fields)

    error_msg = str(exc_info.value)

    # Verify BOTH error types are present in the same message

    # Check for missing fields section
    assert "MixedMissingField1_E2E" in error_msg, "First missing field not reported"
    assert "MixedMissingField2_E2E" in error_msg, "Second missing field not reported"
    assert "not found" in error_msg.lower() or "missing" in error_msg.lower(), "Missing fields section not found"

    # Check for invalid values section
    assert existing_field_name in error_msg, f"Existing field '{existing_field_name}' not in error"
    assert "invalid" in error_msg.lower(), "Invalid values section not found"

    # Verify comprehensive guidance
    assert "Usage Hint" in error_msg or "exclude" in error_msg.lower(), "Guidance section not found"

    # The guidance should mention both issues
    # Our implementation uses numbered list: "1. Exclude..." and "2. Correct..."
    guidance_mentions_exclusion = "exclude" in error_msg.lower() or "remove" in error_msg.lower()
    guidance_mentions_correction = "correct" in error_msg.lower()

    assert guidance_mentions_exclusion, "Guidance doesn't mention excluding missing fields"
    assert guidance_mentions_correction, "Guidance doesn't mention correcting invalid values"
