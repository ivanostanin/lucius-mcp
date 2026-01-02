# PermissionSetDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**permissions** | [**List[PermissionDto]**](PermissionDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.permission_set_dto import PermissionSetDto

# TODO update the JSON string below
json = "{}"
# create an instance of PermissionSetDto from a JSON string
permission_set_dto_instance = PermissionSetDto.from_json(json)
# print the JSON string representation of the object
print(PermissionSetDto.to_json())

# convert the object into a dict
permission_set_dto_dict = permission_set_dto_instance.to_dict()
# create an instance of PermissionSetDto from a dict
permission_set_dto_from_dict = PermissionSetDto.from_dict(permission_set_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


