# NormalizedScenarioStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**archived** | **bool** |  | [optional] 
**attachment_id** | **int** |  | [optional] 
**body** | **str** |  | [optional] 
**body_json** | [**DefaultTextMarkupDocument**](DefaultTextMarkupDocument.md) |  | [optional] 
**children** | **List[int]** |  | [optional] 
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**expected_result** | **str** |  | [optional] 
**expected_result_id** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**shared_step_id** | **int** |  | [optional] 
**test_case_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.normalized_scenario_step_dto import NormalizedScenarioStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of NormalizedScenarioStepDto from a JSON string
normalized_scenario_step_dto_instance = NormalizedScenarioStepDto.from_json(json)
# print the JSON string representation of the object
print(NormalizedScenarioStepDto.to_json())

# convert the object into a dict
normalized_scenario_step_dto_dict = normalized_scenario_step_dto_instance.to_dict()
# create an instance of NormalizedScenarioStepDto from a dict
normalized_scenario_step_dto_from_dict = NormalizedScenarioStepDto.from_dict(normalized_scenario_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


