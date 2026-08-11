from unittest.mock import Mock

import src.tools as tools
from tests.support.tool_patching import patch


def test_tool_module_patch_preserves_package_export() -> None:
    exported_tool = tools.create_test_case

    with patch("src.tools.create_test_case.TestCaseService") as service:
        assert isinstance(service, Mock)
        assert tools.create_test_case is exported_tool

    assert tools.create_test_case is exported_tool
