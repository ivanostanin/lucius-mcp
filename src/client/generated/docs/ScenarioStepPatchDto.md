# ScenarioStepPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attachment_id** | **int** |  | [optional] 
**body** | **str** |  | [optional] 
**body_json** | [**DefaultTextMarkupDocument**](DefaultTextMarkupDocument.md) |  | [optional] 
**expected_result** | **str** |  | [optional] 
**shared_step_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.scenario_step_patch_dto import ScenarioStepPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of ScenarioStepPatchDto from a JSON string
scenario_step_patch_dto_instance = ScenarioStepPatchDto.from_json(json)
# print the JSON string representation of the object
print(ScenarioStepPatchDto.to_json())

# convert the object into a dict
scenario_step_patch_dto_dict = scenario_step_patch_dto_instance.to_dict()
# create an instance of ScenarioStepPatchDto from a dict
scenario_step_patch_dto_from_dict = ScenarioStepPatchDto.from_dict(scenario_step_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


