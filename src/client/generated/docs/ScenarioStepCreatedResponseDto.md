# ScenarioStepCreatedResponseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_step_id** | **int** |  | [optional] 
**scenario** | [**NormalizedScenarioDto**](NormalizedScenarioDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.scenario_step_created_response_dto import ScenarioStepCreatedResponseDto

# TODO update the JSON string below
json = "{}"
# create an instance of ScenarioStepCreatedResponseDto from a JSON string
scenario_step_created_response_dto_instance = ScenarioStepCreatedResponseDto.from_json(json)
# print the JSON string representation of the object
print(ScenarioStepCreatedResponseDto.to_json())

# convert the object into a dict
scenario_step_created_response_dto_dict = scenario_step_created_response_dto_instance.to_dict()
# create an instance of ScenarioStepCreatedResponseDto from a dict
scenario_step_created_response_dto_from_dict = ScenarioStepCreatedResponseDto.from_dict(scenario_step_created_response_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


