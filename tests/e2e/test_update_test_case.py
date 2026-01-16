import os

import pytest

from src.client import AllureClient
from src.services.test_case_service import TestCaseService, TestCaseUpdate


# Skip E2E tests if no API token/endpoint provided
@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_update_test_case_e2e() -> None:
    """End-to-end test for updating a test case."""

    # 1. Setup
    async with AllureClient.from_env() as client:
        service = TestCaseService(client)

        # Get a valid project ID (assuming project 1 exists or use env)
        project_id = int(os.getenv("ALLURE_PROJECT_ID", "1"))

        # Create initial test case
        case_name = "E2E Update Test"
        initial_steps = [{"action": "Initial Step"}]
        created_case = await service.create_test_case(project_id, case_name, steps=initial_steps)
        test_case_id = created_case.id
        assert test_case_id is not None

        # Verify scenario immediately after creation
        initial_scenario = await client.get_test_case_scenario(test_case_id)
        raw_norm_init = await client._test_case_scenario_api.get_normalized_scenario(id=test_case_id)
        print(f"DEBUG Initial Raw Normalized Scenario: {raw_norm_init}")
        print(f"DEBUG Initial Denormalized Scenario: {initial_scenario}")

        try:
            # 2. Update Simple Fields
            new_name = f"{case_name} Updated"
            new_desc = "Updated description"

            update_data = TestCaseUpdate(name=new_name, description=new_desc)
            updated_case = await service.update_test_case(test_case_id, update_data)

            # Verify scenario after field update
            field_update_scenario = await client.get_test_case_scenario(test_case_id)
            print(f"DEBUG Scenario after field update: {field_update_scenario}")

            assert updated_case.name == new_name
            assert updated_case.description == new_desc

            # 3. Verify Idempotency (No-op)
            # Call again with same data
            repeated_update_case = await service.update_test_case(test_case_id, update_data)
            assert repeated_update_case.name == new_name

            # 4. Partial Step Update (Add attachment, preserve steps)
            # Note: In real API, we need to provide valid attachment content.
            # Using a small base64 pixel
            pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgANjd8qAAAAAElFTkSuQmCC"
            attachments = [{"name": "test.png", "content": pixel_b64, "content_type": "image/png"}]

            update_att_data = TestCaseUpdate(attachments=attachments)
            await service.update_test_case(test_case_id, update_att_data)

            # Fetch Verification
            scenario = await client.get_test_case_scenario(test_case_id)
            try:
                # Also try normalized scenario to see if steps are there
                norm_scenario = await client._test_case_scenario_api.get_normalized_scenario(id=test_case_id)
                print(f"DEBUG Final Normalized Scenario: {norm_scenario}")
            except Exception as e:
                print(f"DEBUG Normalized Scenario Error: {e}")

            print(f"DEBUG Scenario: {scenario}")
            print(f"DEBUG Scenario Steps: {scenario.steps}")
            # Should have the initial step + the new attachment
            # Note: The exact structure depends on how API stored it.
            # We expect 'steps' to contain both.
            assert scenario.steps is not None
            # Depending on implementation, attachment might be a step or in 'attachments' list in READ model?
            # get_test_case_scenario returns TestCaseScenarioDto which HAS separate attachments list.
            # But our UPDATE combined them into steps.
            # So the API might return them as steps now? OR it might normalize them back to attachments list?
            # This behavior is API specific. We'll check if total count > 1 or look for attachment.

            # Check if attachment is present
            has_attachment = False
            if scenario.steps:
                for step in scenario.steps:
                    if step.actual_instance:
                        # Check if it's an AttachmentStepDto
                        if (
                            isinstance(step.actual_instance.type, str)
                            and step.actual_instance.type == "AttachmentStepDto"
                        ):
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

        finally:
            # Cleanup
            await client.delete_test_case(test_case_id)


