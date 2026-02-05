import pytest

from src.client import AllureClient
from src.services.test_case_service import TestCaseService
from src.tools.update_test_case import update_test_case
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.mark.asyncio
async def test_manage_custom_fields_lifecycle(  # noqa: C901
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
    8. Update Multiple Custom Fields
    9. Verify Multi-field Update
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
    print(f"DEBUG: Created Case Automated Status: {created_case.automated}")

    # DEBUG: See what the server says about current custom fields
    existing_dtos = await allure_client.get_test_case_custom_fields(test_case_id, project_id)
    print(f"DEBUG: Created Test Case: {created_case.id}")
    print("DEBUG: Existing Custom Fields on Test Case:")
    for d in existing_dtos:
        print(f"CF: {d.custom_field.name} (ID: {d.custom_field.id})")
        print(f"  Nested CF ID: {d.custom_field.custom_field.id if d.custom_field.custom_field else 'None'}")
        print(f"  Values: {[v.name for v in d.values or []]}")
        print(f"  Raw DTO: {d.model_dump()}")

    # 2. Update Custom Fields using Standard Tool (Patched)
    custom_fields_update = {target_cf: target_value_1}
    print(f"DEBUG: Update Custom Fields using Tool: {custom_fields_update}")

    await update_test_case(test_case_id=test_case_id, custom_fields=custom_fields_update, project_id=project_id)

    # 3. Verify Value using Service (since tool returns formatted string)
    cf_values = await service.get_test_case_custom_fields_values(test_case_id)
    assert cf_values.get(target_cf) == target_value_1

    # 4. Change Value
    await update_test_case(test_case_id=test_case_id, custom_fields={target_cf: target_value_2}, project_id=project_id)

    # 5. Verify Change using Service
    cf_values = await service.get_test_case_custom_fields_values(test_case_id)
    assert cf_values.get(target_cf) == target_value_2

    # 6. Clear Value
    await update_test_case(test_case_id=test_case_id, custom_fields={target_cf: ""}, project_id=project_id)

    # 7. Verify Cleared using Service
    cf_values = await service.get_test_case_custom_fields_values(test_case_id)
    val = cf_values.get(target_cf)
    # If key is missing or is empty list/string, it's considered cleared
    assert val is None or val == [] or val == ""
    # 8. Update multiple custom fields with proper assertions
    optional_fields = []
    for cf in project_cfs:
        if not cf.custom_field or not cf.custom_field.custom_field:
            continue
        project_cf = cf.custom_field
        global_cf = project_cf.custom_field
        if project_cf.required or not global_cf.name:
            continue
        values = [v.name for v in (cf.values or []) if v.name]
        if not values:
            continue
        single_select = getattr(global_cf, "single_select", True)
        if single_select is None:
            single_select = True
        optional_fields.append({"name": global_cf.name, "values": values, "single_select": single_select})

    update_payload: dict[str, str | list[str]] = {target_cf: target_value_2}
    expected_values: dict[str, str | list[str]] = {target_cf: target_value_2}

    for cf in optional_fields:
        if cf["name"] in update_payload:
            continue
        if cf["single_select"] is False and len(cf["values"]) >= 2:
            update_payload[cf["name"]] = [cf["values"][0], cf["values"][1]]
            expected_values[cf["name"]] = [cf["values"][0], cf["values"][1]]
            break

    for cf in optional_fields:
        if cf["name"] in update_payload:
            continue
        update_payload[cf["name"]] = cf["values"][0]
        expected_values[cf["name"]] = cf["values"][0]
        break

    if len(update_payload) < 2:
        pytest.skip("No additional optional custom fields with values available for multi-field update")

    await update_test_case(test_case_id=test_case_id, custom_fields=update_payload, project_id=project_id)

    # 9. Verify multi-field update
    cf_values = await service.get_test_case_custom_fields_values(test_case_id)
    for field_name, expected in expected_values.items():
        actual = cf_values.get(field_name)
        if isinstance(actual, list) and isinstance(expected, list):
            assert sorted(actual) == sorted(expected)
        else:
            assert actual == expected
