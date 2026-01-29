from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.generated.models import (
    CustomFieldDto,
    CustomFieldProjectDto,
    CustomFieldProjectWithValuesDto,
)
from src.services.test_case_service import TestCaseService


@pytest.fixture
def mock_client():
    client = AsyncMock(spec=AllureClient)
    client.get_project.return_value = 1
    # Mock the api_client attribute which is used to instantiate the controller
    client.api_client = MagicMock()
    return client


@pytest.fixture
def service(mock_client):
    return TestCaseService(client=mock_client)


@pytest.mark.asyncio
async def test_create_test_case_aggregated_missing_fields_error(service, mock_client):
    """
    Test that providing multiple missing custom fields returns a single aggregated error
    listing ALL missing fields, not just the first one.
    """
    # Setup: Mock the custom field API to return only one valid field "ExistingField"
    with patch(
        "src.client.generated.api.test_case_custom_field_controller_api.TestCaseCustomFieldControllerApi"
    ) as mock_api_cls:
        mock_api_instance = mock_api_cls.return_value

        # Define one existing field
        existing_cf = CustomFieldProjectWithValuesDto(
            custom_field=CustomFieldProjectDto(custom_field=CustomFieldDto(id=100, name="ExistingField"))
        )

        # Return list containing only the existing field
        mock_api_instance.get_custom_fields_with_values2 = AsyncMock(return_value=[existing_cf])

        # Action: Try to create a test case with:
        # 1. One existing field
        # 2. Two MISSING fields
        custom_fields = {"ExistingField": "Value", "MissingField1": "Value", "MissingField2": "Value"}

        # Assert: Expect AllureValidationError
        with pytest.raises(AllureValidationError) as exc_info:
            await service.create_test_case(name="Test Case", custom_fields=custom_fields)

        error_msg = str(exc_info.value)

        # verify both missing fields are listed in the error
        assert "MissingField1" in error_msg
        assert "MissingField2" in error_msg

        # Verify the specific guidance text is present
        assert (
            "Usage Hint" in error_msg
            or "Please remove these fields" in error_msg
            or "exclude all missing custom fields" in error_msg
        )


@pytest.mark.asyncio
async def test_create_test_case_invalid_values_aggregation(service, mock_client):
    """
    Placeholder for second AC: Invalid values aggregation.
    Note: Current implementation of TestCaseService might not validate values client-side
    unless checking against enum values from the fetched CFs.
    If value validation is added, this test should be expanded.
    """
    pass
