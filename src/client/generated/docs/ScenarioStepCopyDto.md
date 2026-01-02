# ScenarioStepCopyDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**after_id** | **int** |  | [optional] 
**before_id** | **int** |  | [optional] 
**parent_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.scenario_step_copy_dto import ScenarioStepCopyDto

# TODO update the JSON string below
json = "{}"
# create an instance of ScenarioStepCopyDto from a JSON string
scenario_step_copy_dto_instance = ScenarioStepCopyDto.from_json(json)
# print the JSON string representation of the object
print(ScenarioStepCopyDto.to_json())

# convert the object into a dict
scenario_step_copy_dto_dict = scenario_step_copy_dto_instance.to_dict()
# create an instance of ScenarioStepCopyDto from a dict
scenario_step_copy_dto_from_dict = ScenarioStepCopyDto.from_dict(scenario_step_copy_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


