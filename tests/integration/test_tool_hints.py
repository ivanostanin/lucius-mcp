from unittest.mock import MagicMock

import pytest

from src.client import AllureClient

# We need to test the TOOLS, or at least the Service which supports them.
# The tools are simple wrappers. Testing the Service validation logic (which we just updated)
# is the most direct way to verify the hints.
from src.services.test_case_service import TestCaseService

# We can test the Service methods directly by instantiating TestCaseService
# and mocking the client. The validation logic is local and doesn't need API.


@pytest.fixture
def mock_client():
    client = MagicMock(spec=AllureClient)
    client.api_client = MagicMock()
    return client


@pytest.fixture
def service(mock_client):
    return TestCaseService(mock_client)


@pytest.mark.asyncio
async def test_create_test_case_invalid_steps_hint(service):
    """Verify hints for invalid steps structure."""
    # Action: Pass a list of integers instead of dicts for steps
    invalid_steps = ["not a dict"]

    with pytest.raises(Exception) as excinfo:  # Catch generic or AllureValidationError
        # We manually call validation or the method
        # Calling create_test_case will trigger validation first
        await service.create_test_case(project_id=1, name="Test", steps=invalid_steps)

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
        await service.create_test_case(project_id=1, name="Test", tags=invalid_tags)

    error_str = str(excinfo.value)
    assert "Tags must be a list" in error_str
    assert "Schema Hint" in error_str or (hasattr(excinfo.value, "suggestions") and excinfo.value.suggestions)


@pytest.mark.asyncio
async def test_create_test_case_invalid_tag_item_hint(service):
    """Verify hints for invalid tag item."""
    # Action: Pass a list containing non-string
    invalid_tags = [123]

    with pytest.raises(Exception) as excinfo:
        await service.create_test_case(project_id=1, name="Test", tags=invalid_tags)

    error_str = str(excinfo.value)
    assert "Tag at index 0 must be a string" in error_str
    assert "Schema Hint" in error_str or (hasattr(excinfo.value, "suggestions") and excinfo.value.suggestions)


@pytest.mark.asyncio
async def test_create_test_case_invalid_attachments_hint(service):
    """Verify hints for invalid attachments."""
    # Action: Pass attachment list with non-dict
    invalid_attachments = ["not a dict"]

    with pytest.raises(Exception) as excinfo:
        await service.create_test_case(project_id=1, name="Test", attachments=invalid_attachments)

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
        await service.create_test_case(project_id=1, name="Test", steps=steps)

    error_str = str(excinfo.value)
    assert "Step 0: 'attachments' must be a list" in error_str or "must be a dictionary" in error_str
    assert "Schema Hint" in error_str or (hasattr(excinfo.value, "suggestions") and excinfo.value.suggestions)


@pytest.mark.asyncio
async def test_create_test_case_invalid_custom_fields_hint(service):
    """Verify hints for invalid custom fields."""
    # Action: Pass custom_fields as list instead of dict
    invalid_cfs = ["not a dict"]

    with pytest.raises(Exception) as excinfo:
        await service.create_test_case(project_id=1, name="Test", custom_fields=invalid_cfs)

    error_str = str(excinfo.value)
    assert "Custom fields must be a dictionary" in error_str
    assert "Schema Hint" in error_str or (hasattr(excinfo.value, "suggestions") and excinfo.value.suggestions)
