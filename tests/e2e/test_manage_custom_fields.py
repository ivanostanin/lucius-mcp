import uuid

import pytest

from src.client import AllureClient
from src.services.custom_field_value_service import CustomFieldValueService
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

    1. Discover target CF (single and optional multiselect).
    2. Dynamically create ephemeral values for target CFs (single & multi).
    3. Create Test Case with initial custom field values.
    4. Verify Value (creation).
    5. Update Custom Fields (change value).
    6. Verify Change.
    7. Clear Custom Field (set to empty).
    8. Verify Cleared.
    9. Update Multiple Custom Fields (Multiselect support).
    10. Verify Multi-field Update (reset single, set multi).
    11. Cleanup ephemeral values.
    """
    service = TestCaseService(client=allure_client)
    cf_value_service = CustomFieldValueService(client=allure_client)

    # 1. Discover available custom fields to use for testing
    project_cfs = await allure_client.get_custom_fields_with_values(project_id)
    target_cf = None
    multiselect_cf = None

    # Find a suitable CF: Not required (to avoid setup issues)
    for cf in project_cfs:
        if cf.custom_field:
            p_cf = cf.custom_field
            if not p_cf.required and p_cf.id > 0:
                if not target_cf and p_cf.single_select:
                    target_cf = p_cf.name

                # Check for multiselect candidate
                if not multiselect_cf:
                    # Check if single_select is explicitly False
                    is_single = p_cf.single_select
                    if is_single is False:
                        multiselect_cf = p_cf.name

                if target_cf and multiselect_cf:
                    break

    if not target_cf:
        pytest.skip("No suitable custom field found in project")

    # Dynamic Value Creation for Single Select
    unique_suffix = uuid.uuid4().hex[:8]
    val1_name = f"e2e-val1-{unique_suffix}"
    val2_name = f"e2e-val2-{unique_suffix}"

    ephemeral_values = {target_cf: [val1_name, val2_name]}

    target_value_1 = val1_name
    target_value_2 = val2_name
    multiselect_vals: list[str] = []

    try:
        print(f"Creating ephemeral values for CF '{target_cf}': {val1_name}, {val2_name}")
        await cf_value_service.create_custom_field_value(custom_field_name=target_cf, name=val1_name)
        await cf_value_service.create_custom_field_value(custom_field_name=target_cf, name=val2_name)

        # Dynamic Value Creation for Multi Select (if found)
        if multiselect_cf:
            ms_val1 = f"e2e-ms1-{unique_suffix}"
            ms_val2 = f"e2e-ms2-{unique_suffix}"
            print(f"Creating ephemeral values for Multiselect CF '{multiselect_cf}': {ms_val1}, {ms_val2}")
            await cf_value_service.create_custom_field_value(custom_field_name=multiselect_cf, name=ms_val1)
            await cf_value_service.create_custom_field_value(custom_field_name=multiselect_cf, name=ms_val2)
            ephemeral_values[multiselect_cf] = [ms_val1, ms_val2]
            multiselect_vals = [ms_val1, ms_val2]

        # 2. Create Test Case WITH Custom Fields
        case_name = "E2E Custom Fields Management"
        custom_fields_init = {target_cf: target_value_1}
        created_case = await service.create_test_case(name=case_name, custom_fields=custom_fields_init)

        test_case_id = created_case.id
        assert test_case_id is not None
        cleanup_tracker.track_test_case(test_case_id)

        print(f"Using Custom Field: {target_cf} with values {target_value_1}, {target_value_2}")

        # 2. Update Custom Fields using Standard Tool (Patched)
        custom_fields_update = {target_cf: target_value_1}
        print(f"DEBUG: Update Custom Fields using Tool: {custom_fields_update}")

        await update_test_case(
            test_case_id=test_case_id, custom_fields=custom_fields_update, project_id=project_id, confirm=True
        )

        # 3. Verify Value using Service
        cf_values = await service.get_test_case_custom_fields_values(test_case_id)
        if cf_values.get(target_cf) != target_value_1:
            pytest.fail(f"Custom field value mismatch. Expected {target_value_1}, got {cf_values.get(target_cf)}")

        # 4. Change Value
        await update_test_case(
            test_case_id=test_case_id, custom_fields={target_cf: target_value_2}, project_id=project_id, confirm=True
        )

        # 5. Verify Change using Service
        cf_values = await service.get_test_case_custom_fields_values(test_case_id)
        if cf_values.get(target_cf) != target_value_2:
            pytest.fail(
                f"Custom field value change mismatch. Expected {target_value_2}, got {cf_values.get(target_cf)}"
            )

        # 6. Clear Value
        await update_test_case(
            test_case_id=test_case_id, custom_fields={target_cf: ""}, project_id=project_id, confirm=True
        )

        # 7. Verify Cleared using Service
        cf_values = await service.get_test_case_custom_fields_values(test_case_id)
        val = cf_values.get(target_cf)
        if not (val is None or val == [] or val == ""):
            pytest.fail(f"Custom field value should be cleared. Got: {val}")

        # 8. Update Multiple Custom Fields (Multiselect)
        if multiselect_cf:
            print(f"Testing Multiselect CF: {multiselect_cf} with values {multiselect_vals}")
            # Reset target_cf to val1 AND set multiselect entries
            update_payload = {target_cf: target_value_1, multiselect_cf: multiselect_vals}

            await update_test_case(
                test_case_id=test_case_id, custom_fields=update_payload, project_id=project_id, confirm=True
            )

            # 9. Verify Multi-field Update
            cf_values = await service.get_test_case_custom_fields_values(test_case_id)

            # Check single select reset
            if cf_values.get(target_cf) != target_value_1:
                pytest.fail(
                    f"Failed to reset single select CF. Expected {target_value_1}, got {cf_values.get(target_cf)}"
                )

            # Check multiselect
            actual_ms = cf_values.get(multiselect_cf)
            if not isinstance(actual_ms, list):
                actual_ms = [actual_ms] if actual_ms else []

            # Sort for comparison
            if sorted(actual_ms) != sorted(multiselect_vals):
                pytest.fail(
                    f"Multiselect mismatch. Expected sorted {sorted(multiselect_vals)}, got sorted {sorted(actual_ms)}"
                )
        else:
            print("Skipping Multiselect test (no suitable CF found)")

    finally:
        # Cleanup Custom Field Values
        print("Cleaning up ephemeral custom field values...")
        for cf_name, created_names in ephemeral_values.items():
            try:
                for created_name in created_names:
                    await cf_value_service.delete_custom_field_value(
                        custom_field_name=cf_name,
                        cfv_name=created_name,
                        force=True,
                    )
            except Exception as e:
                print(f"Error during cleanup of CF values for '{cf_name}': {e}")
