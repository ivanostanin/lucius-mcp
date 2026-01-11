"""Allure TestOps API client and models."""

from .client import (
    AllureClient,
    ScenarioStepCreatedResponseDto,
    ScenarioStepCreateDto,
    TestCaseAttachmentRowDto,
    TestCaseCreateV2Dto,
    TestCaseDto,
    TestCaseOverviewDto,
    TestCasePatchV2Dto,
    TestCaseScenarioDto,
)
from .exceptions import (
    AllureAPIError,
    AllureAuthError,
    AllureNotFoundError,
    AllureRateLimitError,
    AllureValidationError,
)

__all__ = [
    "AllureAPIError",
    "AllureAuthError",
    "AllureClient",
    "AllureNotFoundError",
    "AllureRateLimitError",
    "AllureValidationError",
    "ScenarioStepCreateDto",
    "ScenarioStepCreatedResponseDto",
    "TestCaseAttachmentRowDto",
    "TestCaseCreateV2Dto",
    "TestCaseDto",
    "TestCaseOverviewDto",
    "TestCasePatchV2Dto",
    "TestCaseScenarioDto",
]
