"""Expose existing CLI tests to the unit/integration coverage slice.

The project keeps CLI-focused tests under ``tests/cli``. The coverage gate used
by the unit/integration command still includes ``src/cli`` modules, so this
proxy lets that existing coverage participate without duplicating test bodies.
"""

from __future__ import annotations

import importlib

_CLI_TEST_MODULES = [
    "tests.cli.test_cli_auth",
    "tests.cli.test_cli_basics",
    "tests.cli.test_cli_coverage_helpers",
    "tests.cli.test_completion_installer",
    "tests.cli.test_e2e_mocked",
    "tests.cli.test_route_matrix",
]


for _module_name in _CLI_TEST_MODULES:
    _module = importlib.import_module(_module_name)
    _prefix = _module_name.rsplit(".", maxsplit=1)[-1]
    for _name, _obj in vars(_module).items():
        if _name.startswith("test_"):
            globals()[f"{_prefix}__{_name}"] = _obj
        elif _name.startswith("Test"):
            globals()[_name] = _obj
