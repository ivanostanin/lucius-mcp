# SharedStepScenarioDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**steps** | [**List[SharedStepScenarioDtoStepsInner]**](SharedStepScenarioDtoStepsInner.md) |  | [optional] 

## Example

```python
from src.client.generated.models.shared_step_scenario_dto import SharedStepScenarioDto

# TODO update the JSON string below
json = "{}"
# create an instance of SharedStepScenarioDto from a JSON string
shared_step_scenario_dto_instance = SharedStepScenarioDto.from_json(json)
# print the JSON string representation of the object
print(SharedStepScenarioDto.to_json())

# convert the object into a dict
shared_step_scenario_dto_dict = shared_step_scenario_dto_instance.to_dict()
# create an instance of SharedStepScenarioDto from a dict
shared_step_scenario_dto_from_dict = SharedStepScenarioDto.from_dict(shared_step_scenario_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


