# TestResultScenarioStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attachments** | [**List[TestResultAttachmentStepDtoAllOfAttachment]**](TestResultAttachmentStepDtoAllOfAttachment.md) |  | [optional] 
**attachments_count** | **int** |  | [optional] 
**duration** | **int** |  | [optional] 
**expandable** | **bool** |  | [optional] 
**expected_result** | **str** |  | [optional] 
**keyword** | **str** |  | [optional] 
**leaf** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**parameters** | [**List[TestResultParameterDto]**](TestResultParameterDto.md) |  | [optional] 
**show_message** | **bool** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**steps** | [**List[TestResultScenarioStepDto]**](TestResultScenarioStepDto.md) |  | [optional] 
**steps_count** | **int** |  | [optional] 
**stop** | **int** |  | [optional] 
**trace** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_scenario_step_dto import TestResultScenarioStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultScenarioStepDto from a JSON string
test_result_scenario_step_dto_instance = TestResultScenarioStepDto.from_json(json)
# print the JSON string representation of the object
print(TestResultScenarioStepDto.to_json())

# convert the object into a dict
test_result_scenario_step_dto_dict = test_result_scenario_step_dto_instance.to_dict()
# create an instance of TestResultScenarioStepDto from a dict
test_result_scenario_step_dto_from_dict = TestResultScenarioStepDto.from_dict(test_result_scenario_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


