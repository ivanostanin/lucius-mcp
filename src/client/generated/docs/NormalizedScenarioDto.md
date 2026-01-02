# NormalizedScenarioDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attachments** | [**Dict[str, NormalizedScenarioDtoAttachmentsValue]**](NormalizedScenarioDtoAttachmentsValue.md) |  | [optional] 
**root** | [**NormalizedScenarioStepDto**](NormalizedScenarioStepDto.md) |  | [optional] 
**scenario_steps** | [**Dict[str, NormalizedScenarioStepDto]**](NormalizedScenarioStepDto.md) |  | [optional] 
**shared_step_attachments** | [**Dict[str, NormalizedScenarioDtoAttachmentsValue]**](NormalizedScenarioDtoAttachmentsValue.md) |  | [optional] 
**shared_step_scenario_steps** | [**Dict[str, NormalizedScenarioStepDto]**](NormalizedScenarioStepDto.md) |  | [optional] 
**shared_steps** | [**Dict[str, NormalizedScenarioStepDto]**](NormalizedScenarioStepDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.normalized_scenario_dto import NormalizedScenarioDto

# TODO update the JSON string below
json = "{}"
# create an instance of NormalizedScenarioDto from a JSON string
normalized_scenario_dto_instance = NormalizedScenarioDto.from_json(json)
# print the JSON string representation of the object
print(NormalizedScenarioDto.to_json())

# convert the object into a dict
normalized_scenario_dto_dict = normalized_scenario_dto_instance.to_dict()
# create an instance of NormalizedScenarioDto from a dict
normalized_scenario_dto_from_dict = NormalizedScenarioDto.from_dict(normalized_scenario_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