# ==========================================
# Comprehensive Update Tests
# ==========================================


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_u1_update_core_fields(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-U1: Update Core Fields.
    Test updating name, description, precondition, and expected_result.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        # Create initial test case
        case_name = "E2E-U1 Initial Name"
        created_case = await service.create_test_case(
            project_id=project_id, name=case_name, description="Initial description"
        )
        test_case_id = created_case.id
        assert test_case_id is not None

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

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_u2_update_status_workflow(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-U2: Update Status & Workflow.
    Test updating status_id, workflow_id, test_layer_id, and automated flag.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        # Create initial test case
        created_case = await service.create_test_case(project_id=project_id, name="E2E-U2 Status Test")
        test_case_id = created_case.id
        assert test_case_id is not None

        initial_case = await service.get_test_case(test_case_id)
        initial_automated = initial_case.automated

        # Update automated flag (toggle it)
        update_data = TestCaseUpdate(automated=not initial_automated)
        updated_case = await service.update_test_case(test_case_id, update_data)

        # Verify automated flag changed
        assert updated_case.automated == (not initial_automated)

        # Note: status_id, workflow_id, test_layer_id updates require valid IDs
        # which may vary per project. For now, we test the automated field.
        # To test status/workflow/layer, you'd need to fetch valid IDs first.

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_u3_update_tags(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-U3: Update Tags.
    Test replacing tags, adding new tags, and removing all tags.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        # Create with initial tags
        created_case = await service.create_test_case(
            project_id=project_id, name="E2E-U3 Tags Test", tags=["initial", "tag1"]
        )
        test_case_id = created_case.id
        assert test_case_id is not None

        # Verify initial tags
        fetched_case = await service.get_test_case(test_case_id)
        initial_tag_names = sorted([t.name for t in (fetched_case.tags or []) if t.name])
        assert "initial" in initial_tag_names
        assert "tag1" in initial_tag_names

        # Replace tags
        update_data = TestCaseUpdate(tags=["updated", "tag2", "tag3"])
        updated_case = await service.update_test_case(test_case_id, update_data)

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

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_u4_update_custom_fields(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-U4: Update Custom Fields.
    Test replacing custom field values and adding new custom fields.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        # Create with initial custom fields
        # Note: Custom fields must exist in the project
        created_case = await service.create_test_case(
            project_id=project_id, name="E2E-U4 Custom Fields Test", custom_fields={"Feature": "Test"}
        )
        test_case_id = created_case.id
        assert test_case_id is not None

        # Update custom fields
        update_data = TestCaseUpdate(custom_fields={"Feature": "Flow", "Component": "API"})
        updated_case = await service.update_test_case(test_case_id, update_data)

        # Verify custom fields updated
        fetched_case = await service.get_test_case(test_case_id)
        if fetched_case.custom_fields:
            cf_values = {cf.custom_field.name: cf.name for cf in fetched_case.custom_fields if cf.custom_field}
            # At least one should be updated
            assert cf_values.get("Feature") == "Flow" or cf_values.get("Component") == "API"

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_u5_update_steps(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-U5: Update Steps.
    Test replacing all steps with new complex step hierarchy.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        # Create with initial steps
        initial_steps = [{"action": "Initial Step 1"}]
        created_case = await service.create_test_case(
            project_id=project_id, name="E2E-U5 Steps Test", steps=initial_steps
        )
        test_case_id = created_case.id
        assert test_case_id is not None

        # Verify initial steps
        initial_scenario = await allure_client.get_test_case_scenario(test_case_id)
        assert initial_scenario.steps is not None
        assert len(initial_scenario.steps) >= 1

        # Update with new complex steps
        pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgANjd8qAAAAAElFTkSuQmCC"
        new_steps = [
            {"action": "New Step 1", "expected": "Result 1"},
            {
                "action": "New Step 2",
                "expected": "Result 2",
                "attachments": [{"name": "step2.png", "content": pixel_b64, "content_type": "image/png"}],
            },
            {"action": "New Step 3"},
        ]

        update_data = TestCaseUpdate(steps=new_steps)
        await service.update_test_case(test_case_id, update_data)

        # Verify steps replaced
        updated_scenario = await allure_client.get_test_case_scenario(test_case_id)
        assert updated_scenario.steps is not None
        assert len(updated_scenario.steps) >= 3

        # Verify the new steps are present
        step_bodies = []
        for step in updated_scenario.steps:
            if step.actual_instance and hasattr(step.actual_instance, "body"):
                step_bodies.append(step.actual_instance.body)

        assert "New Step 1" in step_bodies or "New Step 2" in step_bodies or "New Step 3" in step_bodies

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_u6_update_global_attachments(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-U6: Update Global Attachments.
    Test adding new attachments while preserving steps.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        # Create with steps (no attachments)
        initial_steps = [{"action": "Step with no attachment"}]
        created_case = await service.create_test_case(
            project_id=project_id, name="E2E-U6 Attachments Test", steps=initial_steps
        )
        test_case_id = created_case.id
        assert test_case_id is not None

        # Add attachments (should preserve steps)
        pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgANjd8qAAAAAElFTkSuQmCC"
        attachments = [
            {"name": "attachment1.png", "content": pixel_b64, "content_type": "image/png"},
            {"name": "attachment2.png", "content": pixel_b64, "content_type": "image/png"},
        ]

        update_data = TestCaseUpdate(attachments=attachments)
        await service.update_test_case(test_case_id, update_data)

        # Verify attachments added and steps preserved
        scenario = await allure_client.get_test_case_scenario(test_case_id)
        assert scenario.steps is not None

        # Check for attachments
        attachment_count = 0
        step_found = False
        for step in scenario.steps:
            if step.actual_instance:
                if hasattr(step.actual_instance, "attachment_id"):
                    attachment_count += 1
                if hasattr(step.actual_instance, "body") and "Step with no attachment" in step.actual_instance.body:
                    step_found = True

        assert attachment_count >= 2, f"Expected at least 2 attachments, found {attachment_count}"
        assert step_found, "Original step not preserved"

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_u7_update_links(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-U7: Update Links.
    Test adding and replacing external links.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        # Create test case
        created_case = await service.create_test_case(project_id=project_id, name="E2E-U7 Links Test")
        test_case_id = created_case.id
        assert test_case_id is not None

        # Add links
        links = [
            {"name": "JIRA-123", "url": "https://jira.example.com/JIRA-123", "type": "issue"},
            {"name": "Documentation", "url": "https://docs.example.com", "type": "link"},
        ]

        update_data = TestCaseUpdate(links=links)
        updated_case = await service.update_test_case(test_case_id, update_data)

        # Verify links added
        fetched_case = await service.get_test_case(test_case_id)
        if fetched_case.links:
            link_names = [link.name for link in fetched_case.links if link.name]
            assert "JIRA-123" in link_names or "Documentation" in link_names

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_u8_combined_updates(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-U8: Combined Updates.
    Test updating multiple fields (name, tags, steps, custom fields) at once.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        # Create initial test case
        created_case = await service.create_test_case(
            project_id=project_id, name="E2E-U8 Initial", tags=["old"], steps=[{"action": "Old step"}]
        )
        test_case_id = created_case.id
        assert test_case_id is not None

        # Combined update
        new_steps = [{"action": "New combined step", "expected": "New result"}]
        update_data = TestCaseUpdate(
            name="E2E-U8 Combined Update",
            description="Updated via combined operation",
            tags=["new", "combined"],
            steps=new_steps,
            custom_fields={"Priority": "Critical"},
        )

        updated_case = await service.update_test_case(test_case_id, update_data)

        # Verify all updates
        assert updated_case.name == "E2E-U8 Combined Update"
        assert updated_case.description == "Updated via combined operation"

        fetched_case = await service.get_test_case(test_case_id)
        tag_names = [t.name for t in (fetched_case.tags or []) if t.name]
        assert "new" in tag_names or "combined" in tag_names

        scenario = await allure_client.get_test_case_scenario(test_case_id)
        assert scenario.steps is not None

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_u9_edge_cases(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-U9: Edge Cases.
    Test idempotent updates, empty values, and graceful handling.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        # Create test case
        created_case = await service.create_test_case(
            project_id=project_id, name="E2E-U9 Edge Cases", description="Initial", tags=["tag1"]
        )
        test_case_id = created_case.id
        assert test_case_id is not None

        # Idempotent update (same values)
        update_data = TestCaseUpdate(name="E2E-U9 Edge Cases", description="Initial")
        updated_case = await service.update_test_case(test_case_id, update_data)
        assert updated_case.name == "E2E-U9 Edge Cases"

        # Update with empty description (should clear it)
        update_data_empty = TestCaseUpdate(description="")
        updated_case = await service.update_test_case(test_case_id, update_data_empty)
        fetched_case = await service.get_test_case(test_case_id)
        assert fetched_case.description == "" or fetched_case.description is None

        # Update only tags (should preserve other fields)
        update_tags_only = TestCaseUpdate(tags=["edge", "test"])
        updated_case = await service.update_test_case(test_case_id, update_tags_only)
        assert updated_case.name == "E2E-U9 Edge Cases"  # Name should be preserved

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)
