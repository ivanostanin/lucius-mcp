# SharedStepScenarioDtoStepsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**attachment_id** | **int** |  | [optional] 
**body** | **str** |  | [optional] 
**body_json** | [**DefaultTextMarkupDocument**](DefaultTextMarkupDocument.md) |  | [optional] 
**shared_step_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.shared_step_scenario_dto_steps_inner import SharedStepScenarioDtoStepsInner

# TODO update the JSON string below
json = "{}"
# create an instance of SharedStepScenarioDtoStepsInner from a JSON string
shared_step_scenario_dto_steps_inner_instance = SharedStepScenarioDtoStepsInner.from_json(json)
# print the JSON string representation of the object
print(SharedStepScenarioDtoStepsInner.to_json())

# convert the object into a dict
shared_step_scenario_dto_steps_inner_dict = shared_step_scenario_dto_steps_inner_instance.to_dict()
# create an instance of SharedStepScenarioDtoStepsInner from a dict
shared_step_scenario_dto_steps_inner_from_dict = SharedStepScenarioDtoStepsInner.from_dict(shared_step_scenario_dto_steps_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


