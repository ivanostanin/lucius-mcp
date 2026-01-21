import os

import pytest

from src.client import AllureClient
from src.client.exceptions import TestCaseNotFoundError
from src.services.search_service import SearchService
from src.tools.search import _format_test_case_details
from src.utils.auth import get_auth_context

pytestmark = pytest.mark.skipif(
    not (os.getenv("ALLURE_ENDPOINT") and os.getenv("ALLURE_API_TOKEN")),
    reason="Sandbox credentials not configured (ALLURE_ENDPOINT/TOKEN)",
)


@pytest.mark.asyncio
async def test_get_test_case_details_smoke(
    allure_client: AllureClient,
    project_id: int,
    api_token: str,
) -> None:
    service = SearchService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    # Use a small page to find at least one test case ID
    page = await service.list_test_cases(project_id=project_id, page=0, size=1)
    assert page.items, "Expected at least one test case in project"
    test_case_id = page.items[0].id
    assert test_case_id is not None

    details = await service.get_test_case_details(test_case_id)
    text = _format_test_case_details(details)

    assert str(test_case_id) in text
    assert details.test_case.name in text
    # Spot-check formatting and metadata presence
    assert "Status:" in text
    assert "Steps:" in text or "Preconditions:" in text or "Description:" in text

    # Stronger metadata assertions (best-effort; scenario/test data dependent)
    assert "Tags:" in text or "Custom Fields:" in text or "Attachments:" in text


@pytest.mark.asyncio
async def test_get_test_case_details_not_found(
    allure_client: AllureClient,
    api_token: str,
) -> None:
    service = SearchService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )
    with pytest.raises(TestCaseNotFoundError):
        await service.get_test_case_details(99999999)
