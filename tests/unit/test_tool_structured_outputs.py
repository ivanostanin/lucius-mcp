from unittest.mock import AsyncMock

import pytest
from fastmcp import Client, FastMCP
from fastmcp.tools import Tool
from fastmcp.tools.base import ToolResult
from mcp.types import TextContent
from pydantic import ValidationError

import src.tools.search as search_tools
from src.client import PageTestCaseDto, TestCaseDto
from src.client.generated.models.test_tag_dto import TestTagDto
from src.tools.output_contract import render_output
from src.tools.output_schemas import output_model_for, output_schema_for
from src.utils.telemetry import _apply_mcp_output_contract, wrap_tool_with_telemetry


class _ClientContext:
    def __init__(self, client: object) -> None:
        self._client = client

    async def __aenter__(self) -> object:
        return self._client

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


class _SearchClient:
    def __init__(self) -> None:
        self.list_test_cases = AsyncMock(
            return_value=PageTestCaseDto(
                content=[
                    TestCaseDto(
                        id=1,
                        name="Login Flow",
                        tags=[TestTagDto.model_construct(name="smoke")],
                    )
                ],
                total_elements=1,
                number=0,
                size=20,
                total_pages=1,
            )
        )
        self.get_test_case = AsyncMock(
            return_value=TestCaseDto(id=1, name="Login Flow", tags=[TestTagDto.model_construct(name="smoke")])
        )
        self.get_test_case_scenario = AsyncMock(return_value=None)
        self.list_test_case_attachments = AsyncMock(return_value=None)

    def get_project(self) -> int:
        return 123

    def get_base_url(self) -> str:
        return "https://example.com"


@pytest.fixture
def search_client(monkeypatch: pytest.MonkeyPatch) -> _SearchClient:
    client = _SearchClient()
    monkeypatch.setattr("src.tools.search.AllureClient.from_env", lambda project=None: _ClientContext(client))
    return client


@pytest.mark.asyncio
async def test_search_test_cases_defaults_to_structured_payload(search_client: _SearchClient) -> None:
    result = await search_tools.search_test_cases(query="login")

    assert result.content == []
    assert result.structured_content == {
        "total": 1,
        "page": 0,
        "size": 20,
        "total_pages": 1,
        "items": [
            {
                "id": 1,
                "name": "Login Flow",
                "status": "unknown",
                "tags": ["smoke"],
                "url": "https://example.com/project/123/test-cases/1",
            }
        ],
        "query": "login",
    }


@pytest.mark.asyncio
async def test_search_test_cases_preserves_explicit_text_formats(search_client: _SearchClient) -> None:
    plain = await search_tools.search_test_cases(query="login", output_format="plain")
    structured_json = await search_tools.search_test_cases(query="login", output_format="json")

    assert isinstance(plain, str)
    assert "Found 1 test cases matching 'login':" in plain
    assert "Test Case URL: https://example.com/project/123/test-cases/1" in plain
    assert structured_json.content == []
    assert structured_json.structured_content["items"][0]["tags"] == ["smoke"]
    assert structured_json.structured_content["items"][0]["url"] == "https://example.com/project/123/test-cases/1"


@pytest.mark.asyncio
async def test_fastmcp_emits_structured_content_for_default_search_output(search_client: _SearchClient) -> None:
    schema = output_schema_for("search_test_cases")
    tool = Tool.from_function(
        wrap_tool_with_telemetry(search_tools.search_test_cases, output_model=output_model_for("search_test_cases")),
        output_schema=schema,
    )

    result = await tool.run({"query": "login"})

    assert result.structured_content == {
        "total": 1,
        "page": 0,
        "size": 20,
        "total_pages": 1,
        "items": [
            {
                "id": 1,
                "name": "Login Flow",
                "status": "unknown",
                "tags": ["smoke"],
                "url": "https://example.com/project/123/test-cases/1",
            }
        ],
        "query": "login",
    }
    assert result.content == []
    assert "x-fastmcp-wrap-result" not in schema


@pytest.mark.asyncio
async def test_fastmcp_keeps_text_content_when_plain_output_is_requested(search_client: _SearchClient) -> None:
    tool = Tool.from_function(
        wrap_tool_with_telemetry(search_tools.search_test_cases, output_model=output_model_for("search_test_cases")),
        output_schema=output_schema_for("search_test_cases"),
    )

    result = await tool.run({"query": "login", "output_format": "plain"})

    expected = await search_tools.search_test_cases(query="login", output_format="json")
    assert result.structured_content == expected.structured_content
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    assert "Found 1 test cases matching 'login':" in result.content[0].text
    assert "Test Case URL: https://example.com/project/123/test-cases/1" in result.content[0].text


