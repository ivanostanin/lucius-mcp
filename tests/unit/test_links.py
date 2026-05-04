from src.utils.links import (
    defect_url,
    launch_url,
    shared_step_url,
)
from src.utils.links import (
    test_case_url as build_test_case_url,
)
from src.utils.links import (
    test_plan_url as build_test_plan_url,
)


def test_testops_entity_url_helpers_use_base_url_project_and_entity_ids() -> None:
    base_url = "https://example.com"
    project_id = 456

    assert build_test_case_url(base_url, project_id, 11) == "https://example.com/project/456/test-cases/11"
    assert launch_url(base_url, project_id, 12) == "https://example.com/launch/12"
    assert defect_url(base_url, project_id, 13) == "https://example.com/project/456/defects/13"
    assert build_test_plan_url(base_url, project_id, 14) == "https://example.com/testplan/14"
    assert shared_step_url(base_url, project_id, 15) == "https://example.com/project/456/shared-steps/15"
