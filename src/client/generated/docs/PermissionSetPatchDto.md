# PermissionSetPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**permissions** | [**List[PermissionDto]**](PermissionDto.md) |  | 

## Example

```python
from src.client.generated.models.permission_set_patch_dto import PermissionSetPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of PermissionSetPatchDto from a JSON string
permission_set_patch_dto_instance = PermissionSetPatchDto.from_json(json)
# print the JSON string representation of the object
print(PermissionSetPatchDto.to_json())

# convert the object into a dict
permission_set_patch_dto_dict = permission_set_patch_dto_instance.to_dict()
# create an instance of PermissionSetPatchDto from a dict
permission_set_patch_dto_from_dict = PermissionSetPatchDto.from_dict(permission_set_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


