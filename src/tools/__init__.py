from collections.abc import Awaitable, Callable

from src.tools.create_test_case import create_test_case
from src.tools.delete_test_case import delete_test_case
from src.tools.get_custom_fields import get_custom_fields
from src.tools.link_shared_step import link_shared_step
from src.tools.search import get_test_case_details, list_test_cases, search_test_cases
from src.tools.shared_steps import create_shared_step, delete_shared_step, list_shared_steps, update_shared_step
from src.tools.unlink_shared_step import unlink_shared_step
from src.tools.update_test_case import update_test_case

__all__ = [
    "create_shared_step",
    "create_test_case",
    "delete_shared_step",
    "delete_test_case",
    "get_custom_fields",
    "get_test_case_details",
    "link_shared_step",
    "list_shared_steps",
    "list_test_cases",
    "search_test_cases",
    "unlink_shared_step",
    "update_shared_step",
    "update_test_case",
]

ToolFn = Callable[..., Awaitable[object]]

all_tools: list[ToolFn] = [
    create_test_case,
    get_test_case_details,
    update_test_case,
    delete_test_case,
    list_test_cases,
    get_custom_fields,
    search_test_cases,
    create_shared_step,
    list_shared_steps,
    update_shared_step,
    delete_shared_step,
    link_shared_step,
    unlink_shared_step,
]
