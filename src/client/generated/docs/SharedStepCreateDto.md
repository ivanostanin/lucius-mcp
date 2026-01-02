# SharedStepCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.shared_step_create_dto import SharedStepCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of SharedStepCreateDto from a JSON string
shared_step_create_dto_instance = SharedStepCreateDto.from_json(json)
# print the JSON string representation of the object
print(SharedStepCreateDto.to_json())

# convert the object into a dict
shared_step_create_dto_dict = shared_step_create_dto_instance.to_dict()
# create an instance of SharedStepCreateDto from a dict
shared_step_create_dto_from_dict = SharedStepCreateDto.from_dict(shared_step_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


