import importlib.util
from pathlib import Path

import pytest

SCRIPT_PATH = Path("deployment/scripts/validate_mcpb.py")


def _load_script_module():
    spec = importlib.util.spec_from_file_location("validate_mcpb", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _BrokenFastMCP:
    async def list_tools(self, *, run_middleware: bool):
        raise RuntimeError("tool registry unavailable")


def test_validate_tools_fails_when_fastmcp_tools_cannot_be_inspected(capsys: pytest.CaptureFixture[str]) -> None:
    module = _load_script_module()

    with pytest.raises(SystemExit, match="1"):
        module.validate_tools({"tools": []}, _BrokenFastMCP())

    assert "❌ Could not inspect FastMCP tools: tool registry unavailable" in capsys.readouterr().out


def test_validate_tools_fails_without_a_fastmcp_instance(capsys: pytest.CaptureFixture[str]) -> None:
    module = _load_script_module()

    with pytest.raises(SystemExit, match="1"):
        module.validate_tools({"tools": []}, None)

    assert "❌ Could not inspect FastMCP tools: no FastMCP instance found" in capsys.readouterr().out
