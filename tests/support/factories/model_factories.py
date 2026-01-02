"""Model factories for Allure TestOps DTOs using Faker."""

from typing import Any

from faker import Faker

from src.client.generated.models import (
    BodyStepDto,
    SharedStepScenarioDtoStepsInner,
    StatusDto,
    TestCaseCreateV2Dto,
    TestCaseOverviewDto,
    TestCaseScenarioStepDto,
    TestCaseScenarioV2Dto,
)

fake = Faker()


def create_test_case_create_v2_dto(**overrides: object) -> TestCaseCreateV2Dto:
    """Factory for TestCaseCreateV2Dto."""
    defaults: dict[str, Any] = {
        "name": fake.sentence(nb_words=3),
        "projectId": 1,
        "automated": False,
        "statusId": 1,
        "description": fake.paragraph(),
        "precondition": fake.paragraph(),
    }
    defaults.update(overrides)
    return TestCaseCreateV2Dto(**defaults)


def create_test_case_overview_dto(**overrides: object) -> TestCaseOverviewDto:
    """Factory for TestCaseOverviewDto."""
    defaults: dict[str, Any] = {
        "id": fake.random_int(min=1, max=10000),
        "name": fake.sentence(nb_words=3),
        "projectId": 1,
        "createdDate": fake.random_int(min=1000000000, max=2000000000),
        "status": StatusDto(id=1, name="Draft"),
        "automated": False,
    }
    defaults.update(overrides)
    return TestCaseOverviewDto(**defaults)


def create_shared_step_scenario_dto_steps_inner(**overrides: object) -> SharedStepScenarioDtoStepsInner:
    """Factory for SharedStepScenarioDtoStepsInner (used in scenarios)."""
    body_step = BodyStepDto(
        body=fake.sentence(nb_words=5),
        type="text",
    )
    # Wrap in oneOf container
    return SharedStepScenarioDtoStepsInner(body_step)


def create_test_case_scenario_step_dto(**overrides: object) -> TestCaseScenarioStepDto:
    """Factory for TestCaseScenarioStepDto (used in list/read)."""
    defaults: dict[str, Any] = {
        "name": fake.sentence(nb_words=5),
        "spacing": False,
    }
    defaults.update(overrides)
    return TestCaseScenarioStepDto(**defaults)


def create_test_case_scenario_v2_dto(**overrides: object) -> TestCaseScenarioV2Dto:
    """Factory for TestCaseScenarioV2Dto."""
    defaults: dict[str, Any] = {
        "steps": [create_shared_step_scenario_dto_steps_inner() for _ in range(3)],
    }
    defaults.update(overrides)
    return TestCaseScenarioV2Dto(**defaults)
