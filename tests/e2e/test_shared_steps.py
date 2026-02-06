import re
import uuid

import pytest

from src.tools.shared_steps import create_shared_step, delete_shared_step, list_shared_steps, update_shared_step


# Helper for unique naming
def get_unique_name(prefix="Shared Step"):
    return f"{prefix} {uuid.uuid4().hex[:8]}"


async def test_shared_step_lifecycle_e2e(
    project_id,
    cleanup_tracker,
):
    """Test full lifecycle of a Shared Step: Create, and List."""

    unique_name = get_unique_name("E2E Shared Step")

    steps = [
        {
            "action": "Do something unique",
            "expected": "Something happens",
            # Attachments not easily testable via tool output unless we grep logs or trust return
            # but we can try adding one if we mock base64
            "attachments": [],
        }
    ]

    # 1. Create
    output = await create_shared_step(
        name=unique_name,
        project_id=project_id,
        steps=steps,
    )

    assert "Successfully created Shared Step" in output
    assert unique_name in output
    assert f"Project ID: {project_id}" in output

    # Extract ID from output for cleanup
    # Output format: "ID: 123"

    match = re.search(r"ID: (\d+)", output)
    assert match, "Could not extract ID from output"
    shared_step_id = int(match.group(1))

    cleanup_tracker.track_shared_step(shared_step_id)

    # 2. List
    list_output = await list_shared_steps(project_id=project_id, search=unique_name)

    assert list_output, "List output should not be empty"
    assert f"[ID: {shared_step_id}]" in list_output
    assert unique_name in list_output
    assert "steps)" in list_output  # e.g. (1 steps) or (3 steps)
    # steps_count might be 1 (action) or 3 (action + expected + att?)
    # "steps_count" usually counts only top level or all?
    # Our implementation logic:
    # Action -> 1
    # Expected -> child
    # Attachment -> child
    # So top level steps count is 1.


async def test_create_shared_step_with_attachment_e2e(
    project_id,
    cleanup_tracker,
    pixel_b64,
):
    """Test creating a shared step with attachment."""
    unique_name = get_unique_name("E2E Attachment Shared Step")

    steps = [{"action": "Check image", "attachments": [{"name": "pixel.png", "content": pixel_b64}]}]

    output = await create_shared_step(
        name=unique_name,
        project_id=project_id,
        steps=steps,
    )

    assert "Successfully created Shared Step" in output

    match = re.search(r"ID: (\d+)", output)
    if match:
        cleanup_tracker.track_shared_step(int(match.group(1)))

    # Validation via list not deep enough to check attachments,
    # but successful return implies API accepted it.


# ==========================================
# E2E Tests for Update and Delete (Story 2.2)
# ==========================================


@pytest.mark.priority("P0")
async def test_update_shared_step_success_e2e(
    project_id,
    cleanup_tracker,
):
    """
    Test updating a shared step name.
    ID: 2.2-E2E-001
    """

    # 1. Create a shared step
    original_name = get_unique_name("Original Name")
    output = await create_shared_step(name=original_name, project_id=project_id)

    match = re.search(r"ID: (\d+)", output)
    assert match
    shared_step_id = int(match.group(1))
    cleanup_tracker.track_shared_step(shared_step_id)

    # 2. Update the name
    new_name = get_unique_name("Updated Name")
    update_output = await update_shared_step(step_id=shared_step_id, name=new_name, confirm=True)

    assert "Updated Shared Step" in update_output
    assert new_name in update_output
    assert "Changes applied" in update_output

    # 3. Verify update by listing
    list_output = await list_shared_steps(project_id=project_id, search=new_name)
    assert f"[ID: {shared_step_id}]" in list_output
    assert new_name in list_output


@pytest.mark.priority("P2")
async def test_update_shared_step_idempotent_e2e(
    project_id,
    cleanup_tracker,
):
    """
    Test idempotency - updating with same name should be no-op.
    ID: 2.2-E2E-004
    """

    # 1. Create
    name = get_unique_name("Idempotent Test")
    output = await create_shared_step(name=name, project_id=project_id)

    match = re.search(r"ID: (\d+)", output)
    assert match
    shared_step_id = int(match.group(1))
    cleanup_tracker.track_shared_step(shared_step_id)

    # 2. Update with same name (should be no-op)
    update_output = await update_shared_step(step_id=shared_step_id, name=name, confirm=True)

    assert "No changes needed" in update_output
    assert "already matches" in update_output


@pytest.mark.priority("P0")
async def test_delete_shared_step_success_e2e(
    project_id,
    cleanup_tracker,
):
    """
    Test deleting a shared step.
    ID: 2.2-E2E-002
    """

    # 1. Create
    name = get_unique_name("To Be Deleted")
    output = await create_shared_step(name=name, project_id=project_id)

    match = re.search(r"ID: (\d+)", output)
    assert match
    shared_step_id = int(match.group(1))

    # Track for cleanup (safe largely because delete is idempotent/soft)
    cleanup_tracker.track_shared_step(shared_step_id)

    # 2. Delete with confirmation
    delete_output = await delete_shared_step(step_id=shared_step_id, confirm=True)

    assert "Archived Shared Step" in delete_output
    assert str(shared_step_id) in delete_output


@pytest.mark.priority("P1")
async def test_delete_shared_step_without_confirmation_e2e(
    project_id,
    cleanup_tracker,
):
    """
    Test delete fails without confirmation.
    ID: 2.2-E2E-003
    """

    # 1. Create
    name = get_unique_name("No Delete")
    output = await create_shared_step(name=name, project_id=project_id)

    match = re.search(r"ID: (\d+)", output)
    assert match
    shared_step_id = int(match.group(1))
    cleanup_tracker.track_shared_step(shared_step_id)

    # 2. Try delete without confirm
    delete_output = await delete_shared_step(step_id=shared_step_id, confirm=False)

    assert "⚠️ Deletion requires confirmation" in delete_output
    assert "confirm=True" in delete_output
