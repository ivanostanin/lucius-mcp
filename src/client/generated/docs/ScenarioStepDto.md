# ScenarioStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 

## Example

```python
from src.client.generated.models.scenario_step_dto import ScenarioStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of ScenarioStepDto from a JSON string
scenario_step_dto_instance = ScenarioStepDto.from_json(json)
# print the JSON string representation of the object
print(ScenarioStepDto.to_json())

# convert the object into a dict
scenario_step_dto_dict = scenario_step_dto_instance.to_dict()
# create an instance of ScenarioStepDto from a dict
scenario_step_dto_from_dict = ScenarioStepDto.from_dict(scenario_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


