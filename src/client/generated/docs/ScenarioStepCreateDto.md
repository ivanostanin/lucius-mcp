# ScenarioStepCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attachment_id** | **int** |  | [optional] 
**body** | **str** |  | [optional] 
**body_json** | [**DefaultTextMarkupDocument**](DefaultTextMarkupDocument.md) |  | [optional] 
**parent_id** | **int** |  | [optional] 
**shared_step_id** | **int** |  | [optional] 
**test_case_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.scenario_step_create_dto import ScenarioStepCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of ScenarioStepCreateDto from a JSON string
scenario_step_create_dto_instance = ScenarioStepCreateDto.from_json(json)
# print the JSON string representation of the object
print(ScenarioStepCreateDto.to_json())

# convert the object into a dict
scenario_step_create_dto_dict = scenario_step_create_dto_instance.to_dict()
# create an instance of ScenarioStepCreateDto from a dict
scenario_step_create_dto_from_dict = ScenarioStepCreateDto.from_dict(scenario_step_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


