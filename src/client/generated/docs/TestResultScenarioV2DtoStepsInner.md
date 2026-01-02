# TestResultScenarioV2DtoStepsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**attachment** | [**TestResultAttachmentStepDtoAllOfAttachment**](TestResultAttachmentStepDtoAllOfAttachment.md) |  | [optional] 
**attachment_id** | **int** |  | [optional] 
**duration** | **int** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 
**body** | **str** |  | [optional] 
**body_json** | [**DefaultTextMarkupDocument**](DefaultTextMarkupDocument.md) |  | [optional] 
**message** | **str** |  | [optional] 
**parameters** | [**List[TestResultScenarioStepParameter]**](TestResultScenarioStepParameter.md) |  | [optional] 
**show_message** | **bool** |  | [optional] 
**trace** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_scenario_v2_dto_steps_inner import TestResultScenarioV2DtoStepsInner

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultScenarioV2DtoStepsInner from a JSON string
test_result_scenario_v2_dto_steps_inner_instance = TestResultScenarioV2DtoStepsInner.from_json(json)
# print the JSON string representation of the object
print(TestResultScenarioV2DtoStepsInner.to_json())

# convert the object into a dict
test_result_scenario_v2_dto_steps_inner_dict = test_result_scenario_v2_dto_steps_inner_instance.to_dict()
# create an instance of TestResultScenarioV2DtoStepsInner from a dict
test_result_scenario_v2_dto_steps_inner_from_dict = TestResultScenarioV2DtoStepsInner.from_dict(test_result_scenario_v2_dto_steps_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


