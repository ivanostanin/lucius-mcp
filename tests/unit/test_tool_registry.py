from src.tools import __all__ as tool_exports
from src.tools import all_tools


def test_delete_test_plan_is_exported_and_registered() -> None:
    assert "delete_test_plan" in tool_exports
    assert any(getattr(tool, "__name__", "") == "delete_test_plan" for tool in all_tools)
