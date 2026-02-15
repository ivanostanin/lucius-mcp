"""Integration tests for defect tools."""

from unittest.mock import AsyncMock, patch

import pytest

from src.client.generated.models.defect_dto import DefectDto
from src.client.generated.models.defect_matcher_dto import DefectMatcherDto
from src.client.generated.models.defect_row_dto import DefectRowDto
from src.client.generated.models.status_dto import StatusDto
from src.client.generated.models.test_case_row_dto import TestCaseRowDto
from src.services.defect_service import DefectTestCaseLinkResult, DefectTestCaseListResult
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

# ── Defect tools ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_defect_tool() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.create_defect = AsyncMock(return_value=DefectDto(id=10, name="Bug A"))

            output = await create_defect(name="Bug A", description="desc")

            assert "Created Defect #10" in output
            assert "'Bug A'" in output
            mock_svc.create_defect.assert_called_once_with(name="Bug A", description="desc")


@pytest.mark.asyncio
async def test_get_defect_tool() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.get_defect = AsyncMock(
                return_value=DefectDto(id=10, name="Bug A", closed=False, description="details")
            )

            output = await get_defect(defect_id=10)

            assert "Defect #10" in output
            assert "Status: Open" in output
            assert "details" in output


@pytest.mark.asyncio
async def test_update_defect_tool() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.update_defect = AsyncMock(return_value=DefectDto(id=10, name="Renamed", closed=True))

            output = await update_defect(defect_id=10, name="Renamed", closed=True)

            assert "Updated Defect #10" in output
            assert "Status: Closed" in output
            mock_svc.update_defect.assert_called_once_with(
                defect_id=10,
                name="Renamed",
                description=None,
                closed=True,
            )


@pytest.mark.asyncio
async def test_delete_defect_tool_confirmed() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.delete_defect = AsyncMock()

            output = await delete_defect(defect_id=10, confirm=True)

            assert "Deleted Defect #10" in output
            mock_svc.delete_defect.assert_called_once_with(10)


@pytest.mark.asyncio
async def test_delete_defect_no_confirm() -> None:
    output = await delete_defect(defect_id=10, confirm=False)

    assert "aborted" in output.lower()
    assert "confirm=true" in output


@pytest.mark.asyncio
async def test_list_defects_tool() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.list_defects = AsyncMock(
                return_value=[
                    DefectRowDto(id=1, name="D1", closed=False),
                    DefectRowDto(id=2, name="D2", closed=True),
                ]
            )

            output = await list_defects()

            assert "2 defect(s)" in output
            assert "#1: D1 (Open)" in output
            assert "#2: D2 (Closed)" in output


@pytest.mark.asyncio
async def test_list_defects_empty() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.list_defects = AsyncMock(return_value=[])

            output = await list_defects()

            assert "No defects found" in output


@pytest.mark.asyncio
async def test_link_defect_to_test_case_tool() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.link_defect_to_test_case = AsyncMock(
                return_value=DefectTestCaseLinkResult(
                    defect_id=10,
                    test_case_id=20,
                    issue_key="PROJ-123",
                    integration_id=7,
                    already_linked=False,
                )
            )

            output = await link_defect_to_test_case(
                defect_id=10,
                test_case_id=20,
                issue_key="PROJ-123",
                integration_id=7,
            )

            assert "Linked Defect #10 to Test Case #20" in output
            assert "PROJ-123" in output
            mock_svc.link_defect_to_test_case.assert_called_once_with(
                defect_id=10,
                test_case_id=20,
                issue_key="PROJ-123",
                integration_id=7,
                integration_name=None,
            )


@pytest.mark.asyncio
async def test_link_defect_to_test_case_tool_with_integration_name() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.link_defect_to_test_case = AsyncMock(
                return_value=DefectTestCaseLinkResult(
                    defect_id=10,
                    test_case_id=20,
                    issue_key="PROJ-123",
                    integration_id=11,
                    already_linked=False,
                )
            )

            output = await link_defect_to_test_case(
                defect_id=10,
                test_case_id=20,
                issue_key="PROJ-123",
                integration_name="Jira",
            )

            assert "Linked Defect #10 to Test Case #20" in output
            mock_svc.link_defect_to_test_case.assert_called_once_with(
                defect_id=10,
                test_case_id=20,
                issue_key="PROJ-123",
                integration_id=None,
                integration_name="Jira",
            )


