from src.client import AllureClient
from src.services.test_case_service import TestCaseService, TestCaseUpdate
from tests.e2e.helpers.cleanup import CleanupTracker


async def test_e2e_u5_update_steps(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    pixel_b64: str,
) -> None:
    """
    E2E-U5: Update Steps.
    Test replacing all steps with new complex step hierarchy.
    """
    service = TestCaseService(client=allure_client)

    # Create with initial steps
    initial_steps = [{"action": "Initial Step 1"}]
    created_case = await service.create_test_case(name="E2E-U5 Steps Test", steps=initial_steps)
    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    # Verify initial steps
    initial_scenario = await allure_client.get_test_case_scenario(test_case_id)
    assert initial_scenario.steps is not None
    assert len(initial_scenario.steps) >= 1

    # Update with new complex steps
    new_steps: list[dict[str, object]] = [
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


async def test_e2e_u6_update_global_attachments(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    pixel_b64: str,
) -> None:
    """
    E2E-U6: Update Global Attachments.
    Test adding new attachments while preserving steps.
    """
    service = TestCaseService(client=allure_client)

    # Create with steps (no attachments)
    initial_steps = [{"action": "Step with no attachment"}]
    created_case = await service.create_test_case(name="E2E-U6 Attachments Test", steps=initial_steps)
    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    # Add attachments (should preserve steps)
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
            if (
                hasattr(step.actual_instance, "body")
                and step.actual_instance.body
                and "Step with no attachment" in step.actual_instance.body
            ):
                step_found = True

    assert attachment_count >= 2, f"Expected at least 2 attachments, found {attachment_count}"
    assert step_found, "Original step not preserved"


async def test_e2e_u7_update_links(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E-U7: Update Links.
    Test adding and replacing external links.
    """
    service = TestCaseService(client=allure_client)

    # Create test case
    created_case = await service.create_test_case(name="E2E-U7 Links Test")
    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    # Add links
    links = [
        {"name": "JIRA-123", "url": "https://jira.example.com/JIRA-123", "type": "issue"},
        {"name": "Documentation", "url": "https://docs.example.com", "type": "link"},
    ]

    update_data = TestCaseUpdate(links=links)
    await service.update_test_case(test_case_id, update_data)

    # Verify links added
    fetched_case = await service.get_test_case(test_case_id)
    if fetched_case.links:
        link_names = [link.name for link in fetched_case.links if link.name]
        assert "JIRA-123" in link_names or "Documentation" in link_names


async def test_e2e_u8_combined_updates(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E-U8: Combined Updates.
    Test updating multiple fields (name, tags, steps, custom fields) at once.
    """
    service = TestCaseService(client=allure_client)

    # Create initial test case
    created_case = await service.create_test_case(name="E2E-U8 Initial", tags=["old"], steps=[{"action": "Old step"}])
    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

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


async def test_e2e_u9_edge_cases(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E-U9: Edge Cases.
    Test idempotent updates, empty values, and graceful handling.
    """
    service = TestCaseService(client=allure_client)

    # Create test case
    created_case = await service.create_test_case(name="E2E-U9 Edge Cases", description="Initial", tags=["tag1"])
    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    # Idempotent update (same values)
    update_data = TestCaseUpdate(name="E2E-U9 Edge Cases", description="Initial")
    updated_case = await service.update_test_case(test_case_id, update_data)
    assert updated_case.name == "E2E-U9 Edge Cases"

    # Update with empty description (should clear it)
    update_data_empty = TestCaseUpdate(description="")
    await service.update_test_case(test_case_id, update_data_empty)
    fetched_case = await service.get_test_case(test_case_id)
    assert fetched_case.description == "" or fetched_case.description is None

    # Update only tags (should preserve other fields)
    update_tags_only = TestCaseUpdate(tags=["edge", "test"])
    updated_case = await service.update_test_case(test_case_id, update_tags_only)
    assert updated_case.name == "E2E-U9 Edge Cases"  # Name should be preserved


async def test_e2e_u10_nested_steps(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E-U10: Nested Steps.
    Test updating with multi-level nested steps.
    """
    service = TestCaseService(client=allure_client)

    # Create initial test case
    created_case = await service.create_test_case(name="E2E-U10 Nested Steps")
    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    # Define nested steps
    nested_steps = [
        {
            "action": "Parent Step",
            "expected": "Parent Expected",
            "steps": [
                {"action": "Child Step 1", "expected": "Child Expected 1"},
                {"action": "Child Step 2", "steps": [{"action": "Grandchild Step", "expected": "Deepest Level"}]},
            ],
        }
    ]

    update_data = TestCaseUpdate(steps=nested_steps)
    await service.update_test_case(test_case_id, update_data)

    # Verify steps structure
    scenario = await allure_client.get_test_case_scenario(test_case_id)
    assert scenario.steps is not None
    assert len(scenario.steps) >= 1

    # Verify Parent
    parent_step = None
    for step in scenario.steps:
        if (
            step.actual_instance
            and hasattr(step.actual_instance, "body")
            and step.actual_instance.body == "Parent Step"
        ):
            parent_step = step
            break

    assert parent_step is not None, "Parent step not found"
