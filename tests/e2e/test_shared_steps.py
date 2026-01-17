import pytest
import datetime
import uuid
import re
from src.tools.shared_steps import create_shared_step, list_shared_steps
from tests.e2e.helpers.cleanup import CleanupTracker

# Helper for unique naming
def get_unique_name(prefix="Shared Step"):
    return f"{prefix} {uuid.uuid4().hex[:8]}"

@pytest.mark.asyncio
async def test_shared_step_lifecycle_e2e(project_id, cleanup_tracker):
    """Test full lifecycle of a Shared Step: Create, and List."""
    
    unique_name = get_unique_name("E2E Shared Step")
    
    steps = [
        {
            "action": "Do something unique",
            "expected": "Something happens",
            # Attachments not easily testable via tool output unless we grep logs or trust return
            # but we can try adding one if we mock base64
            "attachments": []
        }
    ]

    # 1. Create
    output = await create_shared_step(
        name=unique_name,
        project_id=project_id,
        steps=steps
    )
    
    assert "Successfully created Shared Step" in output
    assert unique_name in output
    assert f"Project ID: {project_id}" in output
    
    # Extract ID from output for cleanup
    # Output format: "ID: 123"
    import re
    match = re.search(r"ID: (\d+)", output)
    assert match, "Could not extract ID from output"
    shared_step_id = int(match.group(1))
    
    cleanup_tracker.track_shared_step(shared_step_id)

    # 2. List
    list_output = await list_shared_steps(
        project_id=project_id,
        search=unique_name
    )
    
    assert list_output, "List output should not be empty"
    assert f"[ID: {shared_step_id}]" in list_output
    assert unique_name in list_output
    assert "steps)" in list_output # e.g. (1 steps) or (3 steps) 
    # steps_count might be 1 (action) or 3 (action + expected + att?)
    # "steps_count" usually counts only top level or all?
    # Our implementation logic:
    # Action -> 1
    # Expected -> child
    # Attachment -> child
    # So top level steps count is 1.
    
    
@pytest.mark.asyncio
async def test_create_shared_step_with_attachment_e2e(project_id, cleanup_tracker, pixel_b64):
    """Test creating a shared step with attachment."""
    unique_name = get_unique_name("E2E Attachment Shared Step")
    
    steps = [
        {
            "action": "Check image",
            "attachments": [
                {
                    "name": "pixel.png",
                    "content": pixel_b64
                }
            ]
        }
    ]
    
    output = await create_shared_step(
        name=unique_name,
        project_id=project_id,
        steps=steps
    )
    
    assert "Successfully created Shared Step" in output
    
    match = re.search(r"ID: (\d+)", output)
    if match:
        cleanup_tracker.track_shared_step(int(match.group(1)))
        
    # Validation via list not deep enough to check attachments, 
    # but successful return implies API accepted it.
