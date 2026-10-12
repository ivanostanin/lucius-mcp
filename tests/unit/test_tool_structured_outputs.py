import asyncio
from unittest.mock import AsyncMock

import pytest
from fastmcp import Client, FastMCP
from fastmcp.tools import Tool
from fastmcp.tools.base import ToolResult
from mcp.types import TextContent
from pydantic import BaseModel, ValidationError

import src.tools.search as search_tools
from src.client import PageTestCaseDto, TestCaseDto
from src.client.generated.models.test_tag_dto import TestTagDto
from src.services.search_service import TestCaseDetails
from src.tools.create_test_case import create_test_case
from src.tools.delete_test_case import delete_test_case
from src.tools.output_contract import OutputFormat, render_message_output, render_output
from src.tools.output_schemas import output_model_for, output_schema_for
from src.utils.telemetry import ToolFn, _apply_mcp_output_contract, wrap_tool_with_telemetry


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
async def test_fastmcp_keeps_text_and_structured_content_when_plain_output_is_requested(
    search_client: _SearchClient,
) -> None:
    tool = Tool.from_function(
        wrap_tool_with_telemetry(search_tools.search_test_cases, output_model=output_model_for("search_test_cases")),
        output_schema=output_schema_for("search_test_cases"),
    )

    result = await tool.run({"query": "login", "output_format": "plain"})

    assert result.structured_content["items"][0]["id"] == 1
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


def _register_tool(server: FastMCP, tool: ToolFn, name: str) -> None:
    server.tool(output_schema=output_schema_for(name))(
        wrap_tool_with_telemetry(tool, output_model=output_model_for(name))
    )


