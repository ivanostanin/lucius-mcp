# ScenarioStepMoveDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**after_id** | **int** |  | [optional] 
**before_id** | **int** |  | [optional] 
**parent_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.scenario_step_move_dto import ScenarioStepMoveDto

# TODO update the JSON string below
json = "{}"
# create an instance of ScenarioStepMoveDto from a JSON string
scenario_step_move_dto_instance = ScenarioStepMoveDto.from_json(json)
# print the JSON string representation of the object
print(ScenarioStepMoveDto.to_json())

# convert the object into a dict
scenario_step_move_dto_dict = scenario_step_move_dto_instance.to_dict()
# create an instance of ScenarioStepMoveDto from a dict
scenario_step_move_dto_from_dict = ScenarioStepMoveDto.from_dict(scenario_step_move_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


