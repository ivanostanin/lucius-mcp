import pytest

from src.client import AllureClient
from src.services.test_case_service import TestCaseService
from src.tools.get_test_case_custom_fields import get_test_case_custom_fields
from src.tools.update_test_case import update_test_case
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.mark.asyncio
async def test_manage_custom_fields_lifecycle(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E Test for Managing Custom Fields.
    1. Create Test Case
    2. Update Custom Fields (add value)
    3. Verify Value
    4. Update Custom Fields (change value)
    5. Verify Change
    6. Clear Custom Field
    7. Verify Cleared
    """
    service = TestCaseService(client=allure_client)

    # 1. Discover available custom fields to use for testing
    project_cfs = await allure_client.get_custom_fields_with_values(project_id)
    target_cf = None
    target_id = -999
    target_value_1 = None
    target_value_2 = None
    # Find a suitable CF: Not required (to avoid setup issues), has at least 2 values
    for cf in project_cfs:
        if cf.custom_field:
            p_cf = cf.custom_field
            g_cf = p_cf.custom_field
            print(f"DISCOVERED CF: {p_cf.name}")
            print(f"  Project CF ID: {p_cf.id}")
            print(f"  Global CF ID: {g_cf.id if g_cf else 'None'}")
            print(f"  Values Count: {len(cf.values or [])}")

            if not p_cf.required and cf.values and len(cf.values) >= 2:
                if not target_cf or (p_cf.id > 0 and target_id < 0):
                    target_cf = p_cf.name
                    target_id = p_cf.id
                    target_value_1 = cf.values[0].name
                    target_value_2 = cf.values[1].name
                    print(f"  => SELECTED as target: {target_cf} (ID: {target_id})")

    if not target_cf:
        pytest.skip("No suitable custom field found in project (need optional field with >= 2 values)")

    # 2. Create Test Case WITH Custom Fields
    case_name = "E2E Custom Fields Management"
    custom_fields_init = {target_cf: target_value_1}
    created_case = await service.create_test_case(name=case_name, custom_fields=custom_fields_init)

    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    print(f"Using Custom Field: {target_cf} with values {target_value_1}, {target_value_2}")

    # DEBUG: See what the server says about current custom fields
    existing_dtos = await allure_client.get_test_case_custom_fields(test_case_id, project_id)
    print("DEBUG: Existing Custom Fields on Test Case:")
    for d in existing_dtos:
        print(f"CF: {d.custom_field.name} (ID: {d.custom_field.id})")
        print(f"  Nested CF ID: {d.custom_field.custom_field.id if d.custom_field.custom_field else 'None'}")
        print(f"  Values: {[v.name for v in d.values or []]}")
        print(f"  Raw DTO: {d.model_dump()}")

    # 2. Update Custom Fields using Standard Tool (Patched)
    custom_fields_update = {target_cf: target_value_1}

    await update_test_case(test_case_id=test_case_id, custom_fields=custom_fields_update, project_id=project_id)

    # 3. Verify Value using Tool
    cf_values = await get_test_case_custom_fields(test_case_id=test_case_id, project_id=project_id)
    assert cf_values.get(target_cf) == target_value_1

    # 4. Change Value
    await update_test_case(test_case_id=test_case_id, custom_fields={target_cf: target_value_2}, project_id=project_id)

    # 5. Verify Change
    cf_values = await get_test_case_custom_fields(test_case_id=test_case_id, project_id=project_id)
    assert cf_values.get(target_cf) == target_value_2

    # 6. Clear Value
    await update_test_case(test_case_id=test_case_id, custom_fields={target_cf: "[]"}, project_id=project_id)

    # 7. Verify Cleared
    cf_values = await get_test_case_custom_fields(test_case_id=test_case_id, project_id=project_id)
    val = cf_values.get(target_cf)
    assert val == []
