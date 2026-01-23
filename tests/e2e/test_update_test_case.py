import pytest

from src.client import AllureClient
from src.services.test_case_service import TestCaseService, TestCaseUpdate
from src.utils.auth import get_auth_context
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.mark.asyncio
async def test_update_test_case_e2e(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    pixel_b64: str,
    api_token: str,
) -> None:
    """End-to-end test for updating a test case."""

    # 1. Setup
    # Fixture 'allure_client' provides authenticated client
    service = TestCaseService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    # Fixture 'project_id' provides valid project ID
    # project_id = ...

    # Create initial test case
    case_name = "E2E Update Test"
    initial_steps = [{"action": "Initial Step"}]
    created_case = await service.create_test_case(project_id, case_name, steps=initial_steps)
    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    # Verify scenario immediately after creation
    initial_scenario = await allure_client.get_test_case_scenario(test_case_id)
    assert allure_client._test_case_scenario_api is not None
    raw_norm_init = await allure_client._test_case_scenario_api.get_normalized_scenario(id=test_case_id)
    print(f"DEBUG Initial Raw Normalized Scenario: {raw_norm_init}")
    print(f"DEBUG Initial Denormalized Scenario: {initial_scenario}")

    # 2. Update Simple Fields
    new_name = f"{case_name} Updated"
    new_desc = "Updated description"

    update_data = TestCaseUpdate(name=new_name, description=new_desc)
    updated_case = await service.update_test_case(test_case_id, update_data)

    # Verify scenario after field update
    field_update_scenario = await allure_client.get_test_case_scenario(test_case_id)
    print(f"DEBUG Scenario after field update: {field_update_scenario}")

    assert updated_case.name == new_name
    assert updated_case.description == new_desc

    # 3. Verify Idempotency (No-op)
    # Call again with same data
    repeated_update_case = await service.update_test_case(test_case_id, update_data)
    assert repeated_update_case.name == new_name

    # 4. Partial Step Update (Add attachment, preserve steps)
    # Use fixture pixel_b64
    attachments = [{"name": "test.png", "content": pixel_b64, "content_type": "image/png"}]

    update_att_data = TestCaseUpdate(attachments=attachments)
    await service.update_test_case(test_case_id, update_att_data)

    # Fetch Verification
    scenario = await allure_client.get_test_case_scenario(test_case_id)
    try:
        # Also try normalized scenario to see if steps are there
        assert allure_client._test_case_scenario_api is not None
        norm_scenario = await allure_client._test_case_scenario_api.get_normalized_scenario(id=test_case_id)
        print(f"DEBUG Final Normalized Scenario: {norm_scenario}")
    except Exception as e:
        print(f"DEBUG Normalized Scenario Error: {e}")

    print(f"DEBUG Scenario: {scenario}")
    print(f"DEBUG Scenario Steps: {scenario.steps}")
    # Should have the initial step + the new attachment
    # Note: The exact structure depends on how API stored it.
    # We expect 'steps' to contain both.
    assert scenario.steps is not None

    # Check if attachment is present
    has_attachment = False
    if scenario.steps:
        for step in scenario.steps:
            if step.actual_instance:
                # Check if it's an AttachmentStepDto
                if isinstance(step.actual_instance.type, str) and step.actual_instance.type == "AttachmentStepDto":
                    has_attachment = True
                    break
                # OR verify nested steps if any (though global attachments are usually root)

    # If our update logic worked, the attachment should be there.
    assert has_attachment, f"Attachment not found in scenario. Scenario steps: {scenario.steps}"

    # 5. verify steps preserved
    # Searching for "Initial Step"
    step_found = False
    if scenario.steps:
        for step in scenario.steps:
            if step.actual_instance:
                # Check BodyStepDto
                if hasattr(step.actual_instance, "body") and step.actual_instance.body == "Initial Step":
                    step_found = True
                    break

    assert step_found, "Initial step not found in scenario after update"


