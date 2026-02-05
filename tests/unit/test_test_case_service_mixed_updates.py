from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client import AllureClient
from src.client.generated.models import (
    CustomFieldDto,
    CustomFieldProjectDto,
    CustomFieldProjectWithValuesDto,
    CustomFieldValueDto,
    CustomFieldValueWithCfDto,
    TestCaseDto,
    TestCasePatchV2Dto,
    TestLayerDto,
)
from src.services.test_case_service import TestCaseService, TestCaseUpdate
from src.services.test_layer_service import TestLayerService


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock(spec=AllureClient)
    client.api_client = MagicMock()
    client.get_project.return_value = 1
    return client


@pytest.fixture
def service(mock_client: AsyncMock) -> TestCaseService:
    return TestCaseService(client=mock_client, test_layer_service=AsyncMock(spec=TestLayerService))


@pytest.mark.asyncio
async def test_update_test_layer_unset_with_zero(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test that passing test_layer_id=0 unsets the layer."""
    test_case_id = 100
    # Current case has a layer
    mock_client.get_test_case.return_value = TestCaseDto(
        id=test_case_id, test_layer=TestLayerDto(id=5, name="Existing")
    )
    mock_client.update_test_case.return_value = TestCaseDto(id=test_case_id)  # No layer in return

    data = TestCaseUpdate(test_layer_id=0)
    await service.update_test_case(test_case_id, data)

    # Verify 0 was passed in patch
    mock_client.update_test_case.assert_called_once()
    patch_arg: TestCasePatchV2Dto = mock_client.update_test_case.call_args[0][1]
    assert patch_arg.test_layer_id == 0


@pytest.mark.asyncio
async def test_mixed_update_custom_fields_and_layer(service: TestCaseService, mock_client: AsyncMock) -> None:
    """Test mixed update of custom fields and test layer (triggers merge logic)."""
    test_case_id = 101

    # Mock current state
    mock_client.get_test_case.return_value = TestCaseDto(
        id=test_case_id, test_layer=TestLayerDto(id=5, name="Old Layer")
    )

    # Mock CF resolution via internal cache
    project_cfs = {
        "Priority": {
            "id": 10,
            "project_cf_id": 100,
            "required": False,
            "single_select": True,
            "values": ["High", "Low"],
            "values_map": {"High": 1, "Low": 2},
        }
    }
    service._cf_cache[1] = project_cfs

    # Mock existing CFs on test case using CORRECT DTO STRUCTURE
    # The service expects a list of CustomFieldProjectWithValuesDto
    current_cfs = [
        CustomFieldProjectWithValuesDto(
            custom_field=CustomFieldProjectDto(
                id=999,  # project_cf_id
                custom_field=CustomFieldDto(id=100, name="Priority"),
            ),
            values=[CustomFieldValueDto(id=2, name="Low")],
        )
    ]
    mock_client.get_test_case_custom_fields.return_value = current_cfs

    # Mock get_test_case_custom_fields_values for check (called by service internally)
    # This actually calls get_test_case_custom_fields inside service, so we don't need to mock it separately
    # if service calls client method directly?
    # Wait, service class methods for values -> it calls client.get_test_case_custom_fields.

    # Mock Layer validation
    service._test_layer_service.get_test_layer.return_value = TestLayerDto(id=99, name="New Layer")

    # Perform Update: Layer -> 99, Priority -> High
    data = TestCaseUpdate(test_layer_id=99, custom_fields={"Priority": "High"})

    await service.update_test_case(test_case_id, data)

    # Verify Patch contains both
    mock_client.update_test_case.assert_called_once()
    patch_arg: TestCasePatchV2Dto = mock_client.update_test_case.call_args[0][1]

    assert patch_arg.test_layer_id == 99
    assert patch_arg.custom_fields is not None

    # Verify CFs merged correctly (Low should be replaced by High)
    cfs = patch_arg.custom_fields
    assert len(cfs) == 1

    # Check that it's High (id=1)
    # The logic builds new DTOs (CustomFieldValueWithCfDto)
    assert isinstance(cfs[0], CustomFieldValueWithCfDto)
    assert cfs[0].custom_field is not None
    assert cfs[0].custom_field.id == 10  # Global ID (10), not Project CF ID (100)
    assert cfs[0].id == 1  # High
