from unittest.mock import AsyncMock

import pytest
from fastmcp.tools import Tool

import src.tools.search as search_tools
from src.client import PageTestCaseDto, TestCaseDto
from src.client.generated.models.test_tag_dto import TestTagDto


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
    tool = Tool.from_function(search_tools.search_test_cases, output_schema=None)

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


@pytest.mark.asyncio
async def test_fastmcp_keeps_text_content_when_plain_output_is_requested(search_client: _SearchClient) -> None:
    tool = Tool.from_function(search_tools.search_test_cases, output_schema=None)

    result = await tool.run({"query": "login", "output_format": "plain"})

    assert result.structured_content is None
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    assert "Found 1 test cases matching 'login':" in result.content[0].text
    assert "Test Case URL: https://example.com/project/123/test-cases/1" in result.content[0].text


@pytest.mark.asyncio
async def test_fastmcp_emits_only_structured_content_when_json_output_is_requested(
    search_client: _SearchClient,
) -> None:
    tool = Tool.from_function(search_tools.search_test_cases, output_schema=None)

    result = await tool.run({"query": "login", "output_format": "json"})

    assert result.content == []
    assert result.structured_content is not None
    assert result.structured_content["items"][0]["tags"] == ["smoke"]
    assert result.structured_content["items"][0]["url"] == "https://example.com/project/123/test-cases/1"
