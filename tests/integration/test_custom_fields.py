from unittest.mock import AsyncMock, patch

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.generated.models import TestCaseTreeSelectionDto


@pytest.mark.asyncio
async def test_client_get_custom_fields_integration() -> None:
    """Test that client wrapper calls the generated API correctly."""
    project_id = 123

    # Mock the generated API controller
    with patch(
        "src.client.generated.api.test_case_custom_field_controller_api.TestCaseCustomFieldControllerApi"
    ) as mock_api_cls:
        mock_instance = mock_api_cls.return_value
        mock_instance.get_custom_fields_with_values2 = AsyncMock(return_value=[])

        # Patch _ensure_valid_token to prevent any auth/refresh logic
        with patch("src.client.client.AllureClient._ensure_valid_token", new_callable=AsyncMock):
            from pydantic import SecretStr

            async with AllureClient("http://localhost", SecretStr("token"), project_id) as client:
                # Inject our mock implementation of the generated client
                # Since _ensure_valid_token is mocked, it won't overwrite this
                client._test_case_custom_field_api = mock_instance

                # This method now exists
                await client.get_custom_fields_with_values(project_id)

                # Verify it called the generated API with correct DTO
                mock_instance.get_custom_fields_with_values2.assert_called_once()
                call_kwargs = mock_instance.get_custom_fields_with_values2.call_args[1]
                call_dto = call_kwargs["test_case_tree_selection_dto"]

                assert isinstance(call_dto, TestCaseTreeSelectionDto)
                assert call_dto.project_id == project_id


@pytest.mark.asyncio
async def test_client_get_custom_fields_validation() -> None:
    """Test validation in client wrapper."""
    # Patch _ensure_valid_token to avoid network calls
    with patch("src.client.client.AllureClient._ensure_valid_token", new_callable=AsyncMock):
        from pydantic import SecretStr

        async with AllureClient("http://localhost", SecretStr("token"), 1) as client:
            # Should raise error for invalid project_id
            with pytest.raises(AllureValidationError):
                await client.get_custom_fields_with_values(0)