@pytest.mark.asyncio
async def test_link_defect_to_test_case_tool_idempotent() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.link_defect_to_test_case = AsyncMock(
                return_value=DefectTestCaseLinkResult(
                    defect_id=10,
                    test_case_id=20,
                    issue_key="PROJ-123",
                    integration_id=7,
                    already_linked=True,
                )
            )

            output = await link_defect_to_test_case(defect_id=10, test_case_id=20, issue_key="PROJ-123")

            assert "already linked" in output.lower()
            assert "No changes made" in output


@pytest.mark.asyncio
async def test_list_defect_test_cases_tool() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.list_defect_test_cases = AsyncMock(
                return_value=DefectTestCaseListResult(
                    items=[TestCaseRowDto(id=20, name="Linked TC", status=StatusDto(name="Draft"))],
                    total=1,
                    page=0,
                    size=20,
                    total_pages=1,
                )
            )

            output = await list_defect_test_cases(defect_id=10, page=0, size=20)

            assert "Found 1 linked test case(s) for Defect #10" in output
            assert "#20: Linked TC [Draft]" in output
            mock_svc.list_defect_test_cases.assert_called_once_with(defect_id=10, page=0, size=20)


# ── Defect Matcher tools ────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_defect_matcher_tool() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.create_defect_matcher = AsyncMock(
                return_value=DefectMatcherDto(id=20, name="NPE Rule", defect_id=10)
            )

            output = await create_defect_matcher(
                defect_id=10,
                name="NPE Rule",
                message_regex="NullPointer.*",
            )

            assert "Created Defect Matcher #20" in output
            assert "Defect #10" in output
            mock_svc.create_defect_matcher.assert_called_once_with(
                defect_id=10,
                name="NPE Rule",
                message_regex="NullPointer.*",
                trace_regex=None,
            )


@pytest.mark.asyncio
async def test_update_defect_matcher_tool() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.update_defect_matcher = AsyncMock(return_value=DefectMatcherDto(id=20, name="Updated Rule"))

            output = await update_defect_matcher(matcher_id=20, name="Updated Rule")

            assert "Updated Defect Matcher #20" in output
            mock_svc.update_defect_matcher.assert_called_once_with(
                matcher_id=20,
                name="Updated Rule",
                message_regex=None,
                trace_regex=None,
            )


@pytest.mark.asyncio
async def test_delete_defect_matcher_confirmed() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.delete_defect_matcher = AsyncMock()

            output = await delete_defect_matcher(matcher_id=20, confirm=True)

            assert "Deleted Defect Matcher #20" in output
            mock_svc.delete_defect_matcher.assert_called_once_with(20)


@pytest.mark.asyncio
async def test_delete_defect_matcher_no_confirm() -> None:
    output = await delete_defect_matcher(matcher_id=20, confirm=False)

    assert "aborted" in output.lower()
    assert "confirm=true" in output


@pytest.mark.asyncio
async def test_list_defect_matchers_tool() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.list_defect_matchers = AsyncMock(
                return_value=[
                    DefectMatcherDto(
                        id=20,
                        name="NPE Rule",
                        defect_id=10,
                        message_regex="NullPointer.*",
                    ),
                ]
            )

            output = await list_defect_matchers(defect_id=10)

            assert "1 matcher(s)" in output
            assert "#20: NPE Rule" in output
            assert "NullPointer" in output


@pytest.mark.asyncio
async def test_list_defect_matchers_empty() -> None:
    with patch("src.tools.defects.AllureClient.from_env") as mock_ctx:
        mock_client = AsyncMock()
        mock_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.defects.DefectService") as mock_svc_cls:
            mock_svc = mock_svc_cls.return_value
            mock_svc.list_defect_matchers = AsyncMock(return_value=[])

            output = await list_defect_matchers(defect_id=10)

            assert "No matchers found" in output