@pytest.mark.asyncio
async def test_mcp_client_accepts_test_case_details_in_all_formats(
    search_client: _SearchClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    details = TestCaseDetails(test_case=TestCaseDto(id=1, name="Login Flow"), scenario=None)
    get_details = AsyncMock(return_value=details)
    monkeypatch.setattr("src.services.search_service.SearchService.get_test_case_details", get_details)
    server = FastMCP("plain-output-regression")
    _register_tool(server, search_tools.get_test_case_details, "get_test_case_details")

    results = []
    async with Client(server) as client:
        for output_format in (None, "json", "plain"):
            arguments = {"test_case_id": 1, "project_id": 123}
            if output_format is not None:
                arguments["output_format"] = output_format
            results.append(await client.call_tool_mcp("get_test_case_details", arguments))

    default, structured, plain = results
    assert default.structured_content == structured.structured_content == plain.structured_content
    assert plain.structured_content["id"] == 1
    assert plain.structured_content["description"] is None
    assert default.content == structured.content == []
    assert len(plain.content) == 1
    direct = await search_tools.get_test_case_details(1, project_id=123, output_format="plain")
    assert isinstance(direct, str)
    assert plain.content[0].text == direct
    assert "Test Case URL: https://example.com/project/123/test-cases/1" in direct
    assert get_details.await_count == 4


@pytest.mark.asyncio
async def test_mcp_plain_mutation_executes_service_once(
    search_client: _SearchClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    create = AsyncMock(return_value=TestCaseDto(id=2, name="New case"))
    monkeypatch.setattr("src.services.test_case_service.TestCaseService.create_test_case", create)
    server = FastMCP("single-mutation-regression")
    _register_tool(server, create_test_case, "create_test_case")

    async with Client(server) as client:
        result = await client.call_tool_mcp("create_test_case", {"name": "New case", "output_format": "plain"})

    create.assert_awaited_once()
    assert create.await_args.kwargs["name"] == "New case"
    assert result.structured_content == {
        "id": 2,
        "name": "New case",
        "issues": [],
        "url": "https://example.com/project/123/test-cases/2",
    }
    assert "Created Test Case ID: 2 Name: New case" in result.content[0].text


class _MessageOutput(BaseModel):
    message: str


@pytest.mark.asyncio
async def test_mcp_plain_empty_collection_satisfies_output_schema(search_client: _SearchClient) -> None:
    search_client.list_test_cases.return_value = PageTestCaseDto(
        content=[], total_elements=0, number=0, size=20, total_pages=0
    )
    server = FastMCP("empty-collection-regression")
    _register_tool(server, search_tools.list_test_cases, "list_test_cases")

    async with Client(server) as client:
        structured = await client.call_tool_mcp("list_test_cases", {"output_format": "json"})
        plain = await client.call_tool_mcp("list_test_cases", {"output_format": "plain"})

    assert plain.is_error is False
    assert plain.structured_content == structured.structured_content
    assert plain.structured_content["items"] == []
    assert plain.structured_content["total"] == 0
    assert plain.content[0].text == "No test cases found in this project."


@pytest.mark.asyncio
async def test_mcp_plain_confirmation_satisfies_output_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    delete = AsyncMock()
    monkeypatch.setattr("src.services.test_case_service.TestCaseService.delete_test_case", delete)
    server = FastMCP("confirmation-regression")
    _register_tool(server, delete_test_case, "delete_test_case")

    async with Client(server) as client:
        structured = await client.call_tool_mcp("delete_test_case", {"test_case_id": 1, "output_format": "json"})
        plain = await client.call_tool_mcp("delete_test_case", {"test_case_id": 1, "output_format": "plain"})

    delete.assert_not_awaited()
    assert plain.is_error is False
    assert (
        plain.structured_content
        == structured.structured_content
        == {
            "requires_confirmation": True,
            "test_case_id": 1,
            "action": "delete_test_case",
        }
    )
    assert "Deletion requires confirmation." in plain.content[0].text


@pytest.mark.asyncio
async def test_mcp_plain_context_is_isolated_from_overlapping_direct_calls() -> None:
    started = asyncio.Event()
    release = asyncio.Event()

    async def message_tool(message: str, output_format: OutputFormat | None = None) -> object:
        if message == "MCP":
            started.set()
            await release.wait()
        return render_message_output(message, output_format=output_format)

    wrapped = wrap_tool_with_telemetry(message_tool, output_model=_MessageOutput)
    pending = asyncio.create_task(wrapped(message="MCP", output_format="plain"))
    try:
        await asyncio.wait_for(started.wait(), timeout=5)
        assert await message_tool("Direct", output_format="plain") == "Direct"
    finally:
        release.set()
        result = await asyncio.wait_for(pending, timeout=5)

    assert result.structured_content == {"message": "MCP"}
    assert result.content[0].text == "MCP"
    assert await message_tool("Later", output_format="plain") == "Later"


@pytest.mark.asyncio
@pytest.mark.parametrize("exception", [ValueError("boom"), asyncio.CancelledError()])
async def test_mcp_plain_context_restores_after_failure_or_cancellation(exception: BaseException) -> None:
    async def failing_tool() -> object:
        raise exception

    wrapped = wrap_tool_with_telemetry(failing_tool, output_model=_MessageOutput)
    with pytest.raises(type(exception)):
        await wrapped()

    assert render_message_output("Direct", output_format="plain") == "Direct"


@pytest.mark.asyncio
async def test_mcp_plain_context_restores_after_payload_validation_failure() -> None:
    async def invalid_tool() -> object:
        return render_output(plain="Invalid", json_payload={"wrong": True}, output_format="plain")

    wrapped = wrap_tool_with_telemetry(invalid_tool, output_model=_MessageOutput)
    with pytest.raises(ValidationError):
        await wrapped()
    assert render_message_output("Direct", output_format="plain") == "Direct"


@pytest.mark.asyncio
@pytest.mark.parametrize("error_payload", [None, {"error": "unavailable"}])
async def test_mcp_client_preserves_explicit_error_results_and_tool_exceptions(
    error_payload: dict[str, str] | None,
) -> None:
    explicit_error = ToolResult(
        content=[TextContent(type="text", text="Backend unavailable")],
        structured_content=error_payload,
        meta={"retry": True},
        is_error=True,
    )

    async def error_tool() -> object:
        return explicit_error

    async def failing_tool() -> object:
        raise ValueError("boom")

    server = FastMCP("error-output-regression")
    for tool in (error_tool, failing_tool):
        server.tool(output_schema=_MessageOutput.model_json_schema())(
            wrap_tool_with_telemetry(tool, output_model=_MessageOutput)
        )

    async with Client(server) as client:
        returned = await client.call_tool_mcp("error_tool", {})
        raised = await client.call_tool_mcp("failing_tool", {})

    assert returned.is_error is True
    assert returned.structured_content == error_payload
    assert returned.meta["retry"] is True
    assert returned.content[0].text == "Backend unavailable"
    assert raised.is_error is True
    assert raised.structured_content is None
    assert "boom" in raised.content[0].text


def test_mcp_contract_preserves_success_metadata() -> None:
    result = ToolResult(content=[], structured_content={"message": "Done"}, meta={"trace": "synthetic"})
    validated = _apply_mcp_output_contract(result, _MessageOutput)
    assert validated.meta == {"trace": "synthetic"}
    assert validated.structured_content == {"message": "Done"}
