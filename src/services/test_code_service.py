"""Service for generating automated test code from TestOps test cases."""

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.generated.api.ide_controller_api import IdeControllerApi
from src.client.generated.models.test_code_generation_request_dto import TestCodeGenerationRequestDto


class TestCodeService:
    """Generate framework-specific test code using the TestOps IDE API."""

    def __init__(self, client: AllureClient) -> None:
        """Initialize the service with an authenticated TestOps client."""
        self._client = client

    @property
    def _api(self) -> IdeControllerApi:
        """Return the generated controller for the IDE API."""
        return IdeControllerApi(self._client.api_client)

    async def generate_code(self, test_case_id: int, lang: str, framework: str) -> str:
        """Generate code for one test case in the requested language and framework.

        The IDE endpoint synchronizes all test-case fields before generating the
        snippet, so callers always receive code for the current TestOps state.

        Args:
            test_case_id: ID of the source TestOps test case.
            lang: Target programming language accepted by TestOps.
            framework: Target test framework accepted by TestOps.

        Returns:
            The generated source-code snippet.

        Raises:
            AllureValidationError: If the test case ID, language, or framework is blank.
        """
        if not isinstance(test_case_id, int) or isinstance(test_case_id, bool) or test_case_id <= 0:
            raise AllureValidationError("Test Case ID must be a positive integer")
        if not lang or not lang.strip():
            raise AllureValidationError("Language is required")
        if not framework or not framework.strip():
            raise AllureValidationError("Framework is required")

        request = TestCodeGenerationRequestDto(
            lang=lang.strip(),
            test_framework=framework.strip(),
            sync_fields=True,
            sync_name=True,
            sync_tags=True,
            sync_scenario=True,
        )
        response = await self._client._call_api(
            self._api.generate_test_code(
                id=test_case_id,
                test_code_generation_request_dto=request,
                _request_timeout=self._client._timeout,
            )
        )
        return response.code
