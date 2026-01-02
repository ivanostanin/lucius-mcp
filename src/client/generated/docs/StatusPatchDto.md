# StatusPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**color** | **str** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.status_patch_dto import StatusPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of StatusPatchDto from a JSON string
status_patch_dto_instance = StatusPatchDto.from_json(json)
# print the JSON string representation of the object
print(StatusPatchDto.to_json())

# convert the object into a dict
status_patch_dto_dict = status_patch_dto_instance.to_dict()
# create an instance of StatusPatchDto from a dict
status_patch_dto_from_dict = StatusPatchDto.from_dict(status_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


