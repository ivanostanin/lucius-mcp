from pydantic import BaseModel, ConfigDict, Field

# Re-export generated models


class TestPlanValues(BaseModel):
    """
    Helper model for creating/updating test plans with specific values.
    This simplifies the interaction with the generated models.
    """

    model_config = ConfigDict(strict=True)

    name: str = Field(..., description="Name of the test plan")
    description: str | None = Field(None, description="Description of the test plan")
    product_area_id: int | None = Field(None, description="ID of the product area")
    tags: list[str] | None = Field(None, description="Tags for the test plan")


class TestPlanCaseSelection(BaseModel):
    """
    Model for selecting test cases to include in a plan.
    Supports both explicit ID list and AQL filtering.
    """

    model_config = ConfigDict(strict=True)

    test_case_ids: list[int] | None = Field(None, description="List of Test Case IDs to include")
    aql_filter: str | None = Field(None, description="AQL query to select test cases")

    def validate_selection(self) -> None:
        if not self.test_case_ids and not self.aql_filter:
            raise ValueError("Either test_case_ids or aql_filter must be provided")
