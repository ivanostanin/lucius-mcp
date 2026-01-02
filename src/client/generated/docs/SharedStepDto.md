# SharedStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**archived** | **bool** |  | [optional] 
**attachments_count** | **int** |  | [optional] 
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**steps_count** | **int** |  | [optional] 
**test_cases_count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.shared_step_dto import SharedStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of SharedStepDto from a JSON string
shared_step_dto_instance = SharedStepDto.from_json(json)
# print the JSON string representation of the object
print(SharedStepDto.to_json())

# convert the object into a dict
shared_step_dto_dict = shared_step_dto_instance.to_dict()
# create an instance of SharedStepDto from a dict
shared_step_dto_from_dict = SharedStepDto.from_dict(shared_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


