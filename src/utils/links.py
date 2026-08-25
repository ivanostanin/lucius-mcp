from __future__ import annotations

from collections.abc import Sequence


def test_case_url(base_url: str, project_id: int, test_case_id: int) -> str:
    return f"{base_url}/project/{project_id}/test-cases/{test_case_id}"


def launch_url(base_url: str, project_id: int, launch_id: int) -> str:
    return f"{base_url}/launch/{launch_id}"


def test_result_url(base_url: str, launch_id: int, test_result_id: int) -> str:
    """Build a result browser URL only from verified upstream launch context."""
    return f"{base_url.rstrip('/')}/launch/{launch_id}/tree/{test_result_id}"


def result_attachment_download_url(base_url: str, attachment_id: int) -> str:
    return f"{base_url.rstrip('/')}/api/testresult/attachment/{attachment_id}/content?inline=false"


def fixture_result_attachment_download_url(base_url: str, attachment_id: int) -> str:
    return f"{base_url.rstrip('/')}/api/testfixtureresult/attachment/{attachment_id}/content?inline=false"


def test_case_attachment_download_url(base_url: str, attachment_id: int) -> str:
    return f"{base_url.rstrip('/')}/api/testcase/attachment/{attachment_id}/content?inline=false"


def defect_url(base_url: str, project_id: int, defect_id: int) -> str:
    return f"{base_url}/project/{project_id}/defects/{defect_id}"


def test_plan_url(base_url: str, project_id: int, plan_id: int) -> str:
    return f"{base_url}/testplan/{plan_id}"


def shared_step_url(base_url: str, project_id: int, shared_step_id: int) -> str:
    return f"{base_url}/project/{project_id}/shared-steps/{shared_step_id}"


def normalize_links(items: Sequence[object]) -> list[tuple[str | None, str | None, str | None]]:
    normalized: list[tuple[str | None, str | None, str | None]] = []
    for item in items:
        if isinstance(item, dict):
            normalized.append((item.get("name"), item.get("url"), item.get("type")))
        else:
            normalized.append((getattr(item, "name", None), getattr(item, "url", None), getattr(item, "type", None)))
    return normalized
