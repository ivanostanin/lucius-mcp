import importlib
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.client.generated.models import TestLayerDto

# We need to test the TOOLS, or at least the Service which supports them.
# The tools are simple wrappers. Testing the Service validation logic (which we just updated)
# is the most direct way to verify the hints.
from src.services.test_case_service import TestCaseService
from src.services.test_layer_service import TestLayerService
from src.tools.create_test_case import create_test_case
from src.tools.update_test_case import update_test_case

update_test_case_module = importlib.import_module("src.tools.update_test_case")

create_test_case_module = importlib.import_module("src.tools.create_test_case")

# We can test the Service methods directly by instantiating TestCaseService
# and mocking the client. The validation logic is local and doesn't need API.


@pytest.fixture
def mock_client():
    client = MagicMock(spec=AllureClient)
    client.api_client = MagicMock()
    client.get_project.return_value = 1
    return client


@pytest.fixture
def service(mock_client):
    return TestCaseService(client=mock_client, test_layer_service=AsyncMock(spec=TestLayerService))


@pytest.mark.asyncio
async def test_create_test_case_invalid_steps_hint(service):
    """Verify hints for invalid steps structure."""
    # Action: Pass a list of integers instead of dicts for steps
    invalid_steps = ["not a dict"]

    with pytest.raises(Exception) as excinfo:  # Catch generic or AllureValidationError
        # We manually call validation or the method
        # Calling create_test_case will trigger validation first
        await service.create_test_case(name="Test", steps=invalid_steps)

    # Assertions
    # Check if we got AllureValidationError (or subclass)
    # Check for "Schema Hint" in the stringified exception OR in suggestions if accessible
    error_str = str(excinfo.value)
    assert "Step at index 0 must be a dictionary" in error_str
    # Check for hint text
    assert "Schema Hint" in error_str or (hasattr(excinfo.value, "suggestions") and excinfo.value.suggestions)


@pytest.mark.asyncio
async def test_create_test_case_invalid_tags_hint(service):
    """Verify hints for invalid tags structure."""
    # Action: Pass tags as string instead of list
    invalid_tags = "not a list"

    with pytest.raises(Exception) as excinfo:
        await service.create_test_case(name="Test", tags=invalid_tags)

    error_str = str(excinfo.value)
    assert "Tags must be a list" in error_str
    assert "Schema Hint" in error_str or (hasattr(excinfo.value, "suggestions") and excinfo.value.suggestions)


@pytest.mark.asyncio
async def test_create_test_case_invalid_tag_item_hint(service):
    """Verify hints for invalid tag item."""
    # Action: Pass a list containing non-string
    invalid_tags = [123]

    with pytest.raises(Exception) as excinfo:
        await service.create_test_case(name="Test", tags=invalid_tags)

    error_str = str(excinfo.value)
    assert "Tag at index 0 must be a string" in error_str
    assert "Schema Hint" in error_str or (hasattr(excinfo.value, "suggestions") and excinfo.value.suggestions)


@pytest.mark.asyncio
async def test_create_test_case_invalid_attachments_hint(service):
    """Verify hints for invalid attachments."""
    # Action: Pass attachment list with non-dict
    invalid_attachments = ["not a dict"]

    with pytest.raises(Exception) as excinfo:
        await service.create_test_case(name="Test", attachments=invalid_attachments)

    error_str = str(excinfo.value)
    error_str = str(excinfo.value)
    assert "Attachment at index 0 must be a dictionary" in error_str
    assert "Schema Hint" in error_str or (hasattr(excinfo.value, "suggestions") and excinfo.value.suggestions)


@pytest.mark.asyncio
async def test_update_test_case_invalid_nested_step_hint(service):
    """Verify hints when validating nested steps manually."""
    # Action: Pass steps with invalid nested attachment
    steps = [{"action": "step 1", "attachments": ["not a dict"]}]

    with pytest.raises(Exception) as excinfo:
        await service.create_test_case(name="Test", steps=steps)

    error_str = str(excinfo.value)
    assert "Step 0: 'attachments' must be a list" in error_str or "must be a dictionary" in error_str
    assert "Schema Hint" in error_str or (hasattr(excinfo.value, "suggestions") and excinfo.value.suggestions)


@pytest.mark.asyncio
async def test_create_test_case_invalid_custom_fields_hint(service):
    """Verify hints for invalid custom fields."""
    # Action: Pass custom_fields as list instead of dict
    invalid_cfs = ["not a dict"]

    with pytest.raises(Exception) as excinfo:
        await service.create_test_case(name="Test", custom_fields=invalid_cfs)

    error_str = str(excinfo.value)
    assert "Custom fields must be a dictionary" in error_str
    assert "Schema Hint" in error_str or (hasattr(excinfo.value, "suggestions") and excinfo.value.suggestions)


