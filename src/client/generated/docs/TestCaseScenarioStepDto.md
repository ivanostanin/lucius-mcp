# TestCaseScenarioStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attachments** | [**List[TestCaseAttachmentRowDto]**](TestCaseAttachmentRowDto.md) |  | [optional] 
**expected_result** | **str** |  | [optional] 
**has_content** | **bool** |  | [optional] [readonly] 
**keyword** | **str** |  | [optional] 
**leaf** | **bool** |  | [optional] [readonly] 
**name** | **str** |  | [optional] 
**steps** | [**List[TestCaseScenarioStepDto]**](TestCaseScenarioStepDto.md) |  | [optional] 
**steps_count** | **int** |  | [optional] [readonly] 

## Example

```python
from src.client.generated.models.test_case_scenario_step_dto import TestCaseScenarioStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseScenarioStepDto from a JSON string
test_case_scenario_step_dto_instance = TestCaseScenarioStepDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseScenarioStepDto.to_json())

# convert the object into a dict
test_case_scenario_step_dto_dict = test_case_scenario_step_dto_instance.to_dict()
# create an instance of TestCaseScenarioStepDto from a dict
test_case_scenario_step_dto_from_dict = TestCaseScenarioStepDto.from_dict(test_case_scenario_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


