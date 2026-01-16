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
            pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgDNjd8qAAAAAElFTkSuQmCC"
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
