from unittest.mock import AsyncMock, patch

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureValidationError


@pytest.mark.asyncio
async def test_client_get_custom_fields_integration() -> None:
    """Test that client wrapper calls the generated V2 and Value APIs correctly."""
    project_id = 123

    # Mock the generated API controllers
    with (
        patch(
            "src.client.generated.api.custom_field_project_controller_v2_api.CustomFieldProjectControllerV2Api"
        ) as mock_v2_cls,
        patch(
            "src.client.generated.api.custom_field_value_project_controller_api.CustomFieldValueProjectControllerApi"
        ) as mock_val_cls,
    ):
        mock_v2 = mock_v2_cls.return_value
        mock_val = mock_val_cls.return_value

        from src.client.generated.models.custom_field_dto import CustomFieldDto
        from src.client.generated.models.custom_field_project_dto import CustomFieldProjectDto
        from src.client.generated.models.page_custom_field_project_dto import PageCustomFieldProjectDto
        from src.client.generated.models.page_custom_field_value_with_tc_count_dto import (
            PageCustomFieldValueWithTcCountDto,
        )

        # Mock find_by_project1 to return one field
        mock_v2.find_by_project1 = AsyncMock(
            return_value=PageCustomFieldProjectDto(
                content=[CustomFieldProjectDto(custom_field=CustomFieldDto(id=1, name="Field1"), required=True)]
            )
        )

        # Mock find_all22 to return no values
        mock_val.find_all22 = AsyncMock(return_value=PageCustomFieldValueWithTcCountDto(content=[]))

        # Patch _ensure_valid_token to prevent any auth/refresh logic
        with patch("src.client.client.AllureClient._ensure_valid_token", new_callable=AsyncMock):
            from pydantic import SecretStr

            async with AllureClient("http://localhost", SecretStr("token"), project_id) as client:
                # Inject mocks
                client._custom_field_project_v2_api = mock_v2
                client._custom_field_value_project_api = mock_val

                await client.get_custom_fields_with_values(project_id)

                # Verify calls
                mock_v2.find_by_project1.assert_called_once_with(project_id=project_id)
                mock_val.find_all22.assert_called_once_with(project_id=project_id, custom_field_id=1)


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