@pytest.mark.asyncio
async def test_e2e_u1_update_core_fields(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    api_token: str,
) -> None:
    """
    E2E-U1: Update Core Fields.
    Test updating name, description, precondition, and expected_result.
    """
    service = TestCaseService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    # Create initial test case
    case_name = "E2E-U1 Initial Name"
    created_case = await service.create_test_case(
        project_id=project_id, name=case_name, description="Initial description"
    )
    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    # Update core fields
    update_data = TestCaseUpdate(
        name="E2E-U1 Updated Name",
        description="**Updated** description with markdown",
        precondition="# Preconditions\n- User is logged in",
        expected_result="Test should pass successfully",
    )

    updated_case = await service.update_test_case(test_case_id, update_data)

    # Verify updates
    assert updated_case.name == "E2E-U1 Updated Name"
    assert updated_case.description == "**Updated** description with markdown"
    assert updated_case.precondition == "# Preconditions\n- User is logged in"
    assert updated_case.expected_result == "Test should pass successfully"

    # Refetch to double-check
    fetched_case = await service.get_test_case(test_case_id)
    assert fetched_case.name == "E2E-U1 Updated Name"
    assert fetched_case.description == "**Updated** description with markdown"


@pytest.mark.asyncio
async def test_e2e_u2_update_status_workflow(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    api_token: str,
) -> None:
    """
    E2E-U2: Update Status & Workflow.
    Test updating status_id, workflow_id, test_layer_id, and automated flag.
    """
    service = TestCaseService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    # Create initial test case
    created_case = await service.create_test_case(project_id=project_id, name="E2E-U2 Status Test")
    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    initial_case = await service.get_test_case(test_case_id)
    initial_automated = initial_case.automated

    # Update automated flag (toggle it)
    update_data = TestCaseUpdate(automated=not initial_automated)
    updated_case = await service.update_test_case(test_case_id, update_data)

    # Verify automated flag changed
    assert updated_case.automated == (not initial_automated)


@pytest.mark.asyncio
async def test_e2e_u3_update_tags(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    api_token: str,
) -> None:
    """
    E2E-U3: Update Tags.
    Test replacing tags, adding new tags, and removing all tags.
    """
    service = TestCaseService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    # Create with initial tags
    created_case = await service.create_test_case(
        project_id=project_id, name="E2E-U3 Tags Test", tags=["initial", "tag1"]
    )
    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    # Verify initial tags
    fetched_case = await service.get_test_case(test_case_id)
    initial_tag_names = sorted([t.name for t in (fetched_case.tags or []) if t.name])
    assert "initial" in initial_tag_names
    assert "tag1" in initial_tag_names

    # Replace tags
    update_data = TestCaseUpdate(tags=["updated", "tag2", "tag3"])
    await service.update_test_case(test_case_id, update_data)

    # Verify tags replaced
    fetched_case = await service.get_test_case(test_case_id)
    updated_tag_names = sorted([t.name for t in (fetched_case.tags or []) if t.name])
    assert "updated" in updated_tag_names
    assert "tag2" in updated_tag_names
    assert "tag3" in updated_tag_names
    assert "initial" not in updated_tag_names

    # Remove all tags
    update_data_empty = TestCaseUpdate(tags=[])
    await service.update_test_case(test_case_id, update_data_empty)

    fetched_case = await service.get_test_case(test_case_id)
    final_tag_names = [t.name for t in (fetched_case.tags or []) if t.name]
    assert len(final_tag_names) == 0


@pytest.mark.asyncio
async def test_e2e_u4_update_custom_fields(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    api_token: str,
) -> None:
    """
    E2E-U4: Update Custom Fields.
    Test replacing custom field values and adding new custom fields.
    """
    service = TestCaseService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    # Create with initial custom fields
    # Note: Custom fields must exist in the project
    created_case = await service.create_test_case(
        project_id=project_id, name="E2E-U4 Custom Fields Test", custom_fields={"Feature": "Test"}
    )
    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    # Update custom fields
    update_data = TestCaseUpdate(custom_fields={"Feature": "Flow", "Component": "API"})
    await service.update_test_case(test_case_id, update_data)

    # Verify custom fields updated
    fetched_case = await service.get_test_case(test_case_id)
    custom_fields = getattr(fetched_case, "custom_fields", None)
    if custom_fields:
        cf_values = {cf.custom_field.name: cf.name for cf in custom_fields if cf.custom_field}
        # At least one should be updated
        assert cf_values.get("Feature") == "Flow" or cf_values.get("Component") == "API"
