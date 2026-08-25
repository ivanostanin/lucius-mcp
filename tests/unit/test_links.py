from src.utils.links import (
    defect_url,
    fixture_result_attachment_download_url,
    launch_url,
    result_attachment_download_url,
    shared_step_url,
)
from src.utils.links import (
    test_case_attachment_download_url as build_test_case_attachment_download_url,
)
from src.utils.links import (
    test_case_url as build_test_case_url,
)
from src.utils.links import (
    test_plan_url as build_test_plan_url,
)
from src.utils.links import (
    test_result_url as build_test_result_url,
)


def test_testops_entity_url_helpers_use_base_url_project_and_entity_ids() -> None:
    base_url = "https://example.com"
    project_id = 456

    assert build_test_case_url(base_url, project_id, 11) == "https://example.com/project/456/test-cases/11"
    assert launch_url(base_url, project_id, 12) == "https://example.com/launch/12"
    assert defect_url(base_url, project_id, 13) == "https://example.com/project/456/defects/13"
    assert build_test_plan_url(base_url, project_id, 14) == "https://example.com/testplan/14"
    assert shared_step_url(base_url, project_id, 15) == "https://example.com/project/456/shared-steps/15"


def test_test_result_and_attachment_urls_use_stable_bearer_authenticated_api_paths() -> None:
    assert build_test_result_url("https://example.com/", 12, 34) == "https://example.com/launch/12/tree/34"
    assert result_attachment_download_url("https://example.com/", 1) == (
        "https://example.com/api/testresult/attachment/1/content?inline=false"
    )
    assert fixture_result_attachment_download_url("https://example.com", 2) == (
        "https://example.com/api/testfixtureresult/attachment/2/content?inline=false"
    )
    assert build_test_case_attachment_download_url("https://example.com", 3) == (
        "https://example.com/api/testcase/attachment/3/content?inline=false"
    )