@pytest.mark.asyncio
async def test_create_test_case_tool_forwards_test_layers(monkeypatch):
    service = AsyncMock()
    service.create_test_case.return_value = MagicMock(id=1, name="Test")

    class DummyClient:
        async def __aenter__(self):
            return MagicMock()

        async def __aexit__(self, exc_type, exc, tb):
            return None

    monkeypatch.setattr(AllureClient, "from_env", MagicMock(return_value=DummyClient()))
    monkeypatch.setattr(create_test_case_module, "TestCaseService", MagicMock(return_value=service))

    result = await create_test_case(
        name="Test",
        test_layer_id=10,
        test_layer_name="Layer10",
        project_id=1,
    )

    assert "Created Test Case ID: 1" in result
    service.create_test_case.assert_called_once_with(
        name="Test",
        description=None,
        steps=None,
        tags=None,
        attachments=None,
        custom_fields=None,
        test_layer_id=10,
        test_layer_name="Layer10",
        issues=None,
    )


@pytest.mark.asyncio
async def test_update_test_case_tool_summary_includes_test_layer(monkeypatch):
    service = AsyncMock()
    service.get_test_case.return_value = MagicMock(id=1, name="Test", test_layer=None)
    service.update_test_case.return_value = MagicMock(id=1, name="Test")

    class DummyClient:
        async def __aenter__(self):
            return MagicMock()

        async def __aexit__(self, exc_type, exc, tb):
            return None

    monkeypatch.setattr(AllureClient, "from_env", MagicMock(return_value=DummyClient()))
    monkeypatch.setattr(
        update_test_case_module,
        "TestCaseService",
        MagicMock(return_value=service),
    )

    result = await update_test_case(
        test_case_id=1,
        test_layer_id=2,
        project_id=1,
    )

    assert "test layer updated" in result
    service.get_test_case.assert_called_once_with(1)
    service.update_test_case.assert_called_once()


@pytest.mark.asyncio
async def test_create_test_case_tool_propagates_errors(monkeypatch):
    service = AsyncMock()
    service.create_test_case.side_effect = ValueError("boom")

    class DummyClient:
        async def __aenter__(self):
            return MagicMock()

        async def __aexit__(self, exc_type, exc, tb):
            return None

    monkeypatch.setattr(AllureClient, "from_env", MagicMock(return_value=DummyClient()))
    monkeypatch.setattr(create_test_case_module, "TestCaseService", MagicMock(return_value=service))

    with pytest.raises(ValueError, match="boom"):
        await create_test_case(name="Test")


@pytest.mark.asyncio
async def test_create_test_case_invalid_test_layer_id_message(service: TestCaseService) -> None:
    service._test_layer_service.get_test_layer.side_effect = AllureNotFoundError("missing")
    service._test_layer_service.list_test_layers.return_value = [
        TestLayerDto(id=1, name="Layer1"),
        TestLayerDto(id=2, name="Layer2"),
    ]

    with pytest.raises(AllureValidationError) as excinfo:
        await service.create_test_case(name="Test", test_layer_id=123)

    error_str = str(excinfo.value)
    assert "Warning:" in error_str
    assert "Test layer ID 123 does not exist" in error_str
    assert "Test case creation was not performed" in error_str
    assert "Available test layers" in error_str
    assert "Use list_test_layers" in error_str
    assert "omit test_layer_id/test_layer_name" in error_str


@pytest.mark.asyncio
async def test_create_test_case_invalid_test_layer_name_message(service: TestCaseService) -> None:
    service._test_layer_service.list_test_layers.return_value = [
        TestLayerDto(id=1, name="Layer1"),
    ]

    with pytest.raises(AllureValidationError) as excinfo:
        await service.create_test_case(name="Test", test_layer_name="Missing")

    error_str = str(excinfo.value)
    assert "Warning:" in error_str
    assert "Test layer name 'Missing' not found" in error_str
    assert "Test case creation was not performed" in error_str
    assert "Available test layers" in error_str
    assert "Use list_test_layers" in error_str
    assert "omit test_layer_id/test_layer_name" in error_str


@pytest.mark.asyncio
async def test_create_test_case_ambiguous_test_layer_name_message(service: TestCaseService) -> None:
    service._test_layer_service.list_test_layers.return_value = [
        TestLayerDto(id=1, name="Layer"),
        TestLayerDto(id=2, name="Layer"),
    ]

    with pytest.raises(AllureValidationError) as excinfo:
        await service.create_test_case(name="Test", test_layer_name="Layer")

    error_str = str(excinfo.value)
    assert "Warning:" in error_str
    assert "Multiple test layers match name 'Layer'" in error_str
    assert "Test case creation was not performed" in error_str
    assert "Use test_layer_id" in error_str
