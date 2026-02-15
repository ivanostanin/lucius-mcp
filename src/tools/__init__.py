from collections.abc import Awaitable, Callable

from src.tools.create_custom_field_value import create_custom_field_value
from src.tools.create_test_case import create_test_case
from src.tools.defects import (
    create_defect,
    create_defect_matcher,
    delete_defect,
    delete_defect_matcher,
    get_defect,
    link_defect_to_test_case,
    list_defect_matchers,
    list_defect_test_cases,
    list_defects,
    update_defect,
    update_defect_matcher,
)
from src.tools.delete_custom_field_value import delete_custom_field_value
from src.tools.delete_test_case import delete_test_case
from src.tools.get_custom_fields import get_custom_fields
from src.tools.get_test_case_custom_fields import get_test_case_custom_fields
from src.tools.launches import close_launch, create_launch, delete_launch, get_launch, list_launches, reopen_launch
from src.tools.link_shared_step import link_shared_step
from src.tools.list_custom_field_values import list_custom_field_values
from src.tools.list_integrations import list_integrations
from src.tools.plans import create_test_plan, list_test_plans, manage_test_plan_content, update_test_plan
from src.tools.search import get_test_case_details, list_test_cases, search_test_cases
from src.tools.shared_steps import create_shared_step, delete_shared_step, list_shared_steps, update_shared_step
from src.tools.test_layers import (
    assign_test_cases_to_suite,
    create_test_layer,
    create_test_layer_schema,
    create_test_suite,
    delete_test_layer,
    delete_test_layer_schema,
    list_test_layer_schemas,
    list_test_layers,
    list_test_suites,
    update_test_layer,
    update_test_layer_schema,
)
from src.tools.unlink_shared_step import unlink_shared_step
from src.tools.update_custom_field_value import update_custom_field_value
from src.tools.update_test_case import update_test_case

__all__ = [
    "assign_test_cases_to_suite",
    "close_launch",
    "create_custom_field_value",
    "create_defect",
    "create_defect_matcher",
    "create_launch",
    "create_shared_step",
    "create_test_case",
    "create_test_layer",
    "create_test_layer_schema",
    "create_test_plan",
    "create_test_suite",
    "delete_custom_field_value",
    "delete_defect",
    "delete_defect_matcher",
    "delete_launch",
    "delete_shared_step",
    "delete_test_case",
    "delete_test_layer",
    "delete_test_layer_schema",
    "get_custom_fields",
    "get_defect",
    "get_launch",
    "get_test_case_custom_fields",
    "get_test_case_details",
    "link_defect_to_test_case",
    "link_shared_step",
    "list_custom_field_values",
    "list_defect_matchers",
    "list_defect_test_cases",
    "list_defects",
    "list_integrations",
    "list_launches",
    "list_shared_steps",
    "list_test_cases",
    "list_test_layer_schemas",
    "list_test_layers",
    "list_test_plans",
    "list_test_suites",
    "manage_test_plan_content",
    "reopen_launch",
    "search_test_cases",
    "unlink_shared_step",
    "update_custom_field_value",
    "update_defect",
    "update_defect_matcher",
    "update_shared_step",
    "update_test_case",
    "update_test_layer",
    "update_test_layer_schema",
    "update_test_plan",
]

ToolFn = Callable[..., Awaitable[object]]

all_tools: list[ToolFn] = [
    create_test_case,
    get_test_case_details,
    update_test_case,
    delete_test_case,
    list_test_cases,
    get_custom_fields,
    list_custom_field_values,
    create_custom_field_value,
    update_custom_field_value,
    delete_custom_field_value,
    get_test_case_custom_fields,
    search_test_cases,
    create_launch,
    get_launch,
    list_launches,
    delete_launch,
    close_launch,
    reopen_launch,
    # Integration Tools
    list_integrations,
    create_shared_step,
    list_shared_steps,
    update_shared_step,
    delete_shared_step,
    link_shared_step,
    unlink_shared_step,
    # Test Layer Tools
    list_test_layers,
    create_test_layer,
    update_test_layer,
    delete_test_layer,
    list_test_layer_schemas,
    create_test_layer_schema,
    update_test_layer_schema,
    delete_test_layer_schema,
    # Test Hierarchy Tools
    create_test_suite,
    list_test_suites,
    assign_test_cases_to_suite,
    # Test Plan Tools
    create_test_plan,
    update_test_plan,
    manage_test_plan_content,
    list_test_plans,
    # Defect Management Tools
    create_defect,
    get_defect,
    link_defect_to_test_case,
    list_defect_test_cases,
    update_defect,
    delete_defect,
    list_defects,
    create_defect_matcher,
    update_defect_matcher,
    delete_defect_matcher,
    list_defect_matchers,
]
