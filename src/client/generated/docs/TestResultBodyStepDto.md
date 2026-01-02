# TestResultBodyStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | [optional] 
**body_json** | [**DefaultTextMarkupDocument**](DefaultTextMarkupDocument.md) |  | [optional] 
**duration** | **int** |  | [optional] 
**message** | **str** |  | [optional] 
**parameters** | [**List[TestResultScenarioStepParameter]**](TestResultScenarioStepParameter.md) |  | [optional] 
**show_message** | **bool** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 
**trace** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_body_step_dto import TestResultBodyStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultBodyStepDto from a JSON string
test_result_body_step_dto_instance = TestResultBodyStepDto.from_json(json)
# print the JSON string representation of the object
print(TestResultBodyStepDto.to_json())

# convert the object into a dict
test_result_body_step_dto_dict = test_result_body_step_dto_instance.to_dict()
# create an instance of TestResultBodyStepDto from a dict
test_result_body_step_dto_from_dict = TestResultBodyStepDto.from_dict(test_result_body_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


