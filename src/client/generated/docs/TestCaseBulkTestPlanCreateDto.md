# TestCaseBulkTestPlanCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 
**test_plan_name** | **str** |  | 
**tree** | [**IdAndNameOnlyDto**](IdAndNameOnlyDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_bulk_test_plan_create_dto import TestCaseBulkTestPlanCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkTestPlanCreateDto from a JSON string
test_case_bulk_test_plan_create_dto_instance = TestCaseBulkTestPlanCreateDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkTestPlanCreateDto.to_json())

# convert the object into a dict
test_case_bulk_test_plan_create_dto_dict = test_case_bulk_test_plan_create_dto_instance.to_dict()
# create an instance of TestCaseBulkTestPlanCreateDto from a dict
test_case_bulk_test_plan_create_dto_from_dict = TestCaseBulkTestPlanCreateDto.from_dict(test_case_bulk_test_plan_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