@pytest.mark.asyncio
async def test_fastmcp_emits_only_structured_content_when_json_output_is_requested(
    search_client: _SearchClient,
) -> None:
    tool = Tool.from_function(
        wrap_tool_with_telemetry(search_tools.search_test_cases, output_model=output_model_for("search_test_cases")),
        output_schema=output_schema_for("search_test_cases"),
    )

    result = await tool.run({"query": "login", "output_format": "json"})

    assert result.content == []
    assert result.structured_content is not None
    assert result.structured_content["items"][0]["tags"] == ["smoke"]
    assert result.structured_content["items"][0]["url"] == "https://example.com/project/123/test-cases/1"


def test_mcp_contract_preserves_explicit_null_fields() -> None:
    result = ToolResult(content=[], structured_content={"id": 1, "name": "Defect", "description": None, "url": "x"})

    validated = _apply_mcp_output_contract(result, output_model_for("create_defect"))

    assert isinstance(validated, ToolResult)
    assert validated.structured_content == {"id": 1, "name": "Defect", "description": None, "url": "x"}


@pytest.mark.asyncio
@pytest.mark.parametrize("output_format", [None, "json", "plain"])
async def test_mcp_client_accepts_test_case_details_in_all_formats(
    search_client: _SearchClient, output_format: str | None
) -> None:
    server = FastMCP("output-contract-regression")
    server.tool(output_schema=output_schema_for("get_test_case_details"))(
        wrap_tool_with_telemetry(
            search_tools.get_test_case_details, output_model=output_model_for("get_test_case_details")
        )
    )
    arguments: dict[str, object] = {"test_case_id": 1, "project_id": 123}
    if output_format is not None:
        arguments["output_format"] = output_format

    async with Client(server) as client:
        result = await client.call_tool("get_test_case_details", arguments)

    search_client.get_test_case.assert_awaited_once_with(1)
    search_client.get_test_case_scenario.assert_awaited_once_with(1)
    search_client.list_test_case_attachments.assert_awaited_once_with(1, page=0, size=100)
    expected = await search_tools.get_test_case_details(test_case_id=1, project_id=123, output_format="json")
    assert result.structured_content == expected.structured_content
    assert result.structured_content["id"] == 1
    assert result.structured_content["description"] is None
    assert result.structured_content["url"] == "https://example.com/project/123/test-cases/1"
    if output_format == "plain":
        plain = await search_tools.get_test_case_details(test_case_id=1, project_id=123, output_format="plain")
        assert isinstance(plain, str)
        assert len(result.content) == 1
        assert result.content[0].text == plain
    else:
        assert result.content == []


def test_mcp_contract_validates_plain_payload() -> None:
    result = render_output(plain="Found a case", json_payload={"unexpected": "field"}, output_format="plain")

    with pytest.raises(ValidationError):
        _apply_mcp_output_contract(result, output_model_for("get_test_case_details"))


@pytest.mark.parametrize("payload", [None, {"error": "upstream unavailable"}])
def test_mcp_contract_preserves_error_results(payload: dict[str, str] | None) -> None:
    result = ToolResult(
        content=[TextContent(type="text", text="upstream unavailable")],
        structured_content=payload,
        is_error=True,
    )

    assert _apply_mcp_output_contract(result, output_model_for("get_test_case_details")) is result


@pytest.mark.asyncio
async def test_mcp_client_accepts_error_without_structured_content(search_client: _SearchClient) -> None:
    search_client.get_test_case.side_effect = RuntimeError("upstream unavailable")
    server = FastMCP("output-contract-error-regression")
    server.tool(output_schema=output_schema_for("get_test_case_details"))(
        wrap_tool_with_telemetry(
            search_tools.get_test_case_details, output_model=output_model_for("get_test_case_details")
        )
    )

    async with Client(server) as client:
        result = await client.call_tool(
            "get_test_case_details", {"test_case_id": 1, "output_format": "plain"}, raise_on_error=False
        )

    assert result.is_error
    assert result.structured_content is None
    assert "upstream unavailable" in result.content[0].text
